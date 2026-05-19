---
source: p0
source_url: https://projectzero.google/2025/05/breaking-sound-barrier-part-i-fuzzing.html
title: "Breaking the Sound Barrier Part I: Fuzzing CoreAudio with Mach Messages - Project Zero"
description: "Guest post by Dillon Franke, Senior Security Engineer, 20% time on Project Zero Every seco..."
---

Guest post by Dillon Franke, Senior Security Engineer, 20% time on Project Zero

Every second, highly-privileged MacOS system daemons accept and process hundreds of IPC messages. In some cases, these message handlers accept data from sandboxed or unprivileged processes.

In this blog post, I’ll explore using Mach IPC messages as an attack vector to find and exploit sandbox escapes. I’ll detail how I used a custom fuzzing harness, dynamic instrumentation, and plenty of debugging/static analysis to identify a high-risk type confusion vulnerability in the coreaudiod system daemon. Along the way, I’ll discuss some of the difficulties and tradeoffs I encountered.

Transparently, this was my first venture into the world of MacOS security research and building a custom fuzzing harness. I hope this post serves as a guide to those who wish to embark on similar research endeavors.

I am open-sourcing the fuzzing harness I built, as well as several tools I wrote that were useful to me throughout this project. All of this can be found here: [https://github.com/googleprojectzero/p0tools/tree/master/CoreAudioFuzz](https://github.com/googleprojectzero/p0tools/tree/master/CoreAudioFuzz)

# The Approach: Knowledge-Driven Fuzzing

For this research project, I adopted a hybrid approach that combined fuzzing and manual reverse engineering, which I refer to as knowledge-driven fuzzing. This method, learned from my friend [Ned Williamson](https://x.com/NedWilliamson), balances automation with targeted investigation. Fuzzing provided the means to quickly test a wide range of inputs and identify areas where the system’s behavior deviated from expectations. However, when the fuzzer’s code coverage plateaued or specific hurdles arose, manual analysis came into play, forcing me to dive deeper into the target’s inner workings.

Knowledge-driven fuzzing offers two key advantages. First, the research process never stagnates, as the goal of improving the code coverage of the fuzzer is always present. Second, achieving this goal requires a deep understanding of the code you are fuzzing. By the time you begin triaging legitimate, security-relevant crashes, the reverse engineering process will have given you extensive knowledge of the codebase, enabling analysis of crashes from an informed perspective.

The cycle I followed during this research is as follows:

1. Identify an attack vector
2. Choose a target
3. Create a fuzzing harness
4. Fuzz and produce crashes
5. Analyze crashes and code coverage
6. Iterate on the fuzzing harness
7. Repeat steps 4-6

# Identify an Attack Vector

Standard browser sandboxing limits code execution by restricting direct operating system access. Consequently, exploiting a browser vulnerability typically requires the use of a separate “sandbox escape” vulnerability.

Since interprocess communication (IPC) mechanisms allow two processes to communicate with each other, they can naturally serve as a bridge from a sandboxed process to an unrestricted one. This makes them a prime attack vector for sandbox escapes, as shown below.

[![A diagram illustrating SANDBOX ESCAPE and PRIVILEGE ESCALATION. The sandbox escape shows a Web Browser Process within a SANDBOX RESTRICTED communicating with a Message Handler via MACH IPC. The privilege escalation shows an Unprivileged Process communicating with a Message Handler Highly Privileged Process via MACH IPC.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi_h5A_s600_unnamed.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi_h5A_s647_unnamed.png)

I chose Mach messages, the lowest level IPC component in the MacOS operating system, as the attack vector of focus for this research. I chose them mostly due to my desire to understand MacOS IPC mechanisms at their most core level, as well as the track record of historical security issues with Mach messages.

## Previous Work and Background

Leveraging Mach messages in exploit chains is far from a novel idea. For example, Ian Beer [identified a core design issue](https://projectzero.google/2016/10/taskt-considered-harmful.html) in 2016 with the XNU kernel related to the handling of task\_t Mach ports, which allowed for exploitation via Mach messages. [Another post](https://projectzero.google/2019/08/in-wild-ios-exploit-chain-2.html) showed how an in-the-wild exploit chain utilized Mach messages in 2019 for heap grooming techniques. I also drew much inspiration from Ret2 Systems’ [blog post](https://blog.ret2.io/2018/06/05/pwn2own-2018-exploit-development/) about leveraging Mach message handlers to find and weaponize a Safari sandbox escape.

I won’t spend too much time detailing the ins and outs of how Mach messages work, (that is better left to a more [comprehensive post](https://dmcyk.xyz/post/xnu_ipc_i_mach_messages/) on the subject) but here’s a brief overview of Mach IPC for this blog post:

1. Mach messages are stored within kernel-managed message queues, represented by a Mach port
2. A process can fetch a message from a given port if it holds the receive right for that port
3. A process can send a message to a given port if it holds a send right to that port

MacOS applications can register a service with the bootstrap server, a special mach port which all processes have a send right to by default. This allows other processes to send a Mach message to the bootstrap server inquiring about a specific service, and the bootstrap server can respond with a send right to that service’s Mach port. MacOS system daemons register Mach services via launchd. You can view their .plist files within the /System/Library/LaunchAgents and /System/Library/LaunchDaemons directories to get an idea of the services registered. For example, the .plist file below highlights a Mach service registered for the Address Book application on MacOS using the identifier com.apple.AddressBook.AssistantService.

<?xmlversion="1.0"encoding="UTF-8"?>

<!DOCTYPEplistPUBLIC"-//Apple//DTDPLIST1.0//EN""http://www.apple.com/DTDs/PropertyList-1.0.dtd">

<plistversion="1.0">

<dict>

<key>POSIXSpawnType</key>

<string>Adaptive</string>

<key>Label</key>

<string>com.apple.AddressBook.AssistantService</string>

<key>MachServices</key>

<dict>

<key>com.apple.AddressBook.AssistantService</key>

<true/>

</dict>

<key>ProgramArguments</key>

<array>

<string>/System/Library/Frameworks/AddressBook.framework/Versions/A/Helpers/ABAssistantService.app/Contents/MacOS/ABAssistantService</string>

</array>

</dict>

</plist>

# Choose a Target

After deciding I wanted to research Mach services, the next question was which service to target. In order for a sandboxed process to send Mach messages to a service, it has to be explicitly allowed. If the process is using Apple’s App Sandbox feature, this is done within a .sb file, written using the [TinyScheme](https://tinyscheme.sourceforge.net/home.html) format. The snippet below shows an excerpt of the sandbox file for a WebKit GPU Process. The allow mach-lookup directive is used to allow a sandboxed process to lookup and send Mach messages to a service.

\# File: /System/Volumes/Preboot/Cryptexes/Incoming/OS/System/Library/Frameworks/WebKit.framework/Versions/A/Resources/com.apple.WebKit.GPUProcess.sb

(with-filter(system-attributeapple-internal)

(allowmach-lookup

(global-name"com.apple.analyticsd")

(global-name"com.apple.diagnosticd")))

(allowmach-lookup

(global-name"com.apple.audio.audiohald")

(global-name"com.apple.CARenderServer")

(global-name"com.apple.fonts")

(global-name"com.apple.PowerManagement.control")

(global-name"com.apple.trustd.agent")

(global-name"com.apple.logd.events"))

This helped me narrow my focus significantly from all MacOS processes, to processes with a sandbox-accessible Mach service:

![A Venn diagram illustrating process types on macOS. The outermost, largest oval represents All MacOS Processes. Within it, a smaller oval represents Processes with a Mach Service. The innermost, smallest oval represents Processes with a Sandbox Allowed Mach Service, indicating a subset of processes with increasing restrictions and specific Mach service permissions.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgKaMJ_s774_image3.png)

In addition to inspecting the sandbox profiles, I used Jonathan Levin’s [sbtool](https://web.archive.org/web/20240519054616/https://newosxbook.com/src.jl?tree%3Dlistings%26file%3D/sbtool.c) utility to test which Mach services could be interacted with for a given process. The tool (which was a bit outdated, but I was able to get it to compile) uses the builtin sandbox\_exec function under the hood to provide a nice list of accessible Mach service identifiers:

❯./sbtool2813mach

com.apple.logd

com.apple.xpc.smd

com.apple.remoted

com.apple.metadata.mds

com.apple.coreduetd

com.apple.apsd

com.apple.coreservices.launchservicesd

com.apple.bsd.dirhelper

com.apple.logind

com.apple.revision

…Truncated…

Ultimately, I chose to take a look at the coreaudiod daemon, and specifically the com.apple.audio.audiohald service for the following reasons:

- It is a complex process
- It allows Mach communications from several impactful applications, including the Safari GPU process
- The Mach service had a large number of message handlers
- The service seemed to allow control and and modification of audio hardware, which would likely require elevated privileges
- The coreaudiod binary and the CoreAudio Framework it heavily uses were both closed source, which would provide a unique reverse engineering challenge

# Create a Fuzzing Harness

Once I chose an attack vector and target, the next step was to create a fuzzing harness capable of sending input through the attack vector (a Mach message) at a proper location within the target.

A coverage-guided fuzzer is a powerful weapon, but only if its energy is focused in the right place—like a magnifying glass concentrating sunlight to start a fire. Without proper focus, the energy dissipates, achieving little impact.

## Determining an Entry Point

Ideally, a fuzzer should perfectly replicate the environment and capabilities available to a potential attacker. However, this isn't always practical. Trade-offs often need to be made, such as accepting a higher rate of false positives for increased performance, simplified instrumentation, or ease of development. Therefore, identifying the “right place” to fuzz is highly dependent on the specific target and research goals.

### Option 1: Interprocess Fuzzing

All Mach messages are sent and received using the mach\_msg API, as shown below. Therefore, I thought the most intuitive way to fuzz coreaudiod‘s Mach message handlers would be to write a fuzzing harness that called the mach\_msg API and allow my fuzzer to modify the message contents to produce crashes. The approach would look something like this:

[![A diagram showing inter-process communication. A "SENDING PROCESS" calls mach_msg API, sending a message via "Mach IPC" to a "Kernel-Managed Message Queue". This queue then forwards the message via "Mach IPC" to a "Mach Message Handler" in the "RECEIVING PROCESS".](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjZpn9_s1200_image17.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjZpn9_s1999_image17.png)

However, this approach had a large downside: since we were sending IPC messages, the fuzzing harness would be in a different process space than the target. This meant code coverage information would need to be shared across a process boundary, which is not supported by most fuzzing tools. Additionally, kernel message queue processing adds a significant performance overhead.

### Option 2: Direct Harness

While requiring a bit more work up front, another option was to write a fuzzing harness that directly loaded and called the Mach message handlers of interest. This would have the massive advantage of putting our fuzzer and instrumentation in the same process as the message handlers, allowing us to more easily obtain code coverage.

[![A diagram illustrating a SINGLE PROCESS communication. It shows Load Library & Call Message Handler communicating via a Fuzzing Harness to a Mach Message Handler all within the same process.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgwheA_s1200_image13.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgwheA_s1999_image13.png)

One notable downside of this fuzzing approach is that it assumes all fuzzer-generated inputs pass the kernel’s Mach message validation layer, which in a real system occurs before a message handler gets called.As we’ll see later, this is not always the case. In my view, however, the pros of fuzzing in the same process space (speed and easy code coverage collection) outweighed the cons of a potential increase in false positives.

The approach would be as follows:

1. Identify a suitable function for processing incoming mach messages
2. Write a fuzzing harness to load the message handling code from coreaudiod
3. Use a fuzzer to generate inputs and call the fuzzing harness
4. Profit, hopefully

## Finding the Mach Messager Handler

To start, I searched for the Mach service identifier, com.apple.audioaudiohald, but found no references to it within the coreaudiod binary. Next, I checked the libraries it loaded using otool. Logically, the CoreAudio framework seemed like a good candidate for housing the code for our message handler.

$ otool -L /usr/sbin/coreaudiod

/usr/sbin/coreaudiod:

        /System/Library/PrivateFrameworks/caulk.framework/Versions/A/caulk (compatibility version 1.0.0, current version 1.0.0)

/System/Library/Frameworks/CoreAudio.framework/Versions/A/CoreAudio (compatibility version 1.0.0, current version 1.0.0)

        /System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation (compatibility version 150.0.0, current version 2602.0.255)

        /usr/lib/libAudioStatistics.dylib (compatibility version 1.0.0, current version 1.0.0, weak)

        /System/Library/Frameworks/Foundation.framework/Versions/C/Foundation (compatibility version 300.0.0, current version 2602.0.255)

        /usr/lib/libobjc.A.dylib (compatibility version 1.0.0, current version 228.0.0)

        /usr/lib/libc++.1.dylib (compatibility version 1.0.0, current version 1700.255.5)

        /usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1345.120.2)

However, I was surprised to find that the path returned by otool did not exist!

$stat/System/Library/Frameworks/CoreAudio.framework/Versions/A/CoreAudio

stat:/System/Library/Frameworks/CoreAudio.framework/Versions/A/CoreAudio:stat:Nosuchfileordirectory

### The Dyld Shared Cache

A bit of research showed me that as of MacOS Big Sur, most framework binaries are not stored on disk but within the [dyld](https://forums.developer.apple.com/forums/thread/692383)[shared cache](https://forums.developer.apple.com/forums/thread/692383), a mechanism for pre-linking libraries to allow applications to run faster. Thankfully, IDA Pro, Binary Ninja, and Ghidra support parsing the dyld shared cache to obtain the libraries stored within. I also used this [helpful tool](https://github.com/keith/dyld-shared-cache-extractor) to successfully extract libraries for additional analysis.

Once I had the CoreAudio Framework within IDA, I quickly found a call to bootstrap\_check\_in with the service identifier passed as an argument, proving the CoreAudio framework binary was responsible for setting up the Mach service I wanted to fuzz. However, it still wasn’t obvious where the message handling code was happening, despite quite a bit of reverse engineering.

![A screenshot of disassembled code. A function macOS_PlatformBehaviors::get_system_port is shown. A call to _bootstrap_check_in is highlighted, along with the string com.apple.audio.audiohald being passed as a service name.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEidfLj_s970_image15.png)

It turns out this is due to the use of the [Mach Interface Generator](https://www.gnu.org/software/hurd/microkernel/mach/mig/gnu_mig.html), (MIG) an Interface Definition Language from Apple that makes it easier to write RPC clients and servers by abstracting away much of the Mach layer. When compiled, MIG message handling code gets bundled into a structure called a subsystem. One can easily grep for these subsystems to find their offsets:

$ nm -m ./System/Library/Frameworks/CoreAudio.framework/Versions/A/CoreAudio \| grep -i subsystem

                 (undefined) external \_CACentralStateDumpRegisterSubsystem (from AudioToolboxCore)

00007ff840470138 (\_\_DATA\_CONST,\_\_const) non-external \_HALC\_HALB\_MIGClient\_subsystem

00007ff840470270 (\_\_DATA\_CONST,\_\_const) non-external \_HALS\_HALB\_MIGServer\_subsystem

Next, I searched in IDA for cross-references to the \_HALS\_HALB\_MIGServer\_subsystem symbol, which identified the MIG server function that parsed incoming Mach messages! The routine is shown below, with the first parameter (the rdi register) being the incoming Mach message and the second (the rsi register) being the message to return to the client. The MIG server function extracted the msgh\_id parameter from the Mach message and used that to index into the MIG subsystem. Then, the necessary function handler was called.

[![A flowchart of disassembled code within HALB_MIGServer_server. Annotations highlight Incoming msg rdi and steps to Get msg ID and Get subsystem offset. This offset is then used to Index into function handler based on msg ID" leading to a Call function block.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEis3Vc_s1200_image5.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEis3Vc_s1266_image5.png)

I further confirmed this by setting an LLDB breakpoint on the coreaudiod process (after [disabling SIP](https://conference.hitb.org/hitbsecconf2021sin/materials/D2T1%2520-%2520Summer%2520of%2520Fuzz%2520-%2520MacOS%2520-%2520Jeremy%2520Brown.pdf#page=11)) for the \_HALB\_MIGServer\_server function. Then, I adjusted the volume on my system, and the breakpoint was hit:

[![A debugger lldb window showing a breakpoint hit in CoreAudio_HALB_MIGServer_server. The process is stopped at the beginning of this function, with the instruction push rbp highlighted. The thread information indicates the queue is com.apple.audio.device.BuiltInSpeakerDevice.event](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhELEO_s1200_image7.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhELEO_s1999_image7.png)

In this example, tracing the message handler called from the MIG subsystem showed the \_XObject\_HasProperty function was called based on the Mach message’s msgh\_id.

[![A debugger lldb window showing two states of a stopped process. The first state shows the process stopped at a call rcx instruction within CoreAudio_HALB_MIGServer_server. After a step into si command, the second state shows the process stopped at the beginning of CoreAudio__XObject_HasProperty, as indicated by the red arrow and highlighted function name.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgnYEZ_s1200_image4.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgnYEZ_s1999_image4.png)

Depending on the msgh\_id, a few dozen message handlers were accessible from the MIG subsystem. They are easily identifiable by the convenient \_\_X prefix to their function names added by MIG.

![A list of function names, likely from a software library or framework, related to object and system context management. Each function name is prefixed with an f icon and highlighted in red, possibly indicating they are of interest for analysis or have been patched. Examples include __XObject_PropertyListener, __XIOContext_PauseIO, __XSystem_CreateIOContext, and __XObject_HasProperty.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhTXFj_s862_image2.png)

The \_HALB\_MIGServer\_server function struck a great balance between getting close to low-level message handling code while still resembling the inputs that a call to mach\_msg would take. I decided this was the place to inject fuzz input into.

## Creating a Basic Fuzzing Harness

After identifying the function I wanted to fuzz, the next step was to write a program to read a file and deliver the file’s contents as input to the target function. This might have been as easy as linking the CoreAudio library with my fuzzing harness and calling the \_HALB\_MIGServer\_server function, but unfortunately the function was not exported.

Instead, I borrowed some logic from [Ivan Fratric](https://x.com/ifsecure) and his [TinyInst](https://github.com/googleprojectzero/TinyInst/) tool (we’ll be talking about it a lot more later) which [returns a provided symbol’s address](https://github.com/googleprojectzero/TinyInst/blob/fb1cceb7ec3c44cb18c4c01685e496777e0bcdc9/macOS/debugger.cpp#L1169) from a library. The code parses the structure of Mach-O binaries, specifically their headers and load commands, to locate and extract symbol information. This made it possible to [resolve and call the target function in my fuzzing harness](https://github.com/googleprojectzero/p0tools/blob/master/CoreAudioFuzz/helpers/initialization.cc), even when it wasn’t exported.

So, the high level function of my harness was as follows:

1. Load the CoreAudio Library
2. Get a function pointer for the target function from the CoreAudio Library
3. Read an input from a file
4. Call the target function with the input

The full implementation of my fuzzing harness can be found [here](https://github.com/googleprojectzero/p0tools/blob/master/CoreAudioFuzz/harness.mm). An example of invoking the harness to send a message from an input file is shown below:

$ ./harness-fcorpora/basic/1-v

\*\*\*\*\*\*\*NEWMESSAGE\*\*\*\*\*\*\*

MessageID:1010000(XSystem\_Open)

\-\-\----MACHMSGHEADER\-\-\----

msg\_bits:2319532353

msg\_size:56

msg\_remote\_port:1094795585

msg\_local\_port:1094795585

msg\_voucher\_port:1094795585

msg\_id:1010000

\-\-\----MACHMSGBODY(32bytes)\-\-\----

0x010x000x000x000x030x300x000x000x410x410x410x410x410x410x110x000x410x410x000x000x000x000x000x000x000x000x000x000x000x000x000x00

\-\-\----MACHMSGTRAILER\-\-\----

msg\_trailer\_type:0

msg\_trailer\_size:32

msg\_seqno:0

msg\_sender:0

\-\-\----MACHMSGTRAILERBODY(32bytes)\-\-\----

0xf50x010x000x000xf50x010x000x000x140x000x000x000xf50x010x000x000x140x000x000x000x7e0x020x000x000xa30x860x010x000x4f0x060x000x00

Processingfunctionresult:1

\*\*\*\*\*\*\*RETURNMESSAGE\*\*\*\*\*\*\*

\-\-\----MACHMSGHEADER\-\-\----

msg\_bits:1

msg\_size:36

msg\_remote\_port:1094795585

msg\_local\_port:0

msg\_voucher\_port:0

msg\_id:1010100

\-\-\----MACHMSGBODY(12bytes)\-\-\----

0x000x000x000x000x010x000x000x000x000x000x000x00

# Harvesting Legitimate Mach Messages

I now had a way to deliver data directly into the MIG subsystem (\_HALB\_MIGServer\_server) I wanted to fuzz. However, I had no idea the specific message size, options, or data the handler was expecting. While a coverage-guided fuzzer will begin to uncover the proper message format over time, it is advantageous to obtain a [seed corpus](https://github.com/google/fuzzing/blob/master/docs/good-fuzz-target.md#seed-corpus) of legitimate inputs when first beginning to fuzz to improve efficiency.

To do this, I used LLDB to set a breakpoint on the MIG subsystem and dump the first argument (containing the incoming Mach message). Then, I played around with the operating system to cause Mach messages to be sent to coreaudiod. The Audio MIDI Setup MacOS application ended up being great for this, as it allows one to create, edit, and delete audio devices.

[![A screenshot of macOS Audio Devices settings. A red arrow points to the "+" button in the bottom left, with a dropdown menu open showing "Create Aggregate Device" highlighted, indicating the action being taken.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh6-HW_s1200_image20.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh6-HW_s1600_image20.png)

# Fuzz and Produce Crashes

Armed with a small seed corpus and an input delivery mechanism, the next step was to configure a fuzzer to use the created fuzzing harness and obtain code coverage. I used the excellent [Jackalope fuzzer](https://github.com/googleprojectzero/Jackalope) built and maintained by Ivan Fratric. I chose Jackalope primarily for its high level of customizability—it allows easy implementation of custom mutators, instrumentation, and sample delivery. Additionally, I appreciated its seamless usage on macOS, particularly its code coverage capabilities powered by [TinyInst](https://github.com/googleprojectzero/TinyInst). In contrast, I tried and failed to collect code coverage using Frida against system daemons on macOS.

I used the following command to start a Jackalope fuzzing run:

$ jackalope-inin/-outout/-deliveryfile-instrument\_moduleCoreAudio-target\_moduleharness-target\_method\_fuzz-nargs1-iterations1000-persist-loop-dump\_coverage-cmp\_coverage-generate\_unwind-nthreads5--./harness-f@@

# Iterate on the Fuzzing Harness

This harness quickly generated many crashes, a sign I was on the right track. However, I quickly learned that initial crashes are often not indicative of a security bug, but of a design bug in the fuzzing harness itself or an invalid assumption.

## Iteration 1: Target Initialization

One of the difficulties with my fuzzing approach was that my target function (the Mach message handler) expected the HAL system to be in a specific state to begin receiving Mach messages. By simply calling the library function with my fuzzing harness, these assumptions were broken.

This caused errors to start popping up. As shown in the diagram below, the harness bypassed much of the bootstrapping functionality the coreaudiod process would normally take care of during startup.

![Two diagrams comparing code execution. The left diagram, labeled "Fuzzer + Harness," shows a single path 1 directly calling "Process Mach Message" within the "CoreAudio Library." The right diagram, labeled "Coreaudiod Native Process," shows multiple steps 1, 2, 3, ..., X before "Process Mach Message" is called in the "CoreAudio Library."](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiZ3Be_s1056_image16.png)

Code coverage, as well as error messages, can be very helpful in helping determine some of the initialization steps a fuzzing harness is neglecting. For example, I noticed my data flow would always fail early in most Mach message handlers, logging the message Error: there is no system.

![A flowchart of disassembled code execution. One path, highlighted with "We always go this way!", leads to a successful HALS_System::GetInstance call. Another path shows an error message "Error: There is no system" after a call to HALS_Object_SetProperty if a different condition is met.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgoV6Z_s1047_image22.png)

It turns out I needed to initialize the HAL System before I could interact correctly with the Mach APIs. In my case, calling the \_AudioHardwareStartServer function [in my fuzzing harness](https://github.com/dillonfranke/breaking-the-sound-barrier/blob/1e221ce5b2b15a9cd56185c42b211a70a0e6d867/harness.mm#L1602) took care of most of the necessary initialization.

## Iteration 2: API Call Chaining

My first crack at a fuzzing harness was cool, but it made a pretty large assumption: all accessible Mach message handlers functioned independently of each other. As I quickly learned, this assumption was incorrect. As I ran the fuzzer, error messages like the following one started popping up:

[![A terminal window showing log output from mach-send. A line is highlighted with a red box and arrow, pointing to the text "Plist: there is no client" associated with a coreaudiod error.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiHtOX_s1200_image19.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiHtOX_s1999_image19.png)

The error seemed to indicate the SetPropertyData Mach handler was expecting a client to be registered via a previous Mach message. Clearly, the Mach handlers I was fuzzing were stateful and depended on each other to function properly. My fuzzing harness would need to take this into consideration in order to have any hope of obtaining good code coverage on the target.

This highlights a common problem in the fuzzing world: most coverage-guided fuzzers accept a single input, (a bunch of bytes) while many things we want to fuzz accept data in a completely different format, such as several arguments of different types, or even several function calls. This [Google writeup](https://github.com/google/fuzzing/blob/master/docs/structure-aware-fuzzing.md) explains the problem well, as does Ned Williamson’s [OffensiveCon Talk from 2019](https://youtu.be/xzG0pLM4Q64).

To get around this limitation, we can use a technique I refer to as API Call Chaining, which considers each fuzz input as a stream that can be read from to craft multiple valid inputs. Thus, each fuzzing iteration would be capable of generating multiple Mach messages. This simple but important insight allows a fuzzer to explore the interdependency of separate function calls using the same code-coverage informed input.

The [FuzzedDataProvider class](https://github.com/llvm/llvm-project/blob/main/compiler-rt/include/fuzzer/FuzzedDataProvider.h), which is part of LibFuzzer but can be included as a header for use with any fuzzing harness, is a great choice for consuming a fuzz sample and transforming it into a more meaningful data type. Consider the following pseudocode:

extern "C"intLLVMFuzzerTestOneInput(const uint8\_t\*data,size\_tsize){

FuzzedDataProviderfuzz\_data(data,size);// Initialize FDP

    while (fuzz\_data.remaining\_bytes()>=MACH\_MSG\_MIN\_SIZE){// Continue until we've consumed all bytes

uint32\_tmsg\_id=fuzz\_data.ConsumeIntegralInRange<uint32\_t>(1010000,1010062);

        switch (msg\_id){

            case '1010000':{

send\_XSystem\_Open\_msg(fuzz\_data);

}

            case '1010001':{

send\_XSystem\_Close\_msg(fuzz\_data);

}

            case '1010002':{

send\_XSystem\_GetObjectInfo\_msg(fuzz\_data);

}

...continued

}

}

}

This code transforms a blob of bytes into a mechanism that can repeatedly call APIs with fuzz data in a deterministic manner. What’s more, a coverage-guided fuzzer will be able to explore and identify a series of API calls that improves code coverage. From the fuzzer’s perspective, it is simply modifying an array of bytes, blissfully unaware of the additional complexity happening under the hood.

For example, my fuzzer quickly identified that most interactions with the audiohald service required a call to the \_XSystem\_Open message handler to register a client before most APIs could be called. The inputs the fuzzer saved to its corpus naturally reflected this fact over time.

## Iteration 3: Mocking Out Buggy/Unneeded Functionality

Sometimes coverage plateaus, and a fuzzer struggles to explore new code paths. For example, say we’re fuzzing an HTTP server and it keeps getting stuck because it’s trying to read and parse configuration files on startup. If our focus was on the server’s request parsing and response logic, we might choose to mock out the functionality we don’t care about in order to focus the fuzzer’s code coverage exploration elsewhere.

In my fuzzing harness’ case, calling the initialization routines was causing my harness to try to register the com.apple.audio.audiohald Mach service with the bootstrap server, which was throwing an error because it was already registered by launchd. Since my harness didn’t need to register the Mach service in order to inject messages, (remember, our harness calls the MIG subsystem directly) I decided to mock out the functionality.

When dealing with pure C functions, [function interposing](http://toves.freeshell.org/interpose/) can be used to easily modify a function’s behavior. In the example below, I declare a new version of the bootstrap\_check\_in function that just says returns KERN\_SUCCESS, effectively nopping it out while telling the caller that it was successful.

#include<mach/mach.h>

#include<stdarg.h>

// Forward declaration for bootstrap\_check\_in

kern\_return\_tbootstrap\_check\_in(mach\_port\_tbootstrap\_port,constchar\*service\_name,mach\_port\_t\*service\_port);

// Custom implementation of bootstrap\_check\_in

kern\_return\_tcustom\_bootstrap\_check\_in(mach\_port\_tbootstrap\_port,constchar\*service\_name,mach\_port\_t\*service\_port){

// Ensure service\_port is non-null and set it to a non-zero value

if(service\_port){

\*service\_port=1;// Set to a non-zero value

}

returnKERN\_SUCCESS;// Return 0 (KERN\_SUCCESS)

}

// Interposing array for bootstrap\_check\_in

\_\_attribute\_\_((used))staticstruct{

constvoid\*replacement;

constvoid\*replacee;

}interposers\[\]\_\_attribute\_\_((section("\_\_DATA,\_\_interpose")))={

{(constvoid\*)custom\_bootstrap\_check\_in,(constvoid\*)bootstrap\_check\_in}

};

In the case of C++ functions, I used TinyInst’s [Hook API](https://github.com/googleprojectzero/TinyInst/blob/master/hook.md) to modify problematic functionality. In one specific scenario, my fuzzer was crashing the target constantly because the CFRelease function was being called with a NULL pointer. Some further analysis told me that this was a non-security relevant bug where a user’s input, which was assumed to contain a valid plist object, was not properly validated. If the plist object was invalid or NULL, a downstream function call would contain NULL, and an abort would occur.

[![A flowchart of disassembled code for a function HALS_SettingsManager::_WriteSetting. Text annotations highlight No Check for NULL Property List before a call to _CFPropertyListCreateDeepCopy. Another annotation points to a jmp _CFRelease instruction, labeled CFRelease" indicating a potential use-after-free or similar memory corruption vulnerability.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEizEjS_s1200_image9.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEizEjS_s1266_image9.png)

So, I wrote the following [TinyInst hook](https://github.com/googleprojectzero/TinyInst/blob/master/hook.md), which checked whether the plist object passed into the function was NULL. If so, my hook returned the function call early, bypassing the buggy code.

void HALSWriteSettingHook::OnFunctionEntered() {

    printf("HALS\_SettingsManager::\_WriteSetting Entered\\n");

if (!GetRegister(RDX)) {

        printf("NULL plist passed as argument, returning to prevent NULL CFRelease\\n");

        printf("Current $RSP: %p\\n", GetRegister(RSP));

void \*return\_address;

        RemoteRead((void\*)GetRegister(RSP), &return\_address, sizeof(void \*));

        printf("Current return address: %p\\n", GetReturnAddress());

        printf("Current $RIP: %p\\n", GetRegister(RIP));

        SetRegister(RAX, 0);

        SetRegister(RIP, GetReturnAddress());

        printf("$RIP register is now: %p\\n", GetRegister(ARCH\_PC));

        SetRegister(RSP, GetRegister(RSP) + 8); // Simulate a ret instruction

        printf("$RSP is now: %p\\n", GetRegister(RSP));

    }

}

Next, I modified Jackalope to use my instrumentation using the [CreateInstrumentation](https://github.com/googleprojectzero/Jackalope/blob/bd461f4adfc3e4e1cb14516661e57a202071ac2d/fuzzer.h#L163) API. That way, my hook was applied during each fuzzing iteration, and the annoying NULLCFRelease calls stopped happening. The output below shows the hook preventing a crash from a NULLplist object passed the troublesome API:

InstrumentedmoduleCoreAudio,codesize:7516156

Hookingfunction\_\_ZN11HALS\_System13\_WriteSettingEP11HALS\_ClientPK10\_\_CFStringPKvinmoduleCoreAudio

HALS\_SettingsManager::\_WriteSettingEntered

NULLplistpassedasargument,returningtopreventNULLCFRelease

Current$RSP:0x7ff7bf83b358

Currentreturnaddress:0x7ff8451e7430

Current$RIP:0x7ff84533a675

$RIPregisterisnow:0x7ff8451e7430

$RSPisnow:0x7ff7bf83b360

Totalexecs:6230

Uniquesamples:184(0discarded)

Crashes:3(2unique)

Hangs:0

Offsets:13550

Execs/s:134

The code to reproduce and build this fuzzer with custom instrumentation can be found here: [https://github.com/googleprojectzero/p0tools/tree/master/CoreAudioFuzz/jackalope-modifications](https://github.com/googleprojectzero/p0tools/tree/master/CoreAudioFuzz/jackalope-modifications)

## Iteration 4: Improving Sample Structure

The great thing about a fuzzing-centric auditing technique is that it highlights knowledge gaps in the code you are auditing. As you address these gaps, you gain a deeper understanding of the structure and constraints of the inputs that your fuzzing harness should generate. These insights enable you to refine your harness to produce more targeted inputs, effectively penetrating deeper code paths and improving overall code coverage. The following subsections highlight examples of how I identified and implemented opportunities to iterate on my fuzzing harness, significantly enhancing its efficiency and effectiveness.

### Message Handler Syntax Checks

Code coverage results from fuzzing runs are incredibly telling. I noticed that after running my fuzzer for a few days, it was having trouble exploring past the beginning of most of the Mach message handlers. One simple example is shown below, (explored basic blocks are highlighted in blue) where several comparisons were not being passed , causing the function to error out early on. Here, the rdi register is the incoming Mach message we sent to the handler.

[![A flowchart of disassembled code for a function _XIOContext_SetClientControlPort. Several conditional branches are shown, labeled Error Out" leading away from the main execution path. The Rest of Functionality block at the bottom includes a call to HALS_IOContext_SetClientControlPort.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi5jyT_s1200_image6.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi5jyT_s1520_image6.png)

The comparisons were checking that the Mach message was well formatted, with a message length set to 0x34 and various options set within the message. If it wasn’t, it was discarded.

With this in mind, I modified my fuzzing harness to set the fields in the Mach messages I sent to the \_XIOContext\_SetClientControlPort handler such that they passed these conditions. The fuzzer could modify other pieces of the message as it pleased, but since these aspects needed to conform to strict guidelines, I simply hardcoded them.

These small modifications were the beginning of an input structure I was building for my target. The efficiency of my fuzzing improved astronomically after adding these guidelines to the fuzzer \- my code coverage increased by 2000% shortly thereafter.

### Out-of-Line (OOL) Message Data

I noticed my fuzzing setup started generating tons of crashes from a call to mig\_deallocate, which [frees a given address](https://github.com/darwin-on-arm/xnu/blob/707bfdc4e9a46e3612e53994fffc64542d3f7e72/osfmk/mach/mig.h#L291). At first, I thought I had found an interesting bug, since I could control the address passed to mig\_deallocate:

I quickly learned, however, that Mach messages can contain various types of [Out-of-line (OOL) data](https://dmcyk.xyz/post/xnu_ipc_iii_ool_data/). This allows a client to allocate a memory region and place a pointer to it within the Mach message, which will be processed and, in some cases, freed by the message handler. When sending a Mach message with the mach\_msg API, the XNU kernel will validate that the memory pointed to by OOL descriptors is properly owned and accessible by the client process.

I hadn’t found a vulnerability; my fuzzing harness was simply attached to the target at a point downstream which bypassed the normal memory checks that would have been performed by the kernel. To remedy this, I [modified my fuzzing harness](https://github.com/googleprojectzero/p0tools/blob/b9936f89d0fbde341df46f7d215c1e9c21381d9e/CoreAudioFuzz/harness.mm#L381)to support allocating space for OOL data and passing the valid memory address within the Mach messages I fuzzed.

# The Vulnerability

After many fuzzing harness iterations, lldb “next instruction” commands, and hours spent overheating my MacBook Pro, I had finally begun to acquire an understanding of the CoreAudio framework and generate some meaningful crashes.

But first, some background knowledge.

## The Hardware Abstraction Layer (HAL)

The com.apple.audio.audiohald Mach service exposes an interface known as the Hardware Abstraction Layer (HAL). The HAL allows clients to interact with audio devices, plugins, and settings on the operating system, represented in the coreaudiod process as C++ objects of type HALS\_Object.

In order to interact with the HAL, a client must first register itself. There are a few ways to do this, but the simplest is using the \_XSystem\_Open Mach API. Calling this API will invoke the HALS\_System::AddClient method, which uses the Mach message’s [audit token](https://knight.sc/reverse%20engineering/2020/03/20/audit-tokens-explained.html) to create a client (clnt) HALS\_Object to map subsequent requests to that client. The code block below shows an IDA decompilation snippet of the creation of a clnt object.

v85\[0\]=v5!=0;

v28=v83\[0\];

v29='clnt';

HALS\_Object::HALS\_Object((HALS\_Object\*)v13,'clnt',0,(\_\_int64)v83\[0\],v30);

\*(\_QWORD\*)v13=&unk\_7FF850E56640;

\*(\_OWORD\*)(v13+72)=0LL;

\*(\_OWORD\*)(v13+88)=0LL;

\*(\_DWORD\*)(v13+104)=1065353216;

Stepping into the HALS\_Object constructor, a mutex is acquired before getting the next available object ID before making a call to HALS\_ObjectMap::MapObject.

void\_\_fastcallHALS\_Object::HALS\_Object(HALS\_Object\*this,\_BOOL4a2,unsignedinta3,\_\_int64a4,HALS\_Object\*a5)

{

unsignedintv5;// r12d

HALB\_Mutex::Locker\*v6;// r15

unsignedintv7;// ebx

HALS\_Object\*v8;// rdx

intv9;// eax

v5=a3;

\*(\_QWORD\*)this=&unk\_7FF850E7C200;

\*((\_DWORD\*)this+2)=0;

\*((\_DWORD\*)this+3)=HALB\_MachPort::CreatePort(0LL,a2,a3);

\*((\_WORD\*)this+8)=257;

\*((\_WORD\*)this+10)=1;

pthread\_once(&HALS\_ObjectMap::sObjectInfoListInitialized,HALS\_ObjectMap::Initialize);

v6=HALS\_ObjectMap::sObjectInfoListMutex;

HALB\_Mutex::Lock(HALS\_ObjectMap::sObjectInfoListMutex);

v7=(unsignedint)HALS\_ObjectMap::sNextObjectID;

LODWORD(HALS\_ObjectMap::sNextObjectID)=(\_DWORD)HALS\_ObjectMap::sNextObjectID+1;

HALB\_Mutex::Locker::~Locker(v6);

\*((\_DWORD\*)this+6)=v7;

\*((\_DWORD\*)this+7)=a2;

if(!v5)

v5=a2;

\*((\_DWORD\*)this+8)=v5;

if(a4)

v9=\*(\_DWORD\*)(a4+24);

else

v9=0;

\*((\_DWORD\*)this+9)=v9;

\*((\_QWORD\*)this+5)=&stru\_7FF850E86420;

\*((\_BYTE\*)this+48)=0;

\*((\_DWORD\*)this+13)=0;

HALS\_ObjectMap::MapObject((HALS\_ObjectMap\*)v7,(\_\_int64)this,v8);

}

The HALS\_ObjectMap::MapObject function adds the freshly allocated object to a linked list stored on the heap. I wrote a program using the TinyInst Hook API that iterates through each object in the list and dumps its raw contents:

[![A terminal window displaying output from a command likely related to debugging or instrumenting CoreAudio. It shows messages like Instrumented module CoreAudio, OnModuleInstrumented: Looks like we made it" and an OBJECT DUMP section with memory addresses and hexadecimal/ASCII data.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj4mr2_s1200_image10.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj4mr2_s1999_image10.png)

To modify an existing HALS\_Object, most of the HAL Mach message handlers use the HALS\_ObjectMap::CopyObjectByObjectID function, which accepts an integer ID (parsed from the Mach message’s body) for a given HALS\_Object, which it then looks up in the Object Map and returns a pointer to the object.

For example, here’s a small snippet of the ​\_XSystem\_GetObjectInfo Mach message handler, which calls the HALS\_ObjectMap::CopyObjectByObjectID function before accessing information about the object and returning it.

HALS\_Client::EvaluateSandboxAllowsMicAccess(v5);

v7=(HALS\_ObjectMap\*)HALS\_ObjectMap::CopyObjectByObjectID((HALS\_ObjectMap\*)v3);

v8=v7;

if(!v7)

{

v13=\_\_cxa\_allocate\_exception(0x10uLL);

\*(\_QWORD\*)v13=&unk\_7FF850E85518;

v13\[2\]=560947818;

\_\_cxa\_throw(v13,(structtype\_info\*)&\`typeinfofor'CAException,CAException::~CAException);

}

## An Intriguing Crash

Whenever my fuzzer produced a crash, I always took the time to fully understand the crash’s root cause. Often, the crashes were not security relevant, (i.e. a NULL dereference) but fully understanding the reason behind the crash helped me understand the target better and invalid assumptions I was making with my fuzzing harness. Eventually, when I did identify security relevant crashes, I had a good understanding of the context surrounding them.

The first indication from my fuzzer that a vulnerability might exist was a memory access violation during an indirect call instruction, where the target address was calculated using an index into the rax register. As shown in the following backtrace, the crash occurred shallowly within the \_XIOContext\_Fetch\_Workgroup\_Port Mach message handler.

[![A debugger lldb output showing a crash in CoreAudio. The stop reason is EXC_BAD_ACCESS code=EXC_I386_GPFLT. The crashing instruction is a call qword ptr rax + 0x168 within CoreAudio_XIOContext_Fetch_Workgroup_Port. A backtrace bt shows the call stack leading to the crash.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjubSB_s1200_image8.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjubSB_s1999_image8.png)

Further investigating the context of the crash in IDA, I noticed that the rax register triggering the invalid memory access was directly derived from a call to the HALS\_ObjectMap::CopyObjectByObjectID function.

[![A flowchart of disassembled code showing execution paths. One block includes calls to HALS_Client::EvaluateSandboxAllowsMicAccess and HALS_ObjectMap::CopyObjectByID. Subsequent blocks show calls to HALS_ObjectMap::ReleaseObject if certain conditions are met or branch to a different location loc_7FF813A5A928.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjKOjl_s1200_image11.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjKOjl_s1308_image11.png)

Specifically, it attempted the following:

1. Fetch a HALS\_Object from the Object Map based on an ID provided in the Mach message
2. Dereference the address a1 at offset 0x68 of the HALS\_Object
3. Dereference the address a2 at offset 0x0 of a1
4. Call the function pointer at offset 0x168 of a2

## What Went Wrong?

The operations leading to the crash indicated that at offset 0x68 of the  HALS\_Object it fetched, the code expected a pointer to an object with a vtable. The code would then look up a function within the vtable, which would presumably retrieve the object’s “workgroup port.”

When the fetched object was of type ioct, (IOContext) everything functioned as normal. However, the test input my fuzzer generated was causing the function to fetch a HALS\_Object of a different type, which led to an invalid function call. The following diagram shows how an attacker able to influence the pointer at offset 0x68 of a HALS\_Object might hijack control flow.

[![A diagram illustrating a vtable exploit. It shows Expected ioct Object and Expected 2nd Object with their vtables pointing to legitimate functions. It contrasts this with an Actual Object where Attacker-Controlled Memory contains a void fake_vtable that redirects a getPort call, via a Malicious vtable containing void doEvil, ultimately leading to a CALL doEvil instead of the expected function.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgX8Qy_s1200_image14.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgX8Qy_s1999_image14.png)

This vulnerability class is referred to as a type confusion, where the vulnerable code makes the assumption that a retrieved object or struct is a specific type, but it is possible to provide a different one. The object’s memory layout might be completely different, meaning memory accesses and vtable lookups might occur in the wrong place, or even out of bounds. Type confusion vulnerabilities can be extremely powerful due to their ability to form [reliable exploits](https://projectzero.google/2015/06/what-is-good-memory-corruption.html).

### Affected Functions

The \_XIOContext\_Fetch\_Workgroup\_Port Mach message handler wasn’t the only function that assumed it was dealing with an ioct object without checking the type. The table below shows several other message handlers that suffered from the same issue:

|     |     |
| --- | --- |
| Mach Message Handler | Affected Routine |
| \_XIOContext\_Fetch\_Workgroup\_Port | \_XIOContext\_Fetch\_Workgroup\_Port |
| \_XIOContext\_Start | \_\_\_ZNK14HALS\_IOContext22HasEnabledInputStreamsEv\_block\_invoke |
| \_XIOContext\_StartAtTime | \_\_\_ZNK14HALS\_IOContext16GetNumberStreamsEb\_block\_invoke |
| \_XIOContext\_Start\_With\_WorkInterval | \_\_\_ZNK14HALS\_IOContext22HasEnabledInputStreamsEv\_block\_invoke |
| \_XIOContext\_SetClientControlPort | \_XIOContext\_SetClientControlPort |
| \_XIOContext\_Stop | \_XIOContext\_Stop |

Apple did perform proper type checking on some of the Mach message handlers. For example, the \_XIOContent\_PauseIO message handler, shown below, calls a function that checks whether the fetched object is of type ioct before using it. It is not clear why these checks were implemented in certain areas, but not others.

![A snippet of disassembled code. Key instructions include calls to HALC_ProxyObjectMap_CopyObjectByID, HALB_Info::IsStandardClass, and HALC_ProxyObjectMap::RetainObject. An 'ioct' string is being compared with a memory location.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEidP9l_s1046_image18.png)

The impact of this vulnerability can range from an information leak to control flow hijacking. In this case, since the vulnerable code is performing a function call, an attacker could potentially control the data at the offset read during the type confusion, allowing them to control the function pointer and redirect execution. Alternatively, if the attacker can provide an object smaller than 0x68 bytes, an out-of-bounds read would be possible, paving the way for further exploitation opportunities such as memory corruption or arbitrary code execution.

## Creating a Proof of Concept

Because my fuzzing harness was connected downstream in the Mach message handling process, it was important to build an end-to-end proof-of-concept that used the mach\_msg API to send a Mach message to the vulnerable message handler within coreaudiod. Otherwise, we might have triggered a false positive as we did in the case of the mig\_deallocate crash where we thought we had a bug, but were actually just bypassing security checks.

In this case, however, the bug was triggerable using the mach\_msg API, making it a legitimate opportunity for use as a sandbox escape. The proof-of-concept code I put together for triggering this issue on MacOS Sequoia 15.0.1 can be found [here](https://github.com/googleprojectzero/p0tools/blob/master/CoreAudioFuzz/cve-2024-54529-poc-macos-sequoia-15.0.1.c).

It’s worth noting that code running on Apple Silicon uses [Pointer Authentication Codes (PACs)](https://support.apple.com/guide/security/operating-system-integrity-sec8b776536b/1/web/1#sec0167b469d) , which could make exploitation more difficult. In order to exploit this bug through an invalid vtable call, an attacker would need the ability to sign pointers, which would be possible if the attacker gained native code execution in an Apple-signed process. However, I only analyzed and tested this issue on x86-64 versions of MacOS.

## How Apple Fixed the Issue

I reported this type confusion vulnerability to Apple on October 9, 2024. It was fixed on December 11, 2024, assigned [CVE-2024-54529](https://nvd.nist.gov/vuln/detail/CVE-2024-54529), and a patch was introduced in MacOS [Sequoia 15.2](https://support.apple.com/en-us/121839), [Sonoma 14.7.2](https://support.apple.com/en-us/121840), and [Ventura 13.7.2](https://support.apple.com/en-us/121842). Interestingly, Apple mentions that the vulnerability allowed for code execution with kernel privileges. That part interested me, since as far as I could tell the execution was only possible as the \_coreaudiod group, which was not equivalent to kernel privileges.

![A screenshot of a security advisory for an Audio vulnerability in macOS Sonoma. The impact states An app may be able to execute arbitrary code with kernel privileges. The description notes A logic issue was addressed with improved checks" and credits CVE-2024-54529 to Dillon Franke working with Google Project Zero.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgdEC2_s1186_image12.png)

Apple’s fix was simple: since each HALS Object contains information about its type, the patch adds a check within the affected functions to ensure the fetched object is of type ioct before dereferencing the object and performing a function call.

[![A snippet of disassembled code with annotations. Several cmp compare instructions are highlighted with Type Check pointing to comparisons with the string ioct. Further down, a call qword ptr rax+158h instruction is highlighted with Object dereference/function call, indicating a potential point of interest for a vulnerability if the object or function pointer can be controlled.](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh2CtO_s1200_image1.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh2CtO_s1999_image1.png)

You might have noticed how the offset derefenced within the HALS Object is 0x70 in the updated version, but was 0x68 in the vulnerable version. Often, such struct modifications are not security relevant, but will differ based on other bug fixes or added features.

# Recommendations

To prevent similar type confusion vulnerabilities in the future, Apple should consider modifying the CopyObjectByObjectID function (or any others that make assumptions about an object’s type) to include a type check. This could be achieved by passing the expected object type as an argument and verifying the type of the fetched object before returning it. This approach is similar to how [deserialization functions](https://www.newtonsoft.com/json/help/html/M_Newtonsoft_Json_JsonConvert_DeserializeObject__1.htm) often include a template parameter to ensure type safety.

# Conclusion

This blog post described my journey into the world of MacOS vulnerability research and fuzzing. I hope I have shown how a knowledge-driven fuzzing approach can allow rapid prototyping and iteration, a deep understanding of the target, and high impact bugs.

In my next post, I will perform a detailed walkthrough of my experience attempting to exploit CVE-2024-54529.