---
source: p0
source_url: https://projectzero.google/2015/12/between-rock-and-hard-link.html
title: "Between a Rock and a Hard Link - Project Zero"
description: "Posted by James Forshaw, File System EnthusiastIn a previous blog post I described some of the ch..."
---

Posted by James Forshaw, File System Enthusiast

In a previous [blog](https://projectzero.google/2015/08/windows-10hh-symbolic-link-mitigations.html) post I described some of the changes that Microsoft has made to the handling of symbolic links from a sandboxed process. This has an impact on the exploitation of privileged file overwrites for sandbox escapes. Windows does support another method of linking files together, Hard Links, which have some similar properties to file level symbolic links but also some downsides. Hard Links were not originally banned from a sandbox so given the right vulnerability we can still develop an exploit. Of course in some circumstances Hard Links can also be useful for exploiting some types of system level privilege escalation. This short blog post describes the pros and cons of Hard Links as an exploitation primitive and demonstrates its use in a real world vulnerability [CVE-2015-4481](https://code.google.com/p/google-security-research/issues/detail?id=427). Also I’ll quickly show what’s changed after the [MS15-115](https://technet.microsoft.com/en-us/library/security/MS15-115) update, which breaks the attack from a sandboxed context.

# NTFS Hard Links

Hard Links, the ability to logically link a single file to multiple names on the same file system together, has been a feature of the Windows NTFS file system since it was originally designed. It was most likely added for POSIX compatibility. In Windows 2000 the [CreateHardlink](https://msdn.microsoft.com/en-us/library/windows/desktop/aa363860(v=vs.85).aspx) API was introduced to allow a program to create these links in an official way from Windows applications.

Why are hard links useful for local privilege escalation? One type of vulnerability is exploited by a file planting attack, where a privilege service tries to write to a file in a known location. The most flexible approach is to use symbolic links but creating these for single files reliably is tricky, especially now in sandboxed applications. To create file symbolic links on Windows you either need to control the entire directory to apply a Mount Point or you need to be an administrator to set a file level symbolic link. When you’re exploiting file writes to an arbitrary directory such as C:\\ProgramData this is probably not achievable and if you already have administrator privileges it doesn’t really matter. So having the ability to drop a file which links to another file is a very useful primitive. If you can then get a privileged service to overwrite the target file it’ll cause corruption or in the ideal case privilege escalation.

Fortunately it looks like we don’t even need to write our own tool; since the release of Vista the command shell has an inbuilt command, [MKLINK](https://technet.microsoft.com/en-us/library/Cc753194.aspx?f=255&MSPPError=-2147217396), which will create a hard link. All you need to do is pass the /H option. If we try and use this command we immediately come across a problem as shown in the following screenshot.

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhco2s_s552_image3.png)

We can create a link to a file we already control but we can’t create a link to a file we don’t have write access to. This completely removes any utility from a local EoP perspective, if we can only overwrite files we can already write to it isn’t much of a concern. We could stop right here and give up, but where’s the fun in that. First let’s look at the actual implementation of CreateHardlink to see what privileges it’s asking for.

BOOL CreateHardLinkW(LPCWSTR lpFileName, LPCWSTR lpExistingFileName){

NTSTATUS status;

OBJECT\_ATTRIBUTES ObjectAttributes;

UNICODE\_STRING ntname;

UNICODE\_STRING target;

HANDLE FileHandle;

if(!RtlDosPathNameToNtPathName\_U(lpExistingFileName,&ntname))

return FALSE;

InitializeObjectAttributes(&ObjectAttributes,&ntname,...);

status = NtOpenFile(&FileHandle, SYNCHRONIZE \|FILE\_WRITE\_ATTRIBUTES,

&ObjectAttributes,...);

if(status <0)

return FALSE;

if(!RtlDosPathNameToNtPathName\_U(lpFileName,&target))

return FALSE;

PFILE\_LINK\_INFORMATION LinkInfo = RtlAllocateHeap(target.Length +16);

memmove(LinkInfo->FileName, target.Buffer, target.Length);

LinkInfo->ReplaceIfExisting = FALSE;

LinkInfo->RootDirectory =NULL;

LinkInfo->FileNameLength = target.Length;

status = NtSetInformationFile(FileHandle, LinkInfo,

              target.Length +16, FileLinkInformation);

if( status <0)

return FALSE;

return TRUE;

}

When the target file is opened the desired access is requesting FILE\_WRITE\_ATTRIBUTES, this kind of makes some sense, there’s a hard link count in the file’s directory entry so perhaps we need to write to the target file entry in some way? Still what would happen if we just open the file for read, would it still work? As the call to [ZwSetInformationFile](https://msdn.microsoft.com/en-us/library/windows/hardware/ff567096(v=vs.85).aspx) with the FileLinkInformation class is [documented](https://msdn.microsoft.com/en-us/library/windows/hardware/ff540324(v=vs.85).aspx) let’s just reimplement the function but not request write permissions when opening the linked to file.

Spoiler, if we try the new function it works without needing write access to the target file. This makes it much more useful. Of course if we’d just looked at the kernel implementation we’d have seen that we didn’t need any specific access rights to the file. In ZwSetInformationFile a call is made to ObReferenceObjectByHandle to get the underlying file object. This takes a desired access parameter, which turns out to be 0 for the FileLinkInformation information class. We don’t need to hold any access on the target file at all, we just need a handle to it with any assigned permissions.

Not every case of file overwrite vulnerabilities can be exploited using hard links. The Win32 and standard C library APIs don’t provide many options to prevent the attack outside of requiring that the file doesn’t already exist. The [MoveFile](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365239(v=vs.85).aspx) API is secure (as long as you don’t pass the MOVEFILE\_COPY\_ALLOWED flag to [MoveFileEx](https://msdn.microsoft.com/en-us/library/windows/desktop/aa365240(v=vs.85).aspx) which would simulate a copy operation) as it always replaces the file entry.

So the pros and cons of Hard Links are:

### Pros

- Can create a new hard link at the file level without privileges even in sandboxes (well, originally).


### Cons

- Must have write access to the directory where the hard link will be placed, can’t just do it from a handle

- Can only overwrite existing files which you can open for access, can’t create new files

- Can’t redirect a MoveFile operation (except cross drive), but can redirect CopyFile.

- Can only link to files on the same volume

- Can’t link directories to each other


I’ve added an implementation of this technique to my Symbolic Link Testing Tools suite available in Github [here](https://github.com/google/symboliclink-testing-tools).

# Quick Exploit, Mozilla Maintenance Service

Let’s see this in a real world exploit; you can read up on the issue in the Project Zero bug tracker [here](https://code.google.com/p/google-security-research/issues/detail?id=427). The vulnerability was in the Mozilla Maintenance Service, which is installed by default. This is a system service which allows Mozilla applications such as Firefox to update without needing administrator privileges. One interesting feature of this service is it can be started by any user on the system and takes command line arguments to specify the update process. This is in contrast to similar services for other products, which typically automatically update via the Internet without the user account being involved.

When an update process is started by the user application the service writes out a status log to the directory C:\\ProgramData\\Mozilla\\logs under the name maintenanceservice.log. This is interesting as ProgramData’s default permissions allow a normal user to create new files in its subdirectories. There is a problem, however: if we look at the permissions on the logs directory (shown below), while any user can create a new file only the owner, through the CREATOR OWNER SID, gets permission to delete it. This means we can’t just delete the log file and replace it with a hard link as the owner is SYSTEM.

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi3J1h_s600_image1.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi3J1h_s810_image1.png)

Fortunately if we look at the [code](https://hg.mozilla.org/mozilla-central/raw-file/a0d5f4706bd2/toolkit/components/maintenanceservice/maintenanceservice.cpp) there’s a window of opportunity, before creating the log file a call is made to the BackupOldLogs function. This function moves each log file to a new numbered log, this ends up freeing up the initial log directory entry for a brief window of time as shown below.

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhTYuP_s600_image2.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhTYuP_s936_image2.png)

As we can create a new file in the directory we can replace the log file directory entry with a hard link to an existing file we want to overwrite. The service will then open and write to that file entry as SYSTEM, which means we can overwrite many files on the system. While we can’t completely control the contents of the file that gets written, we can inject commands through the service’s command line (it doesn’t check for new-lines etc.). This at least gives us the ability to cause a local DoS on the system by overwriting a critical file, or we can replace certain script files such as Powershell modules, which could get executed in a privileged context and the parser doesn’t care so much about garbage in the file. Ultimately in this case the real issue was that the user could write to the log directory, and this was changed to writing logs into the service’s program files directory instead.

# So What’s Changed?

I was originally going to describe this trick as a replacement for Symbolic Links inside a sandbox in my [44con](http://44con.com/) presentation on Windows 10 security. Microsoft requested I send them the slides, which I did for their own interest. After reviewing them they felt the fact that this was usable from a sandboxed context effectively gets around some of the restrictions they were adding regards Symbolic Links so asked me to not present the information. While I’d publicly disclosed this technique in the Maintenance Service issue (as well as a vulnerability in Adobe Reader [CVE-2015-4446](https://code.google.com/p/google-security-research/issues/detail?id=406)) and so pointed out the information was already available I did agree to the redaction with a promise they would fix it in a security bulletin.

That bulletin, [MS15-115](https://technet.microsoft.com/en-us/library/security/MS15-115), came out in the November patch releases and the fix is referenced as [CVE-2015-6113](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2015-6113). The fix adds the following code to the kernel’s NtSetInformationFile function.

ACCESS\_MASK RequiredAccess =0;

if(FileInformationClass == FileLinkInformation){

if(RtlIsSandboxedToken()){

    RequiredAccess \|= FILE\_WRITE\_ATTRIBUTES;

}

}

// Will return STATUS\_ACCESS\_DENIED if we don't have access

ObReferenceObjectByHandle(FileHandle, RequiredAccess,...);

This mitigates the issue in sandboxed processes as it now requires FILE\_WRITE\_ATTRIBUTES permission on the file handle, which matches with what the CreateHardLink function expects. This would fix the vulnerability in Adobe Reader but would do nothing for the Maintenance Service vulnerability.

# Conclusions

Hopefully this blog at least gives you an idea of how to use Hard Links on Windows. It should also give you an impression that you should never trust the documented interfaces for an operating system to behave as documented. This technique can be used to exploit local system services that try and write known files to directories the user can create files in, including things like ProgramData and the Windows Temp folder. Almost certainly there are other similar vulnerabilities that you could find.

It’s good to see MSRC again taking a practical approach to improving sandbox security by closing off known attack techniques. Keep looking for more changes that use the RtlIsSandboxedToken API as time goes on.