---
source: p0
source_url: https://projectzero.google/2014/07/pwn4fun-spring-2014-safari-part-i_24.html
title: "pwn4fun Spring 2014 - Safari - Part I - Project Zero"
description: "Posted by Ian BeerBack in March this year I entered the pwn4fun hacking contest at CanSecWest [ h..."
---

Posted by Ian Beer

Back in March this year I entered the pwn4fun hacking contest at CanSecWest \[ [http://www.pwn2own.com/2014/03/pwning-lulzand-charity/](http://www.pwn2own.com/2014/03/pwning-lulzand-charity/) \] targeting Safari running on a brand new MacBook Air. In this first post I’ll detail how I got code execution within the Safari renderer sandbox using a bug in its javascript engine JavaScriptCore. In the second part I’ll explain how I broke out of the sandbox and into the kernel to be able to fully compromise the target system.

Bug Hunting

Looking at old bugs is a great way to quickly find new ones. Sometimes the root cause of a bug can be subtler than it appears and the patch only fixes a symptom rather than the bug. Sometimes there can be other variants of a bug which the patch missed. And sometimes the patch just introduces new bugs, especially if the code is complicated.

In this case I chose to target a bug which was incorrectly fixed by \[ [https://trac.webkit.org/changeset/145594](http://trac.webkit.org/changeset/145594) \] which was fixing \[ [https://bugs.webkit.org/show\_bug.cgi?id=112093](https://bugs.webkit.org/show_bug.cgi?id=112093) \]. WebKit security bugs are rarely opened up to the public so we can’t see the original bug report, only the fix:

Index: trunk/Source/JavaScriptCore/runtime/JSStringJoiner.h

===================================================================

\-\-\- a/trunk/Source/JavaScriptCore/runtime/JSStringJoiner.h

\+\+\+ b/trunk/Source/JavaScriptCore/runtime/JSStringJoiner.h

@@ -47,5 +47,5 @@

     Vector<String> m\_strings;

\-    unsigned m\_cumulatedStringsLength;

\+    Checked<unsigned, RecordOverflow> m\_accumulatedStringsLength;

     bool m\_isValid;

     bool m\_is8Bits;

Index: trunk/Source/JavaScriptCore/runtime/JSStringJoiner.cpp

===================================================================

\-\-\- a/trunk/Source/JavaScriptCore/runtime/JSStringJoiner.cpp

\+\+\+ b/trunk/Source/JavaScriptCore/runtime/JSStringJoiner.cpp

@@ -103,10 +103,14 @@

         return jsEmptyString(exec);

\-    size\_t separatorLength = m\_separator.length();

\+    Checked<size\_t, RecordOverflow> separatorLength = m\_separator.length();

     // FIXME: add special cases of joinStrings() for (separatorLength == 0) and (separatorLength == 1).

     ASSERT(m\_strings.size() > 0);

\-    size\_t totalSeparactorsLength = separatorLength \* (m\_strings.size() - 1);

\-    size\_t outputStringSize = totalSeparactorsLength + m\_cumulatedStringsLength;

\+    Checked<size\_t, RecordOverflow> totalSeparactorsLength = separatorLength \* (m\_strings.size() - 1);

\+    Checked<size\_t, RecordOverflow> outputStringSize = totalSeparactorsLength + m\_accumulatedStringsLength;

\+    size\_t finalSize;

\+    if (outputStringSize.safeGet(finalSize) == CheckedState::DidOverflow)

\+        return throwOutOfMemoryError(exec);

\+

This patch is trying to fix multiple integer overflow bugs in the JSStringJoiner class by replacing raw integer types with the Checked<> template. This template abstracts away the fiddly details of checking for integer overflow and makes it easier to write safe code. If the safeGet() method returns CheckedState::DidOverflow then the computed value (outputStringSize) is discarded and a javascript out-of-memory exception will be generated.

Grepping the JavaScriptCore source code we can see that JSStringJoiner is used in three places: arrayProtoFuncToString, arrayProtoFuncToLocaleString and arrayProtoFuncJoin which are all in the file ArrayPrototype.cpp. The function names are quite self-explanatory, these three functions implement the toString, toLocaleString and join methods of the javascript Array object prototype.

Taking a look at the MDN documentation for the Array object \[ [https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global\_Objects/Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array) \] we can see that these three functions are quite similar. They all return a string representation of an array, just formatted slightly differently:

- Array.prototype.toString calls the toString() method for each element in the array and connects all those strings together with a comma

- Array.prototype.toLocaleString is the same but calls toLocaleString() for each element instead

- Array.prototype.join calls toString() for each element and also allows you to specify your own separator string rather than having to use “,”


Here’s the implementation of arrayProtoFuncJoin, edited to just show the interactions with JSStringJoiner:

EncodedJSValue JSC\_HOST\_CALL arrayProtoFuncJoin(ExecState\* exec)

{

\[...\]

If an argument to the javascript function was supplied, then convert it to a string and assign that to separator. Otherwise create a string containing a comma and assign that to separator:

String separator;

if (!exec->argument(0).isUndefined())

    separator = exec->argument(0).toWTFString(exec);

if (separator.isNull())

    separator = String(",", String::ConstructFromLiteral);

Create a JSStringJoiner on the stack, passing the separator string and array length to the constructor:

JSStringJoiner stringJoiner(separator, length);

For each element of the array, convert the element to a string and pass that string to the append method of the JSStringJoiner:

\[...\]

unsigned k = 0;

for (; k < length; k++) {

    JSValue element = thisObj->get(exec, k);

    if (!element.isUndefinedOrNull())

      stringJoiner.append(element.toWTFStringInline(exec));

}

Finally call the join method of the JSStringJoiner to get the resulting string and return it:

return JSValue::encode(stringJoiner.join(exec));

}

Looking at the implementation of JSStringJoiner::append it’s clear what one of the patched bugs was:

inline void JSStringJoiner::append(const String& str)

{

\[...\]

m\_strings.append(str);

if (!str.isNull()) {

    m\_accumulatedStringsLength += str.length();

    m\_is8Bits = m\_is8Bits && str.is8Bit();

}

}

Since m\_accumulatedStringsLength used to be an unsigned int, by creating an array containing many references to a long string and calling the join method we could have easily overflowed the m\_accumulatedStringsLength variable:

var long\_string = “A”;

for (var i = 0; i < 16; i++){

long\_string = long\_string + long\_string;

}

//long string is now “A”\*0x10000

arr = \[\];

for(var i = 0; i < 0x10001; i++){

arr.push(long\_string)

}

arr.join()

Here we create the string long\_string with a length of 0x10000 then append that same string 0x10001 times to the array arr. Note that this doesn’t create 0x10001 copies of long\_string; each element of the array is just a reference to long\_string.

When we call join on arr we’ll invoke the native code seen earlier (arrayProtoFuncJoin) and end up calling JSStringJoiner::append0x10001 times, each time passing a pointer to long\_string. The 0x10000’th time append is called m\_accumulatedStringsLength will have the value 0xffff0000, therefore the following line:

    m\_accumulatedStringsLength += str.length();

will correspond to performing the following calculation:

    m\_accumulatedStringsLength = 0xffff0000 + 0x10000

The result of that addition is 0x100000000 (that number has 8 zeros) or 2^32 which is outside the range of values representable by an unsigned int. This is an integer overflow, and after executing this line m\_accumulatedStringsLength will have the value 0 (the upper bits outside the range of a 32-bit value are simply dropped.)

When we append the final 0x10001’th string m\_accumulatedStringsLength will become 0x10000 again. Presumably bad things will now happen. This bug was patched by changing the type of m\_accumulatedStringsLength to Checked<unsigned, RecordOverflow> so when that 0x10000'th string is appended the overflow will be detected and any subsequent safeGet will fail.

## LP64

Safari on OS X is a 64-bit process and OS X uses the LP64 type model which means that size\_t is a 64-bit type and int and unsigned int are 32-bit types. With this in mind, lets look at that patched code again, specifically the new overflow checks added in the JSStringJoiner::join method:

Checked<size\_t, RecordOverflow> separatorLength = m\_separator.length();

Checked<size\_t, RecordOverflow> totalSeparactorsLength =

      separatorLength \* (m\_strings.size() - 1);

Checked<size\_t, RecordOverflow> outputStringSize =

      totalSeparactorsLength + m\_accumulatedStringsLength;

size\_t finalSize;

if (outputStringSize.safeGet(finalSize) == CheckedState::DidOverflow)

    return throwOutOfMemoryError(exec);

(Note that the state stored by Checked<RecordOverflow> is transitive. If a Checked<> value which has overflowed is used again to compute another Checked<> value the overflowed state will be copied. Therefore if we reach this code and m\_accumulatedStringsLength has overflowed (as in the earlier example) then outputStringSize will also be deemed to have overflowed, even if the totalSeparactorsLength + m\_accumulatedStringsLength calculation doesn’t itself overflow.)

m\_separator is the separator string we passed to the javascript Array.prototype.join method (or “,” if we didn’t pass one.) This code is computing the total length of the result string by multiplying the length of the separator string by one less than the array length, then adding that to m\_accumulatedStringsLength. These calculations are clearly prone to integer overflow and the patch also added the use of the Checked<RecordOverflow> template here.

One thing is different here though: m\_accumulatedStringsLength became Checked<unsigned, RecordOverflow> but the three variables used here have all become Checked<size\_t, RecordOverflow>. This means that if we reach this code, and importantly if m\_accumulatedStringsLength hasn’t overflowed, then these three Checked<> variables will only detect overflows which exceed the range of a size\_t (which is 64-bits wide.)

So by also passing a long separator string to Array.prototype.join, and making sure that the combined length of all the strings in the array doesn’t itself overflow an unsigned int, we can get finalSize to exceed the range of an unsigned int without triggering any of the integer overflow checks. This isn’t a security bug though yet, but following the code forwards we see that finalSize is immediately passed to joinStrings:

outputStringImpl = joinStrings<LChar>(m\_strings, m\_separator, finalSize);

The prototype of that function is:

template<typename CharacterType>

static inline PassRefPtr<StringImpl> joinStrings(const Vector<String>& strings, const String& separator, unsigned outputLength)

The third parameter of joinStrings is an unsigned int, so when finalSize (a size\_t) gets passed to this function it will be truncated from 64-bit to 32-bits.

This is body of the JSStringJoiner::joinStrings function:

CharacterType\* data;

RefPtr<StringImpl> outputStringImpl = StringImpl::tryCreateUninitialized(outputLength, data);

if (!outputStringImpl)

    return PassRefPtr<StringImpl>();

const String firstString = strings.first();

appendStringToData(data, firstString);

for (size\_t i = 1; i < strings.size(); ++i) {

appendStringToData(data, separator);

appendStringToData(data, strings\[i\]);

}

StringImpl::tryCreateUninitialized will malloc a buffer large enough to contain the StringImpl header followed by a buffer for outputLength characters and return a pointer to that character buffer in data (which is passed by reference.)

appendStringToData is a simple memcpy-like function which copies characters from the string passed as the second argument to the data buffer passed as the first argument (which is again a pointer passed by reference.)

By triggering the integer truncation in the call to this function we can force outputLength to be shorter than the actual length of all the strings which will end up being copied in the appendStringToData calls, meaning that they will start to write outside of the bounds of the allocated string. Note however that the minimum length of data that will get written out-of-bounds is over 4 gigabytes, since the total length must be >= 2^32 to trigger the truncation, and that truncation will have the effect of subtracting at least 2^32 from the length which will then be passed to tryCreateUninitialized.

## Exploiting unbounded copies

Perhaps the most well-known example of an exploit involving an unbounded copy is the Apache on BSD negative memcpy \[ [https://web.archive.org/web/20040319164357/http://securityfocus.com/archive/1/278270/2002-06-17/2002-06-23/0](https://web.archive.org/web/20040319164357/http://securityfocus.com/archive/1/278270/2002-06-17/2002-06-23/0) \]. Here they were able to exploit a unbounded memcpy onto the stack by overwriting the remaining length of the copy (which was stored on the stack) due to a quirk of the BSD memcpy implementation. I also recently reported a integer overflow in python which required a similar trick to exploit: \[ [https://hackerone.com/reports/6389](https://hackerone.com/reports/6389) \]

In the case of this JavaScriptCore bug there is one fundamental insight that will allow us to exploit it: the total length of the copy is based on values read from the heap during the copy, and this bug lets us corrupt the heap.

In order to bound the memory copying loop and let us turn this into a controlled heap buffer overflow we're going to have to set up the heap in a very exact way such that we're able to corrupt all the strings which are involved in the copy (truncating them) whilst also corrupting something else useful for getting code execution.

At this point it’s worth clarifying what all the different string types which we’ve seen so far are:

JSC::JSString is the string object which javascript manipulates. These are garbage-collected and live on the JavaScriptCore GC heap, not the main process heap. This object doesn’t contain any string character data but has a member variable of type WTF::String:

WTF::String is the main string type used in WebKit. It too however doesn’t actually contain any character data; its only member variable is a reference-counted pointer to a WTF::StringImpl:

WTF::StringImpl is the actual underlying string type which both JSString and String are built from. Looking at the in-memory layout of a StringImpl we can see it stores the length of each string inline, therefore it should be quite easy to use the overflow to set the m\_length field to 0:

class StringImpl {

unsigned m\_refCount;

unsigned m\_length;

union {

    const LChar\* m\_data8;

    const UChar\* m\_data16;

};

union {

    void\* m\_buffer;

    StringImpl\* m\_substringBuffer;

    mutable UChar\* m\_copyData16;

};

mutable unsigned m\_hashAndFlags;

}

(The character data of a StringImpl is stored inline, directly following this header.)

Note also that javascript strings have no byte restrictions, it’s perfectly valid to have a string containing null bytes, so overwriting fields with zero is quite possible.

## The heap

Strings in JavaScriptCore are allocated using fastMalloc which is in fact just tcmalloc. There are already some great resources for learning about tcmalloc internals: this talk from Sean Heelan and Agustin Gianni gives a good overview of tcmalloc exploitation \[ [https://immunityinc.com/infiltrate/archives/webkit\_heap.pdf](https://immunityinc.com/infiltrate/archives/webkit_heap.pdf) \]. The tcmalloc code itself is also quite readable \[ [https://code.google.com/p/gperftools/](https://code.google.com/p/gperftools/) \].

There are two major things to understand about tcmalloc for heap overflow exploitation:

- By forcing enough allocations of the same size we can force subsequent allocations of that size to be next to each other in memory, with each new allocation being at a lower address until after a certain number of allocations the addresses will jump up again.

- Free lists are Last-In-First-Out: if you free an object the next allocation of an object of the same size is very likely to get allocated where that free’d object was.


This is a very simplified explanation but it’s enough for this exploit. Check out the tcmalloc specific links to understand exactly how and why this happens.

We’re aiming to use those two behaviours of tcmalloc to “groom” something like the following heap layout: (for some background on heap manipulation check out Alex Sotirov’s Heap Feng-Shui research from 2007 \[ [http://www.phreedom.org/research/heap-feng-shui/heap-feng-shui.html](http://www.phreedom.org/research/heap-feng-shui/heap-feng-shui.html) \])

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgnf1C_s1600_pwn4fun+spring+2014+-+Safari+-+part+1+writeup-img1.png)

undersized buffer is the buffer which joinStrings will allocate to copy all the copies of the strings in the JSStringJoiner into. What we’re aiming to do is line up following this allocation in memory any strings which we used to build up the array (so that we can overwrite their length fields with 0) followed by a target object we want to overwrite.

## Leaking useful addresses

My high level exploitation strategy for this bug is to trigger it twice: the first time setting things up to create an infoleak which will allow us to defeat ASLR and the second time round setting things up to overwrite a vtable pointer and pivot to a ROP stack.

Fermin Serna’s “Info leak era” talk \[ [https://media.blackhat.com/bh-us-12/Briefings/Serna/BH\_US\_12\_Serna\_Leak\_Era\_Slides.pdf](https://media.blackhat.com/bh-us-12/Briefings/Serna/BH_US_12_Serna_Leak_Era_Slides.pdf) \] gives a good overview of common techniques used to turn various bug classes into infoleaks. Fermin mentions overwriting string length fields to be able to read off of the end, and looking at the layout of a StringImpl we can see that the length field comes before the pointer to the inline data. This means that if we can set up the heap such that we can overwrite just the length field we’ll be able to read off of the end of the string from javascript:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiJ6y5_s1600_pwn4fun+spring+2014+-+Safari+-+part+1+writeup-img2.png)

On the left is the heap layout we’ll try to groom, it consists of 5 objects: the first is the undersized buffer which joinStrings allocated - this is the buffer which if we do nothing else more than 4GB will be copied into. Following this are the two strings which will form almost all the contents of the array. These are the strings which we want to truncate by setting their lengths to 0. We need two strings since we have to be able to control the integer truncation exactly so that the allocation of the undersized buffer is the right size and the length of the overwrite string is the right length. By using two strings with one character difference in their lengths we can easily truncate to any length by calculating how many copies of each string should be in the array.

Following these is the StringImpl which we’ll overwrite the length of and use for the infoleak. Finally, the fifth object is an HTMLLinkElement; we want to read the vtable of this object.

The string on the right of this diagram will be the first element in the array to be joined and consequently will be the only string which will actually be copied into the undersized buffer (if the grooming works.) This is the string which will completely overwrite source string and separator string (setting their lengths to 0) and the length field of leak string (setting it to 0xffffffff.) It doesn’t matter where on the heap this string is allocated.

## Allocation and free primitives

Due to the nature of tcmalloc getting allocations to line up in memory is very easy, simply allocate them one after the other in reverse order and there's a good probability it'll work (good enough for this contest at least.)

In order to start getting these contiguous memory allocations we need a malloc primitive we can trigger from javascript. For this we can just use javascript strings, since as we saw they're actually just wrappers around the StringImpl type. JavaScriptCore does however use one optimization we have to be aware of: when using the addition operator ‘+’ to connect strings JSC won’t create a brand new string but instead will create a JSRopeString which has two pointers, one to the string on the left of the ‘+’ and one to the string on the right.

These rope strings won’t help us make controlled size allocations, however looking at the implementation of JSRopeString we can see the JSRopeString::resolveRope method which ‘flattens’ the string by allocating a new StringImpl large enough for the whole string then copying all the sections of the rope into the right place. This flatten operation can be triggered on a javascript string by simply indexing the first character allowing us to build a simple alloc() function:

/\\* helper function to build strings which have a power-of-two length \*/

function pow2str(p, b) {

var str = String.fromCharCode(b);

for (; p; p--){

    str += str;

}

return str;

}

/\\* build a string of any length

\\* note the actual malloc’ed size will include the StringImpl header size \*/

function alloc(n, b) {

var res = '';

for(var i = 0; i < 32; i++){

    if(n & 0x1)

      res += pow2str(i, b);

    n >>= 1;

}

/\\* this will flatten the rope and actually make the allocation \*/

res\[0\];

return res;

}

We can allocate the first four objects for the groom in quick succession (the HTMLLinkElement and three strings) but the undersized buffer will only be allocated after we’ve built the entire array which will be joined and called join. Since this array will have a few million entries building it is likely to cause some heap churn and it’s very unlikely that there will be no other heap allocations of the target size we're trying to groom. Therefore it would be useful to have a free primitive such that we can allocate a placeholder object where we would like undersized buffer to end up, build the array and then free the placeholder right before calling join to trigger the bug. As tcmalloc’s freelists are LIFO we’re much more likely to end up getting the undersized buffer allocation in the right place if we can free the placeholder object reliably.

One option is to use javascript strings again: by removing all references to them and then forcing a garbage collection we can get the underlying StringImpl to be free’d. Unfortunately there’s no API exposed to javascript for forcing a GC so we’re left having to trigger one manually, usually by making many allocations. This can be very noisy and unreliable - it’s hard to know when the GC has actually occurred. It would be much better if we could find a way to directly cause an allocation and free of a buffer of a controlled size from javascript. The tcmalloc presentation linked to earlier suggested leveraging a StringBuilder to do this but I chose to use the same JSStringJoiner we’ve already been looking at to build a free primitive:

The JSStringJoiner constructor will create a Vector m\_strings to hold all the Strings which will be joined, reserving the estimated capacity:

inline JSStringJoiner::JSStringJoiner(const String& separator, size\_t stringCount)

: m\_separator(separator)

, m\_isValid(true)

, m\_is8Bits(m\_separator.is8Bit())

{

ASSERT(!m\_separator.isNull());

m\_isValid = m\_strings.tryReserveCapacity(stringCount);

}

stringCount is completely controlled, and the Vector backing storage will be allocated on the heap giving us a controlled heap allocation. In arrayProtoFuncJoin as we saw earlier a JSStringJoiner is created on the stack, which means that after the array has been joined and the JSStringJoiner goes out of scope the m\_strings vector will be destructed and the backing storage will be free’d. All we need to be able to do is execute arbitrary javascript while this array is being joined which we can do easily by setting a toString function on one of the elements of the array like this for example:

function doNoisyThing(){...}

var arr = \[\]

arr.push({toString: doNoisyThing})

for(var i = 1; i < 0x1a0/8;i++){

arr.push("");

}

The function doNoisyThing() is then free to make any allocations it needs. The join method when called on arr will make a 0x1a0 byte heap allocation, call doNoisyThing() (indirectly via a toString method) and then free that 0x1a0 byte heap allocation. For example, after the following snippet executes c, b and a are likely to be contiguous on the heap, no matter what doNoisyThing did:

var a = alloc(0x1a0 - 0x20, ‘A’);

var b = alloc(0x1a0 - 0x20, ‘B’);

arr.join(); // will call doNoisyThing

var c = document.createElement(“HTMLLinkElement”); // 0x1a0 bytes

## Leaking useful things

We’re now at the point where we can groom the heap and trigger the overflow to unbound the infoleak string allowing us to read beyond its bounds. Why did we groom an HTMLLinkElement in particular after the leak string? HTMLLinkElement is actually very useful as it allows us to leak not only the load address of the WebCore library in memory but also to leak the addresses of arbitrary strings:

### WebCore base address leak

We can compute the load address of the WebCore library by reading the vtable pointer of the HTMLLinkElement and subtracting the known offset of that vtable in the library.

### Arbitrary javascript string address leak

HTMLLinkElement has two String members: m\_type and m\_media. Looking at the HTMLLinkElement::parseAttribute function we can see that we can control m\_type easily from javascript:

void HTMLLinkElement::parseAttribute(const QualifiedName& name, const AtomicString& value)

{

\[...\]

} else if (name == typeAttr) {

    m\_type = value;

\[...\]

By setting the type attribute of the groomed HTMLLinkElement to a string from javascript and reading the m\_type field using the unbounded infoleak string we can find the address of the underlying character data. The final step is to make sure to keep hold of a reference to those strings to ensure they don’t get garbage-collected and free’d.

## Code execution

For code execution we set up a similar heap groom to that which we used for the infoleak, except we don’t need the infoleak string this time:

![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj0Mt7_s1600_pwn4fun+spring+2014+-+Safari+-+part+1+writeup-img3.png)

We can build a fake vtable as a javascript string and then use the string infoleak technique to find its address. We then trigger the overflow and overwrite the vtable pointer of the HTMLLinkElement to point to the controlled vtable. Having done this the renderer will almost instantly call a virtual function on the HTMLLinkElement we just corrupted as during garbage collection (which happens frequently) the virtual eventTargetData method will be called. This virtual function pointer is at offset 0x60 in the vtable, meaning that the value at that offset into our fake vtable string will be called. This call instruction is of the form:

call \[rax + 0x60\]

meaning that rax points to our controlled fake vtable. We just need to find a suitable sequence of instructions which will let us pivot the stack to rax. At offset 0x1f6235 in the WebCore library we can find the following instructions:

push rax

pop rsp

pop rbp

ret

Executing these instructions will set the stack pointer to point to the fake vtable string, so if we’re careful about how we build that string we can use it as both a fake vtable and a ROP stack.

## ROP payload

At this point we’ve achieved native code execution; the last step for part I is to load a secondary payload and execute it. For this I’m using a very simple ROP stack which writes a dynamic library to disk and calls dlopen to load it allowing me write the real payload in C. Take a look at the linked exploit to see how this ROP stack actually works.

We’ll look at the implementation of sandboxing in detail in the next post, but it suffices for now to see that this line:

(allow file-read\* file-write\* (home-subpath "/Library/Keychains"))

in the sandbox definition file for the web process means that we can read and write arbitrary files in the user’s ~/Library/Keychains folder from inside the Safari renderer sandbox. The ROP stack opens a file in there, writes the contents of a dynamic library to it and calls dlopen to load it.

For now that payload library is simply this:

#include <SpeechSynthesis/SpeechSynthesis.h>

\_\_attribute\_\_((constructor))

static void init(void){

SpeakString("\\x06pwned!");

}

In part II we’ll replace this payload with a kernel exploit allowing us to break out of the sandbox.

You can take a look at the complete exploit here \[ [https://code.google.com/p/google-security-research/issues/detail?id=77](https://code.google.com/p/google-security-research/issues/detail?id=77) \]. It’s been edited from the actual one thrown at CanSecWest to target this \[ [http://builds.nightly.webkit.org/files/trunk/mac/WebKit-SVN-r161944.dmg](http://builds.nightly.webkit.org/files/trunk/mac/WebKit-SVN-r161944.dmg) \] old nightly build which is also vulnerable and easy to test with if you want to fire up a debugger and try it out. All the offsets and assembly snippets in the write-up are also from that build.