---
source: p0
source_url: https://projectzero.google/2018/12/adventures-in-video-conferencing-part-4.html
title: "Adventures in Video Conferencing Part 4: What Didn't Work Out with WhatsApp - Project Zero"
description: "Posted by Natalie Silvanovich, Project ZeroNot every attempt to find bugs is successful. When loo..."
---

Posted by Natalie Silvanovich, Project Zero

Not every attempt to find bugs is successful. When looking at WhatsApp, we spent a lot of time reviewing call signalling hoping to find a remote, interaction-less vulnerability. No such bugs were found. We are sharing our work with the hopes of saving other researchers the time it took to go down this very long road. Or maybe it will give others ideas for vulnerabilities we didn’t find.

As discussed in Part 1, signalling is the process through which video conferencing peers initiate a call. Usually, at least part of signalling occurs before the receiving peer answers the call. This means that if there is a vulnerability in the code that processes incoming signals before the call is answered, it does not require any user interaction.

WhatsApp implements signalling using a series of WhatsApp messages. Opening libwhatsapp.so in IDA, there are several native calls that handle incoming signalling messages.

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallOffer

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallOfferAck

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallGroupInfo

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallRekeyRequest

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallFlowControl

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallOfferReceipt

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallAcceptReceipt

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallOfferAccept

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallOfferPreAccept

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallVideoChanged

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallVideoChangedAck

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallOfferReject

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallTerminate

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallTransport

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallRelayLatency

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallRelayElection

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallInterrupted

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallMuted

Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleWebClientMessage

Using apktool to extract the WhatsApp APK, it appears these natives are called from a loop in the com.whatsapp.voipcalling.Voip class. Looking at the smali, it looks like signalling messages are sent as WhatsApp messages via the WhatsApp server, and this loop handles the incoming messages.

Immediately, I noticed that there was a peer-to-peer encrypted portion of the message (the rest of the message is only encrypted peer-to-server). I thought this had the highest potential of reaching bugs, as the server would not be able to sanitize the data. In order to be able to read and alter encrypted packets, I set up a remote server with a python script that opens a socket. Whenever this socket receives data, the data is displayed on the screen, and I have the option of either sending the unaltered packet or altering the packet before it is sent. I then looked for the point in the WhatsApp smali where messages are peer-to-peer encrypted.

Since WhatsApp uses libsignal for peer-to-peer encryption, I was able to find where messages are encrypted by matching log entries. I then added smali code that sends a packet with the bytes of the message to the server I set up, and then replaces it with the bytes the server returns (changing the size of the byte array if necessary). This allowed me to view and alter the peer-to-peer encrypted message. Making a call using this modified APK, I discovered that the peer-to-peer message was always exactly 24 bytes long, and appeared to be random. I suspected that this was the encryption key used by the call, and confirmed this by looking at the smali.

A single encryption key doesn’t have a lot of potential for malformed data to lead to bugs (I tried lengthening and shortening it to be safe, but got nothing but unexploitable null pointer issues), so I moved on to looking at the peer-to-server encrypted messages. Looking at the Voip loop in smali, it looked like the general flow is that the device receives an incoming message, it is deserialized and if it is of the right type, it is forwarded to the messaging loop. Then certain properties are read from the message, and it is forwarded to a processing function based on its type. Then the processing function reads even more properties, and calls one of the above native methods with the properties as its parameters. Most of these functions have more than 20 parameters.

Many of these functions perform logging when they are called, so by making a test call, I could figure out which functions get called before a call is picked up. It turns out that during a normal incoming call, the device only receives an offer and calls Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallOffer, and then spawns the incoming call screen in WhatsApp. All the other signal types are not used until the call is picked up.

An immediate question I had was whether other signal types are processed if they are received before a call is picked up. Just because the initiating device never sends these signal types before the call is picked up doesn’t mean the receiving device wouldn’t process them if it received them.

Looking through the APK smali, I found the class com.whatsapp.voipcalling.VoiceService$DefaultSignalingCallback that has several methods like sendOffer and sendAccept that appeared to send the messages that are processed by these native calls. I changed sendOffer to call other send methods, like sendAccept instead of its normal messaging functionality. Trying this, I discovered that the Voip loop will process any signal type regardless of whether the call has been answered. The native methods will then parse the parameters, process them and put the results in a buffer, and then call a single method to process the buffer. It is only at that point processing will stop if the message is of the wrong type.

I then reviewed all of the above methods in IDA. The code was very conservatively written, and most needed checks were performed. However, there were a few areas that potentially had bugs that I wanted to investigate more. I decided that changing the parameters to calls in the com.whatsapp.voipcalling.VoiceService$DefaultSignalingCallback was too slow to test the number of cases I wanted to test, and went looking for another way to alter the messages.

Ideally, I wanted a way to pass peer-to-server encrypted messages to my server before they were sent, so I could view and alter them. I went through the WhatsApp APK smali looking for a point after serialization but before encryption where I could add my smali function that sends and alters the packets. This was fairly difficult and time consuming, and I eventually put my smali in every method that wrote to a non-file ByteArrayOutputStream in the com.whatsapp.protocol and com.whatsapp.messaging packages (about 10 total) and looked for where it got called. I figured out where it got called, and fixed the class so that anywhere a byte array was written out from a stream, it got sent to my server, and removed the other calls. (If you’re following along at home, the smali file I changed included the string “Double byte dictionary token out of range”, and the two methods I changed contained calls to toByteArray, and ended with invoking a protocol interface.) Looking at what got sent to my server, it seemed like a reasonably comprehensive collection of WhatsApp messages, and the signalling messages contained what I thought they would.

WhatsApp messages are in a compressed XMPP format. A lot of parsers have been written for reverse engineering this protocol, but I found the [whatsapp-reveng](https://github.com/sigalor/whatsapp-web-reveng/tree/master/backend) parser worked the best. I did have to replace the tokens in [whatsapp\_defines.py](https://github.com/sigalor/whatsapp-web-reveng/blob/master/backend/whatsapp_defines.py) with a list extracted from the APK for it to work correctly though. This made it easier to figure out what was in each packet sent to the server.

Playing with this a bit, I discovered that there are three types of checks in WhatsApp signalling messages. First, the server validates and modifies incoming signalling messages. Secondly, the messages are deserialized, and this can cause errors if the format is incorrect, and generally limits the contents of the Java message object that is passed on. Finally, the native methods perform checks on their parameters.

These additional checks prevented several of the areas I thought were problems from actually being problems. For example, there is a function called by Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallOffer that takes in an array of byte arrays, an array of integers and an array of booleans. It uses these values to construct candidates for the call. It checks that the array of byte arrays and the array of integers are of the same length before it loops through them, using values from each, but it does not perform the same check on the boolean array. I thought that this could go out of bounds, but it turns out that the integer and booleans are serialized as a vector of <int,bool> pairs, and the arrays are then copied from the vector, so it is not actually possible to send arrays with different lengths.

One area of the signalling messages that looked especially concerning was the voip\_options field of the message. This field is never sent from the sending device, but is added to the message by the server before it is forwarded to the receiving device. It is a buffer in JSON format that is processed by the receiving device and contains dozens of configuration parameters.

|     |
| --- |
| {"aec":{"offset":"0","mode":"2","echo\_detector\_mode":"4","echo\_detector\_impl":"2","ec\_threshold":"50","ec\_off\_threshold":"40","disable\_agc":"1","algorithm":{"use\_audio\_packet\_rate":"1","delay\_based\_bwe\_trendline\_filter\_enabled":"1","delay\_based\_bwe\_bitrate\_estimator\_enabled":"1","bwe\_impl":"5"},"aecm\_adapt\_step\_size":"2"},"agc":{"mode":"0","limiterenable":"1","compressiongain":"9","targetlevel":"1"},"bwe":{"use\_audio\_packet\_rate":"1","delay\_based\_bwe\_trendline\_filter\_enabled":"1","delay\_based\_bwe\_bitrate\_estimator\_enabled":"1","bwe\_impl":"5"},"encode":{"complexity":"5","cbr":"0"},"init\_bwe":{"use\_local\_probing\_rx\_bitrate":"1","test\_flags":"982188032","max\_tx\_rott\_based\_bitrate":"128000","max\_bytes":"8000","max\_bitrate":"350000"},"ns":{"mode":"1"},"options":{"connecting\_tone\_desc": "test","video\_codec\_priority":"2","transport\_stats\_p2p\_threshold":"0.5","spam\_call\_threshold\_seconds":"55","mtu\_size":"1200","media\_pipeline\_setup\_wait\_threshold\_in\_msec":"1500","low\_battery\_notify\_threshold":"5","ip\_config":"1","enc\_fps\_over\_capture\_fps\_threshold":"1","enable\_ssrc\_demux":"1","enable\_preaccept\_received\_update":"1","enable\_periodical\_aud\_rr\_processing":"1","enable\_new\_transport\_stats":"1","enable\_group\_call":"1","enable\_camera\_abtest\_texture\_preview":"1","enable\_audio\_video\_switch":"1","caller\_end\_call\_threshold":"1500","call\_start\_delay":"1200","audio\_encode\_offload":"1","android\_call\_connected\_toast":"1"} |

Sample voip\_options (truncated)

If a peer could send a voip\_options parameter to another peer, it would open up a lot of attack surface, including a JSON parser and the processing of these parameters. Since this parameter almost always appears in an offer, I tried modifying an offer to contain one, but the offer was rejected by the WhatsApp server with error 403. Looking at the binary, there were three other signal types in the incoming call flow that could accept a voip\_options parameter. Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallOfferAccept and Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallVideoChanged were accepted by the server if a voip\_options parameter was included, but it was stripped before the message was sent to the peer. However, if a voip\_options parameter was attached to a Java\_com\_whatsapp\_voipcalling\_Voip\_nativeHandleCallGroupInfo message, it would be forwarded to the peer device. I confirmed this by sending malformed JSON looking at the log of the receiving device for an error.

The voip\_options parameter is processed by WhatsApp in three stages. First, the JSON is parsed into a tree. Then the tree is transformed to a map, so JSON object properties can be looked up efficiently even though there are dozens of them. Finally, WhatsApp goes through the map, looking for specific parameters and processes them, usually copying them to an area in memory where they will set a value relevant to the call being made.

Starting off with the JSON parser, it was clearly the PJSIP JSON parser. I compiled the code and fuzzed it, and only found one minor out-of-bounds read issue.

I then looked at the conversion of the JSON tree output from the parser into the map. The map is a very efficient structure. It is a hash map that uses FarmHash as its hashing algorithm, and it is designed so that the entire map is stored in a single slab of memory, even if the JSON objects are deeply nested. I looked at many open source projects that contained similar structures, but could not find one that looked similar. I looked through the creation of this structure in great detail, looking especially for type confusion bugs as well as errors when the memory slab is expanded, but did not find any issues.

I also looked at the functions that go through the map and handle specific parameters. These functions are extremely long, and I suspect they are generated using a code generation tool such as bison. They mostly copy parameters into static areas of memory, at which point they become difficult to trace. I did not find any bugs in this area either. Other than going through parameter names and looking for value that seemed likely to cause problems, I did not do any analysis of how the values fetched from JSON are actually used. One parameter that seemed especially promising was an A/B test parameter called setup\_video\_stream\_before\_accept. I hoped that setting this would allow the device to accept RTP before the call is answered, which would make RTP bugs interaction-less, but I was unable to get this to work.

In the process of looking at this code, it became difficult to verify its functionality without the ability to debug it. Since WhatsApp ships an x86 library for Android, I wondered if it would be possible to run the JSON parser on Linux.

Tavis Ormandy created a tool that can load the libwhatsapp.so library on Linux and run native functions, so long as they do not have a dependency on the JVM. It works by patching the .dynamic ELF section to remove unnecessary dependencies by replacing DT\_NEEDED tags with DT\_DEBUG tags. We also needed to remove constructors and deconstructors by changing the DT\_FINI\_ARRAYSZ and DT\_INIT\_ARRAYSZ to zero. With these changs in place, we could load the library using dlopen() and use dlsym() and dlclose() as normal.

Using this tool, I was able to look at the JSON parsing in more detail. I also set up distributed fuzzing of the JSON binary. Unfortunately, it did not uncover any bugs either.

Overall, WhatsApp signalling seemed like a promising attack surface, but we did not find any vulnerabilities in it. There were two areas where we were able to extend the attack surface beyond what is used in the basic call flow. First, it was possible to send signalling messages that should only be sent after a call is answered before the call is answered, and they were processed by the receiving device. Second, it was possible for a peer to send voip\_options JSON to another device. WhatsApp could reduce the attack surface of signalling by removing these capabilities.

I made these suggestions to WhatsApp, and they responded that they were already aware of the first issue as well as variants of the second issue. They said they were in the process of limiting what signalling messages can be processed by the device before a call is answered. They had already fixed other issues where a peer can send voip\_options JSON to another peer, and fixed the method I reported as well. They said they are also considering adding cryptographic signing to the voip\_options parameter so a device can verify it came from the server to further avoid issues like this. We appreciate their quick resolution of the voip\_options issue and strong interest in implementing defense-in-depth measures.

In Part 5, we will discuss the conclusions of our research and make recommendations for better securing video conferencing.