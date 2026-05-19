---
source: p0
source_url: https://projectzero.google/2020/04/fuzzing-imageio.html
title: "Fuzzing ImageIO - Project Zero"
description: "Posted by Samuel Groß, Project ZeroThis blog post discusses an old type of issue, vulnerabilities..."
---

**Posted by Samuel Groß, Project Zero**

This blog post discusses an old type of issue, vulnerabilities in image format parsers, in a new(er) context: on interactionless code paths in popular messenger apps. This research was focused on the Apple ecosystem and the image parsing API provided by it: the ImageIO framework. Multiple vulnerabilities in image parsing code were found, reported to Apple or the respective open source image library maintainers, and subsequently fixed. During this research, a lightweight and low-overhead guided fuzzing approach for closed source binaries was implemented and is released alongside this blogpost.

To reiterate an important point, the vulnerabilities described throughout this blog are reachable through popular messengers but are not part of their codebase. It is thus not the responsibility of the messenger vendors to fix them.

## Introduction

While reverse engineering popular messenger apps, I came across the following code (manually decompiled into ObjC and slightly simplified) on a code path reachable without user interaction:

NSData\* payload = \[handler decryptData:encryptedDataFromSender, ...\];

if (isImagePayload) {

    UIImage\* img = \[UIImage imageWithData:payload\];

    ...;

}

This code decrypts binary data received as part of an incoming message from the sender and instantiates a [UIImage](https://developer.apple.com/documentation/uikit/uiimage?language=objc) instance from it. The UIImage constructor will then try to determine the image format automatically. Afterwards, the received image is passed to the following code:

CGImageRef cgImage = \[image CGImage\];

CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();

CGContextRef cgContext = CGBitmapContextCreate(0, thumbnailWidth, thumbnailHeight, ...);

CGContextDrawImage(cgContext, cgImage, ...);

CGImageRef outImage = CGBitmapContextCreateImage(cgContext);

UIImage\* thumbnail = \[UIImage imageWithCGImage:outImage\];

The purpose of this code is to render a smaller sized version of the input image for use as a thumbnail in a notification for the user. Unsurprisingly, similar code can be found in other messenger apps as well. In essence, code like the one shown above turns Apple’s UIImage image parsing and CoreGraphics image rendering code into 0click attack surface.

One of the insights gained from [developing an exploit for an iMessage vulnerability](https://projectzero.google/2020/01/remote-iphone-exploitation-part-1.html) was that a memory corruption vulnerability could likely be exploited using the described techniques if the following preconditions are met:

1. A form of automatic delivery receipt sent from the same process handling the messages

2. Per-boot ASLR of at least some memory mappings

3. Automatically restarting services


In that case, the vulnerability could for example be used to corrupt a pointer to an ObjC object (or something similar), then construct a crash oracle to bypass ASLR, then gain code execution afterwards.

All preconditions are satisfied in the current attack scenario, thus prompting some research into the robustness of the exposed image parsing code. Looking into the [documentation of UImage](https://developer.apple.com/documentation/uikit/uiimage?language=objc), the following sentence can be found: “You use image objects to represent image data of all kinds, and the UIImage class is capable of managing data for all image formats supported by the underlying platform”. As such, the next step was determining exactly what image formats were supported by the underlying platform.

## An Introduction to ImageIO.framework

Parsing of image data passed to UIImage is implemented in the ImageIO framework. As such, the supported image formats can be enumerated by reverse engineering the ImageIO library (/System/Library/Frameworks/ImageIO.framework/Versions/A/ImageIO on macOS or part of the dyld\_shared\_cache on iOS).

In the ImageIO framework, every supported image format has a dedicated IIO\_Reader subclass for it. Each IIO\_Reader subclass is expected to implement a testHeader function which, when given a chunk of bytes, should decide whether these bytes represent an image in the format supported by the reader. An example implementation of the testHeader implementation for the LibJPEG reader is shown below. It simply tests a few bytes of the input to detect the JPEG header magic.

bool IIO\_Reader\_LibJPEG::testHeader(IIO\_Reader\_LibJPEG \*this, const unsigned \_\_int8 \*a2, unsigned \_\_int64 a3, const \_\_CFString \*a4)

{

return \*a2 == 0xFF && a2\[1\] == 0xD8 && a2\[2\] == 0xFF;

}

By listing the different testHeader implementations, it thus becomes possible to compile a list of file formats supported by the ImageIO library. The list is as follows:

IIORawCamera\_Reader::testHeader

IIO\_Reader\_AI::testHeader

IIO\_Reader\_ASTC::testHeader

IIO\_Reader\_ATX::testHeader

IIO\_Reader\_AppleJPEG::testHeader

IIO\_Reader\_BC::testHeader

IIO\_Reader\_BMP::testHeader

IIO\_Reader\_CUR::testHeader

IIO\_Reader\_GIF::testHeader

IIO\_Reader\_HEIF::testHeader

IIO\_Reader\_ICNS::testHeader

IIO\_Reader\_ICO::testHeader

IIO\_Reader\_JP2::testHeader

IIO\_Reader\_KTX::testHeader

IIO\_Reader\_LibJPEG::testHeader

IIO\_Reader\_MPO::testHeader

IIO\_Reader\_OpenEXR::testHeader

IIO\_Reader\_PBM::testHeader

IIO\_Reader\_PDF::testHeader

IIO\_Reader\_PICT::testHeader  (macOS only)

IIO\_Reader\_PNG::testHeader

IIO\_Reader\_PSD::testHeader

IIO\_Reader\_PVR::testHeader

IIO\_Reader\_RAD::testHeader

IIO\_Reader\_SGI::testHeader  (macOS only)

IIO\_Reader\_TGA::testHeader

IIO\_Reader\_TIFF::testHeader

While this list contains many familiar formats (JPEG, PNG, GIF, …) there are numerous rather exotic ones as well (KTX and ASTC, apparently used for textures or AI: Adobe Illustrator Artwork) and some that appear to be specific to the Apple ecosystem (ICNS for icons, ATX likely for Animojis)

Support for the different formats also varies. Some formats appear fully supported and are often implemented using what appear to be the open source parsing library which can be found in /System/Library/Frameworks/ImageIO.framework/Versions/A/Resources on macOS: libGIF.dylib, libJP2.dylib, libJPEG.dylib, libOpenEXR.dylib, libPng.dylib, libRadiance.dylib, and libTIFF.dylib. Other formats seem to have only rudimentary support for handling the most common cases.

Finally, some formats (e.g. PSD), also appear to support out-of-process decoding (on macOS this is handled by /System/Library/Frameworks/ImageIO.framework/Versions/A/XPCServices/ImageIOXPCService.xpc) which can help sandbox vulnerabilities in the parsers. It does not, however, seem to be possible to specify whether parsing should be performed in-process or out-of-process in the public APIs, and no attempt was made to change the default behaviour.

## Fuzzing Closed Source Image Parsers

Given the wide range of available image formats and the fact that no source code is available for the majority of the code, fuzzing seemed like the obvious choice.

The choice of which fuzzer and fuzzing approach to use was not so obvious. Since the majority of the target code was not open source, many standard tools were not directly applicable. Further, I had decided to limit fuzzing to a single Mac Mini for simplicity. Thus, the fuzzer should:

1. Run with as little overhead as possible to fully utilize the available compute resources, and

2. Make use some kind of code coverage guidance


In the end I decided to implement something myself on top of [Honggfuzz](https://github.com/google/honggfuzz). The idea for the fuzzing approach is loosely based on the paper: [Full-speed Fuzzing: Reducing Fuzzing Overhead through Coverage-guided Tracing](https://arxiv.org/abs/1812.11875)

and achieves lightweight, low-overhead coverage guided fuzzing for closed source code by:

1. Enumerating the start offset of every basic block in the program/library. This is done with a simple IDAPython script

2. At runtime, in the fuzzed process, replacing the first byte of every undiscovered basic block with a breakpoint instruction (int3 on Intel). The original byte and the corresponding offset in the coverage bitmap are stored in a dedicated shadow memory mapping whose address can be computed from the address of the modified library, and

3. Installing a SIGTRAP handler that will:

1. Retrieve the faulting address and compute the offset in the library as well as the address of the corresponding entry in the shadow memory

2. Mark the basic block as found in the global coverage bitmap

3. Replace the breakpoint with the original byte

4. Resume execution

As only undiscovered basic blocks are instrumented and since every breakpoint is only triggered once, the runtime overhead quickly approaches zero. It should, however, be noted that this approach only achieves basic block coverage and not edge coverage as used for example by [AFL](https://lcamtuf.coredump.cx/afl/) and which, for closed source targets, can be achieved through [dynamic](https://project.inria.fr/FranceJapanICST/files/2019/04/19-Kyoto-Fuzzing_Binaries_using_Dynamic_Instrumentation.pdf) [binary](https://github.com/googleprojectzero/winafl/blob/master/readme_dr.md) [instrumentation](https://youtu.be/fTNzylTMYks) albeit with some performance overhead. It will thus be more “coarse grained” and for example treat different transitions to the same basic block as equal whereas AFL would not. As such, this approach will likely find fewer vulnerabilities given the same number of iterations. I deemed this acceptable as the goal of this research was not to perform thorough discovery of all vulnerabilities but rather to quickly test the robustness of the image parsing code and highlight the attack vector. Thorough fuzzing, in any case, is always best performed by the maintainers with source code access.

The described approach was fairly easy to implement by patching honggfuzz’s client instrumentation code and writing an IDAPython script to enumerate the basic block offsets. Both patch and IDAPython script can be found [here](https://github.com/googleprojectzero/p0tools/tree/master/TrapFuzz).

The fuzzer then started from a small corpus of around 700 seed images covering the supported image formats and ran for multiple weeks. In the end, the following vulnerabilities were identified:

[P0 Issue 1952](https://bugs.chromium.org/p/project-zero/issues/detail?id=1952)

A bug in the usage of libTiff by ImageIO which caused controlled data to be written past the end of a memory buffer. No CVE was assigned for this issue likely because it had already been discovered internally by Apple before we reported it.

[CVE-2020-3826/P0 Issue 1953](https://bugs.chromium.org/p/project-zero/issues/detail?id=1953)

An out-of-bounds read on the heap when processing DDS images with invalid size parameters.

[CVE-2020-3827/P0 Issue 1956](https://bugs.chromium.org/p/project-zero/issues/detail?id=1956)

An out-of-bounds write on the heap when processing JPEG images with an optimized parser.

[CVE-2020-3878/P0 Issue 1974](https://bugs.chromium.org/p/project-zero/issues/detail?id=1974)

Possibly an off-by-one error in the PVR decoding logic leading to an additional row of pixel data being written out-of-bounds past the end of the output buffer.

[CVE-2020-3878/P0 Issue 1984](https://bugs.chromium.org/p/project-zero/issues/detail?id=1984)

A related bug in the PVR decoder leading to an out-of-bounds read which likely had the same root cause as P0 Issue 1974 and thus was assigned the same CVE number.

[CVE-2020-3880/P0 Issue 1988](https://bugs.chromium.org/p/project-zero/issues/detail?id=1988)

An out-of-bounds read during handling of OpenEXR images.

The last issue was somewhat special as it occurred in 3rd party code bundled with ImageIO, namely that of the [OpenEXR library](https://github.com/AcademySoftwareFoundation/openexr). As that library is open source, I decided to fuzz it separately as well.

## OpenEXR

[OpenEXR](https://www.openexr.com/) is “a high dynamic-range (HDR) image file format \[...\] for use in computer imaging applications”. The parser is implemented in C and C++ and can be found on [github](https://github.com/AcademySoftwareFoundation/openexr).

As described above, the OpenEXR library is exposed through Apple’s ImageIO framework and therefore is exposed as a 0click attack surface through various popular messenger apps on Apple devices. It is likely that the attack surface is not limited to messaging apps, though I haven't conducted additional research to support that claim.

As the library is open source, “conventional” guided fuzzing is much easier to perform. I used a Google internal, coverage-guided fuzzer running on roughly 500 cores for around two weeks. The fuzzer was guided by edge coverage using llvm’s [SanitizerCoverage](https://clang.llvm.org/docs/SanitizerCoverage.html) and generated new inputs by mutating existing ones using common binary mutation strategies and starting from a set of roughly 80 existing OpenEXR images as seeds.

Eight likely unique vulnerabilities were identified and reported as [P0 issue 1987](https://bugs.chromium.org/p/project-zero/issues/detail?id=1987) to the OpenEXR maintainers, then fixed in the [2.4.1 release](https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v2.4.1). They are briefly summarized next:

CVE-2020-11764

An out-of-bounds write (of presumably image pixels) on the heap in the copyIntoFrameBuffer function.

CVE-2020-11763

A bug that caused a std::vector to be read out-ouf-bounds. Afterwards, the calling code would write into an element slot of this vector, thus likely corrupting memory.

CVE-2020-11762

An out-of-bounds memcpy that was reading data out-of-bounds and afterwards potentially writing it out-of-bounds as well.

CVE-2020-11760, CVE-2020-11761, CVE-2020-11758

Various out-of-bounds reads of pixel data and other data structures.

CVE-2020-11765

An out-of-bounds read on the stack, likely due to an off-by-one error previously overwriting a string null terminator on the stack.

CVE-2020-11759

Likely an integer overflow issue leading to a write to a wild pointer.

Interestingly, the crash initially found by the ImageIO fuzzer ( [issue 1988](https://bugs.chromium.org/p/project-zero/issues/detail?id=1988)) did not appear to be reproducible in the upstream OpenEXR library and was thus reported directly to Apple. A possible explanation is that Apple was shipping an outdated version of the OpenEXR library and the bug had been fixed upstream in the meantime.

## Recommendations

Media format parsing remains an important issue. This was also demonstrated by other researchers and vendor advisories, with the two following coming immediately to mind:

- [https://awakened1712.github.io/hacking/hacking-whatsapp-gif-rce/](https://awakened1712.github.io/hacking/hacking-whatsapp-gif-rce/)

- [https://www.facebook.com/security/advisories/cve-2019-11931](https://www.facebook.com/security/advisories/cve-2019-11931)


This of course suggests that continuous fuzz-testing of input parsers should occur on the vendor/code maintainer side. Further, allowing clients of a library like ImageIO to restrict the allowed input formats and potentially to opt-in to out-of-process decoding can help prevent exploitation.

On the messenger side, one recommendation is to reduce the attack surface by restricting the receiver to a small number of supported image formats (at least for message previews that don’t require interaction). In that case, the sender would then re-encode any unsupported image format prior to sending it to the receiver. In the case of ImageIO, that would reduce the attack surface from around 25 image formats down to just a handful or less.

## Conclusion

This blog post described how image parsing code, as part of the operating system or third party libraries, end up being exposed to 0click attack surface through popular messengers. Fuzzing of the exposed code turned up numerous new vulnerabilities which have since been fixed. It is likely that, given enough effort (and exploit attempts granted due to automatically restarting services), some of the found vulnerabilities can be exploited for RCE in a 0click attack scenario. Unfortunately it is also likely that other bugs remain or will be introduced in the future. As such, continuous fuzz-testing of this and similar media format parsing code as well as aggressive attack-surface reduction, both in operating system libraries (in this case ImageIO) as well as messenger apps (by restricting the number of accepted image formats on the receiver) are recommended.