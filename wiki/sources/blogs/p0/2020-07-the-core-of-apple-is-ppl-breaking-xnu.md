---
source: p0
source_url: https://projectzero.google/2020/07/the-core-of-apple-is-ppl-breaking-xnu.html
title: "The core of Apple is PPL: Breaking the XNU kernel's kernel - Project Zero"
description: "Posted by Brandon Azad, Project ZeroWhile doing research for the one-byte exploit technique,..."
---

Posted by Brandon Azad, Project Zero

While doing research for the[one-byte exploit technique](https://projectzero.google/2020/07/one-byte-to-rule-them-all.html), I considered several ways it might be possible to bypass Apple's [Page Protection Layer](https://support.apple.com/guide/security/page-protection-layer-sec38dc659b4/web) (PPL) using just a physical address mapping primitive, that is, before obtaining kernel read/write or defeating PAC. Given that PPL is even more privileged than the rest of the XNU kernel, the idea of compromising PPL "before" XNU was appealing. In the end, though, I wasn't able to think of a way to break PPL using the physical mapping primitive alone.

PPL's goal is to prevent an attacker from modifying a process's executable code or page tables, even after obtaining kernel read/write/execute privileges. It does this by leveraging [APRR](https://siguza.github.io/APRR/) to create something of a "kernel inside the kernel" that protects page tables. During normal kernel execution, page tables and page table metadata are read-only, and code that modifies page tables is non-executable; the only way for the kernel to modify page tables is to enter PPL by calling a "PPL routine", which is analogous to a syscall from XNU into PPL. This limits the entry points into the kernel code that can modify page tables to just those PPL routines.

I considered several ideas to bypass PPL using the one-byte technique's physical mapping primitive, including mapping page tables directly, mapping a [DART](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/vm/vm.html) to allow modifying physical memory from a coprocessor, and mapping the I/O addresses used to control clock gating to power down certain components of the system. Unfortunately, none of these ideas panned out.

However, it's not the Project Zero way to leave any mitigation unbroken. So, having exhausted my search for design flaws, I returned to the ever-faithful technique of memory corruption. Sure enough, decompiling a few PPL functions in IDA was sufficient to find some memory corruption.

[![Decompiler output showing a call to pmap_remove_range_options().](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgfLPh_s1200_image1%2810%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgfLPh_s1382_image1%2810%29.png) Some memory corruption in pmap\_remove\_options\_internal(). Using a kernel function calling primitive, both va\_start and size are controlled.

The function pmap\_remove\_options\_internal() is a PPL routine, one of the "PPL syscalls" from the XNU kernel to the even more privileged PPL. It is called by invoking pmap\_remove\_options() in XNU, which validates arguments and then calls pmap\_remove\_options\_internal() in PPL. Its purpose is to unmap the supplied virtual address range from the physical memory map (pmap) of a process.

MARK\_AS\_PMAP\_TEXT staticint

pmap\_remove\_options\_internal(

pmap\_t pmap,

vm\_map\_address\_t start,

vm\_map\_address\_t end,

int options)

The actual work of removing the translation table entries (TTEs) that map the supplied virtual address range is done by calling pmap\_remove\_range\_options(), which takes pointers to the beginning and end of the TTE range to remove from the level 3 (leaf) translation table.

staticint

pmap\_remove\_range\_options(

pmap\_t pmap,

pt\_entry\_t \*bpte,   // The first L3 TTE to remove

pt\_entry\_t \*epte,   // The end of the TTEs

uint32\_t \*rmv\_cnt,

int options)

Unfortunately, when pmap\_remove\_options\_internal() calls pmap\_remove\_range\_options(), it seems to assume that the supplied virtual address range will not cross an L3 translation table boundary, because if it does then the calculated TTE range will span out-of-bounds memory:

remove\_count = pmap\_remove\_range\_options(

pmap,

                   &l3\_table\[(va\_start >\> 14) & 0x7FF\],

                   (u64 \*)((char \*)&l3\_table\[(va\_start >\> 14) & 0x7FF\]

                         \+ ((size >\> 11) & 0x1FFFFFFFFFFFF8LL)),

                   &rmv\_spte,

options);

This means that if we have an arbitrary kernel function calling primitive, we can invoke the PPL-entering wrapper function directly and get pmap\_remove\_options\_internal() called with an improper virtual address range, which makes pmap\_remove\_range\_options() try to remove "TTEs" read from out-of-bounds memory while in PPL mode. And since the removed TTEs are zeroed out, this means that we can corrupt PPL-protected memory.

[![Calling pmap_remove_options_internal() with an address range spanning an L2 TTE boundary (that is, the address range requires two L2 TTEs to map it) will cause the processed TTE array to run off the end of the L3 translation table page, resulting in out-of-bounds TTEs being removed.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgW8K5_s1200_image2%287%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgW8K5_s2500_image2%287%29.png)

But zeroing out-of-bounds TTEs would be a rather annoying primitive to try and leverage for a PPL bypass. Much of the data we'd like to corrupt has probably already been allocated far away from our page tables, and PPL isn't a large enough code base that we're guaranteed to find something interesting we can do just by zeroing memory. And that's to say nothing of the accounting in PPL that would probably detect an attempt to unmap non-existent TTEs!

So instead I chose to focus on a side effect of this out-of-bounds processing: improper TLB invalidation.

Later on in pmap\_remove\_options\_internal(), after the TTEs have been removed, the [translation lookaside buffer](https://en.wikipedia.org/wiki/Translation_lookaside_buffer) (TLB) needs to be invalidated in order to ensure that the process cannot continue to access the unmapped pages through stale TLB entries.

flush\_mmu\_tlb\_region\_asid\_async(va\_start, size, pmap);

This TLB flush occurs on the supplied virtual address range, not the removed TTEs. Thus, there could be a disagreement between the TLB entries invalidated and the L3 TTEs removed if the out-of-bounds TTEs were from a separate region of the process's address space, leaving stale TLB entries for those out-of-bounds TTEs.

[![By carefully controlling the layout of translation tables, it's possible to transform the out-of-bounds TTE removal into a different bug: improper TLB invalidation. This is because the out-of-bounds TTEs can correspond to discontiguous parts of the virtual address space, causing the set of TTEs removed to differ from the set of TLB entries flushed.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhV0OB_s1200_image3%285%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhV0OB_s2048_image3%285%29.png)

A stale TLB entry would allow a process to continue accessing the physical page after that page has been unmapped and potentially reused for page tables. So if we had a stale TLB entry for an L3 translation table, then we could insert L3 TTEs to map arbitrary PPL-protected pages as writable.

That's pretty much exactly how the PPL bypass works:

1. Call the kernel function cpm\_allocate() to allocate 2 pages of contiguous physical memory called A and B.

2. Call pmap\_mark\_page\_as\_ppl\_page() to insert pages A and B at the head of the ppl\_page\_list so they can be reused for page tables.

3. Fault in pages for virtual addresses P and Q so that A and B are allocated as L3 TTs for mapping P and Q, respectively. P and Q are discontiguous but have TTEs that are contiguous.

4. Start a spinner thread bound to a CPU core that reads from page Q in a loop to keep the TLB entry alive.

5. Call pmap\_remove\_options() to remove 2 pages starting from virtual address P (which does not include Q). The vulnerability means that TTEs for both P and Q are removed, but only the TLB entry for P is invalidated.

6. Call pmap\_mark\_page\_as\_ppl\_page() to insert page Q at the head of the ppl\_page\_list so it can be reused for page tables.

7. Fault in a page for virtual address R so that page Q is allocated as an L3 TT for R, even while we continue to have a stale TLB entry for Q.

8. Using the stale TLB entry, write to page Q to insert an L3 TTE which maps Q itself as writable.


[![An animation showing the progression of the exploit over time. The vulnerability is used to establish a stale TLB entry for an unmapped page Q which then gets reallocated as an L3 translation table. The stale TLB entry for Q allows us to modify it and insert an L3 TTE mapping Q itself, which can then be used to modify page tables even after the stale TLB entry has been cleared.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhVnrT_s1200_image4.gif)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhVnrT_s2500_image4.gif)

This bypass was reported as [Project Zero issue 2035](https://bugs.chromium.org/p/project-zero/issues/detail?id=2035) and fixed in iOS 13.6; you can find a POC that demonstrates how to map arbitrary physical addresses into EL0 there. Also, for a much more detailed look at exploiting improper TLB invalidation, check out Jann Horn's [excellent blog post](https://projectzero.google/2019/01/taking-page-from-kernels-book-tlb-issue.html) on the topic.

This bug demonstrates a common problem when creating a security boundary where none existed before. It's easy for code to make subtle assumptions about the security model (such as where argument validation occurs or what functionality is exposed vs. private) that no longer hold true under the new model. I wouldn't be surprised to see more bugs along this line in PPL.

Overall, though, I came away from this exercise impressed with the design of PPL. I think it's a sound mitigation with a clear security boundary that doesn't [introduce more attack surface](https://projectzero.google/2020/02/mitigations-are-attack-surface-too.html). My biggest criticism is that the value-add proposition of PPL is still not yet clear to me: What real-world attacks does PPL mitigate? Is it simply laying the groundwork for more sophisticated and powerful mitigations to come? Whatever the answer may be, I still prefer having it. Kudos to Apple for an interesting and well-thought-out mitigation.