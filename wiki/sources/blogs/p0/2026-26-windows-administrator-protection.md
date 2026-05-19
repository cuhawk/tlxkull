---
source: p0
source_url: https://projectzero.google/2026/26/windows-administrator-protection.html
title: "Bypassing Windows Administrator Protection - Project Zero"
description: "A headline feature introduced in the latest release of Windows 11, 25H2 is Administrator Protecti..."
---

A headline feature introduced in the latest release of Windows 11, 25H2 is [Administrator Protection](https://blogs.windows.com/windowsdeveloper/2025/05/19/enhance-your-application-security-with-administrator-protection/). The goal of this feature is to replace User Account Control (UAC) with a more robust and importantly, securable system to allow a local user to access administrator privileges only when necessary.

This blog post will give a brief overview of the new feature, how it works and how it’s different from UAC. I’ll then describe some of the security research I undertook while it was in the insider preview builds on Windows 11. Finally I’ll detail one of the nine separate vulnerabilities that I found to bypass the feature to silently gain full administrator privileges. All the issues that I reported to Microsoft have been fixed, either prior to the feature being officially released (in optional update [KB5067036](https://support.microsoft.com/en-gb/topic/october-28-2025-kb5067036-os-builds-26200-7019-and-26100-7019-preview-ec3da7dc-63ba-4b1d-ac41-cf2494d2123a)) or as subsequent security bulletins.

_Note: As of 1st December 2025 the Administrator Protection feature has been disabled by Microsoft while an application compatibility issue is dealt with. The issue is unlikely to be related to anything described in this blog post so the analysis doesn’t change._

## The Problem Administration Protection is Trying to Solve

UAC was introduced in Windows Vista to facilitate granting a user administrator privileges temporarily, while the majority of the user’s processes run with limited privileges. Unfortunately, due to the way it was designed, it was quickly apparent it didn’t represent a hard security boundary, and Microsoft downgraded it to a security feature. This was an important change as it made it no longer a priority to fix bypasses of the UAC which allowed a limited process to silently gain administrator privileges.

The main issue with the design of UAC was that both the limited user and the administrator user were the same account just with different sets of groups and privileges. This meant they shared profile resources such as the user directory and [registry hive](https://www.tiraniddo.dev/2017/05/exploiting-environment-variables-in.html). It was also possible to open an administrators process’ access token and [impersonate it](https://www.tiraniddo.dev/2017/05/reading-your-way-around-uac-part-1.html) to grant administrator privileges as the impersonation permission checks didn’t originally consider if an access token was “elevated” or not, it just considered the user and the integrity level.

Even so, on Vista it wasn’t that easy to silently acquire administrator privileges as most routes still showed a prompt to the user. Unfortunately, Microsoft decided to reduce the number of elevation prompts a user would see when modifying system configuration and introduced an “auto-elevation” feature in Windows 7. Select Microsoft binaries could be opted in to be automatically elevated. However, it also meant that in some cases it was possible to repurpose the binaries to silently gain administrator privileges. It was possible to configure UAC to always show a prompt, but the default, which few people change, would allow the auto-elevation.

A good repository of known bypasses is the [UACMe](https://github.com/hfiref0x/UACME) tool which currently lists 81 separate techniques for gaining administrator privileges. A proportion of those have been fixed through major updates to the OS, even though Microsoft never officially acknowledges when a UAC bypass is fixed. However, there still exist silent bypasses that impact the latest version of Windows 11 that remain unfixed.

The fact that malware is regularly using known bypasses to gain administrator privileges is what Administrator Protection aims to solve. If the weaknesses in UAC can be mitigated then it can be made a secure boundary which not only requires more work to bypass but also any vulnerabilities in the implementation could be fixed as security issues.

In fact there is already a more secure mechanism that UAC can use that doesn’t suffer from many of the problems of the so-called “admin approval” elevation. This mechanism is used when the user is not a member of the administrators group, it’s referred to as “over-the-shoulder” elevation. This mechanism requires a user to know the credentials of a local administrator user which must be input into the UAC elevation prompt. It’s more secure than admin approval elevation for the following reasons:

- The profile data is no longer shared, which prevents the limited user from modifying files or registry keys which might be used by an elevated administrator process.
- It’s no longer possible to get an access token for the administrator user and impersonate it as limited users cannot impersonate other user accounts.
- Auto-elevation of Microsoft binaries is not supported, all elevation requests require confirmation through a prompt.

Unfortunately, the mechanism is difficult to use securely in practice as sharing the credentials to another local administrator account would be a big risk. Thus it’s primarily useful as a means for technical support where a sysadmin types in the credentials over the user’s shoulder.

Administrator Protection improves on over-the-shoulder elevation by using a separate shadow administrator account that is automatically configured by the UAC service. This has all the benefits of over-the-shoulder elevation plus the following:

- The user does not need to know the credentials for the shadow administrator as there aren’t any. Instead UAC can be configured to prompt for the limited user’s credentials, including using biometrics if desired.
- A separate local administrator account isn’t required, only the user needs to be configured to be a member of the administrators group making deployment easier.

While Microsoft is referring to Administrator Protection as a separate feature it can really be considered a third UAC mechanism as it uses the same infrastructure and code to perform elevation, just with some tweaks. However, the feature replaces admin-approval mode so you can’t use the “legacy” mode and Administrator Protection at the same time. If you want to enable it there’s currently no UI to do so but you can [modify the local security policy](https://techcommunity.microsoft.com/blog/windows-itpro-blog/administrator-protection-on-windows-11/4303482) to do so.

The big question, will this make UAC a securable boundary so malware no longer has a free ride? I guess we better take a look and find out.

## Researching Administrator Protection

I typically avoid researching new Windows features before they’re released. It hasn’t been a good use of time in the past where I’ve found a security issue in a new feature during the insider preview stages only for that bug to be due to temporary code that is subsequently removed. Also if security issues are fixed in the insider preview stage they do not result in a security bulletin, making it harder to track when something is fixed. Therefore, there’s little incentive to research features until they are released when I can be confident any bugs that are discovered are real security issues and they’re fixed in a timely manner.

This case was slightly different, Microsoft reached out to me to see if I wanted to help them find issues in the implementation during the insider preview stage. No doubt part of the reason they reached out was my history of finding complex logical UAC bypasses. Also, I’d already taken a brief look and noted that the feature was still vulnerable to a few well known public bypasses such as my abuse of [loopback Kerberos](https://www.tiraniddo.dev/2022/03/bypassing-uac-in-most-complex-way.html).

I agreed to look at a design document and provide feedback without doing a full “pentest”. However, if I did find issues, considering the goal was for Administration Protection to be a securable boundary I was assured that they would be fixed through a bulletin, or at least would be remediated before the final release of the feature.

The Microsoft document provided an overview, but not all design details. For example, I did have a question around what the developers considered the security boundary. In keeping with the removal of auto-elevation I made the assumption that bypassing the boundary would require one or more of the following:

- Compromising the shadow administrators profile, such as writing arbitrary files or registry keys.
- Hijacking an existing process running as the shadow administrator.
- Get a process executing as an administrator without showing a prompt.

The prompt being a boundary is important, there’s a number of UAC bypasses, such as those which rely on elevated COM objects that would still work in Administrator Protection. However as auto-elevation is no longer permitted they will always show a prompt, therefore these are not considered bypasses. Of course, what is shown in the prompt, such as the executable being elevated, doesn’t necessarily correlate with the operation that is about to be performed with administrator rights.

In the document there was some lack of consideration of some associated UAC features such as UI Access processes (this will be discussed in part 2 of this series) but even so some descriptions stuck out to me. Therefore, I couldn’t help myself and decided to at least take a look at the current implementation in the canary build of insider preview. This research was a mix of reverse engineering of the UAC service code in `appinfo.dll` as well as behavioral analysis.

At the end of the research I found [9 separate](https://project-zero.issues.chromium.org/issues?q=reporter:forshaw@google.com%20title:%22administrator%20protection%22) means to bypass the feature and silently gain administrator privileges. Some of the bypasses were long standing UAC issues with publicly available test cases. Others were due to implementation flaws in the feature itself. But the most interesting bug class was where there wasn’t a bug at all, until the rest of the OS got involved.

Let’s dive into this most interesting bypass I identified during the research. If you want to skip ahead you can read the full details on the [issue tracker](https://project-zero.issues.chromium.org/issues/432313668). This issue is interesting, not just because it allowed me to bypass the protection but also because it was a potential UAC bypass that I had known about for many years, but only became practically exploitable because of the introduction of this feature.

## Logon Sessions

First a little bit of background knowledge to understand the vulnerability. When a user authenticates to a Windows system successfully they’re assigned a unique [logon session](https://learn.microsoft.com/en-us/windows/win32/secauthn/lsa-logon-sessions). This session is used to control the information about the user, for example it keeps a copy of the user’s credentials so that they can be used for network authentication.

The logon session is added as a reference in the access token created during the logon process, so that it can be easily referred to during any kernel operations using the token. You can find the unique 64-bit authentication ID for the session by querying the token using the `NtQueryInformationToken` system call. In UAC, separate logon sessions are assigned to the limited and the linked administrator access tokens as shown in the following script where you can observe that the limited token and linked token have distinct authentication ID LUID values:

```
# Get authentication ID of current token
PS> Get-NtTokenId -Authentication
LUID
----
00000000-11457F17

# Query linked administrator token and get its authentication ID.
PS> $t = Get-NtToken -Linked
PS> Get-NtTokenId -Authentication -Token $t
LUID
----
00000000-11457E9E
```

One important place the logon session is referenced by the kernel is when looking up DOS drive letters. From the kernels perspective drive letters are stored in a special object directory `\??`. When this path is looked up by the kernel it’ll first see if there’s a logon session specific directory to check, this is stored under the path `\Sessions\0\DosDevices\X-Y`, where X-Y is the hexadecimal representation of the authentication ID for the logon session. If the drive letter symbolic link isn’t found in that directory the kernel falls back to checking the `\GLOBAL??` directory. You can observe this behavior by opening the `\??` object directory using the `NtOpenDirectoryObject` system call as shown:

```
PS> $d = Get-NtDirectory "\??"
PS> $d.FullPath
\Sessions\0\DosDevices\00000000-11457f17
```

It’s [well known](https://project-zero.issues.chromium.org/issues/42451540) that if you can write a symbolic link to a DOS device object directory you can hijack the `C:` drive of any process running with that access token in that logon session. Even though the `C:` drive is defined in the global object directory, the logon session specific directory is checked first and so it can be overridden.

If a user can write into another logon session’s DOS device object directory they can redirect any file access to the system drive. For example you could redirect system DLL loading to force arbitrary code to run in the context of a process running in that logon session. In the case of UAC this isn’t an issue as the separate DOS device object directories have different access control and therefore the limited user can’t hijack the `C:` drive of an administrator process. The access control for the administrator’s DOS device object directory is shown below:

```
PS> Get-NtTokenSid
Name           Sid
----           ---
DOMAIN\user    S-1-5-21-5242245-89012345-3239842-1001

PS> $d = Get-NtDirectory "\??"
PS> Format-NtSecurityDescriptor $d -Summary
<Owner> : BUILTIN\Administrators
<Group> : DOMAIN\Domain Users
<DACL>
NT AUTHORITY\SYSTEM: (Allowed)(ObjectInherit, ContainerInherit)(Full Access)
BUILTIN\Administrators: (Allowed)(ObjectInherit, ContainerInherit)(Full Access)
BUILTIN\Administrators: (Allowed)(None)(Full Access)
CREATOR OWNER: (Allowed)(ObjectInherit, ContainerInherit, InheritOnly)(GenericAll)
```

## Creating a DOS Device Object Directory

A question you might have is who creates this DOS device object directory? It turns out the kernel creates it on demand when the directory is first accessed. The code to do the creation is in `SeGetTokenDeviceMap`, which looks roughly like the following:

```
NTSTATUS SeGetTokenDeviceMap(PTOKEN Token, PDEVICE_MAP *ppDeviceMap) {
  *ppDeviceMap = Token->LogonSession->pDeviceMap;
  if (*ppDeviceMap) {
    return STATUS_SUCCESS;
  }
  WCHAR path[64];
    swprintf_s(
      path,
      64,
      L"\\Sessions\\0\\DosDevices\\%08x-%08x",
      Token->AuthenticationId.HighPart,
      Token->AuthenticationId.LowPart);
  PUNICODE_STRING PathString;
  RtlInitUnicodeString(&PathString, path);
  OBJECT_ATTRIBUTES ObjectAttributes;
  InitializeObjectAttributes(&ObjectAttributes,
                             &PathString,
                             OBJ_CASE_INSENSITIVE |
                             OBJ_OPENIF |
                             OBJ_KERNEL_HANDLE |
                             OBJ_PERMANENT, 0, NULL);
  HANDLE Handle;
  NTSTATUS status = ZwCreateDirectoryObject(&Handle,
                                            0xF000F,
                                            &ObjectAttributes);
  if (NT_ERROR(status)) {
    return status;
  }
  status = ObpSetDeviceMap(Token->LogonSession, Handle);
  if (NT_ERROR(status)) {
    return status;
  }
  *ppDeviceMap = Token->LogonSession->pDeviceMap;
  return STATUS_SUCCESS;
}
```

One thing you might notice is that the object directory is created using the `ZwCreateDirectoryObject` system call. One important security detail of using a `Zw` system call in the kernel is it disables security access checking unless the optional `OBJ_FORCE_ACCESS_CHECK` flag is set in the `OBJECT_ATTRIBUTES`, which isn’t the case here.

Bypassing access checking is necessary for this code to function correctly; let’s look at the access control of the `\Sessions\0\DosDevices` directory.

```
PS> Format-NtSecurityDescriptor -Path \Sessions\0\DosDevices -Summary
<Owner> : BUILTIN\Administrators
<Group> : NT AUTHORITY\SYSTEM
<DACL>
NT AUTHORITY\SYSTEM: (Allowed)(ObjectInherit, ContainerInherit)(Full Access)
BUILTIN\Administrators: (Allowed)(ObjectInherit, ContainerInherit)(Full Access)
CREATOR OWNER: (Allowed)(ObjectInherit, ContainerInherit, InheritOnly)(GenericAll)
```

The directory cannot be written to by a non-administrator user, but as this code is called in the security context of the user it needs to disable access checking to create the directory as it can’t be sure the user is an administrator. Importantly the access control of the directory has an inheritable rule for the special `CREATOR OWNER` group granting full access. This is automatically replaced by the assigned owner of the access token used during object creation.

Therefore even though the access checking has been disabled the final directory that’s created can be accessed by the caller. This explains how the UAC administrator DOS device object directory blocks access to the limited user. The administrator token is created with the local administrators group set as its owner and so that’s what `CREATOR OWNER` is replaced with. However, the limited user can only set their own SID as the owner and so it just grants access to the user.

How is this useful? I noticed a long time ago that this behavior is a potential UAC bypass, in fact it’s a potential EoP, but UAC bypass was the most likely outcome. Specifically it’s possible to get a handle to the access token for the administrator user by calling `NtQueryInformationToken` with the `TokenLinkedToken` information class. For security reasons this token is limited to `SecurityIdentification` impersonation level so it can’t be used to grant access to any resources.

However if you impersonate the token and open the `\??` directory then the kernel will call `SeGetTokenDeviceMap` using the identification token and if it’s not currently created it’ll use `ZwCreateDirectoryObject` to create the DOS device object directory. As access checking is disabled the creation will still succeed, however once it’s created the kernel will do an access check for the directory itself and will fail due to the identification token being impersonated.

This might not seem to get us very much, while the directory is created it’ll use the owner from the identification token which would be the local administrator’s group. But we can change the token’s owner SID to the user’s SID before impersonation, as that’s a permitted operation. Now the final DOS device object directory will be owned by the user and can be written to. As there’s only a single logon session used for the administrator side of UAC then any elevated process can now have its `C:` directory hijacked.

There’s just one problem with this as a UAC bypass, I could never find a scenario where the limited user got code running before any administrator process was created. Once the process was created and running there’s almost a certainty that some code would open a file and therefore access the `\??` directory. By the time the limited user has control the DOS device object directory has already been created and assigned the expected access control. Still as UAC is not a security boundary there was no point reporting it, so I filed this behavior away for another day in case it ever became relevant.

## Bypassing Administrator Protection

Fast forward to today, and along comes Administrator Protection. For reasons of compatibility Microsoft made calling `NtQueryInformationToken` with the `TokenLinkedToken` information class still returns an identification handle to the administrator token. But in this case it’s the shadow administrator’s token instead of the administrator version of the user’s token. But a crucial difference is while for UAC this token is the same every time, in Administrator Protection the kernel calls into the LSA and authenticates a new instance of the shadow administrator. This results in every token returned from `TokenLinkedToken` having a unique logon session, and thus does not currently have the DOS device object directory created as can be seen below:

```
PS> $t = Get-NtToken -Linked
PS> $auth_id = Get-NtTokenId -Authentication -Token $t
PS> $auth_id
LUID
----
00000000-01C23BB3

PS> Get-NtDirectory "\Sessions\0\DosDevices\$auth_id"
Get-NtDirectory : (0xC0000034) - Object Name not found.
```

While in theory we can now force the creation of the DOS device object directory, unfortunately this doesn’t help us much. As the UAC service also uses `TokenLinkedToken` to get the token to create the new process with it means every administrator process currently running or will run in the future doesn’t share logon sessions, thus doesn’t share the same DOS device object directories and we can’t hijack their `C:` drives using the token we queried in our own process.

To exploit this we’d need to use the token for an actual running process. This is possible, because when creating an elevated process it can be started suspended. With this suspended process we can open the process token for reading, duplicate it as an identification token then create the DOS device object directory while impersonating it. The process can then be resumed with its hijacked `C:` drive.

There’s only two problems with this as a bypass, first creating an elevated process suspended will require clicking through an elevation prompt. For UAC with auto-elevation this wasn’t a problem, but for Administrator Protection it will always prompt, and showing a prompt isn’t considered to be crossing the security boundary. There are ways around this, for example the UAC service exposes the `RAiProcessRunOnce` API which will run an elevated binary silently. The only problem is the process isn’t suspended and so you’d have to win a race condition to open the process and perform the bypass before any code runs in that process. This is something which should be doable, say by playing with thread priorities to prevent the new process’ main thread from being scheduled.

The second issue seems more of a deal breaker. When setting the owner for an access token it will only allow you to set a SID that’s either the user SID for the token, or a member group that has the `SE_GROUP_OWNER` flag set. The only group with the owner flag is the local administrators group, and of course the shadow administrator’s SID differs from the limited user’s. Therefore setting either of these SIDs as the owner doesn’t help us when it comes to accessing the directory after creation.

Turns out this isn’t a problem as I was not telling the whole truth about the owner assignment process. When building the access control for a new object the kernel doesn’t trust the impersonation token if it’s at identification level. This is for a good security reason, an identification token is not supposed to be usable to make access control decisions, therefore it makes no sense to assign its owner when creating the object. Instead the kernel uses the primary token of the process to make that decision, and so the assigned owner is the limited user’s SID. In fact setting the owner SID for the UAC bypass was never necessary, it was never used. You can verify this behavior by creating an object without a name so that it can be created while impersonating an identification token and checking the assigned owner SID:

```
PS> $t = Get-NtToken -Anonymous
# Impersonate anonymous token and create directory
PS> $d = Invoke-NtToken $t { New-NtDirectory }
PS> $d.SecurityDescriptor.Owner.Sid.Name
NT AUTHORITY\ANONYMOUS LOGON
# Impersonate at identification level
PS> $d = Invoke-NtToken $t -ImpersonationLevel Identification {
      New-NtDirectory
}
PS> $d.SecurityDescriptor.Owner.Sid.Name
DOMAIN\user
```

One final question you might have is how come creating a process with the shadow admin’s token doesn’t end up accessing some DOS drive’s file resource as that user thus causing the DOS device object directory to be created? The implementation of the `CreateProcessAsUser` API runs all its code in the security context of the caller, regardless of what access token is being assigned so by default it wouldn’t ever open a file under the new logon session.

However, if you know about how to securely create a process in a system service you might expect that you’re supposed to impersonate the new token over the call to `CreateProcessAsUser` to ensure you don’t allow a user to create a process for an executable file they can’t access. The UAC service is doing this correctly, so surely it must have accessed a drive to create the process and the DOS device object directory should have been created, why isn’t it?

In a small irony what’s happening is the UAC service is tripping over a recently introduced security mitigation to prevent the hijack of the `C:` drive when impersonating a low privileged user in a system service. This mitigation kicks in if the caller of a system call is the `SYSTEM` user and it’s trying to access the `C:` drive. This was added by Microsoft in response to multiple vulnerabilities in manifest file parsing, if you want an overview [here’s a video](https://www.youtube.com/watch?v=H03b0UaogVs) of the talk me and Maddie Stone did at OffensiveCon 23 describing some of the attack surface.

It just so happens that the UAC service is running as `SYSTEM` and as long as the elevated executable is on the `C:` drive, which is very likely, the mitigation ignores the impersonated token’s DOS device object directory entirely. Thus `SeGetTokenDeviceMap` never gets calls and so the first time a file is accessed under the logon session is once the process is up and running. As long as we can perform the exploit before the new process touches a file we can create the DOS device object directory and redirect the process’ `C:` drive.

To conclude, the steps to exploit this bypass is as follows:

1. Spawn a shadow admin process through `RAiProcessRunOnce`, which will run the `runonce.exe` from the `C:` drive.
2. Open the new process before it has accessed a file resource, and query the primary token.
3. Duplicate the token to an identification token.
4. Force the DOS device object directory to be created while impersonating the shadow admin token. This can be done by opening `\??` through a call to `NtOpenDirectoryObject`.
5. Create a C: drive symlink in the new DOS device directory to hijack the system drive.
6. Let the process resume and wait for a redirected DLL to be loaded.

## Final Thoughts

The bypass was interesting because it’s hard to point to the specific bug that causes it. The vulnerability is a result of 5 separate OS behaviors:

- The Administrator Protection feature changes to the `TokenLinkedToken` query generates a new logon session for every shadow admin token.
- The per-token DOS device directory is lazily initialized for each new logon session meaning when the linked token is first created the directory does not currently exist.
- The kernel creates the DOS device directory when it’s accessed by using `Zw` functions, which disables access checking. This allows a limited user to impersonate the shadow admin token at identification level and create the directory by opening `\??`.
- If a thread impersonates a token at identification level any security descriptor assignment takes the owner SID from the primary token, not the impersonation token. This results in the limited user being granted full access to the shadow admin token’s DOS device object directory.
- The DOS device object directory isn’t already created once the low-privileged user gets access to the process token because of the security mitigation which disables the impersonated DOS device object directory when opening files from the `C:` drive in a `SYSTEM` process.

I don’t necessarily blame Microsoft for not finding this issue during testing. It’s a complex vulnerability with many moving pieces. It’s likely I only found it because I knew about the weird behavior when creating the DOS device object directory.

The fix Microsoft implemented was to prevent creating the DOS device object directory when impersonating a shadow administrator token at identification level. As this fix was added into the final released build as part of the optional update KB5067036 it doesn’t have a security bulletin associated with it. I would like to thank the Administrator Protection team and MSRC for the quick response in fixing all the issues and demonstrating that this feature will be taken seriously as a security boundary. I’d also like to thank them for providing additional information such as the design document which aided in the research.

As for my views on Administrator Protection as a feature, I feel that Microsoft have not been as bold as they could have been. Making small tweaks to UAC resulted in carrying along the almost 20 years of unfixed bypasses which manifest as security vulnerabilities in the feature. What I would have liked to have seen was something more configurable and controllable, perhaps a proper version of [sudo](https://www.tiraniddo.dev/2024/02/sudo-on-windows-quick-rundown.html) or Linux capabilities where a user can be granted specific additional access for certain tasks.

I guess app compatibility is ultimately the problem here, Windows isn’t designed for such a radical change. I’d have also liked to have seen this as a separate configurable mode rather than replacing admin-approval completely. That way a sysadmin could choose when people are opted in to the new model rather than requiring everyone to use it.

I do think it improves security over admin-approval UAC assuming it becomes enabled by default. It presents a more significant security boundary that should be defendable unless more serious design issues are discovered. I expect that malware will still be able to get administrator privileges even if that’s just by forcing a user to accept the elevation prompt, but any silent bypasses they might use should get fixed which would be a significant improvement on the current situation. Regardless of all that, the safest way to use Windows is to never run as an administrator, with any version of UAC. And ideally avoid getting malware on your machine in the first place.