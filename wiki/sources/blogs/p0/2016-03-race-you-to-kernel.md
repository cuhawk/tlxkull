---
source: p0
source_url: https://projectzero.google/2016/03/race-you-to-kernel.html
title: "Race you to the kernel! - Project Zero"
description: "Posted by Ian Beer of Google Project ZeroThe OS X and iOS kernel code responsible for loading a s..."
---

Posted by Ian Beer of Google Project Zero

The OS X and iOS kernel code responsible for loading a setuid root binary invalidates the old task port after first swapping the new virtual memory map pointer into the old task object, leaving a short race window where you can manipulate the memory of an euid 0 process before the old task port is invalidated. Going a step further this also allows you to also gain any entitlement and, on OS X, load an unsigned kernel extension.

I reported this bug to Apple on December 16th 2015 and it was patched in OS X 10.11.4/iOS 9.3 as CVE-2016-1757. For more technical details see the [original bug report](https://code.google.com/p/google-security-research/issues/detail?id=676) where you can also grab the updated exploit.

# Task Ports

If you’ve ever tried to use ptrace on OS X you were probably sorely disappointed. Whilst the syscall does exists it’s severely limited in what it can do. For example there’s no support for peeking and poking memory, a pretty fundamental use-case.

This is one of many areas of XNU where the duality of its kernel is evident; along with ptrace there’s a parallel abstraction layer in the Mach side of the kernel which supports building debugging tools via a set of special mach task ports

Each process executing on OS X has a task port. For example, to allocate a page of memory in your process you might use code like this:

mach\_vm\_address\_t addr = 0;

mach\_vm\_allocate(mach\_task\_self(),

                 &addr,

                 0x1000,

                 VM\_FLAGS\_ANYWHERE);

mach\_vm\_allocate is a MIG method implemented by the kernel (and defined in mach\_vm.defs in the xnu kernel source.) The first argument to this method is the current task port; if you happened to have send rights to another task’s task port and you were to call this method passing that other task’s task port then the allocation would end up in that other task’s virtual address space, even though your task made the call. Similarly the mach\_vm\_read and mach\_vm\_write methods allow you to read and write the memory of other processes if you  have their task ports, effectively giving you complete control over them.

By default tasks only have send rights to their own task ports, but it’s easy to give other processes send rights to your task port using the standard mach messaging mechanisms.

# execve

Usually new task ports will only be created when new processes are created (via fork or posix\_spawn). Just execing a new binary won’t reset the task port. This leads to the obvious question: since having a send right to a process’s task port give you complete control over that process, how do they deal with SUID binaries where the exec call will increase the privileges of the process?

Looking through the exec code we find this snippet:

/\*

\\* Have mach reset the task and thread ports.

\\* We don't want anyone who had the ports before

\\* a setuid exec to be able to access/control the

\\* task/thread after.

\*/

ipc\_task\_reset(p->task);

Sounds sensible. But execve is a really complex syscall and there’s a lot going on here:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhbII-_s600_2016-03-22_2.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhbII-_s640_2016-03-22_2.png)

This diagram outline the four major phases of the exec syscall which we’re interested in along with the lifetimes of some data structures.

In phase 1 the old task port is still valid, and via the task struct gives us access to the old vm\_map which still contains the virtual address space of the task prior to the exec. As part of the load\_machfile method the kernel will create a new vm\_map into which it will load the new executable image. Note though that at this point the new vm\_map isn’t matched up with any task; it’s just a virtual address space with no process.

In phase 2 the parse\_machfile method does the actual parse and load of the MachO image into the new virtual address space. It’s also during this phase that any code signatures which the binary has are checked; we’ll come back to that detail later.

In phase 3 load\_machfile calls swap\_task\_map; this sets the task struct to point to the new vm\_map into which the target executable was just loaded. From this point on any mach\_vm\\* methods invoked on the old task port will target the new vm\_map.

In phase 4 exec\_handle\_sugid will check if this binary is SUID, and if it is, will reset the task port, at which point the old task port will no longer work.

# Somethings not right there…

From this high-level view it’s clear that there’s a fundamental race condition. Between phase 3, when the vm\_map is swapped, and phase 4, when the task port is invalidated, we will have full read/write access via the old task port to the new vm\_map containing the loaded binary which is about to be executed, even if it’s SUID which means that we can just use mach\_vm\_write to overwrite its text segment with code we control!

From the diagram it’s hard to tell but there’s actually quite a long period between those two phases, certainly enough time to sneak in a few mach kernel MIG calls.

# Building a reliable exploit

There’s one small stumbling block to overcome though: although we can now try to write to the new vm\_map, where should we write? Userspace ASLR on OS X (for binaries, not dynamic libraries) is randomized per-exec so we first have to figure out where the kernel loaded the image.

Luckily with the task port we can do a lot more than just blindly read and write the new vm\_map; we can also API’s like mach\_vm\_region to ask about properties of memory regions in the map. In this case we just loop constantly asking for the address of the lowest mapping. When it changes we know that it changed to the base address of the image in the new vm\_map and  that we’re now in the race window between phases 3 and 4.

Using this base address we can work out the address of the binary’s entrypoint in the new vm\_map, mark that page as RWX using mach\_vm\_protect and overwrite it with shellcode using mach\_vm\_write.

Run root\_shell.sh in the attached exploit to see this in action. It should work out of the box on any semi-recent OS X system, using otool to extract the entrypoint of the traceroute6 suid-root executable.

# Going further: codesigning and entitlements

In the exec phases diagram I mentioned that parse\_machfile (in phase 2) is responsible for both loading the MachO as well as verifying any code signatures present. You might ask why this is relevant on OS X since, unlike iOS, there’s no mandatory userspace code signing and we can quite happily execute unsigned code anyway.

But OS X does use userspace code signing to enforce entitlements which are just xml blobs stored in your MachO and signed as part of your code signature.

Kernel code can check whether user space processes have particular entitlements (via IOTaskHasEntitlement) and the kernel kext loading code will now only accept load requests from processes which are both running as root and also have the com.apple.rootless.kext-management entitlement.

This is particularly important since on OS X kext code signatures are enforced by userspace. This means that the kext-management entitlement is a vital part of the separation between root in userspace and kernel code execution.

Two system binaries which do have the kext-management entitlement are kextd and kextload; so in order to defeat kernel code signing we just need to first exec a suid-root binary to get root then exec either kextload or kextd to get the right entitlement.

# Patching kextload

kextload is probably the easier target for a binary patch since it’s a standalone tool which can load a kext without talking to to kextd. We just need to patch the checkAccess function so that kextload thinks it can’t reach kextd and will try to load the kext itself. Then patch out the calls to checkKextSignature and checkSignaturesOfDependents such that kextload thinks they succeeded and it will now load any kext, signed or unsigned :-)

The released exploit contain a binary patch file to remove the signature checks in kextload on OS X 10.11.3 as well as a simple HelloWorld kext and load\_kext.sh and unload\_kext.sh scripts to load and unload it. These can be run as a regular user. Look in Console.app to see the kernel debug printf output.