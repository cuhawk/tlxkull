---
source: p0
source_url: https://projectzero.google/2020/07/one-byte-to-rule-them-all.html
title: "One Byte to rule them all - Project Zero"
description: "Posted by Brandon Azad, Project ZeroOne Byte to rule them all, One Byte to type them,One Byte to ..."
---

Posted by Brandon Azad, Project Zero

One Byte to rule them all, One Byte to type them,

One Byte to map them all, and in userspace bind them

\-\- Comment above vm\_map\_copy\_t

For the last several years, nearly all iOS kernel exploits have followed the same high-level flow: memory corruption and fake Mach ports are used to gain access to the kernel task port, which provides an ideal kernel read/write primitive to userspace. Recent iOS kernel exploit mitigations like PAC and zone\_require seem geared towards breaking the canonical techniques seen over and over again to achieve this exploit flow. But the fact that so many iOS kernel exploits look identical from a high level begs questions: Is targeting the kernel task port really the best exploit flow? Or has the convergence on this strategy obscured other, perhaps more interesting, techniques? And are existing iOS kernel mitigations equally effective against other, previously unseen exploit flows?

In this blog post, I'll describe a new iOS kernel exploitation technique that turns a one-byte controlled heap overflow directly into a read/write primitive for arbitrary physical addresses, all while completely sidestepping current mitigations such as KASLR, PAC, and zone\_require. By reading a special hardware register, it's possible to locate the kernel in physical memory and build a kernel read/write primitive without a fake kernel task port. I'll conclude by discussing how effective various iOS mitigations were or could be at blocking this technique and by musing on the state-of-the-art of iOS kernel exploitation. You can find the proof-of-concept code [here](https://bugs.chromium.org/p/project-zero/issues/detail?id=1986#c7).

# I - The Fellowship of the Wiring

## A struct of power

While looking through the XNU sources, I often keep an eye out for interesting objects to manipulate or corrupt for future exploits. Soon after discovering [CVE-2020-3837](https://bugs.chromium.org/p/project-zero/issues/detail?id=1986) (the oob\_timestamp vulnerability), I stumbled across the definition of vm\_map\_copy\_t:

struct vm\_map\_copy {

int                     type;

#defineVM\_MAP\_COPY\_ENTRY\_LIST1

#defineVM\_MAP\_COPY\_OBJECT2

#defineVM\_MAP\_COPY\_KERNEL\_BUFFER3

vm\_object\_offset\_t      offset;

vm\_map\_size\_t           size;

union {

struct vm\_map\_header    hdr;      /\\* ENTRY\_LIST \*/

vm\_object\_t             object;   /\\* OBJECT \*/

uint8\_t                 kdata\[0\]; /\\* KERNEL\_BUFFER \*/

        } c\_u;

};

This looked interesting to me for several reasons:

1. The structure has a type field at the very start, so an out-of-bounds write could change it from one type to another, leading to type confusion. Because iOS is little-endian, the least significant byte comes first in memory, meaning that even a single-byte overflow would be sufficient to set the type to any of the three values.

2. The type discriminates a union between arbitrary controlled data (kdata) and kernel pointers (hdr and object). Thus, corrupting the type could let us directly fake pointers to kernel objects without needing to perform any reallocations.

3. I remembered reading about vm\_map\_copy\_t being used as an interesting primitive in past exploits (before iOS 10), though I couldn't remember where or how it was used. vm\_map\_copy objects were also used by Ian Beer in [Splitting atoms in XNU](https://projectzero.google/2019/04/splitting-atoms-in-xnu.html).


So, vm\_map\_copy looks like a possibly interesting target for corruption; however, it's only truly interesting if the code uses it in a truly interesting way.

Digging through osfmk/vm/vm\_map.c, I found that vm\_map\_copyout\_internal() does indeed use the copy object in a very interesting way. But first, let's talk a little more about what vm\_map\_copy is and how it works.

A vm\_map\_copy represents a copy-on-write slice of a process's virtual address space which has been packaged up, ready to be inserted into another virtual address space. There are three possible internal representations: as a list of vm\_map\_entry objects, as a vm\_object, or as an inline array of bytes to be directly copied into the destination. We'll focus on types 1 and 3.

Fundamentally, the ENTRY\_LIST type is the most powerful and general representation, while the KERNEL\_BUFFER type is strictly an optimization. A vm\_map\_entry list consists of several allocations and several layers of indirection: each vm\_map\_entry describes a virtual address range \[vme\_start, vme\_end) that is being mapped by a specific vm\_object, which in turn contains a list of vm\_pages describing the physical pages backing the vm\_object.\
\
[![A diagram showing the heap arrangement of a vm_map_copy object of type ENTRY_LIST. The vm_map_entrys are stored in a circular doubly-linked list. Each entry holds a pointer to a vm_object describing the memory region for that entry. Each vm_object contains a singly-linked list of vm_pages describing the physical pages backing the memory object.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEic4hr_s1200_image18.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEic4hr_s2048_image18.png)\
\
Meanwhile, if the data being inserted is not shared memory and if the size is roughly two pages or less, then the vm\_map\_copy is simply over-allocated to hold the data contents inline in the same allocation, no indirection or further allocations required.\
\
[![A diagram showing the layout of a vm_map_copy of type KERNEL_BUFFER. Rather than having a linked list of vm_map_entrys, there is an inline array of data to be copied directly into the receiving address space.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhw9Ao_s1200_image5%283%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhw9Ao_s1800_image5%283%29.png)\
\
As a consequence of this optimization, the 8 bytes of the vm\_map\_copy object at offset 0x20 can be either a pointer to the head of a vm\_map\_entry list, or fully attacker-controlled data, all depending on the type field at the start. So corrupting the first byte of a vm\_map\_copy object causes the kernel to interpret arbitrary controlled data as a vm\_map\_entry pointer.\
\
[![Comparing vm_map_copy objects of type KERNEL_BUFFER and ENTRY_LIST, the "next" pointer of the ENTRY_LIST-type copy falls into the inline data of the KERNEL_BUFFER-type copy.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgvmpD_s1200_image6%284%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgvmpD_s1800_image6%284%29.png)\
\
With this understanding of vm\_map\_copy internals, let's turn back to vm\_map\_copyout\_internal(). This function is responsible for taking a vm\_map\_copy and inserting it into the destination address space (represented by type vm\_map\_t). It is reachable when sharing memory between processes by sending an out-of-line memory descriptor in a Mach message: the out-of-line memory is stored in the kernel as a vm\_map\_copy, and vm\_map\_copyout\_internal() is the function that inserts it into the receiver's process.\
\
As it turns out, things get rather exciting if vm\_map\_copyout\_internal() processes a corrupted vm\_map\_copy containing a pointer to a fake vm\_map\_entry hierarchy. In particular, consider what happens if the fake vm\_map\_entry claims to be wired, which causes the function to try to fault in the page immediately:\
\
kern\_return\_t\
\
vm\_map\_copyout\_internal(\
\
vm\_map\_t                dst\_map,\
\
vm\_map\_address\_t        \*dst\_addr,      /\\* OUT \*/\
\
vm\_map\_copy\_t           copy,\
\
vm\_map\_size\_t           copy\_size,\
\
boolean\_t               consume\_on\_success,\
\
vm\_prot\_t               cur\_protection,\
\
vm\_prot\_t               max\_protection,\
\
vm\_inherit\_t            inheritance)\
\
{\
\
...\
\
if (copy->type == VM\_MAP\_COPY\_OBJECT) {\
\
...\
\
    }\
\
...\
\
if (copy->type == VM\_MAP\_COPY\_KERNEL\_BUFFER) {\
\
...\
\
    }\
\
...\
\
vm\_map\_lock(dst\_map);\
\
...\
\
    adjustment = start - vm\_copy\_start;\
\
...\
\
/\*\
\
     \*    Adjust the addresses in the copy chain, and\
\
     \*    reset the region attributes.\
\
     \*/\
\
for (entry = vm\_map\_copy\_first\_entry(copy);\
\
        entry != vm\_map\_copy\_to\_entry(copy);\
\
        entry = entry->vme\_next) {\
\
...\
\
        entry->vme\_start += adjustment;\
\
        entry->vme\_end += adjustment;\
\
...\
\
/\*\
\
         \\* If the entry is now wired,\
\
         \\* map the pages into the destination map.\
\
         \*/\
\
if (entry->wired\_count != 0) {\
\
...\
\
            object = VME\_OBJECT(entry);\
\
            offset = VME\_OFFSET(entry);\
\
...\
\
while (va < entry->vme\_end) {\
\
...\
\
                m = vm\_page\_lookup(object, offset);\
\
...\
\
vm\_fault\_enter(m,      // Calls pmap\_enter\_options()\
\
                    dst\_map->pmap,     // to map m->vmp\_phys\_page.\
\
                    va,\
\
                    prot,\
\
                    prot,\
\
VM\_PAGE\_WIRED(m),\
\
FALSE,            /\\* change\_wiring \*/\
\
                    VM\_KERN\_MEMORY\_NONE,    /\\* tag - not wiring \*/\
\
                    &fault\_info,\
\
NULL,             /\\* need\_retry \*/\
\
                    &type\_of\_fault);\
\
...\
\
                offset += PAGE\_SIZE\_64;\
\
                va += PAGE\_SIZE;\
\
           }\
\
       }\
\
}\
\
...\
\
vm\_map\_copy\_insert(dst\_map, last, copy);\
\
...\
\
vm\_map\_unlock(dst\_map);\
\
...\
\
}\
\
Let's walk through this step-by-step. First, other vm\_map\_copy types are handled:\
\
if (copy->type == VM\_MAP\_COPY\_OBJECT) {\
\
...\
\
    }\
\
...\
\
if (copy->type == VM\_MAP\_COPY\_KERNEL\_BUFFER) {\
\
...\
\
    }\
\
The vm\_map is locked:\
\
vm\_map\_lock(dst\_map);\
\
We enter a for loop over the linked list of (fake) vm\_map\_entry objects:\
\
for (entry = vm\_map\_copy\_first\_entry(copy);\
\
        entry != vm\_map\_copy\_to\_entry(copy);\
\
        entry = entry->vme\_next) {\
\
We handle the case where the vm\_map\_entry is wired and should thus be faulted in immediately:\
\
if (entry->wired\_count != 0) {\
\
When set, we loop over every virtual address in the wired entry. Since we control the contents of the fake vm\_map\_entry, we can control the object pointer (of type vm\_object) and offset value that are read:\
\
            object = VME\_OBJECT(entry);\
\
            offset = VME\_OFFSET(entry);\
\
...\
\
while (va < entry->vme\_end) {\
\
We look up the vm\_page struct for each physical page of memory that needs to be wired in. Since we control the fake vm\_object and the offset, we can cause vm\_page\_lookup() to return a pointer to a fake vm\_page struct whose contents we control:\
\
                m = vm\_page\_lookup(object, offset);\
\
And finally, we call vm\_fault\_enter() to fault in the page:\
\
vm\_fault\_enter(m,      // Calls pmap\_enter\_options()\
\
                    dst\_map->pmap,     // to map m->vmp\_phys\_page.\
\
                    va,\
\
                    prot,\
\
                    prot,\
\
VM\_PAGE\_WIRED(m),\
\
FALSE,            /\\* change\_wiring \*/\
\
                    VM\_KERN\_MEMORY\_NONE,    /\\* tag - not wiring \*/\
\
                    &fault\_info,\
\
NULL,             /\\* need\_retry \*/\
\
                    &type\_of\_fault);\
\
The call to vm\_fault\_enter() is rather complicated, so I won't put the code here. Suffice to say, by setting fields in our fake objects appropriately, it is possible to navigate vm\_fault\_enter() with a fake vm\_page object in order to reach a call to pmap\_enter\_options() with a completely arbitrary physical page number:\
\
kern\_return\_t\
\
pmap\_enter\_options(\
\
pmap\_t pmap,\
\
vm\_map\_address\_t v,\
\
ppnum\_t pn,\
\
vm\_prot\_t prot,\
\
vm\_prot\_t fault\_type,\
\
unsignedint flags,\
\
boolean\_t wired,\
\
unsignedint options,\
\
        \_\_unused void   \*arg)\
\
pmap\_enter\_options() is responsible for modifying the page tables of the destination to insert the translation table entry that will establish a mapping from a virtual address to a physical address. Analogously to how vm\_map manages the state for the virtual mappings of an address space, the pmap struct manages the state for the physical mappings (i.e. page tables) of an address space. And according to the sources in osfmk/arm/pmap.c, no further validation is performed on the supplied physical page number before the translation table entry is added.\
\
Thus, our corrupted vm\_map\_copy object actually gives us an incredibly powerful primitive: mapping arbitrary physical memory directly into our process in userspace!\
\
[![If we start with a KERNEL_BUFFER vm_map_copy and corrupt the first byte to change the type to ENTRY_LIST, then we can control the value of the "next" field to make it point to a fake vm_map_entry hierarchy, including a fake vm_page. The physical address specified in the vm_page's "vmp_phys_page" field will be mapped by the call to vm_map_copyout_internal().](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj7V5r_s1200_image14%282%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj7V5r_s2048_image14%282%29.png)\
\
## An old friend\
\
I decided to build the POC for the vm\_map\_copy physical memory mapping technique on top of the kernel read/write primitive provided by the [oob\_timestamp exploit](https://bugs.chromium.org/p/project-zero/issues/detail?id=1986) for iOS 13.3. There were two primary reasons for this.\
\
First, I did not have a good bug available to develop a complete exploit with it. Even though I had initially stumbled upon the idea while trying to exploit the oob\_timestamp bug, it quickly became apparent that that bug wasn't a good fit for this technique.\
\
Second, I wanted to evaluate the technique independently of the vulnerability or vulnerabilities used to achieve it. It seemed that there was a good chance that the technique could be made deterministic (that is, without a failure case); implementing it on top of an unreliable vulnerability would make it hard to evaluate separately.\
\
This technique most naturally fits a controlled one-byte linear heap overflow in any of the allocator zones kalloc.80 through kalloc.32768 (i.e., general-purpose allocations of between 65 and 32768 bytes). For ease of reference in the rest of this post, I'll simply call it the one-byte exploit technique.\
\
## Leaving the Shire\
\
We've already laid out the bones of the technique above: create a vm\_map\_copy of type KERNEL\_BUFFER containing a pointer to a fake vm\_map\_entry list, corrupt the type to ENTRY\_LIST, receive it with vm\_map\_copyout\_internal(), and get arbitrary physical memory mapped into our address space. However, successful exploitation is a little bit more complicated:\
\
1. We still have not addressed where this fake vm\_map\_entry/vm\_object/vm\_page hierarchy will be constructed.\
\
2. We need to ensure that the kernel thread that calls vm\_map\_copyout\_internal() does not crash, panic, or deadlock after mapping the physical page.\
\
\
3. Mapping one physical page is great, but probably not sufficient by itself to achieve arbitrary kernel read/write. This is because:\
\
\
1. The kernelcache's exact load address in physical memory is unknown, so we cannot map any specific page of it directly without locating it first.\
\
2. It is possible that some hardware device exposes an MMIO interface that is powerful enough by itself to build some sort of read/write primitive; however, I'm not aware of any such component.\
\
Thus, we will need to map more than one physical address, and most likely we will need to use data read from one mapping to find the physical address to use for another. This means our mapping primitive can not be one-shot.\
\
4. The call to vm\_map\_copy\_insert() after the for loop tries to zfree() the vm\_map\_copy to the vm\_map\_copy\_zone. This will panic given a vm\_map\_copy originally of type KERNEL\_BUFFER, since KERNEL\_BUFFER objects are initially allocated using kalloc().\
\
\
\
Thus, the only way to safely break out of the for loop and resume normal operation is to first get kernel read/write and then patch up state in the kernel to prevent this panic.\
\
\
These constraints will guide the course of this exploit technique.\
\
## A short cut to PAN\
\
An important prerequisite for the one-byte technique is to create a fake vm\_map\_entry object hierarchy at a known address. Since we are already building this POC on oob\_timestamp, I decided to leverage a neat trick I picked up while exploiting that bug. In the real world, another vulnerability in addition to the one-byte overflow might be needed to leak a kernel address.\
\
While developing the POC for oob\_timestamp, I learned that the AGXAccelerator kernel extension provides a very interesting primitive: IOAccelSharedUserClient2 and IOAccelCommandQueue2 together allow the creation of large regions of pageable memory shared between userspace and the kernel. Having access to user/kernel shared memory can be extremely helpful when developing exploits, since you can place fake kernel data structures there and manipulate them while the kernel accesses them. Of course, this AGXAccelerator primitive is not the only way to get kernel/user shared memory; the physmap, for example, also maps most of DRAM into virtual memory, so it can also be used to reflect userspace memory contents into the kernel. However, the AGXAccelerator primitive is often much more convenient in practice: for one, it provides a very large contiguous shared memory region in a much more constrained address range; and for two, it's easier to leak addresses of adjacent objects to locate it.\
\
Now, before the iPhone 7, iOS devices did not support the Privileged Access Never (PAN) security feature. This meant that all of userspace was effectively shared memory with the kernel, and you could just overwrite pointers in the kernel to point to fake data structures in userspace.\
\
However, modern iOS devices enable PAN, so attempts by the kernel to directly access userspace memory will fault. This is what makes the existence of the AGXAccelerator shared memory primitive so useful: if you can establish a large shared memory region and learn its address in the kernel, that's basically equivalent to having PAN turned off.\
\
Of course, a key part of that sentence is "and learn its address in the kernel"; doing that usually requires a vulnerability and some effort. Instead, as we already rely on oob\_timestamp, we will simply hardcode the shared memory address and note that finding the address dynamically is left as an exercise for the reader.\
\
## At the sign of the panicking POC\
\
With kernel read/write and a user/kernel shared memory buffer in hand, we are ready to write the POC. The overall flow of the exploit is essentially what was outlined above.\
\
We start by creating the shared memory region in the kernel.\
\
We initialize a fake vm\_map\_entry list inside the shared memory. The entry list contains 3 entries: a "ready" entry, a "mapping" entry, and a "done" entry. Together these entries will represent the current state of each mapping operation.\
\
[![There are 3 fake vm_map_entry objects in the shared memory buffer, representing the 3 states of our mapping operation. To start, the "ready" entry forwards to the "done" entry, which loops back to itself.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg1H0c_s1200_image11%282%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg1H0c_s2048_image11%282%29.png)\
\
We send an out-of-line memory descriptor containing a fake vm\_map\_header in a Mach message to a holding port. The out-of-line memory is stored in the kernel as a vm\_map\_copy object of type KERNEL\_BUFFER (value 3).\
\
[![A vm_map_copy of type KERNEL_BUFFER includes inline kernel data; overlapping what would be the "next" field in an ENTRY_LIST copy is the value of a pointer to the "ready" entry in our shared memory buffer. But at this point, the copy's type is KERNEL_BUFFER, so the "pointer" is really just inline data.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg7pCt_s1200_image13%282%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg7pCt_s2048_image13%282%29.png)\
\
We simulate a one-byte linear heap overflow that corrupts the type field of the vm\_map\_copy, changing it to ENTRY\_LIST (value 1).\
\
[![A one-byte overflow into the vm_map_copy changes its type from KERNEL_BUFFER to ENTRY_LIST. At this point, the inline data is now interpreted as a vm_map_header with a "next" field pointing to the "ready" entry.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh-f4z_s1200_image12%284%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh-f4z_s2048_image12%284%29.png)\
\
We start a thread that receives the Mach message queued on the holding port. This triggers a call to vm\_map\_copyout\_internal() on the corrupted vm\_map\_copy.\
\
Due to the way the vm\_map\_entry list was initially configured, the vm\_map\_copyout thread will spin in an infinite loop on the "done" entry, ready for us to manipulate it.\
\
[![Calling vm_map_copyout_internal() on the corrupted vm_map_copy will traverse the linked list, going from "ready" to "done" and spinning in an infinite loop on "done".](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhfVRv_s1200_image19.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhfVRv_s2048_image19.png)\
\
At this point, we have a kernel thread that is spinning ready to map any physical page we request.\
\
To map a page, we first set the "ready" entry to link to itself, and then set the "done" entry to link to the "ready" entry. This will cause the vm\_map\_copyout thread to spin on "ready".\
\
[![To get ready to map a physical page, we make the "ready" entry point to itself and then make the "done" entry point to the "ready" entry. The for loop in vm_map_copyout_internal() will follow the updated link from the "done" entry to the "ready" entry then spin on "ready". This state indicates that we're ready to set up the physical mapping.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjg4tD_s1200_image17.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjg4tD_s2048_image17.png)\
\
While spinning on "ready", we mark the "mapping" entry as wired with a single physical page and link it to the "done" entry, which we link to itself. We also populate the fake vm\_object and vm\_page to map the desired physical page number.\
\
[![Now that the mapping primitive is "ready", we will modify the "mapping" entry to map the desired physical page. We mark it as wired and specify a vm_object and vm_page containing the physical address to map. Also, we make the "done" entry link to itself to ensure the mapping happens only once.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgVlSH_s1200_image9%282%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgVlSH_s2048_image9%282%29.png)\
\
Then, we can perform the mapping by linking the "ready" entry to the "mapping" entry. vm\_map\_copyout\_internal() will map in the page and then spin on the "done" entry, signaling completion.\
\
[![Finally, we map a page by simply linking the "ready" entry to the "mapping" entry, causing vm_map_copyout_internal() to follow the link and process the "mapping" entry. Since it is wired, it maps in the page right away. Finally, once the mapping is complete, vm_map_copyout_internal() will follow the link and start spinning on the "done" entry, indicating that the operation has completed.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEihZ_d_s1200_image16.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEihZ_d_s2048_image16.png)\
\
This gives us a reusable primitive that maps arbitrary physical addresses into our process. As an initial proof of concept, I mapped the non-existent physical address 0x414140000 and tried to read from it, triggering an LLC bus error from EL0:\
\
[![This is a screenshot of a device panic.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEivkV5_s1200_image20.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEivkV5_s1335_image20.png) The mines of memory\
\
At this point we have proved that the mapping primitive is sound, but we still don't know what to do with it.\
\
My first thought was that the easiest approach would be to go after the kernelcache image in memory. Note that on modern iPhones, even with a direct physical read/write primitive, [KTRR](https://projectzero.google/2019/10/ktrw-journey-to-build-debuggable-iphone.html) prevents us from modifying the locked down portions of the kernel image, so we can't just patch the kernel's executable code. However, certain segments of the kernelcache image remain writable at runtime, including the part of the \_\_DATA segment that contains sysctls. Since sysctls have been (ab)used before to build read/write primitives, this felt like a stable path forward.\
\
The challenge was then to use the mapping primitive to locate the kernelcache in physical memory, so that the sysctl structs could then be mapped into userspace and modified.\
\
But first, before we figure out how to locate the kernelcache, some background on physical memory on the iPhone 11 Pro.\
\
The iPhone 11 Pro has 4 GB of DRAM based at physical address 0x800000000, so physical DRAM addresses span 0x800000000 to 0x900000000. Of this, the range 0x801b80000 to 0x8ec9b4000 is reserved for the Application Processor (AP), the main processor of the phone which runs the XNU kernel and applications. Memory outside this region is reserved for coprocessors like the Always On Processor (AOP), Apple Neural Engine (ANE), SIO (possibly Apple SmartIO), AVE, ISP, IOP, etc. The addresses of these and other regions can be found by parsing the [devicetree](https://gist.github.com/bazad/1faef1a6fe396b820a43170b43e38be1) or by dumping the iboot-handoff region at the start of DRAM.\
\
[![A map of DRAM. The first little slice at the beginning, and a bigger slice at the end, are reserved for coprocessors, while the vast bulk of DRAM in the middle is for the Application Processor.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi87qI_s1200_image4%284%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi87qI_s2500_image4%284%29.png)\
\
At boot time, the kernelcache is loaded contiguously into physical memory, which means that finding a single kernelcache page is sufficient to locate the whole image. Also, while KASLR may slide the kernelcache by a large amount in virtual memory, the load address in physical memory is quite constrained: in my testing, the kernel header was always loaded at an address between 0x805000000 and 0x807000000, a range of just 32 MB.\
\
As it turns out, this range is smaller than the kernelcache itself at 0x23d4000 bytes, or 35.8 MB. Thus, we can be certain at runtime that address 0x807000000 contains a kernelcache page.\
\
However, I quickly ran into panics when trying to map the kernelcache:\
\
panic(cpu 4 caller 0xfffffff0156f0c98): "pmap\_enter\_options\_internal: page belongs to PPL, " "pmap=0xfffffff031a581d0, v=0x3bb844000, pn=2103160, prot=0x3, fault\_type=0x3, flags=0x0, wired=1, options=0x1"\
\
This panic string purports to come from the function pmap\_enter\_options\_internal(), which is in the open-source part of XNU (osfmk/arm/pmap.c), and yet the panic is not present in the sources. Thus, I reversed the version of pmap\_enter\_options\_internal() in the kernelcache to figure out what was happening.\
\
The issue, I learned, is that the specific page I was trying to map was part of Apple's [Page Protection Layer](https://support.apple.com/guide/security/page-protection-layer-sec38dc659b4/web) (PPL), a portion of the XNU kernel that manages page tables and that is considered even more privileged than the rest of the kernel. The goal of PPL is to prevent an attacker from modifying protected pages (in particular, executable code pages for codesigned binaries) even after compromising the kernel to obtain a read/write capability.\
\
In order to enforce that protected pages cannot be modified, PPL must protect page tables and page table metadata. Thus, when I tried to map a PPL-protected page into userspace, it triggered a panic.\
\
if (pa\_test\_bits(pa, 0x4000/\\* PP\_ATTR\_PPL? \*/)) {\
\
panic("%s: page belongs to PPL, " ...);\
\
}\
\
if (pvh\_get\_flags(pai\_to\_pvh(pai)) & PVH\_FLAG\_LOCKDOWN) {\
\
panic("%s: page locked down, " ...);\
\
}\
\
The presence of PPL significantly complicates use of the physical mapping primitive, since trying to map a PPL-protected page will panic. And the kernelcache itself contains many PPL-protected pages, splitting the contiguous 35 MB binary into smaller PPL-free chunks that no longer bridge the physical slide of the kernelcache. Thus, there is no longer a single physical address we can (safely) map that is guaranteed to be a kernelcache page.\
\
And the rest of the AP's DRAM region is an equally treacherous minefield. Physical pages are grabbed for use by PPL and returned to the kernel as-needed, and so at runtime PPL pages are scattered throughout physical memory like mines. Thus, there is no static address anywhere that is guaranteed not to blow up.\
\
![Looking at the AP's DRAM over time, unmappable pages are scattered semi-randomly throughout the physical address space, and pages can both enter and exit PPL.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi8pyg_s1024_image3.gif) A map showing the protection flags on every page of AP DRAM on the A13 over time. Yellow is PPL+LOCKDOWN, red is PPL, green is LOCKDOWN, and blue is unguarded (i.e., mappable).\
\
II - The Two Techniques\
\
## The road to DRAM's guard\
\
Yet, that's not quite true. The Application Processor's DRAM region might be a minefield, but anything outside of it is not. That includes the DRAM used by coprocessors and also any other addressable components of the system, such as hardware registers for system components that are typically accessed via memory-mapped I/O ( [MMIO](https://en.wikipedia.org/wiki/Memory-mapped_I/O)).\
\
With such a powerful primitive, I expect that there are a plethora of techniques that could be used to build a read/write primitive. And I expect that there are many clever things that could be done by leveraging direct access to special hardware registers and coprocessors. Unfortunately, this is not an area with which I'm very familiar, so I'll just describe one (failed) attempt to bypass PPL here.\
\
The idea I had was to take control of some coprocessor and use execution on both the coprocessor and the AP together to attack the kernel. First, we use the physical mapping primitive to modify the part of DRAM storing data for a coprocessor in order to get code execution on that coprocessor. Next, back on the main processor, we use the mapping primitive a second time to map and disable the coprocessor's Device Address Resolution Table, or [DART](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/vm/vm.html) (basically an [IOMMU](https://en.wikipedia.org/wiki/Input%E2%80%93output_memory_management_unit)). With code execution on the coprocessor and the corresponding DART disabled, we have direct unguarded access from the coprocessor to physical memory, allowing us to completely sidestep the protections of PPL (which are only enforced from the AP).\
\
However, whenever I tried to modify certain regions of DRAM used by coprocessors, I would get kernel panics. In particular, the region 0x800000000 \- 0x801564000 appeared to be readonly:\
\
panic(cpu 5 caller 0xfffffff0189fc598): "LLC Bus error from cpu1: FAR=0x16f507f10 LLC\_ERR\_STS/ADR/INF=0x11000ffc00000080/0x214000800000000/0x1 addr=0x800000000 cmd=0x14(acc\_cifl2c\_cmd\_ncwr)"\
\
panic(cpu 5 caller 0xfffffff020ca4598): "LLC Bus error from cpu1: FAR=0x15f03c000 LLC\_ERR\_STS/ADR/INF=0x11000ffc00000080/0x214030800104000/0x1 addr=0x800104000 cmd=0x14(acc\_cifl2c\_cmd\_ncwr)"\
\
panic(cpu 5 caller 0xfffffff02997c598): "LLC Bus error from cpu1: FAR=0x10a024000 LLC\_ERR\_STS/ADR/INF=0x11000ffc00000082/0x21400080154c000/0x1 addr=0x80154c000 cmd=0x14(acc\_cifl2c\_cmd\_ncwr)"\
\
This was very weird: these addresses are outside of the KTRR lockdown region, so nothing should be able to block writing to this part of DRAM with a physical mapping primitive! Thus, there must be some other undocumented lockdown enforced on this physical range.\
\
On the other hand, the region 0x801564000 \- 0x801b80000 remains writable as expected, and writing to different areas in this region produces odd system behaviors, supporting the theory that this is corrupting data used by coprocessors. For example, writing to some areas would cause the camera and flashlight to become unresponsive, while writing to other areas would cause the phone to panic when the mute slider was switched on.\
\
To get a better sense of what might be happening, I identified the regions in this range by examining the [devicetree](https://gist.github.com/bazad/1faef1a6fe396b820a43170b43e38be1) and dumping memory. In the end, I discovered the following layout of coprocessor firmware segments in the range 0x800000000 \- 0x801b80000:\
\
[![Mapping out the data in the (smaller) physical memory region before the AP carveout, it seems that there are in fact two segments: A larger read-only span containing __TEXT segments (i.e. code) for coprocessor firmwares, and a smaller writable span containing the corresponding __DATA segments of the same firmwares.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiNhe9_s1200_image7%282%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiNhe9_s2500_image7%282%29.png)\
\
Thus, the regions that are locked down are all \_\_TEXT segments of coprocessor firmwares; this strongly suggests that Apple has added a new mitigation to make coprocessor \_\_TEXT segments read-only in physical memory, similar to KTRR on the AMCC (probably Apple's [memory controller](https://en.wikipedia.org/wiki/Memory_controller)) but for coprocessor firmwares instead of just the AP kernel. This might be the undocumented CTRR mitigation referenced in the originally published xnu-6153.41.3 sources that appears to be an enhanced replacement for KTRR on A12 and up; Ian Beer suggested CTRR might stand for Coprocessor Text Readonly Region.\
\
Nevertheless, code execution on these coprocessors should still be viable: just as KTRR does not prevent exploitation on the AP, the coprocessor \_\_TEXT lockdown mitigation does not prevent exploitation on coprocessors. So, even though this mitigation makes things more difficult, at this point our plan of disabling a DART and using code execution on the coprocessor to write to a PPL-protected physical address should still work.\
\
## The voice of PPL\
\
What did turn out to be a roadblock however was the DART/IOMMU lockdown enforced by PPL on the Application Processor. At boot, XNU parses the "pmap-io-ranges" property in the devicetree to populate the io\_attr\_table array, which stores page attributes for certain physical I/O addresses. Then, when trying to map the physical address, pmap\_enter\_options\_internal() checks the attributes to see if certain mappings should be disallowed:\
\
wimg\_bits = pmap\_cache\_attributes(pn); // checks io\_attr\_table\
\
if ( flags )\
\
wimg\_bits = wimg\_bits & 0xFFFFFF00 \| (u8)flags;\
\
pte \|= wimg\_to\_pte(wimg\_bits);\
\
if ( wimg\_bits & 0x4000 )\
\
{\
\
xprr\_perm = (pte >\> 4) & 0xC \| (pte >\> 53) & 1 \| (pte >\> 53) & 2;\
\
    if ( xprr\_perm == 0xB )\
\
pte\_perm\_bits = 0x20000000000080LL;\
\
    else if ( xprr\_perm == 3 )\
\
pte\_perm\_bits = 0x20000000000000LL;\
\
    else\
\
panic("Unsupported xPRR perm ...");\
\
pte = pte\_perm\_bits \| pte & ~0x600000000000C0uLL;\
\
}\
\
pmap\_enter\_pte(pmap, pte\_p, pte, vaddr);\
\
Thus, we can only map the DART's I/O address into our process if bit 0x4000 is clear in the wimg field. Unfortunately, a quick look at the "pmap-io-ranges" property in the devicetree confirmed that bit 0x4000 was set for every DART:\
\
    addr         len        wimg     signature\
\
0x620000000, 0x40000000,       0x27, 'PCIe'\
\
0x2412C0000,     0x4000,     0x4007, 'DART' ; dart-sep\
\
0x235004000,     0x4000,     0x4007, 'DART' ; dart-sio\
\
0x24AC00000,     0x4000,     0x4007, 'DART' ; dart-aop\
\
0x23B300000,     0x4000,     0x4007, 'DART' ; dart-pmp\
\
0x239024000,     0x4000,     0x4007, 'DART' ; dart-usb\
\
0x239028000,     0x4000,     0x4007, 'DART' ; dart-usb\
\
0x267030000,     0x4000,     0x4007, 'DART' ; dart-ave\
\
...\
\
0x8FC3B4000,     0x4000, 0x40004016, 'GUAT' ; sgx.gfx-handoff-base\
\
Thus, we cannot map the DART into userspace to disable it.\
\
## The palantír\
\
Even though PPL prevents us from mapping page tables and DART I/O addresses, the physical I/O addresses for other hardware components are still mappable. Thus, it is still possible to map and read some system component's hardware registers to try and locate the kernel.\
\
My initial attempt was to read from IORVBAR, the Reset Vector Base Address Register accessible via MMIO. The reset vector is the first piece of code that executes on a CPU after it resets; thus, reading IORVBAR would give us the physical address of XNU's reset vector, which would pinpoint the kernelcache in physical memory.\
\
IORVBAR is mapped at offset 0x40000 after the "reg-private" address for each CPU in the devicetree; for example, on A13 CPU 0 it is located at physical address 0x210050000. It is part of the same group of register sets containing CoreSight and DBGWRAP that had been previously used to [bypass KTRR](https://projectzero.google/2019/10/ktrw-journey-to-build-debuggable-iphone.html). However, I found that IORVBAR is not accessible on A13: trying to read from it will panic.\
\
I spent some time searching the A13 SecureROM for interesting physical addresses before Jann Horn suggested that I map the KTRR lockdown registers on the AMCC, Apple's memory controller. These registers store the physical memory bounds of the KTRR region in order to enforce the KTRR readonly region against attacks from coprocessors.\
\
[![The AMCC has MMIO registers that store the physical addresses of the bounds of the KTRR lockdown region.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhyi9x_s1200_image8%282%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhyi9x_s2048_image8%282%29.png)\
\
Mapping and reading the AMCC's RORGNBASEADDR register at physical address 0x200000680 worked like a charm, yielding the start address of the lockdown region containing the kernelcache in physical memory. Using security mitigations to break other security mitigations is fun. :)\
\
## The back gate is closed\
\
After finding a definitive way forward using AMCC, I looked at one last possibility before giving up on bypassing PPL.\
\
iOS is configured with 40-bit physical addresses and 16K pages (14 bits). Meanwhile, the arbitrary physical page number passed to pmap\_enter\_options\_internal() is 32 bits, and is shifted by 14 and masked with 0xFFFF\_FFFF\_C000 when inserted into the level 3 translation table entry (L3 TTE). This means that we could control bits 45 - 14 of the TTE, even though bits 45 - 40 should always be zero based on the physical address size programmed in TCR\_EL1.IPS.\
\
If the hardware ignored the bits beyond the maximum supported physical address size, then we could bypass PPL by supplying a physical page number that exactly matches the DART I/O address or page table page, but with one of the high bits set. Having the high bits set would cause the mapped address to fail to match any of the addresses in "pmap-io-ranges", even though the TTE would map the same physical address. This would be neat as it would allow us to bypass PPL as a precursor to kernel read/write/execute, rather than the other way around.\
\
Unfortunately, it turns out that the hardware does in fact check that TTE bits beyond the supported physical address size are zero. Thus, I went forward with the AMCC trick to locate the kernelcache instead.\
\
## The taming of sysctl\
\
At this point, we have a physical read/write primitive for non-PPL physical addresses, and we know the address of the kernelcache in physical memory. The next step is to build a virtual read/write primitive.\
\
I decided to stick with known techniques for this part: using the fact that the sysctl\_oid tree used by the sysctl() syscall is stored in writable memory in the kernelcache to manipulate it and convert benign sysctls allowed by the app sandbox into kernel read/write primitives.\
\
XNU inherited [sysctls](https://en.wikipedia.org/wiki/Sysctl) from FreeBSD; they provide access to certain kernel variables to userspace. For example, the "hw.l1dcachesize" readonly sysctl allows a process to determine the L1 data cache line size, while the "kern.securelevel" read/write sysctl controls the "system security level" used for some operations in the BSD portion of the kernel.\
\
The sysctls are organized into a tree hierarchy, with each node in the tree represented by a sysctl\_oid struct. Building a kernel read primitive is as simple as mapping the sysctl\_oid struct for some sysctl that is readable in the app sandbox and changing the target variable pointer (oid\_arg1) to point to the virtual address we want to read. Invoking the sysctl then  reads that address.\
\
[![An example sysctl_oid struct in the kernelcache.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiWb-g_s1200_image1%289%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiWb-g_s1700_image1%289%29.png)\
\
Using sysctls to build a write primitive is a bit more complicated, since no sysctls are listed as writable in the container sandbox profile. The [ziVA](https://github.com/doadam/ziVA) exploit for iOS 10.3.1 worked around this by changing the oid\_handler field of the sysctl to call copyin(). However, on PAC-enabled devices like the A13, oid\_handler is protected with a PAC, meaning that we cannot change its value.\
\
However, when disassembling the function hook\_system\_check\_sysctlbyname() that implements the sandbox check for the sysctl() system call, I noticed an interesting undocumented behavior:\
\
// Sandbox check sysctl-read\
\
ret = sb\_evaluate(sandbox, 116u, &context);\
\
if ( !ret )\
\
{\
\
// Sandbox check sysctl-write\
\
    if ( newlen \| newptr && (namelen != 2 \|\| name\[0\] != 0 \|\| name\[1\] != 3) )\
\
ret = sb\_evaluate(sandbox, 117u, &context);\
\
    else\
\
ret = 0;\
\
}\
\
For some reason, if the sysctl node is deemed readable inside the sandbox, then the write check is not performed on the specific sysctl node {0,3}! What this means is that {0,3} will be writable in every sandbox from which it is readable, regardless of whether or not the sandbox profile allows writes to that sysctl.\
\
As it turns out, the name of the sysctl {0,3} is "sysctl.name2mib", which is a writable sysctl used to convert the string-name of a sysctl into the numeric form, which is faster to look up. It is used to implement sysctlnametomib(). So it makes sense that this sysctl should usually be writable.\
\
The upshot is that even though there are no writable sysctls specified in the sandbox profile, sysctl {0,3} is in fact writable anyways, allowing us to build a virtual write primitive alongside our read primitive. Thus, we now have full arbitrary kernel read/write.\
\
# III - The Return of the Copyout\
\
## The battle of pmap fields\
\
We have come far, but the journey is not yet done: we must break the ring. As things stand, vm\_map\_copyout\_internal() is spinning in an infinite loop on the "done" vm\_map\_entry, whose vme\_next pointer points to itself. We must guide the safe return of this function to preserve the stability of the system.\
\
[![Looking back to the vm_map_copyout_internal() function, we are currently spinning in an infinite loop on the "done" entry, having just finished mapping a page.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiU6OA_s1200_image10%282%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiU6OA_s2048_image10%282%29.png)\
\
There are two basic issues preventing this. First, because we've inserted entries into our page tables at the pmap layer without creating corresponding virtual entries at the vm\_map layer, there is currently an accounting conflict between the pmap and vm\_map views of our address space. This will cause a panic on process exit if not addressed. Second, once the loop is broken, vm\_map\_copyout\_internal() has a call to vm\_map\_copy\_insert() that will panic trying to free the corrupted vm\_map\_copy to the wrong zone.\
\
We will address the pmap/vm\_map conflict first.\
\
Suppose for the moment that we were able to break out of the for loop and allow vm\_map\_copyout\_internal() to return. The call to vm\_map\_copy\_insert() that occurs after the for loop walks through all the entries in the vm\_map\_copy, unlinks them from the vm\_map\_copy's entry list, and links them into the vm\_map's entry list instead.\
\
staticvoid\
\
vm\_map\_copy\_insert(\
\
vm\_map\_t        map,\
\
vm\_map\_entry\_t  after\_where,\
\
vm\_map\_copy\_t   copy)\
\
{\
\
vm\_map\_entry\_t  entry;\
\
while (vm\_map\_copy\_first\_entry(copy) !=\
\
vm\_map\_copy\_to\_entry(copy)) {\
\
        entry = vm\_map\_copy\_first\_entry(copy);\
\
vm\_map\_copy\_entry\_unlink(copy, entry);\
\
vm\_map\_store\_entry\_link(map, after\_where, entry,\
\
            VM\_MAP\_KERNEL\_FLAGS\_NONE);\
\
        after\_where = entry;\
\
    }\
\
zfree(vm\_map\_copy\_zone, copy);\
\
}\
\
Since the vm\_map\_copy's vm\_map\_entrys are all fake objects residing in shared memory, we really do not want them linked into our vm\_map's entry list, where they will be freed on process exit. The simplest solution is thus to update the corrupted vm\_map\_copy's entry list so that it appears to be empty.\
\
Forcing the vm\_map\_copy's entry list to appear empty certainly lets us safely return from vm\_map\_copyout\_internal(), but we would nevertheless still get a panic once our process exits:\
\
panic(cpu 3 caller 0xfffffff01f4b1c50): "pmap\_tte\_deallocate(): pmap=0xfffffff06cd8fd10 ttep=0xfffffff0a90d0408 ptd=0xfffffff132fc3ca0 refcnt=0x2 \\n"\
\
The issue is that during the course of the exploit, our mapping primitive forces pmap\_enter\_options() to insert level 3 translation table entries (L3 TTEs) into our process's page tables, but the corresponding accounting at the vm\_map layer never happens. This disagreement between the pmap and vm\_map views matters because the pmap layer requires that all physical mappings be explicitly removed before the pmap can be destroyed, and the vm\_map layer will not know to remove a physical mapping if there is no vm\_map\_entry describing the corresponding virtual mapping.\
\
Due to PPL, we can not update the pmap directly, so the simplest solution is to grab a pointer to a legitimate vm\_map\_entry with faulted-in pages and overlay it on top of the virtual address range at which pmap\_enter\_options() established our physical mappings. Thus we will update the corrupted vm\_map\_copy's entry list so that it points to this single "overlay" entry instead.\
\
## The fires of stack doom\
\
Finally, it is time to break vm\_map\_copyout\_internal() out of the for loop.\
\
for (entry = vm\_map\_copy\_first\_entry(copy);\
\
        entry != vm\_map\_copy\_to\_entry(copy);\
\
        entry = entry->vme\_next) {\
\
The macro vm\_map\_copy\_to\_entry(copy) expands to:\
\
    (struct vm\_map\_entry \*)(&copy->c\_u.hdr.links)\
\
Thus, in order to break out of the loop, we need to process a vm\_map\_entry with vme\_next pointing to the address of the c\_u.hdr.links field in the corrupted vm\_map\_copy originally passed to this function.\
\
The function is currently spinning on the "done" vm\_map\_entry, and we need to link in one final "overlay" vm\_map\_entry to address the pmap/vm\_map accounting issue anyway. So the simplest way to break the loop is to modify the "overlay" entry's  vme\_next to point to &copy->c\_u.hdr.links. and then update the "done" entry's vme\_next to point to the overlay entry.\
\
[![To break out of the loop, we will have to link the "done" entry to an "overlay" entry that links back to the corrupted vm_map_copy.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjmWiT_s1200_image15%282%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjmWiT_s2048_image15%282%29.png)\
\
The problem is the call to vm\_map\_copy\_insert() mentioned earlier, which frees the vm\_map\_copy as if it were of  type ENTRY\_LIST:\
\
zfree(vm\_map\_copy\_zone, copy);\
\
However, the object passed to zfree() is our corrupted vm\_map\_copy, which was allocated with kalloc(); trying to free it to the vm\_map\_copy\_zone will panic. Thus, we somehow need to ensure that a different, legitimate vm\_map\_copy object gets passed to the zfree() instead.\
\
Fortunately, if you check the disassembly of vm\_map\_copyout\_internal(), the vm\_map\_copy pointer is spilled to the stack for the duration of the for loop!\
\
FFFFFFF007C599A4     STR     X28, \[SP,#0xF0+copy\]\
\
FFFFFFF007C599A8     LDR     X25, \[X28,#vm\_map\_copy.links.next\]\
\
FFFFFFF007C599AC     CMP     X25, X27\
\
FFFFFFF007C599B0     B.EQ    loc\_FFFFFFF007C59B98\
\
...; The for loop\
\
FFFFFFF007C59B98     LDP     X9, X19, \[SP,#0xF0+dst\_addr\]\
\
FFFFFFF007C59B9C     LDR     X8, \[X19,#vm\_map\_copy.offset\]\
\
This makes it easy to ensure that the pointer passed to zfree() is a legitimate vm\_map\_copy allocated from the vm\_map\_copy\_zone: just scan the kernel stack of the vm\_map\_copyout\_internal() thread while it's still spinning and swap any pointers to the corrupted vm\_map\_copy with the legitimate one.\
\
[![Replacing the corrupted vm_map_copy with a valid vm_map_copy that can be safely freed simply requires changing pointers on the kernel stack to point to the replacement copy instead.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiZS8O_s1200_image21.gif)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiZS8O_s1575_image21.gif)\
\
At last, we have fixed up the state enough to allow vm\_map\_copyout\_internal() to break the loop and return safely.\
\
## Homeward bound\
\
Finally, with a virtual kernel read/write primitive and the vm\_map\_copyout\_internal() thread safely returned, we have achieved our goal: a stable kernel compromise achieved by turning a one-byte controlled heap overflow directly into an arbitrary physical address mapping primitive.\
\
Or rather, a nearly-arbitrary physical address mapping primitive. As we have seen, PPL-protected addresses like page table pages and DARTs cannot be mapped using this technique.\
\
When I started on this journey, I had intended to demonstrate that the conventional approach of going after the kernel task port was both unnecessary and limiting, that other kernel read/write techniques could be equally powerful. I suspected that the introduction of Mach-port based techniques in iOS 10 had biased the sample of publicly-disclosed exploits in favor of Mach-port oriented vulnerabilities, and that this in turn obscured other techniques that were just as promising but publicly less well understood.\
\
The one-byte technique initially seemed to offer a counterpoint to the mainstream exploit flow. After reading the code in vm\_map.c and pmap.c, I had expected to be able to simply map all of DRAM into my address space and then implement kernel read/write by performing manual page table walks using those mappings. But it turned out that PPL blocks this technique on modern iOS by preventing certain pages from being mapped at all.\
\
It's interesting to note that similar research was touched upon years ago as well, back when such a thing would have worked. While doing background research for this blog post, I came across a presentation by Azimuth called [iOS 6 Kernel Security: A Hacker’s Guide](https://conference.hitb.org/hitbsecconf2012kul/materials/D1T2%20-%20Mark%20Dowd%20&%20Tarjei%20Mandt%20-%20iOS6%20Security.pdf) that introduced no fewer than four separate primitives that could be constructed by corrupting various fields of vm\_map\_copy\_t: an adjacent memory disclosure, an arbitrary memory disclosure, an extended heap overflow, and a combined address disclosure and heap overflow at the disclosed address.\
\
[![A slide from an Azimuth presentation introducing the use of vm_map_copy_t in iOS kernel heap overflow attacks.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEimr29_s1200_image2%286%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEimr29_s1440_image2%286%29.png)\
\
At the time of the presentation, the KERNEL\_BUFFER type had a slightly different structure, so that c\_u.hdr.links.next overlapped a field storing the vm\_map\_copy's kalloc() allocation size. It might have still been possible to turn a one-byte overflow into a physical memory mapping primitive on some platforms, but it would have been harder since it would require mapping the NULL page and a shared address space. However, a larger overflow like those used in the four aforementioned techniques could certainly change both the type and the c\_u.hdr.links.next fields.\
\
After its apparent public introduction in that [Azimuth presentation](https://conference.hitb.org/hitbsecconf2012kul/materials/D1T2%20-%20Mark%20Dowd%20&%20Tarjei%20Mandt%20-%20iOS6%20Security.pdf) by Mark Dowd and Tarjei Mandt, vm\_map\_copy corruption was repeatedly cited as a widely used exploit technique. See for example: [From USR to SVC: Dissecting the 'evasi0n' Kernel Exploit](http://blog.azimuthsecurity.com/2013/02/from-usr-to-svc-dissecting-evasi0n.html) by Tarjei Mandt; [Tales from iOS 6 Exploitation](https://conference.hitb.org/hitbsecconf2013kul/materials/D2T2%20-%20Stefan%20Esser%20-%20Tales%20from%20iOS%206%20Exploitation%20and%20iOS%207%20Security%20Changes.pdf) by Stefan Esser; [Attacking the XNU Kernel in El Capitan](https://www.blackhat.com/docs/eu-15/materials/eu-15-Todesco-Attacking-The-XNU-Kernal-In-El-Capitain.pdf) by Luca Todesco; [Shooting the OS X El Capitan Kernel Like a Sniper](https://recon.cx/2016/resources/slides/RECON-0xA-Shooting_the_OSX_El_Capitan_Kernel_Like_A_Sniper_Chen_He.pdf) by Liang Chen and Qidan He; [iOS 10 - Kernel Heap Revisited](https://gsec.hitb.org/materials/sg2016/D2%20-%20Stefan%20Esser%20-%20iOS%2010%20Kernel%20Heap%20Revisited.pdf) by Stefan Esser; [iOS kernel exploitation archaeology](https://census-labs.com/media/iOS-kernel-exploitation-archaeology.pdf) by Patroklos Argyroudis; and \*OS Internals, Volume III: Security and Insecurity by Jonathan Levin, in particular Chapter 18 on TaiG. Given the prevalence of these other forms of vm\_map\_copy corruption, it would not surprise me to learn that someone had discovered the physical mapping primitive as well.\
\
Then, in OS X 10.11 and iOS 9, the vm\_map\_copy struct was modified to remove the redundant allocation size and inline data pointer fields in KERNEL\_BUFFER instances. It is possible that this was done to mitigate the frequent abuse of this structure in exploits, although it's hard to tell because those fields were redundant and could have been removed simply to clean up the code. Regardless, removing those fields changed vm\_map\_copy into its current form, weakening the precondition required to carry out this technique to a single byte overflow.\
\
## The mitigating of the Shire\
\
So, how effective were the various iOS kernel exploit mitigations at blocking the one-byte technique, and how effective could they be if further hardened?\
\
The mitigations I considered were KASLR, PAN, PAC, PPL, and zone\_require. Many other mitigations exist, but either they don't apply to the heap overflow bug class or they aren't sensible candidates to mitigate this particular technique.\
\
First, kernel address space layout randomization, or KASLR. KASLR can be divided into two parts: the sliding of the kernelcache image in virtual memory and the randomization of the kernel\_map and submaps (zone\_map, kalloc\_map, etc.), collectively referred to as the "kernel heap". The kernel heap randomization means that you do need some way to determine the address of the kernel/user shared memory buffer in which we build the fake VM objects. However, once you have the address of the shared buffer, neither form of randomization has much bearing on this technique, for two reasons: First, generic iOS kernel heap shaping primitives exist that can be used to reliably place almost any allocation in the target kalloc zones before a vm\_map\_copy allocation, so randomization does not block the initial memory corruption. Second, after the corruption occurs, the primitive granted is arbitrary physical read/write, which is independent of virtual address randomization.\
\
The only address randomization which does impact the core exploit technique is that of the kernelcache load address in physical memory. When iOS boots, iBoot loads the kernelcache into physical DRAM at a random address. As discussed in Part I, this physical randomization is quite small at 32 MB. However, improved randomization would not help because the AMCC hardware registers can be mapped to locate the kernelcache in physical memory regardless of where it is located.\
\
Next consider PAN, or Privileged Access Never. This is an ARMv8.1 security mitigation that prevents the kernel from directly accessing userspace virtual memory, thereby preventing the common technique of overwriting pointers to kernel objects so that they point to fake objects living in userspace. Bypassing PAN is a prerequisite for this technique: we need to establish a complex hierarchy of vm\_map\_entry, vm\_object, and vm\_page objects at a known address. While hardcoding the shared buffer address is good enough for this POC, better techniques would be needed for a real exploit.\
\
PAC, or [Pointer Authentication Codes](https://www.qualcomm.com/media/documents/files/whitepaper-pointer-authentication-on-armv8-3.pdf), is an ARMv8.3 security feature introduced in Apple's [A12 SOC](https://projectzero.google/2019/02/examining-pointer-authentication-on.html). The iOS kernel uses PAC for two purposes: first as an exploit mitigation against certain common bug classes and techniques, and second as a form of kernel control flow integrity to prevent an attacker with kernel read/write from gaining arbitrary code execution. In this setting, we're only interested in PAC as an exploit mitigation.\
\
Apple's website has a [table showing how various types of pointers are protected by PAC](https://support.apple.com/guide/security/pointer-authentication-codes-seca5759bf02/1/web/1). Most of these pointers are automatically PAC-protected by the compiler, and the biggest impact of PAC so far is on C++ objects, especially in IOKit. Meanwhile, the one-byte exploit technique only involves vm\_map\_copy, vm\_map\_entry, vm\_object, and vm\_page objects, all plain C structs in the Mach part of the kernel, and so is unaffected by PAC.\
\
However, at BlackHat 2019, Ivan Krstić of Apple [announced](https://i.blackhat.com/USA-19/Thursday/us-19-Krstic-Behind-The-Scenes-Of-IOS-And-Mas-Security.pdf) that PAC would soon be used to protect certain "members of high value data structures", including "processes, tasks, codesigning, the virtual memory subsystem, \[and\] IPC structures". As of May 2020, this enhanced PAC protection has not yet been released, but if implemented it might prove effective at blocking the one-byte technique.\
\
The next mitigation is PPL, which stands for [Page Protection Layer](https://support.apple.com/guide/security/page-protection-layer-sec38dc659b4/web). PPL creates a security boundary between the code that manages page tables and the rest of the XNU kernel. This is the only mitigation besides PAN that impacted the development of this exploit technique.\
\
In practice, PPL could be much stricter about which physical addresses it allows to be mapped into a userspace process. For example, there is no legitimate use case for a userspace process to have access to kernelcache pages, so setting a flag like PVH\_FLAG\_LOCKDOWN on kernelcache pages could be a weak but sensible step. More generally, addresses outside the Application Processor's DRAM region (including physical I/O addresses for hardware components) could probably be made unmappable for most processes, perhaps with an entitlement escape hatch for exceptional cases.\
\
Finally, the last mitigation is zone\_require, a software mitigation introduced in iOS 13 that checks that some kernel pointers are allocated from the expected zalloc zone before using them. I don't believe that XNU's zone allocator was initially intended as a security mitigation, but the fact remains that many objects that are frequently targeted during exploits (in particular ipc\_ports, tasks, and threads) are allocated from a dedicated zone. This makes zone checks an effective funnel point for detecting exploitation shenanigans.\
\
In theory, zone\_require could be used to protect almost any object allocated from a dedicated zone; in practice, though, the vast majority of zone\_require() checks in the kernelcache are on ipc\_port objects. Because the one-byte technique avoids the use of fake Mach ports altogether, none of the existing zone\_require() checks apply.\
\
However, if the use of zone\_require were expanded, it is possible to partially mitigate the technique. In particular, inserting a zone\_require() call in vm\_map\_copyout\_internal() once the vm\_map\_copy has been determined to be of type ENTRY\_LIST would ensure that the vm\_map\_copy cannot be a KERNEL\_BUFFER object with a corrupted type. Of course, like all mitigations, this isn't 100% robust: using the technique in an exploit would probably still be possible, but it might require a better initial primitive than a one-byte overflow.\
\
## "Appendix A": Annals of the exploits\
\
In my opinion, the one-byte exploit technique outlined in this blog post is a divergence from the [conventional strategies](https://projectzero.google/2020/06/a-survey-of-recent-ios-kernel-exploits.html) employed at least since iOS 10. Fully 19 of the 24 original public exploits that I could find since iOS 10 used dangling or fake Mach ports as an intermediate exploitation primitive. And of the 20 exploits released since iOS 10.3 (when Apple initially started locking down the kernel task port), 18 of those ended by constructing a fake kernel task port. This makes Mach ports the defining feature of modern public iOS kernel exploitation.\
\
Having gone through the motions of using the one-byte technique to build a kernel read/write primitive on top of a simulated heap overflow, I certainly can see the logic of going after the kernel task port instead. Most of the exploits I looked at since iOS 10 have a relatively modular design and a linear flow: an initial primitive is obtained, state is manipulated, an exploitation technique is applied to build a stronger primitive, state is manipulated again, another technique is applied after that, and so on, until finally you have enough to build a fake kernel task port. There are checkpoints along the way: initial corruption, dangling Mach port, 4-byte read primitive, etc. The exact sequence of steps in each case is different, but in broad strokes the designs of different exploits converge. And because of this convergence, the last steps of one exploit are pretty much interchangeable with those of any other. The design of it all "feels clean".\
\
That modularity is not true of this one-byte technique. Once you start the vm\_map\_copyout\_internal() loop, you are committed to this course until after you've obtained a kernel read/write primitive. And because vm\_map\_copyout\_internal() holds the vm\_map lock for the duration of the loop, you can't perform any of the virtual memory operations (like allocating virtual memory) that would normally be integral steps in a conventional exploit flow. Writing this exploit thus feels different, more messy.\
\
All that said, and at the risk of sounding like I'm tooting my own horn, the one-byte technique intuitively feels to me somewhat more "technically elegant": it turns a weaker precondition directly into a very strong primitive while sidestepping most mitigations and avoiding most sources of instability and slowness seen in public iOS exploits. Of the 24 iOS exploits I looked at, 22 depend on reallocating a slot for an object that has been recently freed with another object, many doing so multiple times; with the notable exception of SockPuppet, this is an inherently risky operation because another thread could race to reallocate that slot instead. Furthermore, 11 of the 19 exploits since iOS 11 depend on forcing a zone garbage collection, an even riskier step that often takes a few seconds to complete.\
\
Meanwhile, the one-byte technique has no inherent sources of instability or substantial time costs. It looks more like the type of technique I would expect sophisticated attackers would be interested in developing. And even if something goes wrong during the exploit and a bad address is dereferenced in the kernel, the fact that the vm\_map lock is held means that the fault results in a deadlock rather than a kernel panic, making the failed exploit look like a frozen process instead of a system crash. (You can even "kill" the deadlocked app in the app switcher UI and then continue using the device afterwards.)\
\
## "Appendix B": Conclusions\
\
I'll conclude by returning to the three questions posed at the very beginning of this post:\
\
Is targeting the kernel task port really the best exploit flow? Or has the convergence on this strategy obscured other, perhaps more interesting, techniques? And are existing iOS kernel mitigations equally effective against other, previously unseen exploit flows?\
\
These questions are all too "fuzzy" to have real answers, but I'll attempt to answer them anyway.\
\
To the first question, I think the answer is no, the kernel task port is not the singular best exploit flow. In my opinion the one-byte technique is just as good by most measures, and in my personal opinion, I expect there are other as-yet unpublished techniques that are also equally good.\
\
To the second question, on whether the convergence on the kernel task port has obscured other techniques: I don't think there is enough public iOS research to say conclusively, but my intuition is yes. In my own experience, knowing the type of bug I'm looking for has influenced the types of bugs I find, and looking at past exploits has guided my choice in exploit flow. I would not be surprised to learn others feel similarly.\
\
Finally, are existing iOS kernel exploit mitigations effective against unseen exploit flows? Immediately after I developed the POC for the one-byte technique, I had thought the answer was no; but here at the end of this journey, I'm less certain. I don't think PPL was specifically designed to prevent this technique, but it offers a very reasonable place to mitigate it. PAC didn't do anything to block the technique, but it's plausible that a future expansion of PAC-protected pointers would. And despite the fact that zone\_require didn't impact the exploit at all, a single-line addition would strengthen the required precondition from a single-byte overflow to a larger overflow that crosses a zone boundary. So, even though in their current form Apple's kernel exploit mitigations were not effective against this unseen technique, they do lay the necessary groundwork to make mitigating the technique straightforward.\
\
## Indices\
\
One final parting thought. In [Deja-XNU](https://projectzero.google/2018/10/deja-xnu.html), published 2018, Ian Beer mused about what the "state-of-the-art" of iOS kernel exploitation might have looked like four years prior:\
\
An idea I've wanted to play with for a while is to revisit old bugs and try to exploit them again, but using what I've learnt in the meantime about iOS. My hope is that it would give an insight into what the state-of-the-art of iOS exploitation could have looked like a few years ago, and might prove helpful if extrapolated forwards to think about what state-of-the-art exploitation might look like now.\
\
This is an important question to consider because, as defenders, we almost never get to see the capabilities of the most sophisticated attackers. If a gap develops between the techniques used by attackers in private and the techniques known to defenders, then defenders may waste resources mitigating against the wrong techniques.\
\
I don't think this technique represents the current state-of-the-art; I'd guess that, like Deja-XNU, it might represent the state-of-the-art of a few years ago. It's worth considering what direction the state-of-the-art may have taken in the meantime.