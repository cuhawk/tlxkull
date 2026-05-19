---
source: p0
source_url: https://projectzero.google/2019/01/taking-page-from-kernels-book-tlb-issue.html
title: "Taking a page from the kernel's book: A TLB issue in mremap() - Project Zero"
description: "Posted by Jann Horn, Project ZeroThis is a technical blog post about TLB flushing bugs in kernels..."
---

Posted by Jann Horn, Project Zero

This is a technical blog post about TLB flushing bugs in kernels, intended for people interested in kernel security and memory management.

# Introduction: Bugs in Memory Management code

There have been some pretty scary bugs in memory management in the past, like:

- [CVE-2016-5195](https://dirtycow.ninja/), a logic bug in the Linux kernel that permitted writing to shared read-only pages

- [CVE-2018-1038](http://blog.frizk.net/2018/03/total-meltdown.html), a Windows bug that existed for about two months, where a bit was set incorrectly in a page table, permitting userspace to overwrite page tables


Memory management is one of the core functions that every kernel and hypervisor needs to implement; and the correctness of memory management code is very important to the security of the entire system. I hope that this post encourages more researchers to look at memory management code and demonstrates that memory management code can have issues with high security impact that fall somewhat outside of the typical security bug patterns.

This blog post focuses on memory management bugs related to TLB flushing. Such bugs can, if the timing works out for the attacker, provide very strong exploitation primitives for local attacks; and they are hard to discover unless you are manually looking for them. They are probably not a big bug class, but occasionally, bugs in TLB flushing logic do happen.

Here are the bugs related to TLB flushing that I have (co-)discovered:

- Xen PV: [XSA-241](https://xenbits.xen.org/xsa/advisory-241.html): "Stale TLB entry due to page type release race" (CVE-2017-15588) (security impact discovered by Xen security team)

- Linux: insufficient shootdown for paging-structure caches ( [link](https://bugs.chromium.org/p/project-zero/issues/detail?id=1633))

- gVisor: pagetable reuse across levels without paging-structure invalidation ( [link](https://bugs.chromium.org/p/project-zero/issues/detail?id=1674))

- \[XNU: pmap\_flush() omits TLB flushes on machines with >32 logical CPU cores ( [link](https://bugs.chromium.org/p/project-zero/issues/detail?id=1716)) \- this was already fixed in a binary release when I reported it, so it doesn't really count\]

- Linux: mremap() TLB flush too late with concurrent ftruncate() ( [link](https://bugs.chromium.org/p/project-zero/issues/detail?id=1695)) (CVE-2018-18281)


This blog post focuses on the last bug in the list.

By the way: Note that the gVisor bug is in memory management code written in Go, which is memory-safe [-ish](https://blog.stalkr.net/2015/04/golang-data-races-to-break-memory-safety.html). This demonstrates that in operating system code, "logic bugs" in some places, like page table management, can have consequences that are as severe as those of classical memory safety issues, and are not in the scope of the language's safety guarantees. Of course, memory-safe languages are still highly useful because they (should) prevent bugs in random, non-critical pieces of kernel code from corrupting completely unrelated system state, and they allow reviewers to spend more time on the security-critical parts of the system.

# Introduction: TLBs and paging-structure caches

If you know what a TLB is, what a TLB flush is, what paging-structure caches are, and how paging-structure caches are managed, you can skip this section. This section does not exhaustively describe the topic of TLB management; in particular, it doesn't deal with processor features like global page table entries and PCID/ASID.

Page tables contain information on how virtual addresses map to physical ones. Page tables are stored in memory, so they are comparatively slow to access; to make address translation fast, CPUs use caches. The classic caches for this are called Translation Lookaside Buffers (TLBs); they cache mappings from virtual to physical page addresses (including mappings for huge pages), or in other words, they (more or less) cache last-level page table entries. (Modern CPU cores often have multiple TLBs with different responsibilities, e.g. Intel CPUs have an instruction TLB, a data TLB and a shared L2 TLB.) TLB parameters are usually fairly well-documented; for example:

- Intel's [Optimization Reference Manual](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-optimization-manual.pdf) has information about TLB structure in the "Cache and Memory Subsystem" subsections for various processor generations

- Arm documents the TLB parameters of their cores in [their processor documentation](http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.set.cortexa/index.html), in the Technical Reference Manual for the core, under "Memory Management Unit > TLB organization".

- AMD publishes TLB parameters in their [Software Optimization Guides](https://developer.amd.com/resources/developer-guides-manuals/).


Paging-structure caches are usually less well-documented; but there is official documentation about their existence and necessary precautions when dealing with them. Intel calls them "Paging-Structure Caches", Arm calls them "Intermediate table walk caches", AMD documents them as part of the L2 data TLB (at least for 17h processors). Paging-structure caches store copies of non-last-level page table entries; they are used when a virtual address without a corresponding TLB entry is being accessed, and they reduce the number of memory accesses for a page table walk. There are some reverse-engineered details about the paging-structure caches of various processors in [a VUSec paper](https://www.cs.vu.nl/~herbertb/download/papers/revanc_ir-cs-77.pdf) (in Table 1).

It generally has to be assumed that entries in TLBs and paging-structure caches can be evicted by the processor whenever it wants to. Similarly, it has to be assumed that a processor can create entries in TLBs and paging-structure caches from page table entries whenever it wants to, because memory accesses in speculatively executed code can create such entries.

Mechanisms to invalidate TLB entries and paging-structure caches differ between processor architectures:

X86 provides instructions to invalidate either individual TLB entries for the current logical CPU core, or to invalidate the entire TLB (either with or without global entries) for the current logical CPU core. Invalidating the TLB entry for a virtual address also at least implies invalidation of any paging-structure cache entries that could be used for translating that virtual address. The Intel SDM documents this in volume 3A, chapter 4.10.4 ("Invalidation of TLBs and Paging-Structure Caches"). (The SDM says that INVLPG invalidates all paging-structure caches, but doesn't make such broad guarantees for individual-address INVPCID as far as I can tell.) To perform TLB invalidation across logical CPU cores, an operating system has to manually run code that invalidates TLB entries on each logical CPU core; this is normally implemented by sending Inter-Processor Interrupts (via APIC) from the processor that wants to perform a TLB invalidation to all other processors that might have relevant stale TLB or paging-structure cache entries.

The ARM architecture provides magic instructions that can perform cross-core TLB invalidation for you; however, if you also need to synchronize against page table walks implemented in software (like the Linux kernel), you may have to send IPIs anyway (depending on the synchronization mechanism used for page table walks).

The general code pattern for performing cache invalidations for page table entries is:

1. Remove an entry from a page table, but keep holding a reference to the physical page it points to.

2. Perform a TLB flush (either for a specific address, or for the entire address space) across all cores that might be using the same page tables as the current thread.

3. Drop the reference that was held on the physical page, potentially freeing it.


This pattern is the same both when unmapping normal data pages and when removing page tables. It can often be batched for better performance - first remove multiple page table entries, then do one TLB flush across cores, then drop all the page references -, but for the mapping of an individual page (including page tables), this pattern is generally true.

On X86 (but ARM64 is similar), there are two bits in a last-level PTE which the CPU can write into as part of address translation: The Accessed bit specifies whether the CPU has ever used the page table entry for address translation; in other words, if the Accessed bit is unset, the value of the page table entry has not been cached by the TLB since the last time the page table entry was written by software. The Dirty bit specifies whether the CPU has ever used the page table entry for a writing memory access; in other words, if the Dirty bit is unset, no TLB entries that can be used to write to the physical page have been created since the last software write to the PTE.

# Linux: mremap() TLB flush too late

## The bug

On Linux, memory management data structures of a process are protected by multiple locks; in particular, the read/write semaphore mmap\_sem in struct mm\_struct is used to protect the VMA (virtual memory area) structures, and page table locks (if the kernel is configured normally, implemented using per-page-table spinlocks for lower-level page tables) are used to protect access to page tables. Accesses to the page tables of a process for syscalls such as mmap()/mremap()/munmap(), as well as syscalls for page fault handling, use both the mmap\_sem and page table locks. However, some other types of page table access (e.g. operations on all places across the system where a given file is mapped, like an ftruncate() syscall that shrinks a file and frees pages beyond the new end of the file) don't hold the mmap\_sem and only use page table locks.

The mremap() syscall allows userspace to move a VMA and its associated page table entries. This syscall moves page tables via mremap\_to() -\> move\_vma() -\> move\_page\_tables() -\> move\_ptes(). The  move\_ptes() function implemented roughly the following logic for moving entries between two L1 page tables, with only the mmap\_sem held initially (locked in exclusive mode):

01. (Take reverse map locks in some cases if the new VMA has been merged into an adjacent VMA.)

02. Take page table locks on the old and new page tables.

03. (Do a TLB flush if the direct reclaim path is in the middle of stealing some pages from the current process.)

04. For each non-empty entry in the relevant range of the current source page table:


    1. Atomically read the current value of the page table entry and clear it (using ptep\_get\_and\_clear(), which e.g. on X86 boils down to a LOCK XCHG).

    2. If the read page table entry is Dirty, set the local force\_flush flag to true.

    3. Write the read page table entry into the page table for the new mapping.


06. Unlock the new page table.

07. If the force\_flush flag was set, perform a TLB flush on the old page table entries that were accessed in step 4.

08. Unlock the old page table.

09. (Drop reverse map locks if they were taken.)

10. If the force\_flush flag wasn't set, signal to the caller move\_page\_tables() that a TLB flush is required.


Later, after iterating over multiple page tables, move\_page\_tables() then performs a TLB flush on the old address range if requested.

move\_ptes() needs to ensure that, when it releases the old page table's reference, there can be no more stale TLB entries. There is nothing in move\_ptes() that explicitly drops a reference, but move\_ptes()moves the reference into the new page table entry. While the page table locks on the new page table are held, other tasks running concurrently can't yet remove the new page table entry and drop its reference, so things are still fine after step 4c - the page can't be freed. But after step 5, another task can theoretically race with mremap() and drop the page. This is long before move\_page\_tables() performs the relevant TLB flush on the old address range (this is the bug I reported), and also slightly before the TLB flush is performed in the force\_flush case (I didn't notice that, but the kernel security team did).

On modern kernels, the big race window only works for non-Dirty page table entries - in other words, the big race window can only be used for use-after-free reads, not use-after-free writes. However, before [commit 5d1904204c99](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5d1904204c99) (from November 2016, first in v4.9), the special case for Dirty page table entries did not exist, and the big race window was also usable for use-after-free writes.

Almost everyone is using kernel versions >=4.9 nowadays - for example, [Debian stable ships a kernel based on 4.9](https://packages.debian.org/search?suite=stretch&searchon=names&keywords=linux-image-amd64). But there are some exceptions: RHEL [still ships 3.10-based kernels](https://access.redhat.com/articles/3078), and many Android devices are based on kernels older than 4.9. For example, the kernel branches used by Google's Pixel phones are:

- Google Pixel: 3.18

- Google Pixel 2: 4.4

- Google Pixel 3: 4.9


I decided to write an exploit for Google's Pixel 2.

## Locks and preemption

This section, along with the following one, describes some background that will be useful for developing an exploit strategy.

The Linux kernel supports three different models for preemption of kernel code, one of which has to be selected at build time:

- CONFIG\_PREEMPT\_NONE ("No Forced Preemption (Server)")

- CONFIG\_PREEMPT\_VOLUNTARY ("Voluntary Kernel Preemption (Desktop)")

- CONFIG\_PREEMPT ("Preemptible Kernel (Low-Latency Desktop)")


(More preemption types [are coming](https://www.youtube.com/watch?v=BxJm-Ujipcg) with the realtime patchset, but that hasn't landed yet.)

The preemption model determines what happens when the kernel wishes to interrupt a task that is currently running kernel code - e.g. because a task with higher priority has become runnable and is waiting to be scheduled.

The Pixel 2 uses a kernel configured with CONFIG\_PREEMPT. This means that by default, kernel code can be interrupted at any point during its execution. This even works while a task is holding a mutex, while it is holding a semaphore, or while it is in an RCU read-side critical section (depending on kernel configuration). Only something like a spinlock actually suppresses preemption.

As an attacker, we would like to make the race window between the time move\_ptes() drops the page table lock and the time the TLB flush occurs in move\_page\_tables() as big as possible. Here, it is very useful for us that kernel code is preemptible: Because only the mmap\_sem is held across the race window, and the mmap\_sem does not inhibit preemption, we can potentially convince the scheduler to kick the task off the CPU core while it is in the middle of the race window, and then keep the task off the CPU for an amount of time on the order of milliseconds.

The kernel allows us to set the affinity of our tasks (the list of CPU cores on which a task is allowed to run), and it also allows us to set various scheduler parameters that control the relative priority of our tasks. This means that we can use affinity masks to pin multiple processes we own together onto a single CPU core, with different priorities - meaning that waking up the higher-priority task implies preemption of the lower-priority one. In this case, by assigning the SCHED\_IDLE priority to the task running mremap(), pinning it together with a task that has normal priority and is blocking on a read() from a pipe, and then writing to the other side of that pipe in the right moment, we can preempt the mremap() syscall.

To know the right moment for calling write() on the other end of the pipe, we can abuse procfs. The procfs file /proc/<pid>/status contains various fields about the memory use of a process, including the VmPTE field, which shows the amount of memory consumed by the page tables of a process. By busy-polling the status file and monitoring the VmPTE field, it is possible to detect the page table allocations performed by the mremap() syscall.

## The page allocator

The Linux page allocator is based on a [buddy allocator](https://en.wikipedia.org/wiki/Buddy_memory_allocation), implemented in [mm/page\_alloc.c](https://elixir.bootlin.com/linux/latest/source/mm/page_alloc.c). This allocator tracks free pages of different orders; an order-n page is 212+n bytes big and is aligned to a 212+n-byte boundary (assuming that the system is using a native page size of 212 bytes).

Page freelists are not just per-order, but also per-zone, per-migration-type and (on NUMA systems, which isn't relevant for Android phones) per-node.

The zone specifies in which ways a page can be used; pages stay associated with a single zone. The following zones can exist; bold text indicates that the zone actually exists on the Pixel 2:

- ZONE\_DMA: like ZONE\_NORMAL, but can also be used for DMA with devices that can only address a small subset of physical memory (used by arm64 before kernel 4.16)

- ZONE\_DMA32: like ZONE\_NORMAL, but can also be used for DMA with devices that can only use 32-bit physical addresses (used by arm64 since kernel 4.16)

- ZONE\_NORMAL: can be used for normal kernel memory allocations and as userspace memory; page is mapped in the linear mapping

- ZONE\_HIGHMEM: Can only be used for special types of kernel memory allocations and as userspace memory; page is not mapped in the linear mapping. This doesn't exist on arm64, since virtual memory is large enough to map all physical memory.

- ZONE\_MOVABLE: manually reserved for pages that the kernel can (usually) move to a different physical address when needed (basically, userspace memory); this [enables limited memory hotplugging](https://events.static.linuxfound.org/sites/events/files/lcjp13_ishimatsu.pdf) and [reduces fragmentation (which can help with the allocation of hugepages)](https://lwn.net/Articles/219589/); the Pixel 2 doesn't seem to be using this

- ZONE\_DEVICE: [something about persistent memory?](https://lwn.net/Articles/717555/) \- arm64 never uses this


The migration type of a page specifies either what kind of allocation the page is currently being used for (if the page is currently in use) or what kind of allocation the page should preferably be used for (if the page is free); the intent is to cluster pages that the kernel can reclaim by moving their contents together, allowing the kernel to later create high-order free pages by moving data out of the way. The following migration types exist:

- MIGRATE\_UNMOVABLE: for allocations that can't simply be removed from their physical page whenever the kernel wants to have the page for something else - e.g. normal kmalloc() allocations

- MIGRATE\_MOVABLE: for data that the kernel can (usually) simply move to another physical page - e.g. userspace memory

- MIGRATE\_RECLAIMABLE: for allocations that the kernel can't simply move to a different address, but that the kernel can free if necessary to free up some memory

- MIGRATE\_HIGHATOMIC: [something about memory reserves for high-order page allocator calls that shouldn't fail but also can't wait for pages to be freed?](https://lwn.net/Articles/658081/)

- MIGRATE\_CMA: [special memory reserves for contiguous memory for DMA](https://lwn.net/Articles/486301/), can only be used for specific DMA allocations and for movable allocations

- MIGRATE\_ISOLATE: no allocations are possible - used for purposes like memory hot-removal and blacklisting of defective RAM at runtime


The first two or three of these are the most relevant ones - the rest are kinda special.

The page allocator also has per-cpu, per-zone, per-migratetype freelists as a performance optimization. These only contain order-0 pages. In kernel versions <4.15, one annoying thing about the per-cpu freelists is that they can be accessed from both sides. Normal freelist accesses push and pop on the same end so that pages coming from the freelist are more likely to be in the CPU cache; but when freeing pages that are expected to be cache-cold, and when allocating pages that have to wait for DMA before they are written to the first time, old kernel versions access the freelist from the other end.

The algorithm for allocating pages via get\_page\_from\_freelist(), before entering the slowpath, works roughly as follows (ignoring things like NUMA and atomic/realtime allocations):

- For each zone (from the most preferred zone to the least preferred zone); in other words, on the Pixel 2, when allocating non-DMA memory, first for ZONE\_NORMAL, then for ZONE\_DMA:

  - rmqueue\_pcplist(): If we want an order-0 page, attempt to allocate from the per-cpu freelist for the current zone and our preferred migratetype. If this freelist is empty, try to refill it by looking through the per-order freelists for the current zone and our preferred migratetype, starting at order 0, iterating through the freelists with increasing order (standard buddy allocator behavior).

  - Attempt to allocate from the buddy allocator directly, by iterating through the per-order freelists for the current zone and our preferred migratetype with increasing order.

  - If we want a movable page, attempt to allocate from MIGRATE\_CMA memory instead.

  - \_\_rmqueue\_fallback(): Tries to grab a free block of maximum order from a freelist with a different migration type, then potentially changes that block's migration type to the desired one.

For an attacker attempting to exploit a use-after-free at the page allocator level, this means that getting the kernel to reallocate a movable page for an unmovable allocation, or the other way around, requires creating memory pressure that forces the buddy allocator to go through \_\_rmqueue\_fallback() and steal pages from a different migration type.

## Exploit strategy

For exploiting the TLB invalidation race, we want to quickly reallocate the freed movable page from the page cache. Preferably we'll do this through a per-cpu freelist, so it is probably easier to have it reallocated as a movable page instead of forcing a migratetype change. With this strategy, we can't attack things like normal kernel memory allocations or page tables, but we can attack the page cache and anonymous userspace memory. I chose to poison page cache memory, since I wanted to avoid having other userspace processes in the critical timing path of the attack.

This means that at a high level, to perform the attack, we need to pick a victim file page (in other words, a page-aligned and page-sized area in a file) that we want to corrupt, in a file to which we have read-only access (e.g. a shared library containing executable code). Then, we need to poison the page cache entry for the victim file page by running roughly the following steps in a loop:

1. Somehow evict the victim file page from the page cache.

2. Allocate a set of file-backed pages (e.g. by writing to a memfd), and map them as mapping A.

3. Trigger the mremap/ftruncate race to free the file-backed pages without removing the corresponding TLB entries for mapping A.

4. Start a read from the victim page, causing the kernel to reallocate one of the freed pages as the page cache entry for the victim page.

5. Poll the contents of pages in mapping A (through the stale TLB entries) until one of them contains the victim page. If a page fault occurs before that, go back to step 1.

6. At this point, we have a stale TLB entry translating the old mapping A to the victim page. Therefore, we can now repeatedly overwrite the victim page through mapping A. (In theory, it seems like a single overwrite should be sufficient; but in practice, that doesn't seem to work. I'm not sure whether this is caused by some sort of cache inconsistency (because memory is concurrently written via DMA and by software), or whether I did something else wrong.)


On kernels <4.15, because of the annoying two-sided behavior of the per-cpu freelist, when a new physical page is allocated to store the victim page, it comes from the "cold" end of the per-cpu freelist; so instead of simply pushing a page with a stale TLB entry onto the per-cpu freelist and letting the kernel use it for the victim page, it is necessary to quickly push enough pages with stale TLB entries to force the kernel to move all existing per-cpu freelist entries to the global freelist.

## Forcing page cache reloads

This section focuses on the first step of the exploit strategy, evicting the victim page from the page cache.

Public prior research on this topic that I used for my PoC is [https://arxiv.org/abs/1710.00551](https://arxiv.org/abs/1710.00551) ("Another Flip in the Wall of Rowhammer Defenses"), which uses page cache eviction as a mechanism to repeatedly move file-backed pages to different physical pages. This paper says in section VIII-B:

A fundamental observation we made is that the replacement algorithm of the Linux page cache prioritizes eviction of nonexecutable pages over executable pages.

In shrink\_active\_list() and page\_check\_references() in mm/vmscan.c, you can see that file-backed executable pages indeed get special handling:

static void shrink\_active\_list(unsigned long nr\_to\_scan,

                   struct lruvec \*lruvec,

                   struct scan\_control \*sc,

                   enum lru\_list lru)

{

\[...\]

    /\*

     \\* Identify referenced, file-backed active pages and

     \\* give them one more trip around the active list. So

     \\* that executable code get better chances to stay in

     \\* memory under moderate memory pressure.  Anon pages

     \\* are not likely to be evicted by use-once streaming

     \\* IO, plus JVM can create lots of anon VM\_EXEC pages,

     \\* so we ignore them here.

     \*/

    if ((vm\_flags & VM\_EXEC) && page\_is\_file\_cache(page)) {

        list\_add(&page->lru, &l\_active);

        continue;

    }

\[...\]

}

\[...\]

static enum page\_references page\_check\_references(struct page \*page,

                          struct scan\_control \*sc)

{

\[...\]

    /\*

     \\* Activate file-backed executable pages after first usage.

     \*/

    if (vm\_flags & VM\_EXEC)

        return PAGEREF\_ACTIVATE;

    return PAGEREF\_KEEP;

\[...\]

}

Therefore, executable file-backed pages are used to create memory pressure to evict the victim page.

For this attack, it is also desirable that the victim page, once evicted, is not reloaded from disk until it is accessed the next time. This is not always the case: The kernel has some readahead logic that, depending on the observed memory access pattern, may read large amounts of data (up to VM\_MAX\_READAHEAD, which is 128KiB) around a page fault from disk. This is implemented in filemap\_fault() by calling into do\_async\_mmap\_readahead() / do\_sync\_mmap\_readahead(). An attacking process can simply opt out of this for its own accesses, but it is also desirable to suppress this behavior for accesses coming from other processes that might be executing code from other pages in the victim file.

For this reason, the PoC first evicts the victim page, then accesses all other pages in the victim file through a mapping with MADV\_RANDOM to reduce the probability that accesses to those other pages trigger readahead logic: When a page being accessed is present in RAM, synchronous readahead won't happen; and when the page being accessed with a minor fault (i.e. the page is present in the page cache, but no corresponding page table entry exists yet) is not marked as PG\_readahead, asynchronous readahead won't happen either.

## Picking a victim page

My exploit targets a victim page in the library /system/lib64/libandroid\_runtime.so that contains the function com\_android\_internal\_os\_Zygote\_nativeForkAndSpecialize(). This function is executed in the context of the zygote process whenever an app process needs to be launched — in other words, it shouldn't run very often on an idle device, meaning that we can evict it and then have time to trigger the bug —, and we can trigger its execution by launching an isolated service, so we can easily cause its execution immediately after successfully triggering the bug. The zygote process has the CAP\_SYS\_ADMIN capability (and is permitted to use it), and because its job is to fork off children that become app processes and system\_server, it has access to the contexts of system\_server and every app.

To demonstrate that the code injection into the zygote is working, the injected code reads its own SELinux context and then overwrites the hostname with that string (using sethostname()).

## Putting it together

The exploit is packaged in an app that, when you press the "run" button, first uses the code in eviction.c to flush the victim page in /system/lib64/libandroid\_runtime.so from the page cache; afterwards, the code in sched\_test.c is used to trigger the mremap bug and overwrite the victim page. If sched\_test.c reports that it has successfully located and overwritten the targeted code page, the Java code launches the isolated app TriggerService to trigger execution of com\_android\_internal\_os\_Zygote\_nativeForkAndSpecialize(); otherwise, the attack is restarted.

sched\_test.c executes the following threads:

- idle\_worker(): on core 4, with SCHED\_IDLE priority; is moved to core 3 during the attack

- spinner(): on core 4, with normal priority

- nicer\_spinner(): on core 3, with normal priority

- read\_worker(): on core 5, with normal priority

- main(): on core 6, with normal priority


The following screenshot shows the running exploit, which has performed a few exploit attempts already, but hasn't managed to visibly trigger the bug yet:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgPbWu_s600_93mlFTkwjMzSRuc3kWFJ76reP8gFsuT2gLPGWrk1pWJkTAH0PSxf65jrIS-Nu7ePBgTibPlash1SjJm1se7aAat-n9au3uu4eiQyhHJV0Yno4IVAVhsyglJhym229R36knksDWJs.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgPbWu_s1600_93mlFTkwjMzSRuc3kWFJ76reP8gFsuT2gLPGWrk1pWJkTAH0PSxf65jrIS-Nu7ePBgTibPlash1SjJm1se7aAat-n9au3uu4eiQyhHJV0Yno4IVAVhsyglJhym229R36knksDWJs.png)

In the next screenshot, the exploit has managed to read data through the stale TLB entry, but still hasn't managed to locate and overwrite the victim page:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEinrCY_s600_3tzNWbs6WBCOqht2FiAq6v-sHWzlpvpxd-3T9ROHpj0UM85_IG8LnJwC5sLYmw6YdSa4JporSm7iSllJ_lg9Dhk6HyO1WvsPi-1LUsa5eZ70rtZzWxpTFwXMRJnCCf988QwmbgoA.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEinrCY_s1600_3tzNWbs6WBCOqht2FiAq6v-sHWzlpvpxd-3T9ROHpj0UM85_IG8LnJwC5sLYmw6YdSa4JporSm7iSllJ_lg9Dhk6HyO1WvsPi-1LUsa5eZ70rtZzWxpTFwXMRJnCCf988QwmbgoA.png)

In the third screenshot, the exploit has succeeded:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj2kt0_s600_reMTDRnRSiNhqlQcK1qu1mgRH-40hjszcRAQTCew_aDUN0Mp3fTgc_Op4P4C4D6_W8fjCMud6xX7HuZryK3erXRVbzU3Um5dlPbTvG3A-LXcnsdoslSp-a8hjXXmLrH8PpzvC71w.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj2kt0_s1600_reMTDRnRSiNhqlQcK1qu1mgRH-40hjszcRAQTCew_aDUN0Mp3fTgc_Op4P4C4D6_W8fjCMud6xX7HuZryK3erXRVbzU3Um5dlPbTvG3A-LXcnsdoslSp-a8hjXXmLrH8PpzvC71w.png)

## Timeline

This bug [was reported](https://bugs.chromium.org/p/project-zero/issues/detail?id=1695) to the Linux kernel on 2018-10-12.

A fix [was committed and made public](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=eb66ae030829605d61fbef1909ce310e29f78821) six days later, on 2018-10-18.

Two days after that, on 2018-10-20, new upstream stable kernels were released on the branches [4.9](https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.135), [4.14](https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.78) and [4.18](https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.16).

On 2018-10-29, we [published](https://bugs.chromium.org/p/project-zero/issues/detail?id=1695#c4) the bug report.

On 2018-11-10, an upstream backport on the 4.4 branch was [released](https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.163).

On 2018-11-14, we [published](https://bugs.chromium.org/p/project-zero/issues/detail?id=1695#c5) the exploit described in this blogpost.

It took more than two months for the upstream kernel change to make its way to user devices; writing an exploit for this bug took far less time.

# Conclusion

There isn't really an overarching conclusion here, but some takeaways:

- Bugs in TLB flushing logic can be exploitable and lead to system compromise from unprivileged userspace.

- When trying to exploit a use-after-free of a physical page on Linux, keep in mind that the page allocator will try to avoid changing the migration types of pages, so usually movable pages (anonymous userspace memory and page cache) will be reused as movable pages, and unmovable pages (normal kernel memory) will be reused as unmovable pages.

- Knowing a bit about the scheduler, and in particular preemption, can be very helpful for widening kernel race windows. Linux exposes fairly powerful control over scheduling to unprivileged userspace.

- Android takes months to ship an upstream kernel security fix to users; it would be nice if that was significantly faster.