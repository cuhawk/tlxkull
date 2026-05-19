---
source: p0
source_url: https://projectzero.google/2019/03/windows-kernel-logic-bug-class-access.html
title: "Windows Kernel Logic Bug Class: Access Mode Mismatch in IO Manager - Project Zero"
description: "Posted by James Forshaw, Project ZeroThis blog post is an in-depth look at an interesting logic b..."
---

Posted by James Forshaw, Project Zero

This blog post is an in-depth look at an interesting logic bug class in the Windows Kernel and what I did to try to get it fixed with our partners at Microsoft. The maximum impact of the bug class is local privilege escalation if kernel and driver developers don’t take into account how the IO manager operates when accessing device objects. This blog discusses how I discovered the bug class and the technical background. For more information about the further investigation, fixing and avoiding writing new code with the bug class refer to MSRC’s [blog post](https://blogs.technet.microsoft.com/srd/2019/03/14/local-privilege-escalation-via-the-windows-i-o-manager-a-variant-finding-collaboration/).

# Technical Background

I first stumbled upon the bug class while trying to exploit [issue 779](https://bugs.chromium.org/p/project-zero/issues/detail?id=779). This issue was a file TOCTOU which bypassed the [custom font loading mitigation policy](https://docs.microsoft.com/en-us/windows/security/threat-protection/block-untrusted-fonts-in-enterprise). The mitigation policy was introduced in Windows 10 to limit the impact of exploitable font memory corruption vulnerabilities. Normally it’d be trivial to exploit a file TOCTOU issue using a combination of file and Object Manager symbolic links. An exploit using symbolic links worked as a normal user, but not inside a sandbox. Rather than spend too much time on this low-impact issue, I exploited it without symbolic links using Shadow Object Directories and Microsoft fixed it as [CVE-2016-3219](https://docs.microsoft.com/en-us/security-updates/SecurityBulletins/2016/ms16-074). I added a note of the unexpected behavior to my list of topics to follow up on at a later date.

Fast forward over a year I decided to go back and take a look at the unexpected behavior in more depth. The code which was failing was similar to the following:

HANDLE OpenFilePath(LPCWSTR pwzPath){

UNICODE\_STRING Path;

OBJECT\_ATTRIBUTES ObjectAttributes;

HANDLE FileHandle;

NTSTATUS status;

RtlInitUnicodeString(&Path, pwzPath);

InitializeObjectAttributes(&ObjectAttributes,

&Path,

                             OBJ\_KERNEL\_HANDLE \| OBJ\_CASE\_INSENSITIVE);

status = IoCreateFile(

&FileHandle,

               GENERIC\_READ,

&ObjectAttributes,

// ...

               FILE\_OPEN,

               FILE\_NON\_DIRECTORY\_FILE,

// ...

               IO\_NO\_PARAMETER\_CHECKING \| IO\_FORCE\_ACCESS\_CHECK);

if(NT\_ERROR(status))

returnNULL;

return FileHandle;

}

When this code tries to open a file with an Object Manager symbolic link in the path the call to [IoCreateFile](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/wdm/nf-wdm-iocreatefile) failed with STATUS\_OBJECT\_NAME\_NOT\_FOUND. Further digging led me to discover the source of the error in ObpParseSymbolicLink, which looks like the following:

NTSTATUS ObpParseSymbolicLink(POBJECT\_SYMBOLIC\_LINK Object,

PACCESS\_STATE AccessState,

KPROCESSOR\_MODE AccessMode){

if(Object->Flags &SANDBOX\_FLAG

&&!RtlIsSandboxedToken(AccessState->SubjectSecurityContext, AccessMode))

returnSTATUS\_OBJECT\_NAME\_NOT\_FOUND;

// ...

}

The failing check is part of the [symbolic link mitigations](https://projectzero.google/2015/08/windows-10hh-symbolic-link-mitigations.html) Microsoft introduced in Windows 10. I was creating the symbolic link inside a sandbox which would set SANDBOX\_FLAG in the object’s structure. When parsing the symbolic link while opening the font file this check is made. With the sandbox flag set the kernel also calls RtlIsSandboxedToken to determine if the caller is still inside a sandbox. As the call to open the font file is in a sandboxed process thread RtlIsSandboxedToken should return TRUE, and the function would continue. Instead it was returning FALSE, which made the kernel think the call was coming from a more privileged process and returns STATUS\_OBJECT\_NAME\_NOT\_FOUND to mitigate any exploitation.

At this point I understood how my exploit was failing, and yet I didn’t understand why. Specifically I didn’t understand why RtlIsSandboxToken was returning FALSE. Digging into the function gave me an important insight:

BOOLEAN RtlIsSandboxedToken(PSECURITY\_SUBJECT\_CONTEXT SubjectSecurityContext,

KPROCESSOR\_MODE AccessMode){

NTSTATUS AccessStatus;

ACCESS\_MASK GrantedAccess;

if(AccessMode == KernelMode)

return FALSE;

if(SeAccessCheck(

         SeMediumDaclSd,

         SubjectSecurityContext,

         FALSE,

         READ\_CONTROL,

0,

NULL,

&RtlpRestrictedMapping,

         AccessMode,

&GrantedAccess,

&AccessStatus)){

return FALSE;

}

return TRUE;

}

The important parameter is AccessMode, which is of type KPROCESSOR\_MODE and can be set to one of two values UserMode or KernelMode. If the AccessMode parameter was set to the value KernelMode then the function would automatically return FALSE indicating the current caller is not in a sandbox. Breakpointing on this function in a kernel debugger confirmed that AccessMode was set to KernelMode when being called from my exploit. If this parameter was always set to KernelMode how would RtlIsSandboxToken ever return TRUE? To understand how the kernel is functioning let’s go into more depth on what the AccessMode parameter represents.

## Previous Access Mode

Every thread in Windows has a [previous access mode](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/previousmode) associated with it. This previous access mode is stored in the PreviousMode member of the KTHREAD structure. The member is accessed by third-parties using [ExGetPreviousMode](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/wdm/nf-wdm-exgetpreviousmode) and returns the KPROCESSOR\_MODE type. The previous access mode is set to UserMode if a user mode thread is running kernel code due to a system call transition. As an example the following diagram shows a call from a user mode application to the system call NtOpenFile, via a system call dispatch stub function in NTDLL.

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEidx0b_s600_User+Access+Modes.jpg)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEidx0b_s637_User+Access+Modes.jpg)

Note how the previous mode is always set to UserMode even when code is executing inside the NtOpenFile system call in the kernel memory space. In contrast, KernelMode is set if the thread is a system thread (in the System process) or due to a system call transition from kernel mode. The following diagram shows the transition when a device driver (which is already running in kernel mode) calls the ZwOpenFile system call, which results in executing NtOpenFile.

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiVDkQ_s600_Kernel+Access+Modes.jpg)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiVDkQ_s793_Kernel+Access+Modes.jpg)

In the diagram a user mode application calls a function inside a device driver, for example using the NtFsControlFile system call. The previous mode equals UserMode during the call to the device driver. However, if the device driver calls ZwOpenFile the kernel simulates a system call transition, this results in the previous mode being changed to KernelMode and the NtOpenFile system call code being executed.

From a security perspective the previous access mode influences two important but fundamentally different security checks in the kernel, Security Access Checking (SecAC) and Memory Access Checking (MemAC). SecAC is used for calls to APIs exposed by the [Security Reference Monitor](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/windows-kernel-mode-security-reference-monitor) such as [SeAccessCheck](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/wdm/nf-wdm-seaccesscheck) or [SePrivilegeCheck](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/ntifs/nf-ntifs-seprivilegecheck). These security APIs are used to determine if the caller has rights to access a resource. Commonly the APIs take an AccessMode parameter, if this parameter is KernelMode then the access checks pass automatically, which might be a security vulnerability if the resource couldn’t normally be accessed by a user. We already saw this use case in RtlIsSandboxToken, the API checked explicitly for AccessMode being KernelMode and returned FALSE. Even without the shortcut, by passing KernelMode to SeAccessCheck the call will succeed regardless of the caller’s access token and RtlIsSandboxToken would have returned FALSE.

MemAC is used to ensure the user application can’t pass pointers to a kernel address location. If the AccessMode is UserMode then all memory addresses passed to the system call/operation should be verified that they're less than MmUserProbeAddress or via functions such as ProbeForRead/ProbeForWrite. Again if this checking is incorrect privilege escalation could occur as the user could trick kernel code into reading or writing into privileged kernel memory locations. Note that not all kernel APIs perform MemAC, for example the SeAccessCheck assumes that the caller has already checked parameters, the AccessMode parameter is only used to determine whether to bypass the security check.

Storing the previous access mode on the thread creates a problem as there’s no way of differentiating between SecAC and MemAC for a kernel API. It’s possible for an API to disable SecAC intentionally and disable MemAC accidentally resulting in security issues and vice-versa. Let’s look in more detail how the IO Manager tries to solve this mismatched access checking issue.

## IO Manager Access Checking

The IO Manager exposes two main API groups for directly accessing files. The first APIs are the system calls NtCreateFile/ZwCreateFile or NtOpenFile/ZwOpenFile. The system calls are primarily for use by user-mode applications, but can be called from kernel mode if needed. The other APIs are exposed only for kernel mode callers, IoCreateFile and [IoCreateFileEx](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/ntddk/nf-ntddk-iocreatefileex).

If you compare the implementations of the two main APIs you find they’re simple forwarding wrappers around the internal function IopCreateFile. By default IopCreateFile uses the current thread’s previous mode to determine whether to perform MemAC and SecAC. For example when calling IopCreateFile via NtCreateFile from a user-mode process the kernel performs MemAC and SecAC as the previous mode will be UserMode. If kernel-mode calls ZwCreateFile then the previous mode is set to KernelMode and both SecAC and MemAC are disabled.

IoCreateFile can only be called from kernel mode code and there’s no syscall transition involved, therefore any calls will use whatever previous mode is set on the thread. If IoCreateFile is called from a thread with previous mode set to UserMode this means that SecAC and MemAC will be performed. Enforcing MemAC is especially problematic as it means that the kernel code can’t pass kernel mode pointers to IoCreateFile which would make the API very difficult to use. However the caller of IoCreateFile can’t just change the thread’s previous mode to KernelMode as then SecAC would be disabled.

IoCreateFile solves this problem by specifying special flags that can be passed via the Options parameter. This parameter is forwarded to IopCreateFile but is not exposed through the NtCreateFile system call. Going back to our font issue, WIN32K is calling IoCreateFile and passing the option flags IO\_NO\_PARAMETER\_CHECKING (INPC) and IO\_FORCE\_ACCESS\_CHECK (IFAC).

INPC is documented as:

“\[If specified\] the parameters for this call should not be validated before attempting to issue the create request. Driver writers should use this flag with caution as certain invalid parameters can cause a system failure. For more information, see Remarks.”

In the remarks section it expands further:

“The Options IO\_NO\_PARAMETER\_CHECKING flag can be useful if a driver is issuing a kernel-mode create request on behalf of an operation initiated by a user-mode application. Because the request occurs within a user-mode context, the I/O manager, by default, probes the supplied parameter values, which can cause an access violation if the parameters are kernel-mode addresses. This flag enables the caller to override this default behavior and avoid the access violation.”

This makes its purpose clear, it disables MemAC, allowing the kernel code to pass pointers into kernel memory as function parameters. As a byproduct it also disables most of the validation of the parameters, such as incompatible flag combinations being checked. There is a separate, not properly documented, flag IO\_CHECK\_CREATE\_PARAMETERS which turns back on just parameter flag checking, but not MemAC.

IFAC on the other hand is documented as:

“The I/O manager must check the create request against the file's security descriptor.”

This implies that the flag reenables SecAC. It makes sense if the caller was a system thread with previous mode set to KernelMode but why would we need to re-enable SecAC if we’re calling from UserMode? Here in lies the seeds to understanding the original unexpected behavior, as we can see in some simplified code from IopCreateFile.

NTSTATUS IopCreateFile(PHANDLE FileHandle,ACCESS\_MASK DesiredAccess,

POBJECT\_ATTRIBUTES ObjectAttributes,...,

                       ULONG Options){

KPROCESSOR\_MODE AccessMode;

if(Options & IO\_NO\_PARAMETER\_CHECKING){

    AccessMode = KernelMode;

}else{

    AccessMode = KeGetCurrentThread()->PreviousMode;

}

FILE\_PARSE\_CONTEXT ParseContext ={};

// Initialize other values

ParseContext->Options = Options;

return ObOpenObjectByName(

                  ObjectAttributes,

                  IoFileObjectType,

AccessMode,

NULL,

                  DesiredAccess,

&ParseContext,

&FileHandle);

}

This code shows that if INPC is specified then the AccessMode for all subsequent calls is set to KernelMode. Therefore specifying that option disables not just MemAC but also SecAC. It’s worth noting that the thread’s previous mode is not changed, just the AccessMode value which is passed forward to ObOpenObjectByName. IopCreateFile is delegating pointer checking to the Object Manager, therefore the only way it can achieve this is to kill all checking. Crucially IFAC is not checked, it’s only passed forward inside the parsing context structure, something for the rest of the IO manager to deal with.

This isn’t the end of the story just yet, it’s also possible to call ZwCreateFile and pass the special flag OBJ\_FORCE\_ACCESS\_CHECK (OFAC) inside the OBJECT\_ATTRIBUTES structure and ensure access checking is performed, even if the previous access mode is set to KernelMode. As you can’t pass in IFAC via ZwCreateFile and there’s no checking for the OFAC flag in IopCreateFile, it must be in ObOpenObjectByName. Actually it’s slightly deeper, first all the parameters are processed based on the AccessMode passed to ObOpenObjectByName, then ObpLookupObjectName is called which checks the OFAC flag, if it’s set then AccessMode is forced back to UserMode.

We can now finally understand why we got the unexpected behavior with opening the font file. Parsing the symbolic link happens inside the Object Manager, not the IO Manager, therefore has no knowledge of the IFAC flag. IopCreateFile has told the Object Manager to do all checks as if the previous access mode is KernelMode, so that’s the value passed to ObpParseSymbolicLink, which gets passed to RtlIsSandboxToken which rightly indicates it’s not running in a sandboxed process. However, once the file is actually opened the IFAC flag kicks in and ensures SecAC is still performed on the file. If the caller had also specified OFAC then the symbolic link would have worked, as the parsing would occur during the lookup operation which has been forced to UserMode.

This in itself is an interesting result, basically any operation which is called during the Object Manager parsing operation which trusts the value of AccessMode will disable security checks unless OFAC has been specified. However, that’s not the bug that this blog is about, for that we need to go even deeper to work out how IFAC works inside the IO Manager.

## IO Device Parsing

The Object Manager’s responsibility for opening a file ends once it finds a named device object in the Object Manager namespace. The Object Manager looks up the parse function for the Device type, which is IopParseDevice, then passes all the information it knows about. This includes the AccessMode value, which we know is set to KernelMode, the remaining path to parse and the parsing context buffer which includes the Options parameter. The IopParseDevice function does some security checks of its own, such as checking device traversal, allocates a new [IO Request Packet](https://msdn.microsoft.com/en-us/library/windows/hardware/ff550694(v=vs.85).aspx) (IRP) and calls the driver responsible for the device object.

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjBIJM_s600_Device+Request.jpg)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjBIJM_s838_Device+Request.jpg)

The IRP structure contains a RequestorMode field which reflects the AccessMode of the file operation. This reason to have a RequestorMode field is the IRP can be dispatched asynchronously. The thread which processes the IO operation might not be the thread which started the IO operation. You might guess now that this is where IFAC comes into play, perhaps the IO manager sets RequestorMode to UserMode? If you actually check this inside a kernel driver when accessed from IoCreateFile using INPC you’d find this field is still set to KernelMode, so it’s not the answer.

The operation type being performed and the operation’s specific parameters are passed in the [IO Stack Location](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/wdm/ns-wdm-_io_stack_location) structure which is located immediately after the IRP structure. In the case of opening a file the major operation type is [IRP\_MJ\_CREATE](https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/irp-mj-create) and uses the Create union field of the IO\_STACK\_LOCATION structure. This is where IFAC comes in, if the flag is specified to IopCreateFile then in the IO Stack Location’s Flags parameter, the new flag SL\_FORCE\_ACCESS\_CHECK(SFAC) will be set. It’s up to the file system driver to ensure it verifies this flag, and not rely on the RequestorMode being set to UserMode. The NTFS driver knows this, and has the following code:

KPROCESSOR\_MODE NtfsEffectiveMode(PIRP Irp){

PIO\_STACK\_LOCATION loc = IoGetCurrentIrpStackLocation(Irp);

if(loc->MajorOperation == IRP\_MJ\_CREATE

&& loc->Flags & SL\_FORCE\_ACCESS\_CHECK){

return UserMode;

}

else{

return Irp->RequestorMode;

}

}

The NtfsEffectiveMode is called by any operation which is going to perform a security related function. It ensures that SecAC is still performed even if the caller was in kernel mode, as long as the IFAC flag was passed. The NTFS filesystem driver is a fundamental part of the Windows OS, and has close interactions with the IO manager, so it’s unsurprising it knows to do the right thing. However, on Windows all drivers are filesystem drivers, even if they don’t explicitly implement a filesystem.

I thought it’d be interesting to find out how many Microsoft and third-party drivers actually did the right checks, or did they all just trust RequestorMode and base their security decisions on it?

## Defining the Bug Class

Finally we get to define the bug class. In order for a privilege escalation vulnerability to exist there needs to be two separate components.

1. A kernel mode Initiator (code which calls IoCreateFile or IoCreateFileEx) which sets the INPC and IFAC flags but doesn’t set OFAC. This could be in a driver or the kernel itself.

2. A vulnerable Receiver which uses RequestorMode during the handling of IRP\_MJ\_CREATE for a security decision but doesn’t also check the Flags for SFAC.


[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhqht3_s600_unnamed.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhqht3_s870_unnamed.png)

The following table summarises an API when the calling thread’s previous mode is set to UserMode. The table includes the state of the input options, INPC, IFAC and OFAC and the corresponding IRP’s RequestorMode and SFAC flag. I’ve highlighted when the calls are a useful initiator.

|     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- |
| Method | INPC | IFAC | OFAC | RequestorMode | SFAC | Initiator? |
| IoCreateFile | NO | NO | NO | User | NO | NO |
| IoCreateFile | YES | NO | NO | Kernel | NO | YES |
| IoCreateFile | YES | YES | NO | Kernel | YES | YES |
| IoCreateFile | N/A | N/A | YES | User | N/A | NO |
| IoCreateFileEx | NO | NO | NO | Kernel | NO | YES |
| IoCreateFileEx | YES | NO | NO | Kernel | NO | YES |
| IoCreateFileEx | YES | YES | NO | Kernel | YES | YES |
| IoCreateFileEx | N/A | N/A | YES | User | N/A | NO |

It’s worth noting that any calls where IFAC is not passed might be vulnerable to a privileged file access vulnerability as without the generated SFAC flag even NTFS would not perform security checks. There are other similar functions to IoCreateFile such as [FltCreateFileEx](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/fltkernel/nf-fltkernel-fltcreatefileex) which are used in special cases but they all have similar properties. Also notice in the table the rules are slightly different for IoCreateFileEx. While it’s not documented, IoCreateFileEx always passes the INPC option to IopCreateFile, therefore unless the OFAC flag is specified it will always run its operations with the previous access mode set to KernelMode.

The ideal Initiator is one which opens an arbitrary path from the user and gives full control over all parameters to IoCreateFile and the opened file handle is returned back to user mode. However, depending on the Receiver full control might not be necessary.

A Receiver could perform a number of actions when receiving the IRP. Common for file system drivers is to parse the remaining filename and perform some further action based on that such as opening a different file. Another possibility is parsing the Extended Attributes (EA) block and performing some action based on that. It might just be the case that opening the device object would normally require an access check which the setting of RequestorMode to KernelMode bypasses.

## Examples

Here’s some examples I’ve found of both Initiators and Receivers. This is based on code shipped with Windows 10 1709 which is two versions behind what’s available today (1809) but many of these examples still exist in the latest versions of Windows as well as Windows 7 and 8. All the examples are Microsoft code, so a third party developer probably has even less understanding of the behavior.

To discover these examples I didn’t use any special static analysis tooling, instead I just searched for them manually. I left deeper investigation to Microsoft.

### Receivers

Finding Receivers can be much harder than Initiators as there’s no imported function to search for which gives a clear signal to look for. Instead I looked for drivers which imported IoCreateDevice to ensure the driver is exposing a device of some sort. I then filtered the drivers' imported APIs to ones which took an explicit AccessMode parameter, such as SeAccessCheck or ObReferenceObjectByHandle. Of course this didn’t really limit the number of drivers very much so ultimately I had to manually analyze drivers which looked the most interesting. In my analysis the “real” file system drivers such as NTFS and FAT always seem to do the right thing.

#### WS2IFSL

While not always enabled this driver is used to create a file object which passes read/write requests to a user mode application using APCs. When creating a new object you can specify an EA with information to create either a Socket or a Process file. The APC is set up in the CreateProcessFile function based on the information in the EA. The driver uses RequestorMode without any further checks, this would allow the callback APC to execute in kernel mode. When creating a process file you also pass a handle to a thread which is opened for THREAD\_SET\_CONTEXT access for use with the APC. Setting KernelMode allows kernel handles to be used with call the call to ObReferenceObjectByHandle however as the thread has to be in the calling process this isn’t much of a benefit.

NTSTATUS DispatchCreate(DEVICE\_OBJECT\* DeviceObject, PIRP Irp){

PFILE\_FULL\_EA\_INFORMATION ea = Irp->AssociatedIrp.SystemBuffer;

PIO\_STACK\_LOCATION loc = IoGetCurrentIrpStackLocation(Irp);

if(ea->EaNameLength !=7)

return STATUS\_INVALID\_PARAMETER;

if(!memcmp(ea->EaName,"NifsSct",8))

return CreateSocketFile(lock->FileObject,Irp->RequestorMode, ea);

if(!memcmp(ea->EaName,"NifsPvd",8))

return CreateProcessFile(lock->FileObject,Irp->RequestorMode, ea);

// ...

}

To be exploitable a compatible initiator must be able to provide an EA on the process file. Then a socket file would need to be created which referenced that process file, and a read/write operation must be performed to force the APC to execute. On modern versions of Windows 10, you’ll also have to worry about SMEP and Kernel CFG. If you point the APC routine at a user mode address the kernel will bug check when it goes to execute the APC in KernelMode as shown in the following screenshot which I created by using a custom initiator to setup WS2IFSL.

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgGxhv_s600_unnamed+%281%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgGxhv_s1118_unnamed+%281%29.png)

#### NPFS

While NPFS correctly checks for the SFAC it does use the RequestorMode to determine if the caller is allowed to specify an arbitrary EA block. Normally when a named pipe is opened the driver records the calling PID and a session ID. This information can then be exposed via APIs such as [GetNamedPipeClientProcessId](https://docs.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-getnamedpipeclientprocessid). If the caller is UserMode then the code isn’t allowed to set the EA block, but if it's KernelMode an arbitrary EA block can be used which means the PID and session ID fields can be spoofed.

NTSTATUS NpCreateClientEnd(PIRP Irp,...){

// ...

PFILE\_FULL\_EA\_INFORMATION ea = Irp->AssociatedIrp.SystemBuffer;

PVOID Data;

SIZE\_T Length;

if(!NpLocateEa(ea,"ClientComputerName",&Data, Length))

return STATUS\_INVALID\_PARAMETER;

if(!IsValidEaString(Data, Length)\|\|Irp->RequestorMode != KernelMode)

return STATUS\_INVALID\_PARAMETER;

NpSetAttributeInList(Irp, CLIENT\_COMPUTER\_NAME, Data, Length);

NpLocateEa(ea,"ClientProcessId", Data, Length);

NpSetAttributeInList(Irp, CLIENT\_PROCESS\_ID, Data, Length);

NpLocateEa(ea,"ClientSessionId", Data, Length);

NpSetAttributeInList(Irp, CLIENT\_SESSION\_ID, Data, Length);

// ...

}

This behavior is used to allow the SMB driver to set the computer name field and session ID. If some service trusted this information it could be used to elevate privileges. To exploit this you’d need to be able to set an arbitrary EA as KernelMode, and to do something interesting you’d need to access the opened handle.

### Initiators

To find Initiators I looked in the kernel and drivers for any functions which called IoCreateFile et al and did basic inspection of the call parameters for the Options and object attributesflags. With suitable candidates I was able to do a closer inspection to determine what parameters the user could influence. Finding Initiators is relatively trivial once you understand the bug class as you can quickly narrow down targets just by looking for imported calls to the target methods.

#### NTOSKRNL NtSetInformationFile FileRenameInformation Class

When renaming a file you can specify an arbitrary path even though the file can’t be on a different volume to the original. The function IopOpenLinkOrRenameTarget is called to open the target path first using IoCreateFileEx passing INPC and normally IFAC (it also sets IO\_OPEN\_TARGET\_DIRECTORY but that’s not important for the operation). This initiator only allows you to specify the full path.

#### SMBv2 Server Driver

The SMB servers will open files on a share using IoCreateFileEx, for example in Smb2CreateFile. It specifies IFAC but not INPC because the call is made on a system thread so the previous access mode is already KernelMode. Normally it’s not possible to redirect the file creation to an arbitrary NT Object Manager path as the server passes a relative path to an open volume handle. While you could add a mount point to a directory on the file system and access the server locally the kernel intentionally limits the target device to a limited set of types.

if(ParseContext->ReparseTag == IO\_REPARSE\_TAG\_MOUNT\_POINT){

switch(ParseContext->TargetDevice){

case FILE\_DEVICE\_DISK:

case FILE\_DEVICE\_CD\_ROM:

case FILE\_DEVICE\_DISK:

case FILE\_DEVICE\_TAPE:

break;

default:

return STATUS\_IO\_REPARSE\_DATA\_INVALID;

}

}

There was a bug in the implementation which allows you to circumvent the device check which allows a local mount point to be used to redirect the SMB server to open any device file. The SMBv2 driver has special requirements when it comes to NTFS symbolic links, it must return the [link information to the client](https://msdn.microsoft.com/en-us/library/cc246542.aspx) for processing. To support the symbolic link feature the server passes the Options flag IO\_STOP\_ON\_SYMLINK as shown below.

NTSTATUS Smb2CreateFile(HANDLE VolumeHandle,PUNICODE\_STRING Name,...){

// ...

int ReparseCount =0;

OBJECT\_ATTRIBUTES ObjectAttributes;

ObjectAttributes.RootDirectory = VolumeHandle;

ObjectAttributes.ObjectName = Name;

IO\_STATUS\_BLOCK IoStatus ={};

do{

    status = IoCreateFileEx(

&FileHandle,

            DesiredAccess,

&ObjectAttributes,

&IoStatus,

...

IO\_STOP\_ON\_SYMLINK \| IO\_FORCE\_ACCESS\_CHECK

);

if(status == STATUS\_STOPPED\_ON\_SYMLINK){

UNICODE\_STRING NewName;

status = SrvGraftName(ObjectAttributes.ObjectName,

(PREPARSE\_DATA\_BUFFER)IoStatus.Information,&NewName);

if(status == STATUS\_STOPPED\_ON\_SYMLINK)

break;

      ObjectAttributes.RootDirectory =NULL;

      ObjectAttributes.ObjectName = NewName;

continue;

}

}while(ReparseCount++< MAXIMUM\_REPARSE\_COUNT);

// ...

}

If IoCreateFileEx returns STATUS\_STOPPED\_ON\_SYMLINK the server extracts the returned REPARSE\_DATA\_BUFFER structure from IO\_STATUS\_BLOCK and passes it to the SrvGraftName utility function. The reparse buffer could be either a mount point or a NTFS symbolic link. If it’s a symbolic link then SrvGraftName returns STATUS\_STOPPED\_ON\_SYMLINK again which allows the server to return the buffer to the caller. If the reparse buffer is a mount point then SrvGraftName builds a new absolute path based only on the string found in the REPARSE\_DATA\_BUFFER, it doesn’t check the destination device. The server reissues the open request with the new absolute path which can now point to any device on the system.

This initiator was the best I found during my analysis. You can specify almost all arguments to IoCreateFileEx including the EA buffer. This allows you to initialize a driver which requires an EA (such as WS2IFSL) which opens up a lot more attack surface. As it’s running on a system thread both the RequestorMode and the thread’s previous mode are set to KernelMode which might introduce other interesting attack surface.

While impressive it’s not an ideal Initiator, the opened device needs to support certain valid IRP’s such as IRP\_MJ\_GET\_INFORMATION\_FILE otherwise the server will not return a valid handle to the caller. Without this check it would be trivial to exploit WS2IFSL as you’d be able to perform a Read/Write operation to get an APC to execute in kernel mode. Even if you can get a handle back to the file the SMB Server intentionally limits the IO control codes you can send which limits many of the interesting things you could do with this vulnerability. Even so I considered this to be a serious issue, so I reported it directly to MSRC. It was fixed as [CVE-2018-0749](https://bugs.chromium.org/p/project-zero/issues/detail?id=1416) by using a special [Extra Creation Parameter](https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/using-extra-create-parameters-with-an-irp-mj-create-operation) which will filter out all other reparse points except for symbolic links.

# Next Steps

While I believed this to be a serious bug class, it turned out that finding a matching Initiator/Receiver pair was very difficult. In my research I didn’t find any pair which would give direct privilege escalation. The best pair I identified was combining the SMBv2 Initiator with the NPFS process ID spoofing. While I couldn’t identity a service which would use the client PID for any security related operation it’s possible that a third-party service exists.

I could have filed this issue back in my list of interesting or unexpected behaviors, to see if I could exploit it at a later date. But instead I decided to talk to my contacts at MSRC to see if we could collaborate instead. With MSRC on side I wrote up a document explaining the bug class and describing some of my findings. At the same time I reported the SMB server issue through the normal channels at it was the most serious issue I’d discovered. This led to meetings with various teams at Bluehat 2017 in Redmond where a plan was formed for Microsoft to use their source code access to discover the extent of this bug class in the Windows kernel and driver code base. Note, I did not have access to the source code, this part of the investigation was delegated to MSRC, the results of which are in their blog post.

It’s worth noting that while I applied the standard 90 day disclosure deadline to the SMB server report, I didn’t apply an explicit deadline to the bug class report. With no single bug to point to it’d be difficult and likely counter productive to enforce such a deadline. However I did ensure that MSRC agreed to publish the technical details on this issue regardless of the outcome. This is why we’re blogging about it now, 12 months after providing the report.

# Conclusions

It’s always interesting to find a new bug class in Windows to go hunting for. By luck this hasn’t turned out to be anywhere as serious as it could have been. While it would have made sense to specify two separate access modes, one for MemAC and one for SecAC, that’s not what the original NT design used. For backwards compatibility it seems unlikely that behavior will be changed. This bug class is as much about poor documentation as it is about technical issues, as while the behavior can’t be changed, it’s also poorly documented.

If you look at the documentation for IoCreateFile you’ll now find a new remark:

“For create requests originating in user mode, if the driver sets both IO\_NO\_PARAMETER\_CHECKING and IO\_FORCE\_ACCESS\_CHECK in the Options parameter of IoCreateFile then it should also set OBJ\_FORCE\_ACCESS\_CHECK in the ObjectAttributes parameter. For info on this flag, see the Attributes member of OBJECT\_ATTRIBUTES.”

This remark was added very recently. With the majority of Microsoft’s developer documentation on GitHub you can even find [this commit](https://github.com/MicrosoftDocs/windows-driver-docs-ddi/commit/27fbdc7f2165d2920636cd78262877075abf6d77#diff-7f874cc821d427ab9ab672c457826c86) which introduced it.

It’s likely that any bugs identified by MSRC will only be fixed in the latest versions of Windows 10, therefore if you’re a developer you should read Microsoft’s blog post to understand how to avoid these issues in your drivers as well as techniques to find these sorts of issues in your code base. For security researchers it’s another thing to bear in mind when you’re reviewing a new Windows kernel driver.

I’d like to thank Steven Hunter and Gavin Thomas from MSRC who were my main points of contact for getting this bug class remediated.