---
source: p0
source_url: https://projectzero.google/2025/09/pointer-leaks-through-pointer-keyed.html
title: "Pointer leaks through pointer-keyed data structures - Project Zero"
description: "IntroductionSome time in 2024, during a Project Zero team discussion, we were talking about how r..."
---

## Introduction

Some time in 2024, during a Project Zero team discussion, we were talking about how remote ASLR leaks would be helpful or necessary for exploiting some types of memory corruption bugs, specifically in the context of Apple devices. Coming from the angle of “where would be a good first place to look for a remote ASLR leak”, this led to the discovery of a trick that could _potentially_ be used to leak a pointer remotely, without any memory safety violations or timing attacks, in scenarios where an attack surface can be reached that deserializes attacker-provided data, re-serializes the resulting objects, and sends the re-serialized data back to the attacker.

The team brainstormed, and we couldn’t immediately come up with any specific attack surface on macOS/iOS that would behave this way, though we did not perform extensive analysis to test whether such attack surface exists. Instead of targeting a real attack surface, I tested the technique described here on macOS with an artificial test case that uses `NSKeyedArchiver` serialization as the target. Because of the lack of demonstrated real-world impact, I reported the issue to Apple without filing it in our bugtracker. It was fixed in [the 31 Mar 2025 security releases](https://support.apple.com/en-us/122373). Links to Apple code in this post go to an outdated version of the code that hasn’t been updated in years, and descriptions of how the code works refer to the old unfixed version.

I decided to write about the technique since it is kind of intriguing and novel, and some of the ideas in it might generalize to other contexts. It is closely related to a partial pointer leak and another pointer ordering leak that I discovered in the past, and shows how pointer-keyed data structures can be used to leak addresses under ideal circumstances.

## Background - the tech tree

### hashDoS

To me, the story of this issue begins in 2011, when the hashDoS attack was presented at 28C3 ( [slides](https://fahrplan.events.ccc.de/congress/2011/Fahrplan/attachments/2007_28C3_Effective_DoS_on_web_application_platforms.pdf), [recording](https://media.ccc.de/v/28c3-4680-en-effective_dos_attacks_against_web_application_platforms)). In essence, hashDoS is a denial-of-service attack on services (in particular web servers) that populate hash tables with lots of attacker-controlled keys (like POST parameters). It is based on the observation that many hash table implementations have O(1) complexity per insert/lookup operation in the average case, but O(n) complexity for the same operations in the worst case (where the hashes of all keys land in the same hash bucket, and the hash table essentially turns into something like a linked list or an unsorted array depending on how it is implemented). In particular if the hash function used for keys is known to the attacker, then by constructing a request full of parameters whose keys all map to the same hash bucket, an attacker can cause the server to spend O(n²) time processing such a request; this turned out to be enough to keep a web server’s CPU saturated using ridiculously small amounts of network traffic.

There is also much older prior work on the idea of deliberately creating hash table collisions to leak addresses, as pointed out [in a 29C3 talk about the same topic](https://www.aumasson.jp/siphash/siphashdos_29c3_slides.pdf). Solar Designer [wrote in Phrack issue 53 back in 1998](https://phrack.org/issues/53/13):

> —-\[ Data Structures and Algorithm Choice\
>\
> When choosing a sorting or data lookup algorithm to be used for a normal\
> application, people are usually optimizing the typical case. However, for\
> IDS \[intrusion detection systems\] the worst case scenario should always be considered: an attacker can\
> supply our IDS with whatever data she likes. If the IDS is fail-open, she\
> would then be able to bypass it, and if it’s fail-close, she could cause\
> a DoS for the entire protected system.\
>\
> Let me illustrate this by an example. In scanlogd, I’m using a hash table\
> to lookup source addresses. This works very well for the typical case as\
> long as the hash table is large enough (since the number of addresses we\
> keep is limited anyway). The average lookup time is better than that of a\
> binary search. However, an attacker can choose her addresses (most likely\
> spoofed) to cause hash collisions, effectively replacing the hash table\
> lookup with a linear search. Depending on how many entries we keep, this\
> might make scanlogd not be able to pick new packets up in time. This will\
> also always take more CPU time from other processes in a host-based IDS\
> like scanlogd.\
>\
> \[…\]\
>\
> It is probably worth mentioning that similar issues also apply to things\
> like operating system kernels. For example, hash tables are widely used\
> there for looking up active connections, listening ports, etc. There’re\
> usually other limits which make these not really dangerous though, but\
> more research might be needed.\
\
### hashDoS as a timing attack\
\
From a slightly different perspective, the central observation of hashDoS is: If an attacker can insert a large number of chosen keys into a hash table (or hash set) and knows which hash buckets these keys hash to, then the attacker can (depending on hash table implementation details) essentially slow down future accesses to a chosen hash bucket.\
\
This becomes interesting if the attacker can cause the insertion of other keys whose hashes are secret into the same hash table. In practice, this can for example happen with hash tables which support mixing multiple key types together, like JavaScript’s [`Map`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map). Back in 2016, in the Firefox implementation, int32 numbers were hashed with a fixed hash function `ScrambleHashCode(number)`, while strings were [atomized/interned](https://en.wikipedia.org/wiki/String_interning) and then hashed based on their virtual address. That made it possible to first fill an attacker-chosen hash table bucket with lots of elements, then insert a string, observe whether its insertion is fast or slow, and determine from that whether the string’s hash matches the attacker-chosen hash bucket.\
\
With some tricks relying on a pattern in the addresses of interned single-character strings in Firefox, that made it possible to leak the lower 32 bits of a heap address through `Map` insertions and timing measurements. For more details, see the [original writeup](https://thejh.net/misc/firefox-cve-2016-9904-and-cve-2017-5378-bugreport) and [bug report](https://bugzilla.mozilla.org/show_bug.cgi?id=1312001). Of course, nowadays that kind of timing-based in-process partial pointer leak from JavaScript would be considered less interesting, since [it is generally assumed that JavaScript can read all memory in the same process anyway](https://chromium.googlesource.com/chromium/src/+/master/docs/security/side-channel-threat-model.md)…\
\
A takeaway from this is: When pointers are used as the basis for object hash codes, this can leak pointers through side channels in keyed data structures.\
\
### Linux: object ordering leak through in-order listing of a pointer-keyed tree\
\
[As I noted in a blog post a few years ago](https://projectzero.google/2021/10/how-simple-linux-kernel-memory.html), on Linux, it is possible for unprivileged userspace to discover in what order `struct file` instances are stored in kernel virtual memory by reading from `/proc/self/fdinfo/<epoll fd>` \- this file lists all files that are watched by an epoll instance by iterating through a red-black tree that is (essentially) sorted by the virtual address of the referenced `struct file`, so the data given to userspace is sorted in the same way.\
\
(As I noted in that post, this could be particularly interesting for breaking probabilistic memory safety mitigations that rely on pointer tagging. If the highest bits of pointers are secret tag bits, and an attacker can determine the order of the addresses (including tag bits) of objects, the attacker can infer whether an object’s tag changed after reallocation.)\
\
A takeaway from this is: Keyed data structures don’t just leak information about object hash codes through timing; iterating over a keyed data structure can also generate data whose ordering reveals information about object hash codes.\
\
### Serialization attacks\
\
There are various approaches to serializing an object graph. On one side of the spectrum is schema-based serialization, where ideally:\
\
- serializable types with their members are declared separately from other types\
- fields explicitly declare which other types they can point to (there are no generic pointers that can point to anything)\
- deserialization starts from a specific starting type\
\
On the other side of the serialization spectrum are things like classic Java serialization (without serialization filters), where essentially any class marked as `Serializable` can be deserialized, serialized fields can often flexibly point to lots of different types, and therefore serialized data can also have a lot of control over the shape of the resulting object graph. There is [a lot of public research](https://github.com/GrrrDog/Java-Deserialization-Cheat-Sheet) on the topic of “serialization gadget chains” in Java, where objects can be combined such that deserializing them results in things like remote code execution. This type of serialization [is generally considered](https://docs.oracle.com/en/java/javase/21/core/addressing-serialization-vulnerabilities.html) to be unsafe for use across security boundaries, though Android [exposes it across local security boundaries](https://www.usenix.org/system/files/conference/woot15/woot15-paper-peles.pdf).\
\
Somewhere in the middle of this spectrum is serialization that is fundamentally built like unsafe deserialization, but adds some coarse filters that only allow deserialized objects to have types from an allowlist to make it safe. In Java, [that is called “serialization filtering”](https://docs.oracle.com/en/java/javase/21/core/java-serialization-filters.html). This is also approximately the behavior of Apple’s [`NSKeyedUnarchiver.unarchivedObjectOfClasses`](https://developer.apple.com/documentation/foundation/nskeyedunarchiver/unarchivedobject(ofclasses:from:)-b9t5?language=objc), which this post focuses on.\
\
## An artificial test case\
\
The goal of the technique described in this post is to leak a pointer to the “shared cache” (a large mapping which is at the same virtual address across all processes on the system, whose address only changes on reboot) through a single execution of the following test case, which uses `NSKeyedUnarchiver.unarchivedObjectOfClasses` to deserialize an attacker-supplied object graph consisting of the types `NSDictionary`, `NSNumber`, `NSArray` and `NSNull`, re-serializes the result, and writes back the resulting serialized data:\
\
```\
@import Foundation;\
int main() {\
  @autoreleasepool {\
    NSArray *args = [[NSProcessInfo processInfo] arguments];\
    if (args.count != 3) {\
      NSLog(@"bad invocation");\
      return 1;\
    }\
    NSString *in_path = args[1];\
    NSString *out_path = args[2];\
\
    NSError *error = NULL;\
\
    NSData *input_binary = [NSData dataWithContentsOfFile:in_path];\
\
    /* decode */\
    NSArray<Class> *allowed_classes = @[ [NSDictionary class], [NSNumber class], [NSArray class], [NSString class], [NSNull class] ];\
    NSObject *decoded_data = [NSKeyedUnarchiver unarchivedObjectOfClasses:[NSSet setWithArray:allowed_classes] fromData:input_binary error:&error];\
    if (error) {\
      NSLog(@"Error %@ decoding", error);\
      return 1;\
    }\
    NSLog(@"decoded");\
\
    NSData *encoded_binary = [NSKeyedArchiver archivedDataWithRootObject:decoded_data requiringSecureCoding:true error:&error];\
    if (error) {\
      NSLog(@"Error %@ encoding", error);\
      return 1;\
    }\
    NSLog(@"reencoded");\
\
    [encoded_binary writeToFile:out_path atomically:NO];\
  }\
  return 0;\
}\
```\
\
(The test case also allows `NSString` but I think that was irrelevant.)\
\
## Building blocks\
\
### The `NSNull` / `CFNull` singleton\
\
[The `CFNull` type](https://developer.apple.com/documentation/corefoundation/cfnull?language=objc) is special: There is only one singleton instance of it, [`kCFNull`](https://developer.apple.com/documentation/corefoundation/kcfnull?language=objc), implemented [in CFBase.c](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/CFBase.c#L831), which is stored in the shared cache. When you deserialize an `NSNull` object, this doesn’t actually create a new object - instead, the singleton is used.\
\
In the [`CFRuntimeClass`](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/CFRuntime.h#L87) for `CFNull`, [`__CFNullClass`](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/CFBase.c#L850), no `hash` handler is provided. When [`CFHash`](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/CFRuntime.c#L709) is called on an object with a type like `__CFNullClass` that does not implement a `->hash` handler, the address of the object is used as the hash code.\
\
Pointer-based hashing is not specific to `NSNull`; but there probably aren’t many other types for which deserialization uses singletons in the shared cache. There are probably way more types for which instances’ hashes are heap addresses.\
\
### `NSNumber`\
\
The `NSNumber` type encapsulates a number and supports several types of numbers; its hash handler [`__CFNumberHash`](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/CFNumber.c#L955) hashes 32-bit integers with [`_CFHashInt`](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/ForFoundationOnly.h#L509), which pretty much just performs a multiplication with some big prime number.\
\
### `NSDictionary`\
\
Instances of [the `NSDictionary` type](https://developer.apple.com/documentation/foundation/nsdictionary?language=objc) are immutable hash tables and can contain arbitrarily-typed keys. Key hashes [are mapped to hash table buckets](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/CFBasicHashFindBucket.m#L65) using a simple modulo operation: `hash_code % num_buckets`. The number of hash buckets in a `NSDictionary` [is always a prime number (see `__CFBasicHashTableSizes`)](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/CFBasicHash.c#L222); hash table sizes are chosen based on [`__CFBasicHashTableCapacities`](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/CFBasicHash.c#L243C24-L243C52) such that hash tables are normally roughly half-full (around 38%-62%), though the sizing is a bit different for small sizes. These are probing-style hash tables; so rather than having a linked list off each hash bucket, collisions are handled [by finding alternate buckets to store colliding elements in](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/CFBasicHashFindBucket.m#L44) using the policy `__kCFBasicHashLinearHashingValue` / `FIND_BUCKET_HASH_STYLE == 1`, under which insertion scans forward through the hash table buckets.\
\
I haven’t found source code for serialization of `NSDictionary`, but it appears to happen in the obvious way, by iterating through the hash buckets in order.\
\
## The attack\
\
### The basic idea: Infoleak through key ordering in serialized `NSDictionary`\
\
If a targeted process fills an `NSDictionary` with attacker-chosen `NSNumber` keys (through deserialization), the attacker can control which hash buckets will be used by using numbers for which the number’s hash modulo the hash table size results in the desired bucket index. If the targeted process then inserts an `NSNull` key (still as part of the same deserialization), and then serializes the resulting `NSDictionary`, the location of the `NSNull` key in the dictionary’s serialized keys will reveal information about the hash of `NSNull`.\
\
In particular, the attacker can create a pattern like this using `NSNumber` keys (where `#` is a bucket occupied by an `NSNumber`, and `_` is a bucket left empty), where even-numbered buckets are occupied and odd-numbered buckets are empty, here with the example of a hash table of size 7:\
\
```\
bucket index:    0123456\
bucket contents: #_#_#_#\
```\
\
This leaves three spots where the `NSNull` could be inserted (marked with `!`):\
\
- At index 1 (`#!#_#_#`). This happens if `hash_code % num_buckets` is 6, 0, or 1. (For 6 and 0, insertion would scan linearly through the buckets until finding the free bucket at index 1.) This would result in `NSNull` being second in the serialized data.\
- At index 3 (`#_#!#_#`). This happens if `hash_code % num_buckets` is 2 or 3. This would result in `NSNull` being third in the serialized data.\
- At index 5 (`#_#_#!#`). This happens if `hash_code % num_buckets` is 4 or 5. This would result in `NSNull` being fourth in the serialized data.\
\
If the serialized data is then sent back to the attacker, the attacker can distinguish between these three states (based on the index of the `NSNull` key in the serialized data), and learn in which range `hash_code % num_buckets` is.\
\
### Extending it: Leaking the entire bucket index\
\
If the attack from the last section is repeated with the following pattern (occupying odd-numbered buckets and leaving even-numbered ones empty), this yields more information about `hash_code % num_buckets`:\
\
```\
0123456\
_#_#_#_\
```\
\
(Caveat: Don’t think too hard about how a hash table with 3 elements would use only 3 buckets and therefore wouldn’t look like this. The actual reproducer uses hash tables with >=23 buckets.)\
\
Now we have four spots where the `NSNull` could be inserted:\
a\
\
- At index 0, if `hash_code % num_buckets` is 0.\
- At index 2, if `hash_code % num_buckets` is 1 or 2.\
- At index 4, if `hash_code % num_buckets` is 3 or 4.\
- At index 6, if `hash_code % num_buckets` is 5 or 6.\
\
By combining the information from an `NSDictionary` that uses the even-buckets-occupied pattern and an `NSDictionary` that uses the odd-buckets-occupied pattern, the exact value of `hash_code % num_buckets` can be determined; for example, if the first pattern results in `#_#!#_#` and the second pattern results in `_#!#_#_`, then `hash_code % num_buckets` is 2.\
\
So by sending a serialized `NSArray` containing two `NSDictionary` instances with these patterns of `NSNumber` and `NSNull` keys to some targeted process, and then receiving a re-serialized copy from the victim, an attacker can determine `hash_code % num_buckets` for `NSArray`.\
\
### Some math: Leaking the entire `hash_code`\
\
To leak even more information about the `hash_code`, this can be repeated with different hash table sizes. The attack from the last section leaks `hash_code % num_buckets`, where `num_buckets` is a prime number that the attacker can pick from the possible sizes `__CFBasicHashTableSizes` based on how many elements are in each `NSDictionary`.\
\
A useful math trick here is: Based on the values resulting from calculating `hash_code` modulo a bunch of different prime numbers, [`hash_code` modulo the product of all those prime numbers can be calculated using the extended Euclidean algorithm](https://en.wikipedia.org/wiki/Chinese_remainder_theorem). Therefore, based on knowing `hash_code % num_buckets` for the hash table sizes 23, 41, 71, 127, 191, 251, 383, 631 and 1087, it is possible to determine `hash_code` modulo `23*41*71*127*191*251*383*631*1087 = 0x5'ce23'017b'3bd5'1495`. Because `0x5'ce23'017b'3bd5'1495` is bigger than the biggest value `hash_code` can have (since `hash_code` is 64-bit), that will be the actual value of `hash_code` \- the address of the `NSNull` singleton.\
\
### Putting it together\
\
So to leak the address of the `NSNull` singleton in the shared cache, an attacker has to send serialized data consisting of one large container (such as an `NSArray`) that, for each prime number of interest, contains two `NSDictionary` instances with the even-indices and odd-indices patterns. (The `NSNull` keys should come last in the attacker-provided serialized `NSDictionary` instances, so my reproducer constructs the serialized data manually as an XML plist, and I then convert it to a binary plist with `plutil`.)\
\
This attacker-provided serialized data is about 50 KiB in size.\
\
The targeted process then has to deserialize this data, serialize it again, and send it back to the attacker.\
\
Afterwards, the attacker can determine in which buckets `NSNull` was stored in each `NSDictionary`, use the bucket indices from pairs of `NSDictionary` to determine `hash_code % num_buckets` for each hash table size, and then use the extended Euclidean algorithm to obtain `hash_code`, the address of the `NSNull` singleton.\
\
### The reproducer\
\
I wrote [a reproducer](https://projectzero.google/downloads/nice-hash-ptr-leak-demo.tar.gz) for this issue, consisting of my own victim program that runs on the target machine and attacker programs that provide serialized data to the target machine and receive re-serialized data from the target. (For easy reproduction, you can test this on a single machine, that’s also what I did; though I rebooted between “attacker” and “target” to make sure the attacker isn’t using the same shared cache address as the target.)\
\
First, on the attacker machine, generate serialized data:\
\
```\
% clang -o attacker-input-generator attacker-input-generator.c\
% ./attacker-input-generator > attacker-input.plist\
% plutil -convert binary1 attacker-input.plist\
```\
\
Then, on the target machine, deserialize and re-serialize this data:\
\
```\
% clang round-trip-victim.m -fobjc-arc -fmodules -o round-trip-victim\
% ./round-trip-victim attacker-input.plist reencoded.plist\
2024-11-25 22:29:44.043 round-trip-victim[1257:11287] decoded\
2024-11-25 22:29:44.049 round-trip-victim[1257:11287] reencoded\
```\
\
For validation, you can also use this helper on the target machine to\
see the real address of the CFNull singleton:\
\
```\
% clang debug-nsnull-hash.m -fobjc-arc -fmodules -o debug-nsnull-hash\
% ./debug-nsnull-hash\
null singleton pointer = 0x1eb91ab60, null_hash = 0x00000001eb91ab60\
```\
\
Then, on the attacker machine, process the re-serialized data:\
\
```\
% plutil -convert xml1 reencoded.plist\
% clang -o extract-pointer extract-pointer.c\
% ./extract-pointer < reencoded.plist\
serialized data with 1111 objects\
NSNull class is 12, NSNull object is 11\
NSNull is elem 8 out of 13\
NSNull is elem 7 out of 12\
NSNull is elem 7 out of 22\
NSNull is elem 7 out of 21\
NSNull is elem 6 out of 37\
NSNull is elem 5 out of 36\
NSNull is elem 61 out of 65\
NSNull is elem 60 out of 64\
NSNull is elem 32 out of 97\
NSNull is elem 31 out of 96\
NSNull is elem 95 out of 127\
NSNull is elem 95 out of 126\
NSNull is elem 175 out of 193\
NSNull is elem 175 out of 192\
NSNull is elem 188 out of 317\
NSNull is elem 188 out of 316\
NSNull is elem 214 out of 545\
NSNull is elem 214 out of 544\
\
NSNull mod 23 = 14\
NSNull mod 41 = 13\
NSNull mod 71 = 10\
NSNull mod 127 = 120\
NSNull mod 191 = 62\
NSNull mod 251 = 189\
NSNull mod 383 = 349\
NSNull mod 631 = 375\
NSNull mod 1087 = 427\
\
NSNull mod 0x000000000000000000000000000003af =\
0x0000000000000000000000000000017e\
NSNull mod 0x00000000000000000000000000010589 =\
0x000000000000000000000000000059e6\
NSNull mod 0x0000000000000000000000000081bef7 =\
0xfffffffffffffffffffffffffff4177a\
NSNull mod 0x00000000000000000000000060cd7a49 =\
0x000000000000000000000000078e47f3\
NSNull mod 0x00000000000000000000005ee976e593 =\
0x000000000000000000000001eb91ab60\
NSNull mod 0x000000000000000000008dff48e176ed =\
0x000000000000000000000001eb91ab60\
NSNull mod 0x0000000000000000015e003ca3bc222b =\
0x000000000000000000000001eb91ab60\
NSNull mod 0x0000000000000005ce23017b3bd51495 =\
0x000000000000000000000001eb91ab60\
\
NSNull = 0x1eb91ab60\
```\
\
## Conclusion\
\
This is a fairly theoretical attack; but I think it demonstrates that using pointers as object hashes for keyed data structures can lead to pointer leaks if everything lines up right, even without using timing attacks.\
\
My example relies on the victim re-serializing the data; but a timing attack version of this might be possible too, with significantly more requests and sufficiently precise measurements.\
\
In my testcase, `NSDictionary` made it possible to essentially leak information about the ordering of pointers and hashes of numbers by mixing keys of different types; but it is probably possible to leak some amount of information even from data structures that only use pointer keys without mixing key types, especially when the attacker can guess how far apart heap objects are allocated or such and/or can reference the same objects repeatedly across multiple containers.\
\
The most robust mitigation against this is to avoid using object addresses as lookup keys, or alternatively hash them with a keyed hash function (which should reduce the potential address leak to a pointer equality oracle). However, that could come with negative performance effects - in particular, using an ID stored inside an object instead of the object’s address could add a memory load to the critical path of lookups.