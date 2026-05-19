---
source: p0
source_url: https://projectzero.google/2018/09/a-cache-invalidation-bug-in-linux.html
title: "A cache invalidation bug in Linux memory management - Project Zero"
description: "Posted by Jann Horn, Google Project ZeroThis blogpost describes a way to exploit a Linux kernel b..."
---

Posted by Jann Horn, Google Project Zero

This blogpost describes a way to exploit a Linux kernel bug (CVE-2018-17182) that exists since kernel version 3.16. While the bug itself is in code that is reachable even from relatively strongly sandboxed contexts, this blogpost only describes a way to exploit it in environments that use Linux kernels that haven't been configured for increased security (specifically, Ubuntu 18.04 with kernel linux-image-4.15.0-34-generic at version 4.15.0-34.37). This demonstrates how the kernel configuration can have a big impact on the difficulty of exploiting a kernel bug.

The bug report and the exploit are filed in our issue tracker as [issue 1664](https://bugs.chromium.org/p/project-zero/issues/detail?id=1664).

Fixes for the issue are in the upstream stable releases 4.18.9, 4.14.71, 4.9.128, 4.4.157 and 3.16.58.

# The bug

Whenever a userspace page fault occurs because e.g. a page has to be paged in on demand, the Linux kernel has to look up the VMA (virtual memory area; struct vm\_area\_struct) that contains the fault address to figure out how the fault should be handled. The slowpath for looking up a VMA (in find\_vma()) has to walk a red-black tree of VMAs. To avoid this performance hit, Linux also has a fastpath that can bypass the tree walk if the VMA was recently used.

The implementation of the fastpath has changed over time; [since version 3.15](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=615d6e8756c87149f2d4c1b93d471bca002bd849), Linux uses per-thread VMA caches with four slots, implemented in mm/vmacache.c and include/linux/vmacache.h. Whenever a successful lookup has been performed through the slowpath, vmacache\_update() stores a pointer to the VMA in an entry of the array current->vmacache.vmas, allowing the next lookup to use the fastpath.

Note that VMA caches are per-thread, but VMAs are associated with a whole process (more precisely with a struct mm\_struct; from now on, this distinction will largely be ignored, since it isn't relevant to this bug). Therefore, when a VMA is freed, the VMA caches of all threads must be invalidated - otherwise, the next VMA lookup would follow a dangling pointer. However, since a process can have many threads, simply iterating through the VMA caches of all threads would be a performance problem.

To solve this, both the struct mm\_struct and the per-thread struct vmacache are tagged with sequence numbers; when the VMA lookup fastpath discovers in vmacache\_valid() that current->vmacache.seqnum and current->mm->vmacache\_seqnum don't match, it wipes the contents of the current thread's VMA cache and updates its sequence number.

The sequence numbers of the mm\_struct and the VMA cache were only 32 bits wide, meaning that it was possible for them to overflow. To ensure that a VMA cache can't incorrectly appear to be valid when current->mm->vmacache\_seqnum has actually been incremented 232 times, vmacache\_invalidate() (the helper that increments current->mm->vmacache\_seqnum) had a special case: When current->mm->vmacache\_seqnum wrapped to zero, it would call vmacache\_flush\_all() to wipe the contents of all VMA caches associated with current->mm. Executing vmacache\_flush\_all() was very expensive: It would iterate over every thread on the entire machine, check which struct mm\_struct it is associated with, then if necessary flush the thread's VMA cache.

In version 3.16, [an optimization was added](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6b4ebc3a9078c5b7b8c4cf495a0b1d2d0e0bfe7a): If the struct mm\_struct was only associated with a single thread, vmacache\_flush\_all() would do nothing, based on the realization that every VMA cache invalidation is preceded by a VMA lookup; therefore, in a single-threaded process, the VMA cache's sequence number is always close to the mm\_struct's sequence number:

/\*

\\* Single threaded tasks need not iterate the entire

\\* list of process. We can avoid the flushing as well

\\* since the mm's seqnum was increased and don't have

\\* to worry about other threads' seqnum. Current's

\\* flush will occur upon the next lookup.

\*/

if (atomic\_read(&mm->mm\_users) == 1)

return;

However, this optimization is incorrect because it doesn't take into account what happens if a previously single-threaded process creates a new thread immediately after the mm\_struct's sequence number has wrapped around to zero. In this case, the sequence number of the first thread's VMA cache will still be 0xffffffff, and the second thread can drive the mm\_struct's sequence number up to 0xffffffff again. At that point, the first thread's VMA cache, which can contain dangling pointers, will be considered valid again, permitting the use of freed VMA pointers in the first thread's VMA cache.

The bug [was fixed](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/mm/vmacache.c?id=7a9cdebdcc17e426fb5287e4a82db1dfe86339b2) by changing the sequence numbers to 64 bits, thereby making an overflow infeasible, and removing the overflow handling logic.

# Reachability and Impact

Fundamentally, this bug can be triggered by any process that can run for a sufficiently long time to overflow the reference counter (about an hour if MAP\_FIXED is usable) and has the ability to use mmap()/munmap() (to manage memory mappings) and clone() (to create a thread). These syscalls do not require any privileges, and they are often permitted even in seccomp-sandboxed contexts, such as the Chrome renderer sandbox ( [mmap](https://cs.chromium.org/chromium/src/sandbox/linux/seccomp-bpf-helpers/baseline_policy.cc?l=192), [munmap](https://cs.chromium.org/chromium/src/sandbox/linux/seccomp-bpf-helpers/syscall_sets.cc?l=498&dr=C), [clone](https://cs.chromium.org/chromium/src/sandbox/linux/seccomp-bpf-helpers/baseline_policy.cc?l=144)), [the sandbox of the main gVisor host component](https://github.com/google/gvisor/blob/master/runsc/boot/filter/config.go), and [Docker's seccomp policy](https://github.com/moby/moby/blob/master/profiles/seccomp/seccomp_default.go).

To make things easy, my exploit uses various other kernel interfaces, and therefore doesn't just work from inside such sandboxes; in particular, it uses /dev/kmsg to read dmesg logs and uses an eBPF array to spam the kernel's page allocator with user-controlled, mutable single-page allocations. However, an attacker willing to invest more time into an exploit would probably be able to avoid using such interfaces.

Interestingly, it looks like Docker in its default config [doesn't prevent containers from accessing the host's dmesg logs](https://github.com/moby/moby/issues/37897) if the kernel permits dmesg access for normal users - while /dev/kmsg doesn't exist in the container, [the seccomp policy whitelists the syslog() syscall](https://github.com/moby/moby/blob/47dfff68e4365668279e235bf8c7778b637f2517/profiles/seccomp/seccomp_default.go#L325) for some reason.

# BUG\_ON(), WARN\_ON\_ONCE(), and dmesg

The function in which the first use-after-free access occurs is vmacache\_find(). [When this function was first added](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/mm/vmacache.c?id=615d6e8756c87149f2d4c1b93d471bca002bd849) \- before the bug was introduced -, it accessed the VMA cache as follows:

       for (i = 0; i < VMACACHE\_SIZE; i++) {

               struct vm\_area\_struct \*vma = current->vmacache\[i\];

               if (vma && vma->vm\_start <= addr && vma->vm\_end > addr) {

BUG\_ON(vma->vm\_mm != mm);

                       return vma;

               }

       }

When this code encountered a cached VMA whose bounds contain the supplied address addr, it checked whether the VMA's ->vm\_mm pointer matches the expected mm\_struct \- which should always be the case, unless a memory safety problem has happened -, and if not, terminated with a BUG\_ON() assertion failure. BUG\_ON() is intended to handle cases in which a kernel thread detects a severe problem that can't be cleanly handled by bailing out of the current context. In a default upstream kernel configuration, BUG\_ON() will normally print a backtrace with register dumps to the dmesg log buffer, then forcibly terminate the current thread. This can sometimes prevent the rest of the system from continuing to work properly - for example, if the crashing code held an important lock, any other thread that attempts to take that lock will then deadlock -, but it is often successful in keeping the rest of the system in a reasonably usable state. Only when the kernel detects that the crash is in a critical context such as an interrupt handler, it brings down the whole system with a kernel panic.

The same handler code is used for dealing with unexpected crashes in kernel code, like page faults and general protection faults at non-whitelisted addresses: By default, if possible, the kernel will attempt to terminate only the offending thread.

The handling of kernel crashes is a tradeoff between availability, reliability and security. A system owner might want a system to keep running as long as possible, even if parts of the system are crashing, if a sudden kernel panic would cause data loss or downtime of an important service. Similarly, a system owner might want to debug a kernel bug on a live system, without an external debugger; if the whole system terminated as soon as the bug is triggered, it might be harder to debug an issue properly.

On the other hand, an attacker attempting to exploit a kernel bug might benefit from the ability to retry an attack multiple times without triggering system reboots; and an attacker with the ability to read the crash log produced by the first attempt might even be able to use that information for a more sophisticated second attempt.

The kernel provides two sysctls that can be used to adjust this behavior, depending on the desired tradeoff:

- kernel.panic\_on\_oops will automatically cause a kernel panic when a BUG\_ON() assertion triggers or the kernel crashes; its initial value can be configured using the build configuration variable CONFIG\_PANIC\_ON\_OOPS. It is off by default in the upstream kernel - and enabling it by default in distributions would probably be a bad idea -, but it is e.g. [enabled by Android](https://android.googlesource.com/platform/system/core/+/fa14d21ca44377f2c70769b6ebb2cc28a65d53d7/rootdir/init.rc#118).

- kernel.dmesg\_restrict controls whether non-root users can access dmesg logs, which, among other things, contain register dumps and stack traces for kernel crashes; its initial value can be configured using the build configuration variable CONFIG\_SECURITY\_DMESG\_RESTRICT. It is off by default in the upstream kernel, but is enabled by some distributions, e.g. [Debian](https://salsa.debian.org/kernel-team/linux/raw/master/debian/config/config). (Android relies on SELinux to block access to dmesg.)


Ubuntu, for example, enables neither of these.

The code snippet from above [was amended](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/mm/vmacache.c?id=50f5aa8a9b248fa4262cf379863ec9a531b49737) in the same month as it was committed:

       for (i = 0; i < VMACACHE\_SIZE; i++) {

                struct vm\_area\_struct \*vma = current->vmacache\[i\];

\-               if (vma && vma->vm\_start <= addr && vma->vm\_end > addr) {

\-                       BUG\_ON(vma->vm\_mm != mm);

\+               if (!vma)

\+                       continue;

\+               if (WARN\_ON\_ONCE(vma->vm\_mm != mm))

\+                       break;

\+               if (vma->vm\_start <= addr && vma->vm\_end > addr)

                        return vma;

\-               }

        }

This amended code is what distributions like Ubuntu are currently shipping.

The first change here is that the sanity check for a dangling pointer happens before the address comparison. The second change is somewhat more interesting: BUG\_ON() is replaced with WARN\_ON\_ONCE().

WARN\_ON\_ONCE() prints debug information to dmesg that is similar to what BUG\_ON() would print. The differences to BUG\_ON() are that WARN\_ON\_ONCE() only prints debug information the first time it triggers, and that execution continues: Now when the kernel detects a dangling pointer in the VMA cache lookup fastpath - in other words, when it heuristically detects that a use-after-free has happened -, it just bails out of the fastpath and falls back to the red-black tree walk. The process continues normally.

This fits in with the kernel's policy of attempting to keep the system running as much as possible by default; if an accidental use-after-free bug occurs here for some reason, the kernel can probably heuristically mitigate its effects and keep the process working.

The policy of only printing a warning even when the kernel has discovered a memory corruption is problematic for systems that should kernel panic when the kernel notices security-relevant events like kernel memory corruption. Simply making WARN() trigger kernel panics isn't really an option because WARN() is also used for various events that are not important to the kernel's security. For this reason, a few uses of WARN\_ON() in security-relevant places have been replaced with CHECK\_DATA\_CORRUPTION(), which permits toggling the behavior between BUG() and WARN() at kernel configuration time. However, CHECK\_DATA\_CORRUPTION() is only used in the linked list manipulation code and in addr\_limit\_user\_check(); the check in the VMA cache, for example, still uses a classic WARN\_ON\_ONCE().

A third important change [was made to this function](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/mm/vmacache.c?id=ddbf369c0a33924f76d092985bd20d9310f43d7f); however, this change is relatively recent and will first be in the 4.19 kernel, which hasn't been released yet, so it is irrelevant for attacking currently deployed kernels.

       for (i = 0; i < VMACACHE\_SIZE; i++) {

\-               struct vm\_area\_struct \*vma = current->vmacache.vmas\[i\];

\+               struct vm\_area\_struct \*vma = current->vmacache.vmas\[idx\];

\-               if (!vma)

\-                       continue;

\-               if (WARN\_ON\_ONCE(vma->vm\_mm != mm))

\-                       break;

\-               if (vma->vm\_start <= addr && vma->vm\_end > addr) {

\-                       count\_vm\_vmacache\_event(VMACACHE\_FIND\_HITS);

\-                       return vma;

\+               if (vma) {

+#ifdef CONFIG\_DEBUG\_VM\_VMACACHE

\+                       if (WARN\_ON\_ONCE(vma->vm\_mm != mm))

\+                               break;

+#endif

\+                       if (vma->vm\_start <= addr && vma->vm\_end > addr) {

\+                               count\_vm\_vmacache\_event(VMACACHE\_FIND\_HITS);

\+                               return vma;

\+                       }

                }

\+               if (++idx == VMACACHE\_SIZE)

\+                       idx = 0;

        }

After this change, the sanity check is skipped altogether unless the kernel is built with the debugging option CONFIG\_DEBUG\_VM\_VMACACHE.

# The exploit: Incrementing the sequence number

The exploit has to increment the sequence number roughly 233 times. Therefore, the efficiency of the primitive used to increment the sequence number is important for the runtime of the whole exploit.

It is possible to cause two sequence number increments per syscall as follows: Create an anonymous VMA that spans three pages. Then repeatedly use mmap() with MAP\_FIXED to replace the middle page with an equivalent VMA. This causes mmap() to first split the VMA into three VMAs, then replace the middle VMA, and then merge the three VMAs together again, causing VMA cache invalidations for the two VMAs that are deleted while merging the VMAs.

# The exploit: Replacing the VMA

Enumerating all potential ways to attack the use-after-free without releasing the slab's backing page (according to /proc/slabinfo, the Ubuntu kernel uses one page per vm\_area\_struct slab) back to the buddy allocator / page allocator:

1. Get the vm\_area\_struct reused in the same process. The process would then be able to use this VMA, but this doesn't result in anything interesting, since the VMA caches of the process would be allowed to contain pointers to the VMA anyway.

2. Free the vm\_area\_struct such that it is on the slab allocator's freelist, then attempt to access it. However, at least the SLUB allocator that Ubuntu uses replaces the first 8 bytes of the vm\_area\_struct (which contain vm\_start, the userspace start address) with a kernel address. This makes it impossible for the VMA cache lookup function to return it, since the condition vma->vm\_start <= addr && vma->vm\_end > addr can't be fulfilled, and therefore nothing interesting happens.

3. Free the vm\_area\_struct such that it is on the slab allocator's freelist, then allocate it in another process. This would (with the exception of a very narrow race condition that can't easily be triggered repeatedly) result in hitting the WARN\_ON\_ONCE(), and therefore the VMA cache lookup function wouldn't return the VMA.

4. Free the vm\_area\_struct such that it is on the slab allocator's freelist, then make an allocation from a slab that has been merged with the vm\_area\_struct slab. This requires the existence of an aliasing slab; in a Ubuntu 18.04 VM, no such slab seems to exist.


Therefore, to exploit this bug, it is necessary to release the backing page back to the page allocator, then reallocate the page in some way that permits placing controlled data in it. There are various kernel interfaces that could be used for this; for example:

pipe pages:

- advantage: not wiped on allocation

- advantage: permits writing at an arbitrary in-page offset if splice() is available

- advantage: page-aligned

- disadvantage: can't do multiple writes without first freeing the page, then reallocating it


BPF maps:

- advantage: can repeatedly read and write contents from userspace

- advantage: page-aligned

- disadvantage: wiped on allocation


This exploit uses BPF maps.

# The exploit: Leaking pointers from dmesg

The exploit wants to have the following information:

- address of the mm\_struct

- address of the use-after-free'd VMA

- load address of kernel code


At least in the Ubuntu 18.04 kernel, the first two of these are directly visible in the register dump triggered by WARN\_ON\_ONCE(), and can therefore easily be extracted from dmesg: The mm\_struct's address is in RDI, and the VMA's address is in RAX. However, an instruction pointer is not directly visible because RIP and the stack are symbolized, and none of the general-purpose registers contain an instruction pointer.

A kernel backtrace can contain multiple sets of registers: When the stack backtracing logic encounters an interrupt frame, it generates another register dump. Since we can trigger the WARN\_ON\_ONCE() through a page fault on a userspace address, and page faults on userspace addresses can happen at any userspace memory access in syscall context (via copy\_from\_user()/copy\_to\_user()/...), we can pick a call site that has the relevant information in a register from a wide range of choices. It turns out that writing to an eventfd triggers a usercopy while R8 still contains the pointer to the eventfd\_fops structure.

When the exploit runs, it replaces the VMA with zeroed memory, then triggers a VMA lookup against the broken VMA cache, intentionally triggering the WARN\_ON\_ONCE(). This generates a warning that looks as follows - the leaks used by the exploit are highlighted:

\[ 3482.271265\] WARNING: CPU: 0 PID: 1871 at /build/linux-SlLHxe/linux-4.15.0/mm/vmacache.c:102 vmacache\_find+0x9c/0xb0

\[...\]

\[ 3482.271298\] RIP: 0010:vmacache\_find+0x9c/0xb0

\[ 3482.271299\] RSP: 0018:ffff9e0bc2263c60 EFLAGS: 00010203

\[ 3482.271300\] RAX: ffff8c7caf1d61a0 RBX: 00007fffffffd000 RCX: 0000000000000002

\[ 3482.271301\] RDX: 0000000000000002 RSI: 00007fffffffd000 RDI: ffff8c7c214c7380

\[ 3482.271301\] RBP: ffff9e0bc2263c60 R08: 0000000000000000 R09: 0000000000000000

\[ 3482.271302\] R10: 0000000000000000 R11: 0000000000000000 R12: ffff8c7c214c7380

\[ 3482.271303\] R13: ffff9e0bc2263d58 R14: ffff8c7c214c7380 R15: 0000000000000014

\[ 3482.271304\] FS:  00007f58c7bf6a80(0000) GS:ffff8c7cbfc00000(0000) knlGS:0000000000000000

\[ 3482.271305\] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033

\[ 3482.271305\] CR2: 00007fffffffd000 CR3: 00000000a143c004 CR4: 00000000003606f0

\[ 3482.271308\] DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000

\[ 3482.271309\] DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400

\[ 3482.271309\] Call Trace:

\[ 3482.271314\]  find\_vma+0x1b/0x70

\[ 3482.271318\]  \_\_do\_page\_fault+0x174/0x4d0

\[ 3482.271320\]  do\_page\_fault+0x2e/0xe0

\[ 3482.271323\]  do\_async\_page\_fault+0x51/0x80

\[ 3482.271326\]  async\_page\_fault+0x25/0x50

\[ 3482.271329\] RIP: 0010:copy\_user\_generic\_unrolled+0x86/0xc0

\[ 3482.271330\] RSP: 0018:ffff9e0bc2263e08 EFLAGS: 00050202

\[ 3482.271330\] RAX: 00007fffffffd008 RBX: 0000000000000008 RCX: 0000000000000001

\[ 3482.271331\] RDX: 0000000000000000 RSI: 00007fffffffd000 RDI: ffff9e0bc2263e30

\[ 3482.271332\] RBP: ffff9e0bc2263e20 R08: ffffffffa7243680 R09: 0000000000000002

\[ 3482.271333\] R10: ffff8c7bb4497738 R11: 0000000000000000 R12: ffff9e0bc2263e30

\[ 3482.271333\] R13: ffff8c7bb4497700 R14: ffff8c7cb7a72d80 R15: ffff8c7bb4497700

\[ 3482.271337\]  ? \_copy\_from\_user+0x3e/0x60

\[ 3482.271340\]  eventfd\_write+0x74/0x270

\[ 3482.271343\]  ? common\_file\_perm+0x58/0x160

\[ 3482.271345\]  ? wake\_up\_q+0x80/0x80

\[ 3482.271347\]  \_\_vfs\_write+0x1b/0x40

\[ 3482.271348\]  vfs\_write+0xb1/0x1a0

\[ 3482.271349\]  SyS\_write+0x55/0xc0

\[ 3482.271353\]  do\_syscall\_64+0x73/0x130

\[ 3482.271355\]  entry\_SYSCALL\_64\_after\_hwframe+0x3d/0xa2

\[ 3482.271356\] RIP: 0033:0x55a2e8ed76a6

\[ 3482.271357\] RSP: 002b:00007ffe71367ec8 EFLAGS: 00000202 ORIG\_RAX: 0000000000000001

\[ 3482.271358\] RAX: ffffffffffffffda RBX: 0000000000000000 RCX: 000055a2e8ed76a6

\[ 3482.271358\] RDX: 0000000000000008 RSI: 00007fffffffd000 RDI: 0000000000000003

\[ 3482.271359\] RBP: 0000000000000001 R08: 0000000000000000 R09: 0000000000000000

\[ 3482.271359\] R10: 0000000000000000 R11: 0000000000000202 R12: 00007ffe71367ec8

\[ 3482.271360\] R13: 00007fffffffd000 R14: 0000000000000009 R15: 0000000000000000

\[ 3482.271361\] Code: 00 48 8b 84 c8 10 08 00 00 48 85 c0 74 11 48 39 78 40 75 17 48 39 30 77 06 48 39 70 08 77 8d 83 c2 01 83 fa 04 75 ce 31 c0 5d c3 <0f> 0b 31 c0 5d c3 90 90 90 90 90 90 90 90 90 90 90 90 90 90 0f

\[ 3482.271381\] ---\[ end trace bf256b6e27ee4552 \]---

At this point, the exploit can create a fake VMA that contains the correct mm\_struct pointer (leaked from RDI). It also populates other fields with references to fake data structures (by creating pointers back into the fake VMA using the leaked VMA pointer from RAX) and with pointers into the kernel's code (using the leaked R8 from the page fault exception frame to bypass KASLR).

# The exploit: JOP (the boring part)

It is probably possible to exploit this bug in some really elegant way by abusing the ability to overlay a fake writable VMA over existing readonly pages, or something like that; however, this exploit just uses classic jump-oriented programming.

To trigger the use-after-free a second time, a writing memory access is performed on an address that has no pagetable entries. At this point, the kernel's page fault handler comes in via page\_fault -\> do\_page\_fault -\> \_\_do\_page\_fault -\> handle\_mm\_fault -\> \_\_handle\_mm\_fault -\> handle\_pte\_fault -\> do\_fault -\> do\_shared\_fault -\> \_\_do\_fault, at which point it performs an indirect call:

static int \_\_do\_fault(struct vm\_fault \*vmf)

{

struct vm\_area\_struct \*vma = vmf->vma;

int ret;

ret = vma->vm\_ops->fault(vmf);

vma is the VMA structure we control, so at this point, we can gain instruction pointer control. R13 contains a pointer to vma. The JOP chain that is used from there on follows; it is quite crude (for example, it crashes after having done its job), but it works.

First, to move the VMA pointer to RDI:

ffffffff810b5c21: 49 8b 45 70           mov rax,QWORD PTR \[r13+0x70\]

ffffffff810b5c25: 48 8b 80 88 00 00 00  mov rax,QWORD PTR \[rax+0x88\]

ffffffff810b5c2c: 48 85 c0              test rax,rax

ffffffff810b5c2f: 74 08                 je ffffffff810b5c39

ffffffff810b5c31: 4c 89 ef              mov rdi,r13

ffffffff810b5c34: e8 c7 d3 b4 00        call ffffffff81c03000 <\_\_x86\_indirect\_thunk\_rax>

Then, to get full control over RDI:

ffffffff810a4aaa: 48 89 fb              mov rbx,rdi

ffffffff810a4aad: 48 8b 43 20           mov rax,QWORD PTR \[rbx+0x20\]

ffffffff810a4ab1: 48 8b 7f 28           mov rdi,QWORD PTR \[rdi+0x28\]

ffffffff810a4ab5: e8 46 e5 b5 00        call ffffffff81c03000 <\_\_x86\_indirect\_thunk\_rax>

At this point, we can call into run\_cmd(), which spawns a root-privileged usermode helper, using a space-delimited path and argument list as its only argument. This gives us the ability to run a binary we have supplied with root privileges. (Thanks to Mark for pointing out that if you control RDI and RIP, you don't have to try to do crazy things like flipping the SM\*P bits in CR4, you can just spawn a usermode helper...)

After launching the usermode helper, the kernel crashes with a page fault because the JOP chain doesn't cleanly terminate; however, since that only kills the process in whose context the fault occured, it doesn't really matter.

# Fix timeline

This bug was reported 2018-09-12. Two days later, 2018-09-14, a fix was in the upstream kernel tree. This is exceptionally fast, compared to the fix times of other software vendors. At this point, downstream vendors could theoretically backport and apply the patch. The bug is essentially public at this point, even if its security impact is obfuscated by the commit message, which is [frequently](https://twitter.com/grsecurity/status/1042376315045916672) [demonstrated](https://twitter.com/grsecurity/status/1036346838121689091) [by](https://twitter.com/grsecurity/status/1034034322389573632) grsecurity.

However, a fix being in the upstream kernel does not automatically mean that users' systems are actually patched. The normal process for shipping fixes to users who use distribution kernels based on upstream stable branches works roughly as follows:

1. A patch lands in the upstream kernel.

2. The patch is backported to an upstream-supported stable kernel.

3. The distribution merges the changes from upstream-supported stable kernels into its kernels.

4. Users install the new distribution kernel.


Note that the patch becomes public after step 1, potentially allowing attackers to develop an exploit, but users are only protected after step 4.

In this case, the backport to the upstream-supported stable kernels 4.18, 4.14, 4.9 and 4.4 were published 2018-09-19, five days after the patch became public, at which point the distributions could pull in the patch.

Upstream stable kernel updates are published very frequently. For example, looking at the last few [stable releases for the 4.14 stable kernel](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/log/?h=linux-4.14.y&qt=grep&q=Linux+4.14.), which is the newest upstream longterm maintenance release:

4.14.72 on 2018-09-26

4.14.71 on 2018-09-19

4.14.70 on 2018-09-15

4.14.69 on 2018-09-09

4.14.68 on 2018-09-05

4.14.67 on 2018-08-24

4.14.66 on 2018-08-22

The 4.9 and 4.4 longterm maintenance kernels are updated similarly frequently; only the 3.16 longterm maintenance kernel has not received any updates between the most recent update on 2018-09-25 ( [3.16.58](https://git.kernel.org/pub/scm/linux/kernel/git/bwh/linux-stable.git/tag/?h=v3.16.58)) and the previous one on 2018-06-16 ( [3.16.57](https://git.kernel.org/pub/scm/linux/kernel/git/bwh/linux-stable.git/tag/?h=v3.16.57)).

However, Linux distributions often don't publish distribution kernel updates very frequently. For example, Debian stable [ships a kernel based on 4.9](https://packages.debian.org/search?keywords=linux-image-amd64&searchon=names&suite=stable&section=all), but as of 2018-09-26, this kernel [was last updated 2018-08-21](http://metadata.ftp-master.debian.org/changelogs//main/l/linux/linux_4.9.110-3+deb9u4_changelog). Similarly, Ubuntu 16.04 ships a kernel that was [last updated 2018-08-27](http://changelogs.ubuntu.com/changelogs/pool/main/l/linux-signed/linux-signed_4.15.0-34.37/changelog). Android only ships security updates once a month. Therefore, when a security-critical fix is available in an upstream stable kernel, it can still take weeks before the fix is actually available to users - especially if the security impact is not announced publicly.

In this case, the security issue was announced on the oss-security mailing list on 2018-09-18, with a CVE allocation on 2018-09-19, making the need to ship new distribution kernels to users clearer. Still: As of 2018-09-26, both Debian and Ubuntu (in releases 16.04 and 18.04) track the bug as unfixed:

[https://security-tracker.debian.org/tracker/CVE-2018-17182](https://security-tracker.debian.org/tracker/CVE-2018-17182)

[https://people.canonical.com/~ubuntu-security/cve/2018/CVE-2018-17182.html](https://people.canonical.com/~ubuntu-security/cve/2018/CVE-2018-17182.html)

Fedora pushed an update to users on 2018-09-22: [https://bugzilla.redhat.com/show\_bug.cgi?id=1631206#c8](https://bugzilla.redhat.com/show_bug.cgi?id=1631206#c8)

# Conclusion

This exploit shows how much impact the kernel configuration can have on how easy it is to write an exploit for a kernel bug. While simply turning on every security-related kernel configuration option is probably a bad idea, some of them - like the kernel.dmesg\_restrict sysctl - seem to provide a reasonable tradeoff when enabled.

The fix timeline shows that the kernel's approach to handling severe security bugs is very efficient at quickly landing fixes in the git master tree, but leaves a window of exposure between the time an upstream fix is published and the time the fix actually becomes available to users - and this time window is sufficiently large that a kernel exploit could be written by an attacker in the meantime.