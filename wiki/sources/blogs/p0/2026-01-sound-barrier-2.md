---
source: p0
source_url: https://projectzero.google/2026/01/sound-barrier-2.html
title: "Breaking the Sound Barrier, Part II: Exploiting CVE-2024-54529 - Project Zero"
description: "In the first part of this series, I detailed my journey into macOS security research, which led t..."
---

In the [first part of this series](https://projectzero.google/2025/05/breaking-sound-barrier-part-i-fuzzing.html), I detailed my journey into macOS security research, which led to the discovery of a type confusion vulnerability ( [CVE-2024-54529](https://project-zero.issues.chromium.org/issues/372511888)) and a double-free vulnerability ( [CVE-2025-31235](https://project-zero.issues.chromium.org/issues/406271181)) in the `coreaudiod` system daemon through a process I call [knowledge-driven fuzzing](https://projectzero.google/2025/05/breaking-sound-barrier-part-i-fuzzing.html#:~:text=The%20Approach%3A%20Knowledge%2DDriven%20Fuzzing). While the first post focused on the process of finding the vulnerabilities, this post dives into the intricate process of exploiting the type confusion vulnerability.

I’ll explain the technical details of turning a potentially exploitable crash into a working exploit: a journey filled with dead ends, creative problem solving, and ultimately, success.

## The Vulnerability: A Quick Recap

If you haven’t already, I highly recommend reading my [detailed writeup](https://googleprojectzero.blogspot.com/2025/05/breaking-sound-barrier-part-i-fuzzing.html) on this vulnerability before proceeding.

As a refresher, [CVE-2024-54529](https://project-zero.issues.chromium.org/issues/372511888) is a type confusion vulnerability within the `com.apple.audio.audiohald` Mach service in the `CoreAudio` framework used by the `coreaudiod` process. Several Mach message handlers, such as `_XIOContext_Fetch_Workgroup_Port`, would fetch a `HALS_Object` from the Object Map based on an ID from the Mach message, and then perform operations on it, assuming it was of a specific type (`ioct`) without proper validation.

This incorrect assumption led to a crash when the code attempted to make a virtual call on an object whose pointer was stored inside the `HALS_Object`, as shown in the stack trace below:

```
Process 82516 stopped
* thread #8, queue = 'com.apple.audio.system-event', stop reason = EXC_BAD_ACCESS (code=1, address=0xffff805cdc7f7daf)
    frame #0: 0x00007ff81224879a CoreAudio`_XIOContext_Fetch_Workgroup_Port + 294
CoreAudio`_XIOContext_Fetch_Workgroup_Port:
    0x7ff81224879a <+291>: mov    rax, qword ptr [rdi]
->  0x7ff81224879d <+294>: call   qword ptr [rax + 0x168]
    0x7ff8122487a3 <+300>: mov    dword ptr [rbx + 0x1c], eax
    0x7ff8122487a6 <+303>: mov    rdi, r13
(lldb) bt
* thread #8, queue = 'com.apple.audio.system-event', stop reason = EXC_BAD_ACCESS (code=1, address=0xffff805cdc7f7daf)
  * frame #0: 0x00007ff81224879a CoreAudio`_XIOContext_Fetch_Workgroup_Port + 294
    frame #1: 0x00007ff812249c81 CoreAudio`HALB_MIGServer_server + 84
    frame #2: 0x00007ff80f359032 libdispatch.dylib`dispatch_mig_server + 362
    frame #3: 0x00007ff811f202ed CoreAudio`invocation function for block in AMCP::Utility::Dispatch_Queue::install_mig_server(unsigned int, unsigned int, unsigned int (*)(mach_msg_header_t*, mach_msg_header_t*), bool, bool) + 42
    frame #4: 0x00007ff80f33e7e2 libdispatch.dylib`_dispatch_client_callout + 8
    frame #5: 0x00007ff80f34136d libdispatch.dylib`_dispatch_continuation_pop + 511
    frame #6: 0x00007ff80f351c83 libdispatch.dylib`_dispatch_source_invoke + 2077
    frame #7: 0x00007ff80f3447ba libdispatch.dylib`_dispatch_lane_serial_drain + 322
    frame #8: 0x00007ff80f3453e2 libdispatch.dylib`_dispatch_lane_invoke + 377
    frame #9: 0x00007ff80f346393 libdispatch.dylib`_dispatch_workloop_invoke + 782
    frame #10: 0x00007ff80f34f0db libdispatch.dylib`_dispatch_root_queue_drain_deferred_wlh + 271
    frame #11: 0x00007ff80f34e9dc libdispatch.dylib`_dispatch_workloop_worker_thread + 659
    frame #12: 0x00007ff80f4e2c7f libsystem_pthread.dylib`_pthread_wqthread + 326
    frame #13: 0x00007ff80f4e1bdb libsystem_pthread.dylib`start_wqthread + 15
```

## Understanding the Objective

Exploiting such a vulnerability seemed simple enough: if we could control the address being dereferenced at offset `0x168` of the `rax` register, we could hijack control flow. But it wasn’t quite that simple. The `HALS_Object` fetched from the heap was dereferenced several times before the `call` instruction happened:

Thus, the exploit required establishing a pointer chain. First, we needed to set a value at offset `0x68` of a `HALS_Object` to point to a region we controlled in memory. This region, in turn, needed to contain a pointer at its own offset `0x0` that pointed to a fake vtable, also under our control. With this chain in place, we could write our target address at offset `0x168` of the fake vtable to hijack control flow. The approach would look like this:


![](<Base64-Image-Removed>)

## Initial Exploitation Attempts and the `CFString` Hurdle

The most direct path to exploitation seemed to be to find an API to write arbitrary data to the vulnerable offset (`0x68`) of a `HALS_Object`. My initial thought was to create a `CFString` object and find a way to place a pointer to it at the vulnerable offset of a `HALS_Object`.

I found a nice looking API in `coreaudiod` I could call that would set offset `0x68` to an attacker-controlled `CFString`:

![](<Base64-Image-Removed>)

However, this approach quickly hit a wall. The `CFString` type has an [uncontrollable header](https://github.com/apple-oss-distributions/CF/blob/dc54c6bb1c1e5e0b9486c1d26dd5bef110b20bf3/CFString.c#L166), which meant that even though I could control the _content_ of the `CFString`, I couldn’t control the object’s header. For this exploit to work, I needed the data at offset `0x0` of the `CFString` to be a pointer to data I controlled. The `CFString`’s header made this impossible.

This meant I needed a new approach. I had to find a different way to control the memory at the vulnerable offset.

## Tools of the Trade

With my initial attempts at finding a suitable object primitive proving fruitless, it became clear I needed a better way to visualize the `coreaudiod` heap and understand the objects living on it. To do this, I built several custom tools.

The most useful of these was a custom object dumper I wrote using Ivan Fratric’s [TinyInst Hook API](https://github.com/googleprojectzero/TinyInst/blob/master/hook.md). This tool hooked into the process and iterated through the `HALS_ObjectMap` linked list, dumping the raw contents, size, type, and subtype of every `HALS_Object` currently on the heap. This gave me a powerful method to inspect the composition of each object, search for controllable data, and see if any interesting pointers already existed at the critical `0x68` offset.

![](<Base64-Image-Removed>)

Alongside this dynamic analysis tool, I used an IDAPython script to perform targeted static analysis, hunting for any code paths that wrote to offsets of interest after an object was fetched via `CopyObjectByObjectID`. This combination of dynamic and static analysis was essential for systematically mapping out the exploitation surface.

## Forcing Out-of-Bounds Reads on the Heap

Armed with my object dumper, I decided to investigate another potential exploitation path. If I couldn’t find a way to write a pointer directly to offset `0x68`, perhaps I could trigger an out-of-bounds read to achieve a similar effect.

The idea was to find a `HALS_Object` smaller than `0x68` bytes, create it on the heap, and then carefully place a second, attacker-controlled object immediately after it in memory. If I then triggered the type confusion on the _first_ (smaller) object, the code’s attempt to read from offset `0x68` would read past the object’s boundary and into the controlled data of the second object.

Unfortunately, my object dumper and static analysis quickly proved this to be a dead end. After cataloging all the object types, it was clear that no object smaller than `0x68` bytes existed. In the latest macOS version available during my research (macOS Sequoia 15.0.1), the smallest object type, `stap`, was `0x70` bytes.

Interestingly, previous versions of macOS I looked at (including macOS Ventura 13.1) _did_ contain smaller `HALS_Object`s, demonstrating that differences in software versions can sometimes introduce new primitives for exploitation.

| Type | Size |
| --- | --- |
| `clnt` | 0x158 |
| `ioct` | 0xF0 |
| `sive` | 0x78 |
| `astr` | 0xD0/0xD8/0xB8/0x98 |
| `stap` | 0x70 |
| `asub` | 0x80 |
| `aplg` | 0x258/0x248/0x1B0/0xB0/0x88 |
| `adev` | 0x740/0x6E0/0x7A0/0x840 |
| `abox` | 0x198 |
| `engn` | 0x308/0x480 |
| `crsd` | 0xB8 |

With the out-of-bounds read possibility eliminated, my focus shifted back to heap manipulation and finding a way to control the contents of an object’s allocation directly.

## A Glimmer of Hope: Uninitialized Memory in the `ngne` Object

To hunt for other exploitation primitives, I turned to a powerful debugging tool on macOS: Guard Malloc with the `PreScribble` option enabled. This feature initializes freshly allocated memory blocks with a specific byte pattern (`0xAA`), making it easy to spot when objects are not properly zeroed out and could lead to the use of uninitialized memory.

Running `coreaudiod` with these settings, I discovered an object type, `ngne`, that had a peculiar property: a portion of the object’s memory was uninitialized. Specifically, 6 high bytes of a pointer-sized field at the correct offset were not being cleared upon allocation, leaving them with the `0xAA` pattern from `PreScribble`.

_![](<Base64-Image-Removed>)_

This was a game-changer. An uninitialized memory vulnerability could provide the primitive I needed to gain control of the pointer at the vulnerable offset.

### The Tricky Constraint

Why only 6 uninitialized bytes you ask? The developer likely did something like this at offset `0x68` when defining the `ngne` object:

```
class NGNE {
...
  size_t previous_var; // offset 0x60
  short var=0; // offset 0x68
  size_t  next_var; // offset 0x70
...
}
```

This happens because the compiler aligns 8-byte variables, like `size_t` on x64, to 8-byte boundaries for optimization. Consequently, the `short` variable causes `next_var` to be placed at offset `0x70` instead of immediately after `var` at `0x6A`, leaving an uninitialized 6-byte gap.

This constraint would make things a bit tricky. Even if we could get controlled memory to show up within the object, the last 2 bytes would be zero’d out.

## A New Exploitation Strategy

Armed with this new knowledge, I formulated a new, more complex exploitation strategy:

1. **Allocate Controlled Data**: Find a way to allocate large amounts of data that I control in the `coreaudiod` process.
2. **Create Indirect Pointers**: Create indirect pointers that point to my controlled data.
3. **Free data containing pointers.**
4. **Reuse Pointers**: Trick the program into reusing memory containing pointers when the `ngne` object is allocated.

## Heap Feng Shui with Property Lists

To control large portions of memory, I turned to a common feature in Apple’s APIs: [Property Lists](https://developer.apple.com/library/archive/documentation/General/Conceptual/DevPedia-CocoaCore/PropertyList.html). Many APIs accept user data as serialized `plist` files, which are then deserialized, allocating memory for `CoreFoundation` objects. `CoreAudio` exposed an API, `HALS_Object_SetPropertyData_DPList`, which did just that, storing it on the heap:


![](<Base64-Image-Removed>)

A `plist` allows you to specify nested values of several types:

| Core Foundation type | XML element |
| --- | --- |
| `CFArrayRef` | `<array>` |
| `CFDictionaryRef` | `<dict>` |
| `CFStringRef` | `<string>` |
| `CFDataRef` | `<data>` |
| `CFDateRef` | `<date>` |
| `CFNumberRef` (`Int`) | `<integer>` |
| `CFNumberRef` (`Float`) | `<real>` |
| `CFBooleanRef` | `<true/>` or `<false/>` |

This meant I could create `plist` files with large arrays of `CFString` or `CFData` objects, giving me a powerful primitive for mass-allocating data and controlling the heap layout. Furthermore, I could add `CFArray` or `CFDictionary` objects to achieve the indirection needed for the exploit as those data types contain pointers to other user-controlled objects.

The overall structure would look like this:

![](<Base64-Image-Removed>)

But you might be wondering: doesn’t this present a similar problem as when we tried to allocate a pointer to a `CFString`? (The pointer chain would try to dereference the `CFRuntimeBase` header and fail). Yes! But ironically, the clearing of the last 2 bytes at offset `0x68` opened up a new possibility: we might allocate an object over a `CFString` pointer in the middle of the array that, after the last 2 bytes were cleared, pointed to raw data. It seemed like a bit of a long shot, but I was up for the challenge!

![](<Base64-Image-Removed>)

## Freeing the Data

Next, I needed to free the memory structure that had been allocated with my data. This was easy enough - I just had to call the API again with a much smaller `plist`. Then, my large, allocated `plist` structure was freed.

## Reusing the Freed Data in an `ngne` Object

After some painful reverse engineering, I found a way to create `ngne` objects on demand by sending a crafted Mach message to the `audiohald` service. I thought I was on the home stretch. My plan was to spray the heap, free the memory, and then immediately allocate my `ngne` object to reclaim it.

![](<Base64-Image-Removed>)

But I quickly ran into a fundamental and frustrating roadblock: `malloc` zones.

The `ngne` objects I could create were 776 bytes in size, which placed them squarely in the `malloc_tiny` memory region. This was a critical problem because, as a security mitigation, macOS’s memory allocator securely zeroes out any memory in the `malloc_tiny` zone upon allocation. My carefully crafted heap spray would be wiped clean moments before the `ngne` object was placed on top of it.

My exploit was dead in the water.

### A New Hope: Startup `ngne` Objects

This forced a pivot. If I wanted to use uninitialized memory, I needed to land an allocation in a malloc zone that didn’t get zeroed out. My analysis showed that larger `ngne` objects—over 1100 bytes—could get created and would be placed in the `malloc_small` region, which is not zeroed on allocation. The catch? I couldn’t find any user-accessible API to trigger their creation. They only seemed to be instantiated when `coreaudiod` registered an audio plugin during startup.

![](<Base64-Image-Removed>)

So, I had found some `ngne` objects suitable for exploitation, but they were only instantiated at startup, before we could deliver our heap spray. This sparked an idea: what if I performed the heap spray and then crashed the process on purpose? When it restarted, (all system daemons automatically restart on macOS) could it allocate an object over our sprayed data?

## Loading Into Memory on Startup

One difficulty I had to overcome was that after crashing, the newly spawned `coreaudiod` would be allocated within a new process space. That meant that the previously allocated heap spray would no longer be in play.

However, I discovered a nice feature that helped with this: when performing our `plist` heap spray, `CoreAudio` serialized the data to a file on disk, `/Library/Preferences/Audio/com.apple.audio.DeviceSettings.plist`.

Then, on startup, the `plist` was fetched from disk, updated with current runtime information, and saved back to disk, as shown below.

```
__int64 __fastcall CASettingsStorage::SetCFTypeValue(
        CFMutableDictionaryRef *this,
        const __CFString *key,
        const void *value)
{
  CASettingsStorage::RefreshSettings((CASettingsStorage *)this);
  CFDictionarySetValue(this[2], key, value);
  return CASettingsStorage::SaveSettings((CASettingsStorage *)this);
}
```

Lucky for me, the `CASettingsStorage::SaveSettings` function created a copy of the in-memory `plist`, wrote it to disk, and then _freed the copy._ Thankfully, this process occurred before the creation of the `ngne` objects by the system.

```
void __fastcall CASettingsStorage::SaveSettings(CASettingsStorage *this)
{
  if ( !*((_BYTE *)this + 50) )
  {
    v1 = (const void *)*((_QWORD *)this + 2);
    if ( v1 )
    {
      Data = CFPropertyListCreateData(0LL, v1, *((CFPropertyListFormat *)this + 3), 0LL, 0LL);
      v3 = fopen(*(const char **)this, "w+");

      ----TRUNCATED FILE WRITE OPERATIONS----

      CACFData::~CACFData(Data);
    }
  }
}
```

This meant that each time the process restarted, our entire `plist` structure was reallocated and then freed, giving us a chance for our data to end up within the vulnerable offset of the `ngne` object.

## Updated Exploitation Strategy

The new attack strategy would look like this:

1. **Allocate Controlled Data**: Send a mach message to `coreaudiod` to invoke the `HALS_Object_SetPropertyData_DPList` message handler. Include a large `plist` with controlled data. The `plist` will be stored to disk.
2. **Trigger the Type Confusion**: Trigger the type confusion vulnerability, simply to crash the process.
3. **Let the Magic Happen**: Wait for `coreaudiod` to:

   - Restart.
   - Load the crafted `plist` from disk.
   - Create a `plist` in memory.
   - Free the `plist.`
   - Allocate an `ngne` object over the freed `plist` object (hopefully).
4. **Trigger the Type Confusion Again**: Trigger it on a random `ngne` object and hope it reused our sprayed data.
5. **Repeat**: Repeat steps 3-4 until it works!

## Validating the Approach

In order for the exploit to work, a lot of things needed to go right. Before proceeding, I wanted to make sure that my attack chain wasn’t purely theoretical - that the pointer chain I sought could actually show up within an object.

To do this, I leveraged the `XSystem_Get_Object_Info` message handler provided by `coreaudiod`. This API allowed me to enumerate all HALS Objects on the system, and determine which ones were of type `ngne`.

Then, I modified my Object Dumper to dump only `ngne` objects, and to continually run until it found a pointer chain to the sprayed data. After much experimentation with crafting the perfect `plist`, I finally caused the stars to perfectly align!

![](<Base64-Image-Removed>)

## Building the ROP Chain

Once I could redirect execution to my controlled data, the final step was to build a Return-Oriented Programming (ROP) chain to achieve arbitrary code execution. Since the target was the `CoreAudio` library, (which is stored in the dyld shared cache and has a constant address until system reboot) defeating ASLR was not necessary in the context of privilege escalation. I crafted a ROP chain to open and write a file at a location normally accessible only to coreaudiod. As the ROP chain is encoded in one of the `CFString` objects, to avoid issues with invalid UTF-8 bytes, UTF-16 string encoding was used.

```
# Beginning of stack after pivot
rop   = bytearray(p64(LOAD_RSP_PLUS_EIGHT)) # lea rax, [rsp + 8] ; ret
rop  += p64(ADD_HEX30_RSP)       # add rsp, 0x30 ; pop rbp ; ret
rop  += INLINE_STRING            # Inline "/Library/Preferences/Audio/malicious.txt"
rop  += b'\x42' * 15             # pop rbp filler and will be moved past
rop  += p64(MOV_RAX_TO_RSI)      # mov rsi, rax ; mov rax, rsi ; pop rbp ; ret
rop  += p64(0x4242424242424242)  # pop rbp filler
rop  += p64(MOV_RSI_TO_RDI)      # mov rdi, rsi ; mov rax, rdi ; mov rdx, rdi ; ret
rop  += p64(POP_RSI_GADGET)      # pop rsi ; ret
rop  += p64(0x201)               # O_CREAT | O_WRONLY
rop  += p64(POP_RDX_GADGET)      # pop rdx ; ret
rop  += p64(0x1A4)               # 0644
rop  += p64(POP_RAX_GADGET)      # pop rax ; ret
rop  += p64(0x2000005)           # syscall number for open()
rop  += p64(SYSCALL)             # syscall
rop += b'\x42' * (1152 - len(rop))

# [rax + 0x168] → pointer to pivot gadget (entrypoint)
rop[0x168:0x170] = p64(STACK_PIVOT_GADGET)  # xchg rsp, rax ; xor edx, edx ; ret
```

With everything in place, the exploit successfully executes the ROP chain, giving me control of the `coreaudiod` process. The following shows the ROP chain sprayed in memory:

![](<Base64-Image-Removed>)

It should be noted that this exploit was written for macOS running on Intel CPUs. On a system with Apple Silicon, exploitation using the same technique would require the ability to correctly sign pointers that make up the pointer chain and ROP gadgets.

## Demo

The following video demo shows the PoC exploit in action on macOS Sequoia 15.0.1:

## Conclusion

Exploiting CVE-2024-54529 was a journey that went from a simple-looking type confusion to a multi-stage exploit involving heap spraying, uninitialized memory, and a carefully orchestrated series of crashes and restarts. This research highlights the power and importance of sandbox escape vectors and demonstrates how a “knowledge-driven fuzzing” approach can lead to the discovery and exploitation of high-impact vulnerabilities.

All the tools used in this research, including the [fuzzing harness, custom instrumentation,](https://github.com/googleprojectzero/p0tools/tree/master/CoreAudioFuzz) and a [proof-of-concept](https://github.com/googleprojectzero/p0tools/tree/master/CoreAudioFuzz/exploit) for CVE-2024-54529, are open-sourced and available.