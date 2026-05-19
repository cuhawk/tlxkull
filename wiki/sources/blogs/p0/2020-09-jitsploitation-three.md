---
source: p0
source_url: https://projectzero.google/2020/09/jitsploitation-three.html
title: "JITSploitation III: Subverting Control Flow - Project Zero"
description: "Posted by Samuel Groß, Project ZeroThis three-part series highlights the technical challenges inv..."
---

Posted by Samuel Groß, Project Zero

This three-part series highlights the technical challenges involved in finding and exploiting JavaScript engine vulnerabilities in modern web browsers and evaluates current exploit mitigation technologies. The exploited vulnerability, CVE-2020-9802, was fixed in iOS 13.5, while two of the mitigation bypasses, CVE-2020-9870 and CVE-2020-9910, were fixed in iOS 13.6.

==========

This post is third in a series about a Safari renderer exploit. [Part 1](https://projectzero.google/2020/09/jitsploitation-one.html) discussed a JIT compiler vulnerability in JSC and [Part 2](https://projectzero.google/2020/09/jitsploitation-two.html) showed how it could be turned into a reliable read/write primitive despite various mitigations. The purpose of this post is to provide an overview of the various code execution mitigations present in WebKit on iOS 13 and to discuss different approaches for bypassing them.

## The Evolution of iOS JIT Hardenings

In the “old” days of browser exploitation, an attacker with a read/write capability in a renderer process would [simply write arbitrary shellcode into the rwx JIT region](http://www.phrack.org/papers/attacking_javascript_engines.html) and call it a day.

The first software-based mitigation against this technique in WebKit was deployed in 2016: the “ [Bulletproof JIT](https://www.blackhat.com/docs/us-16/materials/us-16-Krstic.pdf)”. It worked by mapping the JIT region twice, once as r-x for execution and once as rw- for writing. The writable mapping was placed at a secret location in memory and the bulletproof JIT then relied on a --x region containing a jit\_memcpy function that would copy given data into the writable JIT mapping without disclosing its secret address. However, this mitigation was rather easy to defeat due to the lack of [CFI](https://en.wikipedia.org/wiki/Control-flow_integrity), for example via ROP. Moreover, if an attacker was able to disclose the location of the writable mapping through some means, they could simply write their shellcode to it.

The iOS JIT hardening became stronger with the addition of hardware assisted mitigations around the introduction of the iPhone Xs, namely APRR and PAC. These will be discussed next. For a fuller picture of the various iOS exploit mitigations, the interested reader is referred to the presentation “ [Evolution of iOS mitigations](https://papers.put.as/papers/ios/2019/Siguza_-_Mitigations.pdf)” by Siguza.

### APRR

While the expansion of this acronym is not known for certain outside of Apple, its functionality is fairly well understood. Without going into too much technical detail - the interested reader is referred to [Siguza’s blog post on APRR](https://siguza.github.io/APRR/) for that - the goal behind APRR is essentially to enable per-thread page permissions. This is implemented by mapping page table entry permissions to their real permission with dedicated CPU registers. With that, page permissions essentially simply become an index into the APRR registers which now hold the actual page permissions. As a simplified example, consider the following APRR mapping:

|     |     |     |
| --- | --- | --- |
| Page Table Entry Permission | Resulting Index | APRR Register at that Index |
| \-\-\- | 0 | \-\-\- |
| --x | 1 | --x |
| -w- | 2 | -w- |
| -wx | 3 | --x |
| r-- | 4 | r-- |
| r-x | 5 | r-x |
| rw- | 6 | rw- |
| rwx | 7 | r-x |

With the APRR register set up in this way, it would effectively enforce a strict W^X policy: no page could ever be writable and executable at the same time.

In WebKit, APRR is now used to protect the JIT region: the JIT region’s page table permissions are rwx, but W^X is enforced as shown above. As such, the JIT region is effectively r-x and thus trying to directly write into it will trigger a segfault. As the JIT region has to be written into from time to time (when new code is compiled or existing code is updated), it is necessary to change the permissions of the region. This is done through a dedicated “unlock” function which changes the value of the APRR register at index 7 (corresponding to the page table permissions rwx) to rw-. However, this happens only for the thread that is about to copy data into the JIT region while the region remains r-x for all other threads. This prevents an attacker from racing the JIT compiler thread when it unlocks the region. Below is the slightly simplified source code of the [performJITMemcpy function](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/jit/ExecutableAllocator.h#L116), responsible for copying code into the JIT region:

ALWAYS\_INLINE void\*

performJITMemcpy(void \*dst, const void \*src, size\_t n)

{

    os\_thread\_self\_restrict\_rwx\_to\_rw();

    memcpy(dst, src, n);

    os\_thread\_self\_restrict\_rwx\_to\_rx();

    return dst;

}

Also note the use of ALWAYS\_INLINE which forces this function to be inlined at every callsite. More on that later.

APRR by itself would be fairly easy to bypass. The two main types of attacks are:

1. ROPing, JOPing, etc. into the performJITMemcpy function (or really, a function where it is inlined) and that way copy arbitrary code into the JIT region.

2. As the compiler assembles machine code into a [temporary heap buffer](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/assembler/AssemblerBuffer.h#L146) which is afterwards copied into the JIT region, it would be possible for an attacker to corrupt the machine code on the heap prior to the copy.


Enter PAC.

### PAC

[PAC](https://github.com/apple/llvm-project/blob/apple/master/clang/docs/PointerAuthentication.rst), short for Pointer Authentication Codes, is another hardware feature which allows storing a cryptographic signature in the otherwise unused top bits of a pointer. It has been the topic of much research and is by now well documented, for example in a [blogpost by Brandon Azad](https://projectzero.google/2019/02/examining-pointer-authentication-on.html). With PAC enabled, every code pointer must have a valid signature which is checked before transferring control flow to it. As the PAC keys are kept in registers, they are inaccessible to an attacker who is thus unable to forge valid pointers.

PAC thus immediately prevents an attacker from performing attack 1) above. Also, since the performJITMemcpy function is marked as ALWAYS\_INLINE, there will be no existing function pointers to it that would allow an attacker to call this function with controlled arguments.

Attack 2) needs additional work to mitigate. The issue mainly manifests inside the [LinkBuffer::copyCompactAndLinkCode](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/assembler/LinkBuffer.cpp#L134) function, responsible for copying (and linking as well as possibly compacting) the previously assembled machine code into the JIT region. If an attacker was able to corrupt the heap buffer containing the machine code before this function copies it into the JIT region, the attacker would gain arbitrary code execution. This attack is mitigated by computing a [PAC-based hash](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/assembler/AssemblerBuffer.h#L152) over the machine code [during assembling](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/assembler/AssemblerBuffer.h#L311), then [recomputing](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/assembler/LinkBuffer.cpp#L184) and [verifying that hash](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/assembler/LinkBuffer.cpp#L239) during copying. This way, it is ensured that whatever the [assembler](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/assembler/ARM64Assembler.h) emitted is also copied into the JIT region without modifications. While it is likely possible to trick the compiler to emit somewhat controllable code, more on that later, it is no longer generally possible to execute arbitrary instructions as the assembler only supports a limited set of instructions.

### Summary

Together, APRR and PAC achieve the following:

- The JIT region is effectively mapped r-x and is “unlocked” only for a short period of time and only for a single thread when JIT code is updated. This prevents an attacker from writing into the JIT region directly

- PAC is used to enforce CFI and thus prevent an attacker from performing classic code reuse attacks like ROP, JOP, etc. It is also not possible to call the performJITMemcpy function directly as it is always inlined into its callers

- PAC is used to ensure the integrity of emitted JIT code before it is copied into the JIT region


This was the starting point for the final part of this research project. The remainder of this post will now discuss different bypass approaches.

## Bypassing The JIT Hardenings

The different attacks presented next ultimately strive to gain a level of control over the program’s execution flow that is powerful enough to implement a second stage exploit (most likely some form of sandbox escape). This is most likely what an attacker would usually attempt to achieve. It should be kept in mind, however, that without something like [site isolation](https://www.chromium.org/Home/chromium-security/site-isolation), an attacker with a memory read/write capability in a renderer process is usually able to construct a UXSS attack, thus gaining access to various web credentials and sessions and possibly even gaining persistence through web workers. These issues have been [demonstrated in the past](https://youtu.be/a0yPYpmUpIA) and will thus not be discussed further.

### Shellcode-less Exploitation

First of all, it is important to note that an attacker does not necessarily need shellcode execution. For example, it is possible to abuse the ObjectiveC and JavaScriptCore runtime so that arbitrary function and syscalls can be performed from JavaScript. This in turn can then be used to implement the next stage of an exploit chain, avoiding the need to bypass the JIT hardenings altogether. This [has already been demonstrated](https://projectzero.google/2020/01/remote-iphone-exploitation-part-3.html) and was thus not researched further during this project.

Similarly, while the JIT’s final output - the machine code - is protected through PAC, its intermediate outputs, in particular the various IRs - DFG, [B3, and AIR](https://webkit.org/blog/5852/introducing-the-b3-jit-compiler/) \- and other supporting data structures are not protected and thus are subject to manipulation by an attacker. A possible approach is thus to corrupt the JIT’s IR code in order to for example trick the compiler into generating calls to arbitrary functions with controlled arguments. This would likely grant a very similar primitive to the one above, i.e. being able to execute controlled syscalls, and was thus not explored further during this research.

### Race Conditions

Race conditions appear to be somewhat widespread along the PAC+APRR boundary. As an example, the following is a rather typical invocation of performJITMemcpy, in this case to [repatch a pointer-sized immediate value in JIT generated code](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/assembler/ARM64EAssembler.h#L326):

int buffer\[4\];

buffer\[0\] = moveWideImediate(Datasize\_64, MoveWideOp\_Z, 0,

                             getHalfword(value, 0), rd);

buffer\[1\] = moveWideImediate(Datasize\_64, MoveWideOp\_K, 1,

                             getHalfword(value, 1), rd);

buffer\[2\] = moveWideImediate(Datasize\_64, MoveWideOp\_K, 2,

                             getHalfword(value, 2), rd);

if (NUMBER\_OF\_ADDRESS\_ENCODING\_INSTRUCTIONS > 3)

    buffer\[3\] = moveWideImediate(Datasize\_64, MoveWideOp\_K, 3,

                                 getHalfword(value, 3), rd);

performJITMemcpy(address, buffer, sizeof(int) \* 4);

Here, the machine instructions necessary to load the immediate value are first emitted into a stack allocated buffer which is subsequently copied into the JIT region via performJITMemcpy. As such, if another thread managed to corrupt the stack allocated buffer before it is copied into the JIT region, the attacker would gain arbitrary code execution. However, the race window here is very small, and losing the race might cause in-use stack memory to be corrupted, possibly leading to a crash. (This code also suffers from another, theoretical bug: should NUMBER\_OF\_ADDRESS\_ENCODING\_INSTRUCTIONS ever be less than 4, then it would copy uninitialized stack memory into the JIT region…).

Ultimately, I decided to exclude race conditions that could not safely be lost from this research project, as it can be argued that a mitigation that forces attackers to win a race while risking a process crash is in some aspect working as intended.

### Unprotected Code Pointers

Another possible attack vector are cases where PAC is used incorrectly. Examples for that include:

1. Places that sign a raw pointer that can be corrupted by the attacker

2. Places that call an unsigned function pointer that can be controlled by the attacker


Finding such cases is possible through static analysis on the assembly code. While I initially wanted to use one of binary ninja’s various ILs for this due to their support for various dataflow analyses, the lack of support for PAC instructions made this harder and I went instead for a very simple IDAPython script which would output sequences of instructions ending in a PAC signing instruction such as [PACIZA](https://developer.arm.com/documentation/dui0801/g/A64-General-Instructions/PACIA--PACIZA--PACIA1716--PACIASP--PACIAZ). When run on a DyldSharedCache image, the script would output many thousands of lines such as

libz.1:\_\_text:0x1b6ba1444  ADRL X16, sub\_1B6BA9434; PACIZA X16

This “gadget” essentially takes a constant (the address of sub\_1B6BA9434) and signs it using the A key and a context of zero. As such, it is not very interesting for an attacker as the signed value cannot be controlled. After filtering out such obviously safe code snippets, one remaining and frequently occurring code pattern looked like this:

ADRP            X16, #\_pow\_ptr\_3@PAGE

LDR             X16, \[X16,#\_pow\_ptr\_3@PAGEOFF\]

PACIZA          X16

This code snippet loads a raw pointer from a writable page, then signs it using the PACIZA instruction. As such, an attacker can bypass PAC by overwriting the raw pointer in memory, then somehow getting this code to execute. It appears that the compiler emitted this vulnerable code every time a function from a different compilation unit was referenced as a pointer instead of being called directly. This particular code snippet was the machine code of the following C++ code in JavaScriptCore:

LValue Output::doublePow(LValue xOperand, LValue yOperand)

{

    double (\*powDouble)(double, double) = pow;

    return callWithoutSideEffects(B3::Double, powDouble, xOperand, yOperand);

}

This function is used by the JIT compiler when a [Math.pow](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/pow) invocation that is known to operate on double values is optimized. In that case, the compiler emits a call to the C pow function, and for that loads and signs its address with this function. Due to the bug in the compiler, the imported function pointer was, however, placed in a writable section but also not protected by PAC. The PoC for this issue is then quite simple:

// offset from iOS 13.4.1, iPhone Xs

let powImportAddr = Add(jscBase, 0x34e1d570);

memory.writePtr(powImportAddr, new Int64('0x41414141'));

function trigger(x) {

    return Math.pow(x, 13.37);

}

for (let i = 0; i < 10000000; i++) {

    trigger(i + 0.1);

}

This will result in a crash with PC=0x41414141, demonstrating that PAC has been bypassed.

Searching with a slightly modified IDAPython script for the second vulnerability type, a call to an unprotected pointer, also resulted in an interesting code snippet:

MOV             W9, #0x6770

ADRP            X16, #\_\_\_chkstk\_darwin\_ptr\_19@PAGE

LDR             X16, \[X16,#\_\_\_chkstk\_darwin\_ptr\_19@PAGEOFF\]

BLR             X16

This code, found at the start of many large functions, branches to the \_\_chkstk\_darwin function, which is likely responsible for preventing a huge stackframe from “jumping over” a stack guard page in case of a stack overflow. For some reason however, the pointer to that function was loaded from a writable memory region and was also not protected by PAC. As such, it was again possible to execute arbitrary code as demonstrated by the following code snippet:

// offset from iOS 13.4.1, iPhone Xs

let \_\_chkstk\_darwin\_ptr = Add(jscBase, 0x34e1d430);

memory.writePtr(\_\_chkstk\_darwin\_ptr, new Int64('0x42424242'));

// Just need to trigger FTL compilation now, we'll crash in FTL::lowerDFGToB3

function foo(x) {

    return Math.pow(x, 13.37);

}

for (let i = 0; i < 10000000; i++) {

    foo(i + 0.1);

}

This works because of the widespread use of \_\_chkstk\_darwin in basically any function with a large stack frame, one of which, namely FTL::lowerDFGToB3, is executed during JIT compilation.

The two issues were reported to Apple as [Project Zero issue #2044](https://bugs.chromium.org/p/project-zero/issues/detail?id=2044) and were subsequently fixed in iOS 13.6 on July 15th and assigned CVE-2020-9870. The IDAPython script used to find these gadgets can also be found in the [report for issue #2044](https://bugs.chromium.org/p/project-zero/issues/detail?id=2044).

### Manipulating Mach Messages

Inspired by various chats with fellow Project Zero team member Brandon Azad, the idea behind this bypass is to corrupt a [mach message struct](http://web.mit.edu/darwin/src/modules/xnu/osfmk/man/mach_msg_header.html) before it is sent out via the [mach\_msg](http://web.mit.edu/darwin/src/modules/xnu/osfmk/man/mach_msg.html) syscall. On iOS and macOS, a large portion of the kernel interface, the entire IOKIT driver interface, as well as basically all userspace IPC is implemented through mach messages, making this a powerful exploit primitive. For example, it should be possible to (ab)use virtual memory related mach syscalls to bypass PAC and/or APRR by changing memory protections or remapping pages. Alternatively, controlling mach messages would again allow implementing a stage 2 exploit from JavaScript, unless the ability to perform BSD syscalls was required for it.

A simple, yet imperfect approach to find code that sends mach messages is to hook the mach\_msg function with a Frida script, then deduplicate its invocations based on their callstack. This is imperfect as it will miss code paths that are rarely executed during normal operations, but is very quick to implement. Doing this in a WebKit renderer process will show roughly the following groups of related calls to mach\_msg:

- [IPC communication](https://github.com/WebKit/webkit/tree/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/WebKit/Platform/IPC/cocoa) with the browser process

- [XPC communication](https://developer.apple.com/documentation/xpc) with other system processes

- Mach syscalls to the kernel


Ultimately, all of these cases appeared to be race conditions, as the constructed mach message was mostly immediately sent out without lingering in memory for some (ideally attacker-controllable) time during which it could be corrupted. As losing the race in these cases results in either heap (in the case of IPC and XPC communication) or stack (in the case of mach syscalls) corruption, the races can likely not safely be repeated and as thus these cases didn’t meet the requirements of a reliable bypass technique.

### Abusing Signal Handlers

PAC (like many other mitigations) relies on crashing the process in order to stop the attacker. An interesting target are thus signal handling mechanisms that can interrupt the crashing process.

WebKit has support for signal handling inside the renderer process, which it uses for some JavaScriptCore optimizations. For example, JSC [supports an execution mode](https://github.com/WebKit/webkit/blob/015fb86d51851fc3e13f05898c85d62d0b1bae8f/Source/JavaScriptCore/runtime/OptionsList.h#L466) for WASM code where all bounds checks are omitted, but where the WASM heap is followed by a 32GB guard region. Since WASM memory accesses use 32bit indices, if an invalid access occurs in WASM, it will always access a guard page, cause a segfault, and then run the [WASM signal handle](https://github.com/WebKit/webkit/blob/master/Source/JavaScriptCore/wasm/WasmFaultSignalHandler.cpp) r. The handler will then repatch the WASM code so that the faulting thread will raise a JavaScript exception upon resuming.

Exception handling in WebKit is based on the [mach exception handling infrastructure](http://web.mit.edu/darwin/src/modules/xnu/osfmk/man/catch_exception_raise.html) instead of the UNIX signal handling facilities. Here is a brief overview of how it works:

1. When an exception occurs in some renderer thread, a [GCD](https://en.wikipedia.org/wiki/Grand_Central_Dispatch) worker thread is woken up by the kernel to handle the exception

2. The thread executes mach\_msg\_server\_once, which fetches the mach message describing the exception from the kernel, allocates the reply message, then passes both to a handler function

3. \_Xmach\_exception\_raise\_state\_identity, an auto-generated [MIG](http://www.cs.cmu.edu/afs/cs/project/mach/public/doc/unpublished/mig.ps) function, is the registered handler for exception messages. It will dissect the input mach message, extracting values like the register contents at the time of the crash, then execute the “real” handler function:

4. [catch\_mach\_exception\_raise\_state](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/WTF/wtf/threads/Signals.cpp#L137) will now iterate over a [linked list of registered handlers](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/WTF/wtf/threads/Signals.cpp#L59) (such as the [WASM fault handler](https://github.com/WebKit/webkit/blob/master/Source/JavaScriptCore/wasm/WasmFaultSignalHandler.cpp)) and execute each one of them, also passing them the output register state which they can modify. Depending on whether one of the handlers handled the exception, this function will return KERN\_SUCCESS or KERN\_FAILURE

5. Back in \_Xmach\_exception\_raise\_state\_identity, the return value as well as the output register state are used to populate the reply message

6. mach\_msg\_server\_once finally sends the reply message to the kernel, then returns control to GCD

7. The kernel will now either resume the crashed thread with the output register state if the return value was KERN\_SUCCESS, otherwise terminate it


The process is visualized again in the following graphics.

[![Image: The interaction between different system components during mach exception handling](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj4SFf_s1200_image1%2814%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj4SFf_s1922_image1%2814%29.png)

This now enables the following attack:

1. The singly-linked list of handlers is corrupted and turned into a cycle. This is possible because, in contrast to the handler function pointers, the next pointer of the list elements are not protected by PAC

2. An access violation is caused in a separate thread. This will cause a GCD thread to become “stuck” in catch\_mach\_exception\_raise\_state, looping infinitely due to the cycle

3. A thread under the attacker's control now searches through all thread stacks (they are allocated contiguously in memory) looking for the return address of catch\_mach\_exception\_raise\_state. Once found, it now also has access to the reply mach message as a pointer to it is spilled on the stack. The reply message can then directly be manipulated by the attacker. In particular, the new register state (except for PC, which is protected by PAC) and the return value, indicating whether the exception was handled or not, can now be set.

4. The spilled pointer on the stack is replaced with a different one to cause \_Xmach\_exception\_raise\_state\_identity to write the actual return value of the signal handler (which will be KERN\_FAILURE) into a different memory location while its caller, mach\_msg\_server\_once will send the attacker-controlled reply message back to the kernel

5. The thread fixes up the handler list, causing the handler thread to break out of the loop and return from catch\_mach\_exception\_raise\_state. The kernel will now receive a completely attacker controlled reply message and will thus resume the crashed thread with attacker controlled register (and stack) context


This is quite a strong exploitation primitive, essentially enabling the construction of a small “debugger” capable of breaking on most data accesses in the program and able to change the execution context at those points mostly arbitrarily. This can in turn be used in multiple ways to bypass PAC and/or APRR. Possible ideas include:

- Corrupt the AssemblerBuffer so arbitrary instructions are copied into the JIT region by the LinkBuffer. This will cause the computed hashes to mismatch and the linker to crash, but that only happens after the instructions have been copied and the crash can then simply be caught

- Crash during [one of the writes](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/assembler/LinkBuffer.cpp#L234) into the JIT region in LinkBuffer::copyCompactAndLinkCode (by corrupting the destination pointer prior to that) and change the content of the source register so that an arbitrary instruction is written into the JIT region while the original instruction is used for the hash computation

- Crash during LinkBuffer::copyCompactAndLinkCode and resume execution somewhere else. This should leave the JIT region writable (although not executable) for that thread

- Brute-force a PAC code (e.g. by repeatedly accessing, crashing, and then changing a PAC protected pointer), then JOP into one of the functions into which performJITMemcpy is inlined


A simple PoC demonstrating how this technique works (or, by now, used to work) can be found in the published proof of concept exploit code in the pwn.js file. It implements a simple PAC bypass with this “debugger” for TypedArrays by corrupting a PAC-protected buffer pointer, catching the exception during its access, then changing the register holding the raw pointer and resuming execution.

This issue was reported to Apple as [Project Zero issue #2042](https://bugs.chromium.org/p/project-zero/issues/detail?id=2042). It was then fixed in WebKit HEAD with commit [014f1fa8c2](https://github.com/WebKit/webkit/commit/014f1fa8c22d9227f8a7d877dbb3673e5a4f6e02) (only 6 days after the report) by initializing the signal handlers when the JavaScript engine is initialized, then marking the memory region holding the signal handlers as read-only. This prevents an attacker from modifying the list. The fix was shipped to users with iOS 13.6 on July 15th and the issue was assigned CVE-2020-9910.

#### Variants

This “bug” pattern is a bit more general and also not strictly related to signal handling. As an example, consider the following code from LinkBuffer::copyCompactAndLinkCode:

if (verifyUncompactedHash.finalHash() != expectedFinalHash) {

    dataLogLn("Hashes don't match: ", ...);

    dataLogLn("Crashing!");

    CRASH();

}

This code is executed if, during linking and copying of the assembled code, JSC determines that the machine code has been corrupted as the cryptographic hashes don’t match. The problem here is that an attacker might be able to corrupt data in a way that causes dataLogLn, a nontrivial function, to block or spin infinitely, for example by corrupting a lock or making some loop run forever. In that case, the attacker-controlled machine code will already have been copied into the JIT region and can afterwards be executed by the attacker in another thread without fear of losing a race against CRASH(). This potential variant was likely identified by Apple shortly after the original issue was reported to them, then fixed in WebKit with commit [e87946b7a8](https://github.com/WebKit/webkit/commit/e87946b7a86e0e0c1b11bcaf19c46ff384e5579d#diff-f751db5d3640969ae224c602ca5eba3f).

As another example, the following function was called by JSC just before it was going to CRASH() when it encountered an incorrectly PAC signature (WebKit’s [PtrTag mechanism](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/runtime/JSCPtrTag.h) is based on PAC), indicating corruption of critical data by an attacker:

void reportBadTag(const void\* ptr, PtrTag expectedTag)

{

    dataLog("PtrTag ASSERTION FAILED on pointer ", RawPointer(ptr), ", actual tag = ", tagForPtr(ptr));

    ...

}

The tagForPtr call actually ends up traversing a linked list:

static const char\* tagForPtr(const void\* ptr)

{

    PtrTagLookup\* lookup = s\_ptrTagLookup;

    while (lookup) {

        const char\* tagName = lookup->tagForPtr(ptr);

        if (tagName)

            return tagName;

        lookup = lookup->next;

    }

    ...

As such, by turning this list into a cycle, it again became possible to prevent crashing due to a PAC failure. This in turn allows a brute-force attack against PAC or possibly leaking a validly signed, arbitrary pointer as documented in the report for this variant. This variant was reported to Apple as a [variant of Project Zero issue #2042](https://bugs.chromium.org/p/project-zero/issues/detail?id=2042#c1), then fixed with commits [13e30ec7a5](https://github.com/WebKit/webkit/commit/13e30ec7a58077dfded00d722d9d9b5e71bd5e01) and [db8b3982f2](https://github.com/WebKit/webkit/commit/db8b3982f245d681677f6e8ecf72bbcc011d2058).

Finally, even “broader” variants of this issue may exist: if there is code that spills sensitive values (e.g. raw pointers after authentication) to the stack temporarily before performing actions that can be made to block by the attacker (e.g. a loop or a lock operation), then, an attacker might be able to corrupt sensitive data without having to win a race. No such places were identified throughout this research though.

#### Summary

In essence, every bit of code that executes after a failure condition has been detected but before the process is ultimately terminated should be considered as an attack surface, with the attacker potentially “winning” if they are able to make this code block. With signal handling, this becomes even more complex as code such as

if (security\_failure) {

    CRASH();

}

Is in fact more like

if (security\_failure) {

    signal\_handler();

    CRASH();

}

Ideally, signal handling would thus be removed entirely from critical processes, or at least restricted to fewer signals. All in all, the speed at which these fixes were implemented implies that Apple is committed to PAC (and APRR) as a serious security mitigation.

## Conclusion

This post discussed multiple ways for bypassing WebKit’s JIT hardenings. While some approaches didn’t work or weren’t attempted further for various reasons, two previously unknown (at least publicly…) issues, as well as multiple variants thereof, were discovered that allowed for reliable bypasses. They were reported to Apple and subsequently fixed in iOS 13.6 as CVE-2020-9870 and CVE-2020-9910.

This post also concludes the three part series. All in all it was a substantial time investment to first find a suitable vulnerability, then bypass the various exploit mitigations with it. However, it is important to keep in mind that a large part of this effort is a one time cost for an attacker, required for the first exploit developed. Afterwards, the attack can likely reuse the majority of the previous exploit work for subsequent vulnerabilities. On the other hand, once mitigation bypasses are treated similarly to vulnerabilities and fixed swiftly once reported (as well as included in bug-bounty programs), this argument becomes weaker as an attacker is now disrupted if either their vulnerability or their mitigation bypass is reported or otherwise found by the vendor. In addition to the exploited vulnerability, Apple also quickly fixed the PAC bypasses and assigned CVE numbers for them. It was pleasing to see Apple's commitment to fixing the mitigation bypass quickly and I hope that they continue to do so in the future.

While logic vulnerabilities will likely allow for sandbox escapes for the foreseeable future and are largely unaffected by exploit mitigation technologies, it seems plausible that a typical exploit chain will still require renderer shellcode execution (or at least something roughly equivalent). Since some form of memory corruption is likely required for that, developing and maintaining memory corruption mitigations at various levels (close to the initial bug with MTE, during the early exploitation phase with the Gigacage and StructureID randomization, and after read/write has already been achieved through PAC and APRR) alongside stronger sandboxing, appears, generally speaking, to be a worthwhile investment.