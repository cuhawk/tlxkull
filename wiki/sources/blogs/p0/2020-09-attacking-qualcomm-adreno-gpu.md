---
source: p0
source_url: https://projectzero.google/2020/09/attacking-qualcomm-adreno-gpu.html
title: "Attacking the Qualcomm Adreno GPU - Project Zero"
description: "Posted by Ben Hawkes, Project ZeroWhen writing an Android exploit, breaking out of the applicatio..."
---

Posted by Ben Hawkes, Project Zero

When writing an Android exploit, breaking out of the application sandbox is often a key step. There are a wide range of remote attacks that give you code execution with the privileges of an application (like the browser or a messaging application), but a sandbox escape is still required to gain full system access.

This blog post focuses on an interesting attack surface that is accessible from the Android application sandbox: the graphics processing unit (GPU) hardware. We describe an unusual vulnerability in Qualcomm's Adreno GPU, and how it could be used to achieve kernel code execution from within the Android application sandbox.

This research was built upon the work by Guang Gong ( [@oldfresher](https://twitter.com/oldfresher)), who reported [CVE-2019-10567](https://www.qualcomm.com/company/product-security/bulletins/february-2020-bulletin#_cve-2019-10567) in August 2019. One year later, in early August 2020, Guang Gong released an excellent [whitepaper](https://github.com/secmob/TiYunZong-An-Exploit-Chain-to-Remotely-Root-Modern-Android-Devices/blob/master/us-20-Gong-TiYunZong-An-Exploit-Chain-to-Remotely-Root-Modern-Android-Devices-wp.pdf) describing CVE-2019-10567, and some other vulnerabilities that allowed full system compromise by a remote attacker.

However in June 2020, I noticed that the patch for CVE-2019-10567 was incomplete, and worked with Qualcomm's security team and GPU engineers to fix the issue at its root cause. The patch for this new issue, CVE-2020-11179, has been released to OEM vendors for integration. It's our understanding that Qualcomm will list this publicly in their November 2020 bulletin.

Qualcomm provided the following statement:

"Providing technologies that support robust security and privacy is a priority for Qualcomm Technologies. We commend the security researchers from Google Project Zero for using industry-standard coordinated disclosure practices. Regarding the Qualcomm Adreno GPU vulnerability, we have no evidence it is currently being exploited, and Qualcomm Technologies made a fix available to OEMs in August 2020. We encourage end users to update their devices as patches become available from their carrier or device maker and to only install applications from trusted locations such as the Google Play Store."

Android Attack Surface

The Android application sandbox is an evolving combination of SELinux, seccomp BPF filters, and discretionary access control based on a unique per-application UID. The sandbox is used to limit the resources that an application has access to, and to reduce attack surface. There are a number of well-known routes that attackers use to escape the sandbox, such as: attacking other apps, attacking system services, or attacking the Linux kernel.

At a high-level, there are several different tiers of attack surface in the Android ecosystem. Here are some of the important ones:

- Tier: Ubiquitous


Description: Issues that affect all devices in the Android ecosystem.

Example: Core Linux kernel bugs like Dirty COW, or vulnerabilities in standard system services.

- Tier: Chipset


Description: Issues that affect a substantial portion of the Android ecosystem, based on which type of hardware is used by various OEM vendors.

Example: Snapdragon SoC perf counter vulnerability, or Broadcom WiFi firmware stack overflow.

- Tier: Vendor


Description: Issues that affect most or all devices from a particular Android OEM vendor

Example: Samsung kernel driver vulnerabilities

- Tier: Device


Description: Issues that affect a particular device model from an Android OEM vendor

Example: Pixel 4 face unlock "attention aware" vulnerability

From an attacker's perspective, maintaining an Android exploit capability is a question of covering the widest possible range of the Android ecosystem in the most cost-effective way possible. Vulnerabilities in the ubiquitous tier are particularly attractive for affecting a lot of devices, but might be expensive to find and relatively short-lived compared to other tiers. The chipset tier will normally give you quite a lot of coverage with each exploit, but not as much as the ubiquitous tier. For some attack surfaces, such as baseband and WiFi attacks, the chipset tier is your primary option. The vendor and device tiers are easier to find vulnerabilities in, but require that a larger number of individual exploits are maintained.

For sandbox escapes, the GPU offers up a particularly interesting attack surface from the chipset tier. Since GPU acceleration is widely used in applications, the Android sandbox allows full access to the underlying GPU device. Furthermore, there are only two implementations of GPU hardware that are particularly popular in Android devices: ARM Mali and Qualcomm Adreno.

That means that if an attacker can find a nicely exploitable bug in these two GPU implementations, then they can effectively maintain an sandbox escape exploit capability against most of the Android ecosystem. Furthermore, since GPUs are highly complex with a significant amount of closed-source components (such as firmware/microcode), there is a good opportunity to find a reasonably powerful and long-lived vulnerability.

Something Looks Weird

With this in mind, in late April 2020, I noticed the following commit in the Qualcomm Adreno kernel driver code:

From 0ceb2be799b30d2aea41c09f3acb0a8945dd8711 Mon Sep 17 00:00:00 2001

From: Jordan Crouse <jcrouse@codeaurora.org>

Date: Wed, 11 Sep 2019 08:32:15 -0600

Subject: \[PATCH\] msm: kgsl: Make the "scratch" global buffer use a random GPU address

Select a random global GPU address for the "scratch" buffer that is used

by the ringbuffer for various tasks.

When we think of adding entropy to addresses, we usually think of Address Space Layout Randomization (ASLR). But here we're talking about a GPU virtual address, not a kernel virtual address. That seems unusual, why would a GPU address need to be randomized?

It was relatively straightforward to confirm that this commit was one of the security patches for CVE-2019-10567, which are linked in Qualcomm's advisory. A related patch was also included for this CVE:

From 8051429d4eca902df863a7ebb3c04cbec06b84b3 Mon Sep 17 00:00:00 2001

From: Jordan Crouse <jcrouse@codeaurora.org>

Date: Mon, 9 Sep 2019 10:41:36 -0600

Subject: \[PATCH\] msm: kgsl: Execute user profiling commands in an IB

Execute user profiling in an indirect buffer. This ensures that addresses

and values specified directly from the user don't end up in the

ringbuffer.

And so the question becomes, why exactly is it important that user content doesn't end up on the ringbuffer, and is this patch really sufficient to prevent that? And what happens if we can recover the base address of the scratch mapping? Both at least superficially looked to be possible, so this research project was off to a great start.

Before we go any further, let's take a step back and describe some of the basic components involved here: GPU, ringbuffer, scratch mapping, and so on.

Adreno Introduction

The GPU is the workhorse of modern graphics computing, and most applications use the GPU extensively. From the application's perspective, the specific implementation of GPU hardware is normally abstracted away by libraries such as OpenGL ES and Vulkan. These libraries implement a standard API for programming common GPU accelerated operations, such as texture mapping and running shaders. At a low level however, this functionality is implemented by interacting with the GPU device driver running in kernel space.

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgBJXo_s577_image2%2810%29.png)

Specifically for Qualcomm Adreno, the /dev/kgsl-3d0 device file is ultimately used to implement higher level GPU functionality. The /dev/kgsl-3d0 file is directly accessible within the untrusted application sandbox, because:

1. The device file has global read/write access set in its file permissions. The permissions are set by [ueventd](https://android.googlesource.com/platform/system/core/+/master/init/README.ueventd.md):


sargo:/ # cat /system/vendor/ueventd.rc \| grep kgsl-3d0

/dev/kgsl-3d0             0666   system     system

2. The device file has its SELinux label set to gpu\_device, and the untrusted\_app SELinux context has a specific allow rule for this label:


sargo:/ # ls -Zal /dev/kgsl-3d0

crw-rw-rw- 1 system system u:object\_r:gpu\_device:s0 239, 0 2020-07-21

15:48 /dev/kgsl-3d0

hawkes@glaptop:~$ adb pull /sys/fs/selinux/policy

/sys/fs/selinux/policy: 1 file pulled, 0 skipped. 16.1 MB/s ...

hawkes@glaptop:~$ sesearch -A -s untrusted\_app policy \| grep gpu\_device

allow untrusted\_app gpu\_device:chr\_file { append getattr ioctl lock map

open read write };

This means that the application can open the device file. The Adreno "KGSL" kernel device driver is then primarily invoked through a number of different ioctl calls (e.g. to allocate shared memory, create a GPU context, submit GPU commands, etc.) and mmap (e.g. to map shared memory in to the userspace application).

GPU Shared Mappings

For the most part, applications use shared mappings to load vertices, fragments, and shaders into the GPU and to receive computed results. That means certain physical memory pages are shared between a userland application and the GPU hardware.

To set up a new shared mapping, the application will ask the KGSL kernel driver for an allocation by calling the IOCTL\_KGSL\_GPUMEM\_ALLOC ioctl. The kernel driver will prepare a region of physical memory, and then map this memory into the GPU's address space (for a particular GPU context, explained below). Finally, the application will map the shared memory into the userland address space by using an identifier returned from the allocation ioctl.

At this point, there are two distinct views on the same pages of physical memory. The first view is from the userland application, which uses a virtual address to access the memory that is mapped into its address space. The CPU's memory management unit (MMU) will perform address translation to find the appropriate physical page.

The other is the view from the GPU hardware itself, which uses a GPU virtual address. The GPU virtual address is chosen by the KGSL kernel driver, which configures the device's IOMMU (called the SMMU on ARM) with a page table structure that is used just for the GPU. When the GPU tries to read or write the shared memory mapping, the IOMMU will translate the GPU virtual address to a physical page in memory. This is similar to the address translation performed on the CPU, but with a completely different address space (i.e. the pointer value used in the application will be different to the pointer value used in the GPU).

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjqqA5_s885_image1%2815%29.png)

Each userland process has its own GPU context, meaning that while a certain application is running operations on the GPU, the GPU will only be able to access mappings that it shares with that process. This is needed so that one application can't ask the GPU to read the shared mappings from another application. In practice this separation is achieved by changing which set of page tables is loaded into the IOMMU whenever a GPU context switch occurs. A GPU context switch occurs whenever the GPU is scheduled to run a command from a different process.

However certain mappings are used by all GPU contexts, and so can be present in every set of page tables. They are called global shared mappings, and are used for a variety of system and debugging functions between the GPU and the KGSL kernel driver. While they are never mapped directly into a userland application (e.g. a malicious application can't read or modify the contents of the global mappings directly), they are mapped into both the GPU and kernel address spaces.

On a rooted Android device, we can dump the global mappings (and their GPU virtual addresses) using the follow command:

sargo:/ # cat /sys/kernel/debug/kgsl/globals

0x00000000fc000000-0x00000000fc000fff             4096 setstate

0x00000000fc001000-0x00000000fc040fff           262144 gpu-qdss

0x00000000fc041000-0x00000000fc048fff            32768 memstore

0x00000000fce7a000-0x00000000fce7afff             4096 scratch

0x00000000fc049000-0x00000000fc049fff             4096 pagetable\_desc

0x00000000fc04a000-0x00000000fc04afff             4096 profile\_desc

0x00000000fc04b000-0x00000000fc052fff            32768 ringbuffer

0x00000000fc053000-0x00000000fc053fff             4096 pagetable\_desc

0x00000000fc054000-0x00000000fc054fff             4096 profile\_desc

0x00000000fc055000-0x00000000fc05cfff            32768 ringbuffer

0x00000000fc05d000-0x00000000fc05dfff             4096 pagetable\_desc

0x00000000fc05e000-0x00000000fc05efff             4096 profile\_desc

0x00000000fc05f000-0x00000000fc066fff            32768 ringbuffer

0x00000000fc067000-0x00000000fc067fff             4096 pagetable\_desc

0x00000000fc068000-0x00000000fc068fff             4096 profile\_desc

0x00000000fc069000-0x00000000fc070fff            32768 ringbuffer

0x00000000fc071000-0x00000000fc0a0fff           196608 profile

0x00000000fc0a1000-0x00000000fc0a8fff            32768 ucode

0x00000000fc0a9000-0x00000000fc0abfff            12288 capturescript

0x00000000fc0ac000-0x00000000fc116fff           438272 capturescript\_regs

0x00000000fc117000-0x00000000fc117fff             4096 powerup\_register\_list

0x00000000fc118000-0x00000000fc118fff             4096 alwayson

0x00000000fc119000-0x00000000fc119fff             4096 preemption\_counters

0x00000000fc11a000-0x00000000fc329fff          2162688 preemption\_desc

0x00000000fc32a000-0x00000000fc32afff             4096 perfcounter\_save\_restore\_desc

0x00000000fc32b000-0x00000000fc53afff          2162688 preemption\_desc

0x00000000fc53b000-0x00000000fc53bfff             4096 perfcounter\_save\_restore\_desc

0x00000000fc53c000-0x00000000fc74bfff          2162688 preemption\_desc

0x00000000fc74c000-0x00000000fc74cfff             4096 perfcounter\_save\_restore\_desc

0x00000000fc74d000-0x00000000fc95cfff          2162688 preemption\_desc

0x00000000fc95d000-0x00000000fc95dfff             4096 perfcounter\_save\_restore\_desc

0x00000000fc95e000-0x00000000fc95efff             4096 smmu\_info

And suddenly our scratch buffer has appeared! To the left we see the GPU virtual addresses of each global mapping, then a size, and then the name of the allocation. By rebooting the device several times and checking the layout, we can see that the scratch buffer is indeed randomized:

0x00000000fc0df000-0x00000000fc0dffff             4096 scratch

...

0x00000000fcfc0000-0x00000000fcfc0fff             4096 scratch

...

0x00000000fc9ff000-0x00000000fc9fffff             4096 scratch

...

0x00000000fcb4d000-0x00000000fcb4dfff             4096 scratch

The same test reveals that the scratch buffer is the only global mapping that is randomized, all other global mappings have a fixed GPU address in the range \[0xFC000000, 0xFD400000\]. That makes sense, because the patch for CVE-2019-10567 only introduced the KGSL\_MEMDESC\_RANDOM flag for the scratch buffer allocation.

So we now know that the scratch buffer is correctly randomized (at least to some extent), and that it is a global shared mapping present in every GPU context. But what exactly is the scratch buffer used for?

The Scratch Buffer

Diving in to the driver code, we can clearly see the scratch buffer being allocated in the driver's probe routines, meaning that the scratch buffer will be allocated when the device is first initialized:

int adreno\_ringbuffer\_probe(struct adreno\_device \*adreno\_dev, bool nopreempt)

{

...

status = kgsl\_allocate\_global(device, &device->scratch,

                            PAGE\_SIZE, 0, KGSL\_MEMDESC\_RANDOM, "scratch");

We also find this useful comment:

/\\* SCRATCH MEMORY: The scratch memory is one page worth of data that

\*  is mapped into the GPU. This allows for some 'shared' data between

\*  the GPU and CPU. For example, it will be used by the GPU to write

\*  each updated RPTR for each RB.

By cross referencing all the usages of the resulting memory descriptor (device->scratch) in the kernel driver, we can find two primary usages of the scratch buffer:

1. The GPU address of a preemption restore buffer is dumped to the scratch memory, which appears to be used if a higher priority GPU command interrupts a lower priority command.

2. The read pointer (RPTR) of the ringbuffer (RB) is read from scratch memory and used when calculating the amount of free space in the ringbuffer.


Here we can start to connect the dots. Firstly, we know that the patch for CVE-2019-10567 included changes to both the scratch buffer and the ringbuffer handling code -- that suggests we should focus on the second use case above.

If the GPU is writing RPTR values to the shared mapping (as the comment suggests), and if the kernel driver is reading RPTR values from the scratch buffer and using it for allocation size calculations, then what happens if we can make the GPU write an invalid or incorrect RPTR value?

Ringbuffer Basics

To understand what an invalid RPTR value might mean for a ringbuffer allocation, we first need to describe the ringbuffer itself. When a userland application submits a GPU command (IOCTL\_KGSL\_GPU\_COMMAND), the driver code dispatches the command to the GPU via the ringbuffer, which uses a producer-consumer pattern. The kernel driver will write commands into the ringbuffer, and the GPU will read commands from the ringbuffer.

This occurs in a similar fashion to classical [circular buffers](https://en.wikipedia.org/wiki/Circular_buffer). At a low level, the ringbuffer is a global shared mapping with a fixed size of 32768 bytes. Two indices are maintained to track where the CPU is writing to (WPTR), and where the GPU is reading from (RPTR). To allocate space on the ringbuffer, the CPU has to calculate whether there is sufficient room between the current WPTR and the current RPTR. This happens in adreno\_ringbuffer\_allocspace:

unsigned int \*adreno\_ringbuffer\_allocspace(struct adreno\_ringbuffer \*rb,

                unsigned int dwords)

{

        struct adreno\_device \*adreno\_dev = ADRENO\_RB\_DEVICE(rb);

        unsigned int rptr = adreno\_get\_rptr(rb); \[1\]

        unsigned int ret;

        if (rptr <= rb->\_wptr) {\[2\]

                unsigned int \*cmds;

                if (rb->\_wptr + dwords <= (KGSL\_RB\_DWORDS - 2)) {

                        ret = rb->\_wptr;

                        rb->\_wptr = (rb->\_wptr + dwords) % KGSL\_RB\_DWORDS;

                        return RB\_HOSTPTR(rb, ret);

                }

                /\*

                 \\* There isn't enough space toward the end of ringbuffer. So

                 \\* look for space from the beginning of ringbuffer upto the

                 \\* read pointer.

                 \*/

                if (dwords < rptr) {

                        cmds = RB\_HOSTPTR(rb, rb->\_wptr);

                        \*cmds = cp\_packet(adreno\_dev, CP\_NOP,

                                KGSL\_RB\_DWORDS - rb->\_wptr - 1);

                        rb->\_wptr = dwords;

                        return RB\_HOSTPTR(rb, 0);

                }

        }

        if (rb->\_wptr + dwords < rptr) {\[3\]

                ret = rb->\_wptr;

                rb->\_wptr = (rb->\_wptr + dwords) % KGSL\_RB\_DWORDS;

                return RB\_HOSTPTR(rb, ret);\[4\]

        }

        return ERR\_PTR(-ENOSPC);

}

unsigned int adreno\_get\_rptr(struct adreno\_ringbuffer \*rb)

{

        struct adreno\_device \*adreno\_dev = ADRENO\_RB\_DEVICE(rb);

        unsigned int rptr = 0;

...

                struct kgsl\_device \*device = KGSL\_DEVICE(adreno\_dev);

                kgsl\_sharedmem\_readl(&device->scratch, &rptr,

                                SCRATCH\_RPTR\_OFFSET(rb->id));\[5\]

...

        return rptr;

}

We can see the RPTR value being read at \[1\], and that it ultimately comes from a read of the scratch global shared mapping at \[5\]. Then we can see the scratch RPTR value being used in two comparisons with the WPTR value at \[2\] and \[3\]. The first comparison is for the case where the scratch RPTR is less than or equal to WPTR, meaning that there may be free space toward the end of the ringbuffer or at the beginning of the ringbuffer. The second comparison is for the case where the scratch RPTR is higher than the WPTR. If there's enough room between the WPTR and scratch RPTR, then we can use that space for an allocation.

So what happens if the scratch RPTR value is controlled by an attacker? In that case, the attacker could make either one of these conditions succeed, even if there isn't actually space in the ringbuffer for the requested allocation size. For example, we can make the condition at \[3\] succeed when it normally wouldn't by artificially increasing the value of the scratch RPTR, which at \[4\] results in returning a portion of the ringbuffer that overlaps the correct RPTR location.

That means that an attacker could overwrite ringbuffer commands that haven't yet been processed by the GPU with incoming GPU commands! Or in other words, controlling the scratch RPTR value could desynchronize the CPU and GPU's understanding of the ringbuffer layout. That sounds like it could be very useful! But how can we overwrite the scratch RPTR value?

Attacking the Scratch RPTR Value

Since global shared mappings are not mapped into userland, an attacker cannot modify the scratch buffer directly from their malicious/compromised userland process. However we know that the scratch buffer is mapped into every GPU context, including any created by a malicious attacker. What if we could make the GPU hardware write a malicious RPTR value into the scratch buffer on our behalf?

To achieve this, there are two fundamental steps. Firstly, we need to confirm that the mapping is writable by user-supplied GPU commands. Secondly, we need a way to recover the base GPU address of the scratch mapping. This latter step is necessary due to the recent addition of GPU address randomization for the scratch mapping.

So are all global shared mappings writable by the GPU? It turns out that not every global shared mapping can be written to by user-supplied GPU commands, but the scratch buffer can be. We can confirm this by using the sysfs debugging method above to find the randomized base of the scratch mapping, and then writing a short sequence of GPU commands to write a value to the scratch mapping:

    /\\* write a value to the scratch buffer at offset 256 \*/

    \*cmds++ = cp\_type7\_packet(CP\_MEM\_WRITE, 3);

    cmds += cp\_gpuaddr(cmds, SCRATCH\_BASE+256);

    \*cmds++ = 0x41414141;

    /\\* ensure that the write has taken effect \*/

    \*cmds++ = cp\_type7\_packet(CP\_WAIT\_REG\_MEM, 6);

    \*cmds++ = 0x13;

    cmds += cp\_gpuaddr(cmds, SCRATCH\_BASE+256);

    \*cmds++ = 0x41414141;

    \*cmds++ = 0xffffffff;

    \*cmds++ = 0x1;

    /\\* write 1 to userland shared memory to signal success \*/

    \*cmds++ = cp\_type7\_packet(CP\_MEM\_WRITE, 3);

    cmds += cp\_gpuaddr(cmds, shared\_mem\_gpuaddr);

    \*cmds++ = 0x1;

Each CP\_\* operation here is constructed in userspace and run on the GPU hardware. Typically OpenGL library methods and shaders would be translated to these raw operations by a vendor supported library, but an attacker can also construct these command sequences manually by setting up some GPU shared memory and calling IOCTL\_KGSL\_GPU\_COMMAND. These operations aren't documented however, so behavior has to be inferred by reading the driver code and manual tests. Some examples are: 1) the CP\_MEM\_WRITE operation writes a constant value to a GPU address, 2) the CP\_WAIT\_REG\_MEM operation stalls execution until a GPU address contains a certain constant value, and 3) the CP\_MEM\_TO\_MEM copies data from one GPU address to another.

That means that we can be sure that the GPU successfully wrote to the scratch buffer by checking that the final write occurs (on a normal userland shared memory mapping) -- if the scratch buffer write wasn't successful, the CP\_WAIT\_REG\_MEM operation would time out and no value would be written back.

It's also possible to confirm that the scratch buffer is writable by looking at how the page tables for the global shared mapping are set up in the kernel driver code. Specifically, since the call to kgsl\_allocate\_global doesn't have KGSL\_MEMFLAGS\_GPUREADONLY or KGSL\_MEMDESC\_PRIVILEGED flags set, the resulting mapping is writable by user-supplied GPU commands.

But if the scratch buffer's base address is randomized, how do we know where to write to? There were two approaches to recovering the base address of the scratch buffer.

The first approach is to simply take the GPU command we used above to confirm that the scratch buffer was writable, and turn it into a bruteforce attack. Since we know that global shared mappings have a fixed range, and we know that only the scratch buffer is randomized, we have a very small search space to explore. Once the other static global shared mapping locations are removed from consideration, there are only 2721 possible locations for the scratch page. On average, it took 7.5 minutes to recover the scratch buffer address on a mid-range smartphone device, and this time could likely be optimized further.

The second approach was even better. As mentioned above, the scratch buffer is also used for preemption. To prepare the GPU for preemption, the kernel driver calls the a6xx\_preemption\_pre\_ibsubmit function, which inserts a number of operations into the ringbuffer. The details of those operations aren't very important for our attack, other than the fact that a6xx\_preemption\_pre\_ibsubmit spilled a scratch buffer pointer to the ringbuffer as an argument to a CP\_MEM\_WRITE operation.

Since the ringbuffer is a global mapping and readable by user-supplied GPU commands, it was possible to immediately extract the base of the scratch mapping by using a CP\_MEM\_TO\_MEM command at the right offset into the ringbuffer (i.e. we copied the contents of the ringbuffer to an attacker controlled userland shared mapping, and the contents contained a pointer to the randomized scratch buffer).

Overwriting the Ringbuffer

Now that we know we can reliably control the scratch RPTR value, we can turn our attention to corrupting the contents of the ringbuffer. What exactly is contained in the ringbuffer, and what does overwriting it buy us?

There are actually four different ringbuffers, each used for different GPU priorities, but we only need one for this attack, so we choose the ringbuffer that gets used the least on a modern Android device in order to avoid any noise from other applications using the GPU (ringbuffer 0, which at the time wasn't used at all by Android). Note that the ringbuffer global shared mapping uses the KGSL\_MEMFLAGS\_GPUREADONLY flag, so an attacker cannot directly modify the ringbuffer contents, and we need to use the scratch RPTR primitive to achieve this.

Recall that the ringbuffer is used to send commands from the CPU to the GPU. In practice however, user-supplied GPU commands are never placed directly onto the ringbuffer. This is for two reasons: 1) space in the ringbuffer is limited, and user-supplied GPU commands can be very large, and 2) the ringbuffer is readable by all GPU contexts, and so we want to ensure that one process can't read commands from a different process.

Instead, a layer of indirection occurs, and user-supplied GPU commands are run after an "indirect branch" from the ringbuffer occurs. Conceptually system level commands are executed straight from the ringbuffer, and user level commands are run after an indirect branch into GPU shared memory. Once the user commands finish, control flow will return to the next ringbuffer operation. The indirect branch is performed with a CP\_INDIRECT\_BUFFER\_PFE operation, which is inserted into the ringbuffer by adreno\_ringbuffer\_submitcmd. This operation takes two parameters, the GPU address of the branch target (e.g. a GPU shared memory mapping with user-supplied commands in it) and a size value.

Aside from the indirect branch operation, the ringbuffer contains a number of other GPU command setup and teardown operations, something a bit like the prologue and epilogue of a compiled function. This includes the preemption setup mentioned earlier, GPU context switches, hooks for performance monitoring, errata fixups, identifiers, and protected mode operations. When considering we have some sort of ringbuffer corruption primitive, protected mode operations certainly sound like a potential target area, so let's explore this further.

Protected Mode

When a user-supplied GPU command is running on the GPU, it runs with protected mode enabled. This means that certain global shared mappings and certain GPU register ranges cannot be accessed (read or written). It turns out that this is critically important to the security model of the GPU architecture.

If we examine the driver code for all instances of protected mode being disabled (using the CP\_SET\_PROTECTED\_MODE operation), we see just a handful of examples. Operations related to preemption, errata fixups, performance counters, and GPU context switches can all potentially run with protected mode disabled.

This last operation, GPU context switches, sounds particularly interesting. As a reminder, the GPU context switch occurs when two different processes are using the same ringbuffer. Since the GPU commands from one process aren't allowed to operate on the shared memory belonging to another process, the context switch is needed to switch out the page tables that the GPU has loaded.

What if we could make the GPU switch to an attacker controlled page table? Not only would our GPU commands be able to read and write shared mappings from other processes, we would be able to read and write to any physical address in memory, including kernel memory!

This is an intriguing proposition, and looking at how the kernel driver sets up the context switch operations in the ringbuffer, it looks alluringly possible. Based on a cursory review of the driver code, it looks like the GPU has an operation to switch page tables called CP\_SMMU\_TABLE\_UPDATE. It's possible that this design was chosen for performance considerations, as it means that the GPU can perform a context switch without having to interrupt the kernel and wait for the IOMMU to be reconfigured -- it can simply reconfigure itself.

Looking further, it looks like the GPU has the IOMMU's "TTBR0" register mapped to a protected mode GPU register as well. By reading the ARM [address translation](https://static.docs.arm.com/100940/0100/armv8_a_address%20translation_100940_0100_en.pdf) and [IOMMU](https://static.docs.arm.com/ihi0070/b/SMMUv3_architecture_specification_IHI0070B.pdf) documentation, we can see that TTBR0 is the base address of the page tables used for translating GPU addresses to physical memory addresses. That means if we can point TTBR0 to a set of malicious page tables, then we can translate any GPU address to any physical address of our choosing.

And suddenly, we have a clear idea of how the original attack in CVE-2019-10567 worked. Recall that aside from randomizing the scratch buffer location, the patch for CVE-2019-10567 also "ensures that addresses and values specified directly from the user don't end up in the ringbuffer".

We can now study Guang Gong's [whitepaper](https://github.com/secmob/TiYunZong-An-Exploit-Chain-to-Remotely-Root-Modern-Android-Devices/blob/master/us-20-Gong-TiYunZong-An-Exploit-Chain-to-Remotely-Root-Modern-Android-Devices-wp.pdf) and confirm that his attack managed to use the RPTR corruption technique (at the time using the static address of the scratch buffer) to smuggle operations into the ringbuffer via the arguments to performance profiling commands, which would then be executed due to clever alignment with the "true" RPTR value on the GPU. The smuggled operations disabled protected mode and branched to attacker controlled GPU commands, which promptly overwrote TTBR0 to gain a R/W primitive to arbitrary physical memory. Amazing!

Recovering the Attack

Since we have already bypassed the first part of the patch for CVE-2019-10567 (randomizing the scratch buffer base), to recover the attack (i.e. to be able to use a modified TTBR0 to write physical memory), we simply need to bypass the second part as well.

In essence the second part of the patch for CVE-2019-10567 prevented attacker-controlled commands from being written to the ringbuffer, particularly by the profiling subsystem. The obvious path to bypassing this fix would be to find a different way to smuggle attacker-controlled commands. While there were some exciting looking avenues (such as using the user-supplied GPU address as a command opcode), I decided to pursue a different approach.

Rather than inserting attacker controlled commands to the ringbuffer, let's use the RPTR ringbuffer corruption primitive to desynchronize and reorder legitimate ringbuffer operations. The two basic ingredients we need is an operation that disables protected mode, and an operation that calls an indirect branch -- both of which occur organically within the GPU kernel driver code.

The typical pattern for protected mode operations is to 1) drop protected mode, 2) perform some privileged operations, and 3) re-enable protected mode. Therefore, to recover the attack, we can perform a race condition between steps 1 and 3.  We can start the execution of a privileged operation such as a GPU context switch, and while it is still executing on the GPU with protected mode disabled, we can overwrite the privileged operations using the RPTR ringbuffer corruption primitive, essentially replacing the GPU context switch with an attacker-controlled indirect branch.

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi7Tow_s837_image3%288%29.png)

In order to win the race condition, we have to write an attacker controlled indirect branch to the correct offset in the ringbuffer (e.g. the offset of a context switch), and we need to time this write operation so that the GPU command processor has executed the operation to disable protected mode, but not yet executed the context switch itself.

In practice this race condition appears to be highly feasible, and the temporal and spatial conditions are relatively stable. Specifically, by stalling the GPU with a wait command, and then synchronizing the context switch and the ringbuffer corruption primitives, we can establish a relative offset from the wait command where the GPU will first observe writes from the ringbuffer corruption. This discrete boundary likely results from caching behavior or a fixed-size internal prefetch buffer, and it makes it straightforward to calculate the correct layout of padding, payload, and context switch.

The race condition can be won at least 20% of the time, and since a failed attempt has no observable negative effects, the race condition can be repeated as many times as needed, which means that the attack can succeed almost immediately just by running the exploit in a loop.

Once the attack succeeds, a branch to attacker supplied shared memory occurs while protected mode is disabled. This means that the TTBR0 register described above can be modified to point to an attacker controlled physical page that contains a fake page table structure. In the past (e.g. for rowhammer attacks) the setup of a known physical address has been achieved by using the ION memory allocator or spraying memory through the buddy allocator, and I found some straightforward success with the latter approach.

This allows the attacker to map a GPU address to an arbitrary physical address. At this point the attacker's GPU commands can overwrite kernel code or data structures to achieve arbitrary kernel code execution, which is straightforward since the kernel is located at a fixed physical address on Android kernels.

Final Attack

A proof-of-concept exploit called Adrenaline is available [here](https://bugs.chromium.org/p/project-zero/issues/detail?id=2052). The proof-of-concept demonstrates the attack on a Pixel 3a device running sargo-user QQ2A.200501.001.B3 with kernel 4.9.200-gdf3ca60d978c-ab6351706. It overwrites an entry in the kernel's sys\_call\_table structure to show PC control.

Aside from the 20% success rate of winning the race condition discussed above, the proof-of-concept has two other areas of unreliability: 1) ringbuffer offsets aren't guaranteed to be the same across kernel versions, but should be stable once you calculate them (and could be calculated automatically), and 2) the spray technique used to allocate attacker-controlled data at a known physical address is very basic and used for demonstration purposes only, and there's a chance the chosen fixed page is already in-use. It should be possible to fix point 2 using ION or some other method.

Patch Timeline

The reported issue was assigned CVE-2020-11179, and was patched by applying GPU firmware and kernel driver changes that enforce new restrictions on memory accesses to the scratch buffer by user-supplied GPU commands (i.e. the scratch buffer is protected while running indirect branches from the ringbuffer).

|     |     |
| --- | --- |
| 2020-06-08 | Bug report sent to Qualcomm and filed Issue 2052 in the Project Zero issue tracker. |
| 2020-06-08 | Qualcomm acknowledges the report and assigns QPSIIR-1378 for tracking. |
| 2020-06-12 | Qualcomm agrees to schedule a meeting to discuss the reported issue. |
| 2020-06-16 | Project Zero and Qualcomm meet to discuss the attack and potential fixes. |
| 2020-06-16 | Additional PoC for the rptr bruteforce attack is shared with Qualcomm, as well as a potential bypass for one of the fix approaches that was discussed. Project Zero asks Qualcomm to coordinate with ecosystem partners as appropriate. |
| 2020-06-23 | Request for update regarding the potential fix bypass, fix timeline, and earlier request for coordination. |
| 2020-06-25 | Qualcomm confirms that the potential bypass can be resolved with a kernel driver patch, indicate that the patch is targeted for the August bulletin, and that Project Zero can ask Android Security to coordinate directly with Qualcomm. |
| 2020-06-25 | Project Zero informs Android Security that an issue exists and only provides a Qualcomm reference number. Project Zero asks Android Security to coordinate with Qualcomm for any further details. |
| 2020-07-17 | Qualcomm gives an update on the progress of a microcode based fix. The plan is that the fix will be available for OEMs by September 7, but Qualcomm will request an extension to patch integration and testing by OEMs.allow more time for patch integration and testing by OEMs. |
| 2020-07-17 | Project Zero responds by explaining the option and requirements for a 14-day grace period extension. |
| 2020-07-29 | Qualcomm confirms technical details of how the patch will work, and asks for a disclosure date of October 5th, and to withhold the PoC exploit if that's not possible. |
| 2020-07-31 | Project Zero reply to confirm a planned disclosure date of September 7 (based on policy). The PoC will be released on Sep 7, and that we predict a low likelihood of opportunistic reuse in the near-term due to the complexity of the exploit and additional R&D requirements for real-world usage. |
| 2020-08-04 | Qualcomm privately shares a security advisory with OEMs. OEMs can then request the fix to be applied to their branch/image. |
| 2020-08-20 | Qualcomm shares the current timeline with Project Zero, indicating that they were targeting a November public security bulletin release, and request a 14-day extension. |
| 2020-08-25 | Project Zero reiterates that a fix needs to be expected within the 14-day window for that extension option to apply. |
| 2020-08-25 | Qualcomm ask if any OEM shipping a fix within the 14-day window would be sufficient for the grace extension to be applied. |
| 2020-08-26 | Project Zero responds with a range of options for how to use the 14-day extension in cases of a complex downstream arrangement. Project Zero requests the CVE-ID for this issue. |
| 2020-08-27 | Qualcomm informs Project Zero that the CVE-ID will be CVE-2020-11179 |
| 2020-09-02 | Qualcomm provides a statement for inclusion in the blogpost. Qualcomm asked to confirm the disclosure date, as the 90 day period ends on a US Public Holiday (Sep 7). |
| 2020-09-02 | Project Zero confirms that the new disclosure date is Sep 8, due to the US Public Holiday. |
| 2020-09-08 | Public disclosure (issue tracker and blog post) |

Recommendations

We can offer a few additional recommendations:

1. Transparency and openness: One of the surprising observations while performing this attack was the level of complexity and the amount of processing of untrusted data that happens on the GPU. Since the GPU is a critical part of Android's security model, increasing the level of openness to be consistent with other similarly critical components is advisable. Note that this guidance applies to both Qualcomm Adreno and ARM Mali. Practically speaking, this could include publishing any relevant design documentation and source code, while also providing a threat model/security model for the GPU device.



More generally, the competitive benefits of a closed platform approach to hardware internals should be reassessed in 2020. This balance may have been historically appropriate when the GPU was not in the critical path for security, but today billions of users are relying on the GPU to uphold the operating system security model.


2. Variant analysis: It's possible that this issue could have been found and fixed earlier, based on the first report of CVE-2019-10567. The initially adopted fixes by the Adreno engineers were a clever attempt at mitigating the issue, but didn't look particularly reliable or comprehensive at first glance.



Between Qualcomm, Android security, and the numerous OEMs that received details of both the original attack and the planned patches, I find it troubling that no one seems to have questioned the efficacy of these patches any further. Personally, I think this is because the work of the teams that triage and respond to external vulnerability reports is often undervalued and underfunded.



When facing a barrage of external bug reports, it's hard enough to keep your head above water, let alone find the time and mental energy to pursue and understand an individual issue to the level required to find variants. But a high quality bug report is a potential gold mine of insights and ideas for improving your products' defensive posture.



Speaking to security engineering managers now: finding ways to resource and structure your vulnerability triage team in a way that allows for individual deep dives and tangential pursuits is the best way to extract the maximum value from your external bug reports, and will certainly pay for itself in the long run (in terms of your product's security posture of course, but also in terms of your team's reputation, motivation, and ability to hire). This type of triage work is often seen as a stepping stone to something better, or as a dreaded busy-work rotation, but it doesn't need to be like that.


3. Vulnerability Remediation: All security critical components in Android devices should be updateable within 90 days, including low-level systems like GPU firmware. For components where this is not yet the case, we disclose issues like this hoping to motivate future investments in technology, staffing, and process improvements that will bring the component in line with industry standards.



There's a temptation to say that "hardware issues" are harder to fix, and so should receive more lenient treatment. However, this bug is best described as a software issue running on an opaque and undocumented platform. This relative obscurity has likely contributed to a lack of review, hardening, testing, and a slower vulnerability remediation process, but these challenges aren't fundamental to the technology itself. With proper investment, bugs like this can be fixed and shipped to users within 90 days. If for any reason that investment isn't possible, it's important that users are made aware of this constraint.


Conclusion

This blog post describes a unique and unusually powerful security issue affecting Qualcomm's Adreno GPU. We outlined the design of the GPU and kernel driver, and some side effects of that design that result in a shared memory attack on the GPU itself. This led to a relatively stable race condition that bypassed the GPU protected mode and gave attacker controlled GPU commands access to arbitrary physical memory. Ultimately this could be used to build an Android sandbox escape exploit that gives kernel code execution. Finally, we discussed the planned fix, the fix timeline, and gave some additional recommendations for areas of future improvement.

Thank you to Guang Gong for first reporting this fascinating style of attack, and to Qualcomm for a very prompt, open, and professional response to my additional research.