---
source: p0
source_url: https://projectzero.google/2015/06/what-is-good-memory-corruption.html
title: "What is a 'good' memory corruption vulnerability? - Project Zero"
description: "Posted by Chris Evans, register whisperer. Part 1 of 4.There are a lot of memory corruption vulne..."
---

Posted by Chris Evans, register whisperer. Part 1 of 4.

There are a lot of memory corruption vulnerabilities in software, but not all are created equal. To a certain degree, the “usefulness” of a given memory corruption vulnerability is determined by how reliably it might be exploited. In some favorable instances, a given bug might be exploitable with near 100% reliability.

In this series of blog posts, we’ll examine what types of memory corruption vulnerabilities have the best potential to lead to 100% reliable exploits, using a few recent public bugs in our bug tracker as learning tools. By providing research and data of this nature to the defensive community, we can guide defensive and mitigation efforts. The tools and techniques for reliable exploitation can be studied and dissected to both find new ideas for mitigations, and to improve existing mitigations. For example, we note below that type confusion vulnerabilities can be quite nasty and we’re investigating compiler-based mitigations for these.

What do we mean by reliable?

At first this might sound like a silly question, but in fact that are a lot of facets to “reliable”. We’re not trying to give an authoritative definition of reliable here, and we’ll narrow the scope below, but here are some of the problems under the umbrella of “reliability”:

- Does the exploit ever crash? This is probably the worst outcome for the attacker: a crash is a noisy signal that may lead to detection.

- Does the exploit ever bail out cleanly? We’ll call this “aborting”, and an abort is defined as a clean exit without successful exploitation but also without any crash or other detectable signal.

- Does the exploit work uniformly across an exhaustive test matrix of different patch levels?

- Does the exploit work in the presence of additional security software such as EMET, Grsecurity, Anti-Virus products, etc.?

- How is the exploit likely to behave upon encountering an unusual environment? Will it succeed, crash or abort?

- Is the exploit cross-platform and cross-version?

- Does the exploit have a robust “continuation of execution” story, i.e. no post-exploitation instability or other untoward effects?


Given all this complexity, we need to define what we mean by “100% reliable” in the context of this post. A “100% reliable” exploit is one that is:

1. Guaranteed to succeed against a specific version and environment, on account of comprising a series of deterministic and fully understood steps;

2. Provides adequate control that at a minimum, all the above sources of unreliability can be detected and lead to aborts, not crashes.


Bug class: stack corruptions

Despite modern compiler technologies such as stack cookies and stack variable re-ordering, we still see the occasional stack corruption that is interesting from an exploitation point of view. For example, [bug 291](https://code.google.com/p/google-security-research/issues/detail?id=291) details a very interesting stack corruption in an open-source JPEG XR image decoder where an array indexing error on the stack leads to a write that “jumps over” the stack cookie and causes a corruption that is not detected by stack protections. The PoC reliably  and dare we claim, deterministically, crashes with ebp==0xffffffef. That hints to the bug’s potential reliability.

Stack corruptions do have the potential to be the basis for 100% reliable exploits, because the stack is often laid out very consistently at the time a vulnerability triggers. The follow code sample illustrates the point nicely by popping a calculator due to a stack corruption. If it works for you the first time, it’ll also work for you the second!

// Fedora 20 x64: gcc -fstack-protector ./stack.c

void subfunc() {

    char buf\[8\];

    buf\[16\] = 1;

}

int main() {

    int run\_calc = 0;

    subfunc();

    if (run\_calc) execl("/bin/gnome-calculator", 0);

}

Bug class: inter-chunk heap overflow or corruption

Probably still the most common vulnerability class we encounter, writing linearly off the end of a heap allocation is usually readily exploitable. However, it is unusual for such a vulnerability to lead to a 100% reliable exploit. One case where we almost got there was this [off-by-one heap overflow in glibc](https://projectzero.google/2014/08/the-poisoned-nul-byte-2014-edition.html). That’s an unusual case because we were attacking a command-line binary, where the heap does end up in a deterministic state at the time of the exploit attempt. Far more common is where the attacker is attacking a heap which is in a completely unknown state -- perhaps in the context of a remote service, a web browser renderer process or a kernel.

There does exist a well-used technique called “heap grooming” which attempts to take a heap from an unknown state into a state where heap chunks are lined up in a productive arrangement for exploitation. There are good examples from previous Project Zero blog posts, such as [this Safari exploit](https://projectzero.google/2014/07/pwn4fun-spring-2014-safari-part-i_24.html), [this Flash regex exploit](https://projectzero.google/2015/02/exploitingscve-2015-0318sinsflash.html) or [this Flash 4GB-out-of-bounds exploit](https://projectzero.google/2014/09/exploiting-cve-2014-0556-in-flash.html). Although heap grooming can generate very reliable exploits, there is still usually a probabilistic element to the technique, so we end up lacking the determinism needed to claim 100% reliable exploitation.

The following code sample illustrates some of the concepts of determinism vs. non-determinism:

// Fedora 20 x64: gcc ./interheap.c; n=0; while true; do ./a.out; done

int main(int argc, const char\* argv\[\]) {

    void\* ptrs\[1024\];

    int i;

    void\* ptr1;

    int \*run\_calc;

    int seed = (argc > 1) ? atoi(argv\[1\]) : getpid();

    srandom(seed); printf("seed: %d\\n", seed);  // ./a.out 21526 pops.

    for (i = 0; i < 1024; ++i) ptrs\[i\] = malloc(random() % 1024);

    for (i = 0; i < 1024; ++i) if (random() % 2) free(ptrs\[i\]);

    ptr1 = malloc(128); run\_calc = malloc(128);

    \*run\_calc = 0;

    memset(ptr1, 'A', 4096);

    if (\*run\_calc) execl("/bin/gnome-calculator", 0);

}

For a given seed on a given machine, the heap often ends up in the same state because a command-line binary starts with a fresh heap. (We’re going to stop shy of calling the state deterministic because we haven’t studied all the potential influences. We also note that different installations of the same Linux OS will vary due to e.g. different malloc() patterns in the dynamic linker depending on installed libraries.) Some of the heap states will lead to a calculator and some will not.

Bug class: use-after-free

Use-after-free vulnerabilities can lead to very reliable exploits, particularly when the “free” and the “use” are close together, and / or the attacker gets to trigger the free via a scripting language. A lot of the reliability comes from the way modern heap allocators tend to work: if an object of size X is free’d, then it will typically be the next free heap slot handed out for the next allocation of size X. This maximizes the use of “cache hot” memory locations. It is also extremely deterministic. For those wanting to study a good use-after-free exploit, one possibility is [this Pinkie Pie exploit from 2013](http://scarybeastsecurity.blogspot.com/2013/02/exploiting-64-bit-linux-like-boss.html). Although there are very non-deterministic elements to the exploit, step 2) is where the free’d object is re-purposed and that does represent a fairly deterministic step.

But, use-after-free bugs are not a perfect basis for a 100% reliable exploit. Generic challenges include:

- Threading. Depending on the heap implementation, a secondary thread might grab the free’d slot that the exploit on the primary thread wanted.

- Heap corner-cases. Depending on the heap implementation, a free operation might well trigger some reshuffle of central structures. Whilst unlikely, it is hard to be sure this will not happen if the heap is in an unknown state at the time of exploitation.

- Sensitivity to object sizes changing. Although this will not affect reliability against a specific software version, there’s always the chance of an exploit breaking (and perhaps even difficulty to repair it) if a patch comes out which makes important object sizes bigger or smaller.


This simple code sample should illustrate the point that use-after-free bugs can be pretty nasty, though:

// Fedora 20 x64: gcc ./uaf.c

struct unicorn\_counter { int num; };

int main() {

    struct unicorn\_counter\* p\_unicorn\_counter;

    int\* run\_calc = malloc(sizeof(int));

    \*run\_calc = 0;

    free(run\_calc);

    p\_unicorn\_counter = malloc(sizeof(struct unicorn\_counter));

    p\_unicorn\_counter->num = 42;

    if (\*run\_calc) execl("/bin/gnome-calculator", 0);

}

Bug class: intra-chunk heap overflow or relative write

Intra-chunk heap overflows or intra-chunk relative writes can provide a very powerful exploitation primitive. This time, we’ll start with the sample code:

// Fedora 20 x64: gcc ./intraheap.c

struct goaty { char name\[8\]; int should\_run\_calc; };

int main(int argc, const char\* argv\[\]) {

    struct goaty\* g = malloc(sizeof(struct goaty));

    g->should\_run\_calc = 0;

    strcpy(g->name, "projectzero");

    if (g->should\_run\_calc) execl("/bin/gnome-calculator", 0);

}

A bug like this is extremely powerful because the memory corruption does not cross a heap chunk. Therefore, all of the uncertainty and non-determinism arising from unknown heap state is eliminated. The heap can be in any state, yet the same program data will always be corrupted in the same way. Bugs like these are very capable of leading to 100% reliable exploits. [Bug 251](https://code.google.com/p/google-security-research/issues/detail?id=251) is a real-world example of a linear buffer overflow within a heap chunk. [Bug 265](https://code.google.com/p/google-security-research/issues/detail?id=265) is a rare but very interesting example of an indexing error leading to an out-of-bounds write but within the confines of a single heap chunk. The trigger is also interesting: a protocol where a virtual pen writes characters on to a virtual screen, and we use a protocol message to set the virtual pen location to co-ordinates that are off-screen! The PoC deterministically crashes whilst operating on a wild but constrant address, free(0x2000000000).

Bug class: type confusion

Type confusion bugs can be very powerful, with the potential to form the basis of 100% reliable exploits. When triggering a type confusion vulnerability, a piece of code has a reference to an object which it believes to be of type A (the API type), but really it is confused and the object is of type B (the in-memory type). Depending on the in-memory structure of type A vs. type B, very weird but usually fully deterministic side-effects can occur. Time for the code sample:

// Fedora 20 x64: gcc ./confused.cc -lstdc++

#include <unistd.h>

class IShouldRunCalculator { public: virtual bool UWannaRun() = 0; };

class CalculatorDecider final : public IShouldRunCalculator {

public:

    CalculatorDecider() : m\_run(false) {}

    virtual bool UWannaRun() { return m\_run; }

private: bool m\_run;

};

class DelegatingCalculatorDecider final : public IShouldRunCalculator {

public:

    DelegatingCalculatorDecider(IShouldRunCalculator\* delegate) : m\_delegate(delegate) {}

    virtual bool UWannaRun() { return m\_delegate->UWannaRun(); }

private: IShouldRunCalculator\* m\_delegate;

};

int main() {

    CalculatorDecider nonono;

    DelegatingCalculatorDecider isaidno(&nonono);

    IShouldRunCalculator\* decider = &isaidno;

    CalculatorDecider\* confused\_decider = reinterpret\_cast<CalculatorDecider\*>(decider);

    if (confused\_decider->UWannaRun()) execl("/bin/gnome-calculator", 0);

}

As you can see from the code, there’s a general attempt to say no to calculation, but a type confusion causes CalculatorDecider::UWannaRun() to perform a boolean check on an underlying piece of memory that is really a (non-null) pointer. So we’ll always end up calculating. (Or will we? It happens to calculate reliably on my machine but there’s a source of non-determinism here for readers that enjoy a thought exercise.)

A good study of a real type confusion bug and exploit is [MWR Infosecurity’s blog post](https://labs.mwrinfosecurity.com/blog/2013/04/19/mwr-labs-pwn2own-2013-write-up---webkit-exploit/) regarding their Pwn2Own 2013 entry against Google Chrome. Interestingly enough, this is one case where the bug does not easily lend itself to a 100% reliable exploit. In this instance, there is a small in-memory type confused against a much larger API type. Therefore, when the code is accessing most of the raw fields, a heap boundary is crossed because the offset of the field in the API type is larger than the size of the in-memory type. As we have seen above, crossing heap boundaries is a no-no for reliability. The following diagram shows the two main possibilities of type confusion member use. The object on the left is the object the compiler has emitted code for, on account of a bad cast. But at runtime, the object memory pointed to happens to be smaller because the type in memory is different. Accesses that happen to be within bounds of the runtime object will behave deterministically -- such as an ASLR defeating pointer infoleak in the GetSize() method. Accesses that cross a heap boundary are out-of-bounds and are unlikely to behave deterministically -- such as a memory corrupting write in the SetFlags() method.

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhgezi_s600_gm_01.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhgezi_s624_gm_01.png)

Case study: ShaderParameter heap corruption, the old school way

This post has been about bug reliability, so it may seem strange that we’re about to present an unreliable exploit. But this is a story about demonstrating conventional wisdom and then challenging ourselves to produce something more reliable using the same bug primitive. We start with poor reliability and will then improve until we have excellent reliability.

So, we end this post by exploiting a recently patched vulnerability in Adobe Flash. It’s [bug 324](https://code.google.com/p/google-security-research/issues/detail?id=324), an out-of-bounds write relating to the ShaderParameter ActionScript class. The attacker gets to write a chosen 32-bit value at a bad index relative to a shader program. A large index will result in an out-of-bounds write off the end of a heap chunk.

Given an out-of-bounds write primitive like this, there’s now a highly standard way of exploiting Adobe Flash: simply use heap grooming to arrange for a Vector.<uint> buffer object to follow the object which the write goes off the end of. The errant write will then clobber the length of the Vector, resulting in the ability to read and write arbitrary process memory past the end of the Vector.

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEix8kh_s600_gm_02.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEix8kh_s624_gm_02.png)

A reasonably commented exploit for Linux x64 is attached to [the bug](https://code.google.com/p/google-security-research/issues/detail?id=324). No particular attempt has been made to make it reliable; it could probably be tidied up to be much more reliable. But we’re not going to get to 100% reliability with this particular exploit for reasons covered above, because we’ve blindly corrupted across a heap chunk boundary.

After Adobe released the patch to fix this bug, but well before we released details of the bug, [non-zero day exploits started showing up in exploit packs in the wild](http://malware.dontneedcoffee.com/2015/06/cve-2015-3105-flash-up-to-1700188-and.html). Perhaps the attackers are fast at binary diffing, or have a MAPP leak, or were already using the vulnerability in a more targeted manner; we may never know. However this happened, it did generate us another data point and another exploit to study -- which also uses the standard Vector exploitation tricks [according to @HaifeiLi on Twitter](https://twitter.com/HaifeiLi/status/613017967547146240).

We’ll conclude this post here with a promise that we’re not done with this specific bug. In the next post in the series, we’ll ask the question, “can we do something more reliable with this bug?” and as you might guess, the answer will be yes.