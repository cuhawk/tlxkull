---
source: p0
source_url: https://projectzero.google/2020/01/part-ii-returning-to-adobe-reader.html
title: "Part II: Returning to Adobe Reader symbols on macOS - Project Zero"
description: "Posted by Mateusz Jurczyk, Project ZeroIn a blog post titled"
---

Posted by Mateusz Jurczyk, Project Zero

In a blog post titled ["The story of Adobe Reader symbols"](https://projectzero.google/2019/10/the-story-of-adobe-reader-symbols.html) published in October 2019, I presented an analysis of the debug symbols shipped with some older versions of Adobe Reader for Unix-family systems released between 1997-2013. Such symbols can prove immensely useful for both understanding the inner workings of various Reader components while reverse engineering, and for automated tasks such as crash classification and deduplication in fuzzing projects. In that blog post, I only briefly mentioned the macOS Reader packages as containing up-to-date symbols for the JP2K and 3D components, but missing any other interesting information beyond that. Upon a closer and more thorough inspection of the Mac releases, I have discovered that in fact more debug metadata made its way to the publicly available installers, some of which is unique (i.e. not present in other symbol sources) and/or more recent than the latest Unix symbols. Considering the added value of this new data, I wish to share it with you here in this follow-up post. As a reminder, legacy builds of Adobe Reader dating back to the '90s can be downloaded from the official ftp.adobe.com FTP server and the corresponding paths on the ardownload.adobe.com HTTP server.

## Review of core Acrobat Mach-O images

Below is a breakdown of the six core components of Reader for macOS, and whether they included symbols in each of the existing software releases. For brevity and readability, the table starts with version 7.x from 2005, as this is where the debug information started making first appearances:

|     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- |
|  | Adobe Reader for Mac OS |
|  | 7.x | 8.x | 9.x | 10.x | 11.x | DC |
|  | 2005-2009 | 2007-2011 | 2008-2013 | 2011-2014 | 2012-2017 | 2015-2019 |
| Acrobat | Stripped | Not stripped ¹ | Stripped | Stripped | Stripped | Stripped |
| AGM | Stripped | Not stripped ¹ | Not stripped ² | Stripped | Stripped | Not stripped ³ |
| CoolType | Stripped | Not stripped ¹ | Not stripped ²<br>(private) | Stripped | Stripped | Stripped |
| BIB | Stripped | Not stripped ¹ | Not stripped ² | Stripped | Stripped | Stripped |
| JP2K | Stripped | Not stripped | Not stripped | Not stripped | Not stripped | Not stripped |
| 3D | Not stripped<br>(private) | Not stripped | Not stripped | Not stripped | Not stripped | Not stripped |

¹ See detailed 8.x version breakdown

² See detailed 9.x version breakdown

³ Up to version 15.016.20045, stripped afterwards

As mentioned in the annotations, the presence of symbols for some modules varied greatly between minor versions of the 8.x and 9.x releases (the reason for which is unclear to me). Detailed tables for these two major versions are shown below:

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
|  | Adobe Reader 8.x for Mac OS |
|  | 8.0, 8.1.x, 8.2.0, 8.2.1 | 8.2.2, 8.2.3 | 8.2.4 | 8.2.5, 8.2.6, 8.3.x |
| Acrobat | Stripped | Not stripped | Stripped | Not stripped |
| AGM | Stripped | Not stripped | Not stripped | Not stripped |
| CoolType | Stripped | Not stripped | Stripped | Not stripped |
| BIB | Stripped | Not stripped | Not stripped | Not stripped |
| JP2K | Not stripped | Not stripped | Not stripped | Not stripped |
| 3D | Not stripped | Not stripped | Not stripped | Not stripped |

|     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- |
|  | Adobe Reader 9.x for Mac OS |
|  | 9.0, 9.1.x, 9.2, 9.3.x, 9.4.0, 9.4.1 | 9.4.2, 9.4.3 | 9.4.4 | 9.4.5 | 9.4.6, 9.5.x |
| Acrobat | Stripped | Stripped | Stripped | Stripped | Stripped |
| AGM | Not stripped | Stripped | Stripped | Not stripped | Not stripped |
| CoolType | Not stripped<br>(private) | Stripped | Not stripped<br>(private) | Not stripped<br>(private) | Not stripped<br>(private) |
| BIB | Not stripped | Stripped | Stripped | Stripped | Not stripped |
| JP2K | Not stripped | Not stripped | Not stripped | Not stripped | Not stripped |
| 3D | Not stripped | Not stripped | Not stripped | Not stripped | Not stripped |

Clearly, there is a lot of useful information hidden in the Reader Mach-O executables, with versions 8.x and 9.x being the most ripe with debug data. I find the following pieces of information to be the most useful and unique compared to the data previously extracted from the Unix files:

- Private symbols in the [stabs](https://sourceware.org/gdb/current/onlinedocs/stabs/) format for the 3D module (version 7.x) and the CoolType font engine (most 9.x versions). This includes not only function and global variable names, but also source file paths, source line numbers corresponding to blocks of assembly code, local variable names, definitions of structures, enums etc. This kind of metadata provides us with some extremely detailed and accurate insight into how the code works. To my best knowledge, such private symbols for these two libraries are not known to be available from any other public source and may therefore be a great assistance to anyone interested in their inner workings.

- The symbols for the Acrobat, AGM, CoolType and BIB modules in versions 8.x and 9.x are generally more recent than the most recent symbols on the Unix side. Furthermore, for the purpose of crash deduplication or root cause analysis, it is arguably easier to run Reader 9 on macOS than Reader 9 on SunOS/Solaris, or Reader 7 on AIX/HP-UX, simply because it is the more common platform.

- Lastly, the AGM component was not stripped in the DC versions between 15.006.30033 (March 2015) to 15.016.20045 (June 2016), which is also a much more recent source of information than what was previously accessible (AIX/HP-UX symbols for versions 7.x from 2007).


Out of all of them, I believe that the private CoolType symbols carry the most interesting and practical information. What makes it especially attractive is the fact that it is not only applicable to Reader and other Adobe products, but also to all other libraries and system components which share the same font rasterization code – such as the Windows kernel drivers (win32k.sys, atmfd.dll), the Windows DirectWrite library (dwrite.dll), the macOS font libraries (libTrueTypeScaler.dylib, libType1Scaler.dylib), and the JRE t2k font rasterizer (libt2k.so etc.). Let's have a deeper look into the kind of data found in the debug builds of AdobeCoolType and how we can extract it and use it in a meaningful way.

## Digging into the CoolType symbols

In total, I have found 17 unique AdobeCoolType files in various versions of Reader 9.x which contain debug data in the stabs format. The format is a largely textual one, so if we glance at the end of the analyzed file, we should see data similar to the following dump:

|     |
| --- |
| parseSeacComponent:f(0,1).h:P(0,17).stdcode:P(0,1).offset:r(0,3)....t1cParse:F(0,1).offset:p(0,3).aux:p(0,27).glyph:p(0,28).h:(0,19).offset:r(0,3).aux:r(0,27).glyph:r(0,28)....t1cDecrypt:F(0,1).lenIV:p(0,1).length:p(2,29).cipher:p(4,36).plain:p(4,36).lenIV:r(0,1).length:r(2,29).r:r(0,9).cnt:(0,3)..c1:(0,11).....t1cUnprotect:F(0,1).lenIV:p(0,1).length:p(2,29).cipher:p(4,36).plain:p(4,36).lenIV:r(0,1).length:r(2,29).single:r(0,11).r1:(0,9).r2:(0,9).cnt:(0,3)..c1:r(0,11).....:t(0,35)=\*(0,36).ctlVersionCallbacks:t(0,36)=(2,19).\_errstrs.4964.t1cErrStr:F(4,36).errcode:p(0,1).errstrs:V(0,37).errcode:r(0,1)...:t(0,37)=ar(9,27);0;18;(4,36)... |

That particular snippet shows names from the open-source [AFDKO](https://github.com/adobe-type-tools/afdko) library, which is compiled into CoolType. Other parts of the debug section reveal more interesting and less public data, such as the detailed stack layout of Type1InterpretCharString, the main Postscript CharString interpreter function shown to be subject to a [number of bugs in 2015](https://projectzero.google/2015/07/one-font-vulnerability-to-rule-them-all.html):

|     |
| --- |
| Type1InterpretCharString:F(5,29).inst:p(38,37).pProcs:p(41,28).pCharDataDesc:p(0,48).pCharIO:p(41,15).pRunData:p(41,13).pPathProcs:p(0,49).pT1Args:p(0,50).etod\_path:(38,117).etod\_arg:(45,3).status:(0,51).temp\_flags:(5,18).did\_retry:(5,1)..moveto\_lineto\_index:r(5,29)...Exception:(13,3)..pPathProcs:(42,6)..substack:(0,52).psstack:(0,53).flexCds:(0,54).hints:(0,55).hint3:(0,56).vStemCount:(5,29).op\_stk:(41,10).op\_sp:r(5,37).sp:r(38,46).cp:(5,39).wid:(5,39).tempfcd:(5,39).dcp:(5,39).delta:(5,39).i:r(5,15).indx:(5,15).sby:(5,35).dmin:(5,35).subindex:(5,15).tfmLockPt:(0,57).flags:(5,18).accentClipBBox:(5,47).pTempClipBBox:(42,5).prevcp:(5,39).initcp:(5,39). |

The amount of information is stunning – within a 6.35 MB AdobeCoolType file from Reader 9.5.5, around 1.78 MB is consumed just by debug strings of various kinds. Unfortunately, IDA Pro or Ghidra don't seem to parse stabs, so while we will see the names of functions and globals in these disassemblers, types (structures, unions, enums, typedefs) and local variable names unfortunately won't be imported. If I missed some way to have these symbols loaded into the database, let me know!

The two tools I have successfully used to load stabs are the old OS X objdump and gdb utilities, with the latter being especially powerful. In my test environment, I have Adobe Reader 9.5.5 installed on Mac OS 10.6.8 (Snow Leopard). When I then start Reader under gdb, I see the following output:

|     |
| --- |
| tests-Mac:~ test$ gdb /Applications/Adobe\ Reader\ 9/Adobe\ Reader.app/Contents/MacOS/AdobeReader<br>\[...\]<br>(gdb) r<br>Starting program: /Applications/Adobe Reader 9/Adobe Reader.app/Contents/MacOS/AdobeReader<br>Reading symbols for shared libraries .+++............................................................................................ done<br>Reading symbols for shared libraries ...<br>\[...\]<br>warning: Could not find object file "/Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/build/MT\_Release\_Symbols/cooltype5.build/Universal/MT\_Release\_Symbols.build/Objects-normal/i386/CT\_CTS\_OpenType.o" - no debug information available for "/Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/cts/cts\_glue/CT\_CTS\_OpenType.cpp".<br>warning: Could not find object file "/Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/build/MT\_Release\_Symbols/cooltype5.build/Universal/MT\_Release\_Symbols.build/Objects-normal/i386/CT\_CTS\_StreamFromBuffer.o" - no debug information available for "/Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/cts/cts\_glue/CT\_CTS\_StreamFromBuffer.c".<br>....... done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries .. done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries . done<br>Reading symbols for shared libraries ... done |

The debugger successfully loads the application and embedded symbols, but it complains about missing object and source files – expecting them to exist as such a build would typically be used for debugging on a developer's machine. At this point, we can conveniently dump various types of general information with the following gdb commands:

- info functions – list all functions found in the loaded modules, or print information about a specific function

- info line – print information about a specific line in the source code file (i.e. which assembly regions it corresponds to)

- info sources – list source file names

- info types – list all known types

- info variables – list all global and static variable names


This already gives us plenty of information; for example, let's go back to our favourite function and look it up:

|     |
| --- |
| (gdb) info functions Type1InterpretCharString<br>All functions matching regular expression "Type1InterpretCharString":<br>File /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/t1interp.c:<br>IntX Type1InterpretCharString(PFontInst, BCProcs \*, T1CharDataDesc \*, CharIO \*, RunRec \*, PathProcs \* volatile, T1Args \* volatile);<br>(gdb) |

We can set a breakpoint on it and learn in which line in the source code it is declared:

|     |
| --- |
| (gdb) b Type1InterpretCharString<br>Breakpoint 1 at 0x7d853e5a: file /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/t1interp.c, line 7037.<br>(gdb) |

We can get some more information on that specific line:

|     |
| --- |
| (gdb) info line /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/t1interp.c:7037<br>Line 7037 of "/Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/t1interp.c" starts at address 0x7d853e5a <Type1InterpretCharString+77> and ends at 0x7d853e80 <Type1InterpretCharString+115>.<br>(gdb) |

Finally, we can check the definition of one of the function argument types, for example thePFontInst structure pointer:

|     |
| --- |
| (gdb) ptype PFontInst<br>type = struct \_t\_FontInst {<br>    Card16 gridRatio;<br>    Card16 xAlign;<br>    Fixed flatnessFactor;<br>    FixMtx tfmMtx;<br>    Card32 lenStemSnapV;<br>    Fixed stemSnapV\[48\];<br>    Card32 lenStemSnapH;<br>    Fixed stemSnapH\[48\];<br>\[...\]<br>    Fixed accentHintedWidth;<br>    Fixed accentCSadjust;<br>    Fixed accentDSdx;<br>    Fixed blueStdHW;<br>    Card32 instructions;<br>    boolean boostNeeded;<br>    Card16 boostPhase;<br>    Card16 fontType;<br>} \*<br>(gdb) print sizeof(struct \_t\_FontInst)<br>$2 = 1020<br>(gdb) |

### Analyzing issue \#1888 (CVE-2019-8048)

Enumerating the global information may prove very informative and bring answers to a number of questions one could have had while reverse engineering font rasterizers. However, the true power of the symbols lies in the context information available during live debugging. In the previous blog post, we tried to recover the stack trace upon triggering a crash with the PoC for [issue #1888](https://bugs.chromium.org/p/project-zero/issues/detail?id=1888). This is how far we got:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhF_9Q_s620_pasted+image+0+%281%29.png)

When we load the same PDF in Adobe Reader 9.5.5 for macOS, here is what we will see under gdb:

|     |
| --- |
| Program received signal EXC\_BAD\_ACCESS, Could not access memory.<br>Reason: KERN\_INVALID\_ADDRESS at address: 0xff978034<br>0x7d87e018 in FixOnePath (maxStem=void, cs=0x7d9dbe98, expansionFactor=3932) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/glbclr.c:787<br>787     /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/glbclr.c: No such file or directory.<br>        in /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/glbclr.c<br>(gdb) bt<br>#0  0x7d87e018 in FixOnePath (maxStem=void, cs=0x7d9dbe98, expansionFactor=3932) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/glbclr.c:787<br>#1  0x7d87ed67 in GlobalColoring (stems=void, counters=0x0, b3=0xbfffa858, expansionFactor=3932, numCounters=15, numStems=14, pClientHook=0xbfffa764) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/glbclr.c:608<br>#2  0x7d85891b in Type1InterpretCharString (inst=0xd6a704, pProcs=0xbfffa748, pCharDataDesc=0xbfffa910, pCharIO=0xbfffa8e0, pRunData=0xbfffa728, pPathProcs=0xbfffa544, pT1Args=0xbfffa6c8) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/t1interp.c:3874<br>#3  0x7d83b1d8 in BuildRuns (inst=0xd6a704, pCharDataDesc=0xbfffa910, pCharIO=0xbfffa8e0, pClipBBox=0x0, pRunData=0xbfffa728, pCallbackProc=0xbfffa748, pClientHook=0xbfffa764, rFlags=33) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/atmbuild.c:384<br>#4  0x7d83b39c in ATMBuildBitMap (pFontInst=0xd6a704, pCallbackProc=0x7d9d9e24, pCharDataDesc=0xbfffa910, pCharIO=0xbfffa8e0, pClipBBox=0x0, pBitMap=0xbfffa994, pClientHook=0xb83ab4) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/buildch/sources/atmbuild.c:625<br>#5  0x7d73bc9f in ATMCGetGlyph () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>#6  0x7d73b517 in Render::RenderToGlyphMap () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>#7  0x7d739d0c in FontInstanceCache::GetGlyph () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>#8  0x7d739239 in FontInstanceCache::GetGlyphMaps () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>#9  0x7d738670 in Text::GetTextGlyphs () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>#10 0x7d738149 in \_CTTextGetTextGlyphs\_GetTextGlyphs () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>\[...\] |

Now that is a much more detailed call stack – we can see the names of the ancestors of ATMBuildBitMap, and we have access to almost complete type/locals information.

### Analyzing issue \#1891 (CVE-2019-8042)

As another example, let's take a CoolType crash in TrueType font processing reported in [issue #1891](https://bugs.chromium.org/p/project-zero/issues/detail?id=1891). When we open poc.pdf in Reader, we get the following crash:

|     |
| --- |
| Program received signal EXC\_BAD\_ACCESS, Could not access memory.<br>Reason: KERN\_PROTECTION\_FAILURE at address: 0x0a68d4cc<br>0x7d72a310 in fsg\_QueryTwilightElement (pPrivateFontSpace=0xa69b008 "", PrivateSpaceOffsets=0x8caad0) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/fsglue.c:915<br>915     /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/fsglue.c: No such file or directory.<br>        in /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/fsglue.c |

Once again, we can obtain a very verbose stack trace:

|     |
| --- |
| (gdb) bt<br>#0  0x7d72a310 in fsg\_QueryTwilightElement (pPrivateFontSpace=0xa69b008 "", PrivateSpaceOffsets=0x8caad0) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/fsglue.c:915<br>#1  0x7d729c93 in fs\_\_NewTransformation (inputPtr=0xbfffc040, outputPtr=0xbfffbf70, useHints=1, pFontInst=0x83238d4) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/fscaler.c:474<br>#2  0x7d729b19 in fs\_NewTransformation (inputPtr=0xbfffc040, outputPtr=0xbfffbf70, pFontInst=0x83238d4) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/fscaler.c:411<br>#3  0x7d72997e in SetGlyph (pCharDataDesc=0xbfffc264, inst=0x83238d4, procs=0x7d9d9e24, mem=0xbfffc1c0, in=0xbfffc040, out=0xbfffbf70) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/ttbuild.c:392<br>#4  0x7d73c331 in TTBuildBitMap (pFontInst=0x83238d4, pCallbackProc=0x7d9d9e24, pCharDataDesc=0xbfffc264, pCharIO=0xbfffc210, pClipBBox=0x0, pBitMap=0xbfffc2c4, pClientHook=0xb67fac) at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/ttbuild.c:1128<br>#5  0x7d73bc9f in ATMCGetGlyph () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>#6  0x7d73b517 in Render::RenderToGlyphMap () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>#7  0x7d739d0c in FontInstanceCache::GetGlyph () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>#8  0x7d739239 in FontInstanceCache::GetGlyphMaps () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>#9  0x7d738670 in Text::GetTextGlyphs () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>#10 0x7d738149 in \_CTTextGetTextGlyphs\_GetTextGlyphs () at /Volumes/BuildDisk\_mbs16/Acro\_root\_nsp/bravo/build/cooltype/xcode2/../../../source/cooltype/source/atm/base/truetype/sources/interp.c:2636<br>\[...\] |

If we wish to dig deeper and analyze the root cause of the problem, we may start with establishing the origin of the unmapped 0x0a68d4cc address. The arguments of the top-level fsg\_QueryTwilightElement function are:

|     |
| --- |
| pPrivateFontSpace=0xa69b008 "", PrivateSpaceOffsets=0x8caad0 |

The 0x0a68d4cc and 0xa69b008 addresses are close to each other, with a difference of 56124 bytes between them, so we might expect that the former is calculated based on the latter. Let's look into the second parameter to see if we find any clues that would align with the existing data:

|     |
| --- |
| (gdb) ptype PrivateSpaceOffsets<br>type = struct fsg\_PrivateSpaceOffsets {<br>    uint32 offset\_storage;<br>    uint32 offset\_functions;<br>    uint32 offset\_instrDefs;<br>    uint32 offset\_controlValues;<br>    uint32 offset\_globalGS;<br>    uint32 offset\_FontProgram;<br>    uint32 offset\_PreProgram;<br>    uint32 offset\_TwilightZone;<br>    uint32 offset\_TwilightOutline;<br>    fsg\_OutlineFieldInfo TwilightOutlineFieldOffsets;<br>} \*<br>(gdb) print \*(fsg\_PrivateSpaceOffsets \*)0x8caad0<br>$2 = {<br>offset\_storage = 0,<br>offset\_functions = 192,<br>offset\_instrDefs = 1096,<br>offset\_controlValues = 1096,<br>offset\_globalGS = 3764,<br>offset\_FontProgram = 4124,<br>offset\_PreProgram = 7149,<br>offset\_TwilightZone = 4294911172,<br>offset\_TwilightOutline = 4294911220,<br>TwilightOutlineFieldOffsets = {<br>    x = 65304,<br>    y = 326488,<br>    ox = 587672,<br>    oy = 848856,<br>    oox = 1110040,<br>    ooy = 1371224,<br>    onCurve = 0,<br>    sp = 65296,<br>    ep = 65298,<br>    f = 1632408,<br>    fc = 65300,<br>    maxPointIndex = 65296<br>}<br>}<br>(gdb) |

Two of the structure fields seem unusually large, what do they look like as signed numbers?

|     |
| --- |
| (gdb) print (int)((fsg\_PrivateSpaceOffsets \*)0x8caad0)->offset\_TwilightZone<br>$3 = -56124<br>(gdb) print (int)((fsg\_PrivateSpaceOffsets \*)0x8caad0)->offset\_TwilightOutline<br>$4 = -56076<br>(gdb) |

We found the culprit! If we open the fsg\_QueryTwilightElement function in a disassembler, we can confirm that this is indeed how the invalid pointer is constructed prior to being dereferenced. We could now decide to continue the analysis to learn why the two fields are assigned out-of-bounds values and what the root cause of the problem is, or leave it at that and provide the extra bit of information to the vendor while reporting the bug.

## Conclusion

As we can see, working with debug metadata can make a world of difference during the security research of a closed-source application. I am hoping that these newly uncovered Reader symbols will make the life of some security engineers easier in the future. For me, it is yet another piece of evidence that reconnaissance is an essential part of vulnerability research and may yield results far exceeding expectations.

On the other hand, the recon step wouldn't be necessary had Adobe made the symbols available to everyone upfront. The fact that the debug data on macOS hasn't been previously discussed means that only the most determined offensive security researchers might have known about it in the past. We would therefore encourage closed-source companies to improve the inspectability of their software by proactively sharing symbols, similarly to what Microsoft does with their public symbol server. Such an approach would level the playing field and base the security of client applications on openness and not obscurity, which we believe would consequently benefit the users in the long term.