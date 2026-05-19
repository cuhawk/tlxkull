---
source: p0
source_url: https://projectzero.google/2019/10/the-story-of-adobe-reader-symbols.html
title: "The story of Adobe Reader symbols - Project Zero"
description: "Posted by Mateusz Jurczyk, Project ZeroModern day security analysis of client applications is oft..."
---

Posted by Mateusz Jurczyk, Project Zero

Modern day security analysis of client applications is often hindered by the inaccessibility of their source code and other aids such as debug symbols. As a result, it is necessary to perform completely black-box reverse engineering of the software, in order to better understand their internals and reconstruct the missing context information, which is required to identify security flaws, triage and deduplicate crashes and so forth. This part of the process may be quite daunting, and the time spent on manual labor takes away from the time that could be spent testing the security properties of the program. Or in other words, it could be considered a waste of time. :-)

On the other hand, it is the researcher's responsibility to effectively use all available resources to their benefit. For very mature software with a long release history, e.g. dating back to the '90s, one such resource may be old versions of the program and/or builds for other platforms than currently supported. While such versions are of little use to the average user right now, they may contain artifacts that are invaluable for a bug hunter. In many cases, the core of the application under inspection doesn't change or changes only slightly over the years, so whatever ancillary information we are able to find is frequently applicable to the latest version at least to some degree. Given the above, I would recommend all security researchers to perform this extra "recon" step early in the process, as it may save one a lot of time and energy later on.

In this post, I will focus on the metadata found in the old and exotic versions of Adobe Reader.

## Adobe Reader debug symbols

The specific type of information I am usually after are the debug symbols. As the name suggests, these are designed to aid debugging of the application by the developers, and depending on their type, they may reveal internal names of functions, enums and source files, as well as full function prototypes, structure layouts and other interesting data. Even just the most basic type of symbols (including only function names) are greatly helpful, as they provide insight into the specific purpose of each area of assembly code, and enable the generation of pretty stack traces while triaging crashes.

On Windows, the Microsoft Visual C++ (MSVC) compiler generates symbols in external .pdb files, e.g. an output Program.pdb file created in the same directory as Program.exe. To my best knowledge, Adobe has never shipped the pdb files corresponding to the executable programs and libraries. Older compilers also had an option to embed symbols in the DBG format into the executables, but I haven't found any signs of them in Reader, so the Windows builds seem to never have included any debug symbols at all.

However on Linux, macOS and other unix-family systems, symbols can be embedded directly in the executable files, which makes them more prone to being shared publicly by the vendor when releasing compiled software, intentionally or unintentionally. This is what has been happening with some components of Adobe Reader for the last 20+ years. It's worth noting that the information has been circulating in the community for a while (see @nils' [tweet](https://twitter.com/nils/status/319085830612324354) from 2013 or [slide 16](https://github.com/bitshifter123/arpwn/blob/master/slidedecks/Infiltrate_2016_-_Pwning_Adobe_Reader_with_XFA.pdf) in Sebastian Apelt's presentation on XFA from 2016), but I find it interesting enough to try to make it even more widely known.

To get a reasonably complete picture of the situation, I decided to analyze the integral executables and libraries of Adobe Reader, across versions dating back to 1997. The components I chose were some of the most frequently researched/exploited ones: acroread (the main program), AGM (Adobe Graphics Manager), CoolType (Typography Engine), BIB (Bravo Interface Binder), JP2K (JPEG2000 Core Library) and rt3d (3D Runtime).

In the past, Adobe used to release Reader for a variety of Unix-based and Unix-like systems, such as SunOS, IRIX, OSF/1, HP-UX, AIX and Linux. Copies of the packages could be downloaded from the ardownload.adobe.com HTTP server or from the ftp.adobe.com FTP server. Specifically, they were served from ftp.adobe.com/pub/adobe/reader/unix and ftp.adobe.com/pub/adobe/acrobatreader/unix; the latter address doesn't seem to work at the time of this writing, but its archived version is available at [https://web.archive.org](https://web.archive.org/) (and the corresponding path on ardownload.adobe.com). Some SunOS packages were also served from other locations. After acquiring all of these builds/versions starting with 3.x (thanks [Gynvael](https://twitter.com/gynvael) for helping with this), I devised the following table, which summarizes the results of my analysis:

|     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- |
|  | Adobe Reader for Unix (SunOS, IRIX, OSF/1, Solaris, HP-UX, AIX, Linux) |
|  | 3.x | 4.x | 5.x | 7.x | 8.x | 9.x |
|  | 1997-1998 | 1999-2000 | 2002-2005 | 2005-2007 | 2007-2010 | 2009-2013 |
| acroread | Not stripped | Not stripped | Not stripped | Not stripped | Not stripped ² | Not stripped ² |
| AGM | Not stripped | Not stripped | Not stripped ¹ | Not stripped ¹ | Stripped | Stripped |
| CoolType | Missing | Not stripped | Not stripped ¹ | Stripped | Stripped | Stripped |
| BIB | Missing | Missing | Not stripped ¹ | Not stripped ¹ | Stripped | Stripped |
| JP2K | Missing | Missing | Missing | Not stripped | Not stripped | Not stripped ⁴ |
| rt3d | Missing | Missing | Missing | Not stripped ³ | Not stripped ² | Not stripped ² |

¹ AIX and HP-UX builds only, stripped otherwise

² SunOS builds only, stripped otherwise

³ In versions 7.0.8+, missing before

⁴ Up to versions 9.5.4, stripped in 9.5.5

Support for unix-based systems was discontinued after version 9.5.5 in 2013. As you can see, all of the above modules had symbols available for them at some point in time. For CoolType, the last revision of the public symbols is from 2005; for others, there are much more recent versions from 2013. Note, even the 2005 version of CoolType is very useful; it helped me understand the internals of the OpenType CharString interpreter during the [One font vulnerability to rule them all](https://j00ru.vexillium.org/slides/2015/recon.pdf) research in 2015.

When it comes to macOS, I initially believed that on that platform, only the JP2K and 3D modules had ever been released with any debug information. After more thorough inspection, I discovered that that assumption was wrong, and symbols for all other major components were also found in Reader 7.x, 8.x, 9.x and DC for Mac. To address this new information, we published a follow-up blog post: [Part II: Returning to Adobe Reader symbols on macOS](https://projectzero.google/2020/01/part-ii-returning-to-adobe-reader.html).

## Putting the symbols to use

In my opinion, the symbols are most useful for getting a better and quicker understanding of the code base, be it for an in-depth analysis of the software or for harnessing it for better fuzzing. In such case, there are two options: either target the older, symbolized binary during the audit/fuzzing and then try to reproduce the results against the latest version, or try to transfer the old symbols onto the new library and operate on that. While the latter option sounds much more reliable (it eliminates potential false positives and false negatives), I have found it difficult to port symbols between two similar modules compiled at a different time, for different platforms and/or with different compilers. I have tested BinDiff and Diaphora.

Another option is to manually copy the names to IDA specifically for the functions and objects being examined in one's research project, using a side-by-side view with the symbolized version. Doing it for a whole library might be a considerable effort (for instance the latest JP2KLib.dll in Reader has more than 3300 functions), but chances are only a small subset of the symbols will be needed in practice. Furthermore, once an .idb with a large number of recognized symbols is created incrementally over a few weeks, these symbols are then easily cross-diffed to the next build released each Patch Tuesday, as there are only minor changes between them.

Let's have a look at an example. Project Zero [issue #1892](https://bugs.chromium.org/p/project-zero/issues/detail?id=1892) is a recent heap corruption bug in the JP2KLib.dll library. After opening the poc.pdf file in Reader, WinDbg reports the following stack trace:

\[...\]

JP2KLib!JP2KCopyRect+0x17ce9:

1111cee9 c6040100        mov byte ptr \[ecx+eax\],0       ds:002b:fff3a008=??

0:000> k

# ChildEBP RetAddr

WARNING: Stack unwind information not available. Following frames may be wrong.

00 0473cb28 1111cfea JP2KLib!JP2KCopyRect+0x17ce9

01 0473cb8c 1111b4ff JP2KLib!JP2KCopyRect+0x17dea

02 0473cbf8 1111898e JP2KLib!JP2KCopyRect+0x162ff

03 0473cd7c 1110d2af JP2KLib!JP2KCopyRect+0x1378e

04 0473cdf0 1110d956 JP2KLib!JP2KCopyRect+0x80af

05 0473ce54 1110dc90 JP2KLib!JP2KCopyRect+0x8756

06 0473ce78 11125e4a JP2KLib!JP2KCopyRect+0x8a90

07 0473ced8 5fafb5be JP2KLib!JP2KImageDecodeTileInterleaved+0x2a

08 0473cf64 5fac449b AcroRd32!AX\_PDXlateToHostEx+0x32046e

09 0473d05c 5f9d828d AcroRd32!AX\_PDXlateToHostEx+0x2e934b

0a 0473d0a0 089ada8c AcroRd32!AX\_PDXlateToHostEx+0x1fd13d

\[...\]

Not very useful, is it? The only correctly recognized symbol is JP2KLib!JP2KImageDecodeTileInterleaved, which is an exported function. Unfortunately, the same crash doesn't reproduce on macOS, so we cannot readily get a symbolized call stack from there, but we can still use the AdobeJP2K Mach-O file to recreate the symbols on Windows. Let's open both JP2KLib.dll and AdobeJP2K in IDA, and start from the JP2KImageDecodeTileInterleaved entry point:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjYgUD_s480_pasted+image+0+%282%29.png)

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiARsu_s573_pasted+image+0+%283%29.png)

We can clearly rename sub\_1004DC58 to IJP2KImage::DecodeTile, or more specifically \_\_ZN10IJP2KImage10DecodeTileEiiiiiP14IJP2KImageData, which is the mangled C++ name of the method. Moving on:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjt048_s475_pasted+image+0+%284%29.png)

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjy8Ar_s597_pasted+image+0+%285%29.png)

There are two overloaded IJP2KImage::DecodeTile methods, in our case the first one was called when the process crashed. Let's rename sub\_1004D91F and look inside it:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiHW4l_s400_pasted+image+0+%286%29.png)

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjfxK1_s531_pasted+image+0+%287%29.png)

Without much doubt, sub\_1004D159 is another implementation of the overloaded IJP2KImage::DecodeTile. We can rename it and continue with the same steps until we reach the crashing location in the library. In this specific case, I had to look up the name of the top-level function in the stack trace in the Linux symbolized version of libJP2K.so, as it was inlined by the compiler in the macOS build.

Once all of the functions we are interested in are named in our database, we can use the IDA debugger with the WinDbg backend to open the proof-of-concept file in Adobe Reader again. Now, that looks much better:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEisqSQ_s615_pasted+image+0+%288%29.png)

I have looked and [asked](https://twitter.com/j00ru/status/1172548748679012352) for ways to export the symbol information from IDA so that it could be used in WinDbg directly. Relevant projects I have found or were recommended are listed below:

- [FakePDB](https://github.com/Mixaill/FakePDB)

- [ret-sync](https://github.com/bootleg/ret-sync)

- [IDA2Sym](https://github.com/siberas/IDA2Sym)

- [llvm-pdbutil](https://llvm.org/docs/CommandGuide/llvm-pdbutil.html)

- [arpwn scripts](https://github.com/bitshifter123/arpwn)


Unfortunately, none of the above fully met my expectations; some of them were posted as proof-of-concept / ad-hoc kind of tools, some threw inexplicable errors, some required manual fixes in the code, etc. This seems like a gap in tooling that I and many others would like to see closed. :-) Since I didn't find a satisfying solution, I will stick with the IDA debugger for the time being.

Let's take a look at another example, [issue #1888](https://bugs.chromium.org/p/project-zero/issues/detail?id=1888). This time the crash occurs in CoolType.dll:

CoolType!CTCleanup+0x22e92:

51ebd2a0 89048e          mov dword ptr \[esi+ecx\*4\],eax ds:002b:520d4000=00000000

0:000> k

# ChildEBP RetAddr

WARNING: Stack unwind information not available. Following frames may be wrong.

00 052fc0f0 51ebd214 CoolType!CTCleanup+0x22e92

01 052fc12c 51ebdabd CoolType!CTCleanup+0x22e06

02 052fc16c 51ec8219 CoolType!CTCleanup+0x236af

03 052fc1a0 51e68e68 CoolType!CTCleanup+0x2de0b

04 052fc8c4 51e64051 CoolType!CTInit+0x460e1

05 052fc9a8 51e9e7bb CoolType!CTInit+0x412ca

06 052fcb00 51e9e47f CoolType!CTCleanup+0x43ad

07 052fcb7c 51e769cd CoolType!CTCleanup+0x4071

08 052fcd44 51e7619f CoolType!CTInit+0x53c46

09 052fce14 51e75091 CoolType!CTInit+0x53418

0a 052fd1dc 51e74728 CoolType!CTInit+0x5230a

0b 052fd21c 51e73751 CoolType!CTInit+0x519a1

0c 052fd388 51e732e4 CoolType!CTInit+0x509ca

0d 052fd3dc 52192182 CoolType!CTInit+0x5055d

0e 052fd724 52190fc8 AGM!AGMInitialize+0x69352

0f 052fd884 5215bcd0 AGM!AGMInitialize+0x68198

\[...\]

Again, the stack trace is quite obscure. To make things worse, we don't have an obvious starting point for analysis, as the first CoolType function called by AGM.dll is not an exported symbol. However, when manually looking through the disassembly of these functions, my familiarity with font engines let me recognize that CoolType!CTInit+0x460e1 is in fact the OpenType CharString interpreter, the largest function in the library that goes by the name of DoType1InterpretCharString (see [this blog post](https://projectzero.google/2015/07/one-font-vulnerability-to-rule-them-all.html) for details). Once we've identified one function, we can follow the call stack upwards and downwards to try to match further names. In this case, we can use the CoolType symbols from Reader 4 and Reader 5, Microsoft's symbols for the DWrite.dll and fontdrvhost.exe images, and Apple's symbols for the libType1Scaler.dylib library. All of them share much of the same OpenType handling code.

When we are finished with renaming the functions and run Reader again in the IDA debugger against poc.pdf, we should see the following call stack at the time of the exception:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhdbi3_s620_pasted+image+0+%289%29.png)

As shown, I have successfully reconstructed most of the CoolType stack trace entries. I didn't manage to match symbols above ATMBuildBitMap, as it was invoked through an indirect call that was impossible to follow back, and I didn't recognize any of the ancestor functions. Still, decoding the eight top-level names is very useful in itself as it helps us better understand the affected code and the way it fails to process the malformed data.

Of course, porting symbols between different builds of the same library might not always be possible due to code being constantly added, removed and modified over time, and due to imperfect bindiffing tools. However, it is worth being aware of this possibility. When such metadata is available, it may prove to be a real time saver and a great aid for reverse engineering. Not to mention all the fun provided by crawling the Internet in search of obscure installers from the 1990's and 2000's, and digging into ancient or esoteric builds of the software under inspection. :)