---
source: p0
source_url: https://projectzero.google/2025/12/thinking-outside-the-box.html
title: "Thinking Outside The Box [dusted off draft from 2017] - Project Zero"
description: "PrefaceHello from the future!This is a blogpost I originally drafted in early 2017. I wrote what ..."
---

## Preface

Hello from the future!

This is a blogpost I originally drafted in early 2017. I wrote what I intended to be the first half of this post (about escaping from the VM to the VirtualBox host userspace process with [CVE-2017-3558](https://bugs.chromium.org/p/project-zero/issues/detail?id=1086)), but I never got around to writing the second half ( [going from the VirtualBox host userspace process to the host kernel](https://bugs.chromium.org/p/project-zero/issues/detail?id=1091)), and eventually sorta forgot about this old post draft… But it seems a bit sad to just leave this old draft rotting around forever, so I decided to put it in our blogpost queue now, 8 years after I originally drafted it. I’ve very lightly edited it now (added some links, fixed some grammar), but it’s still almost as I drafted it back then.

When you read this post, keep in mind that unless otherwise noted, it is describing the situation as of 2017. Though a lot of the described code seems to not have changed much since then…

## Introduction

VM software typically offers multiple networking modes, including a NAT mode that causes traffic from the VM to appear as normal traffic from the host system. Both QEMU and VirtualBox use forks of [Slirp](http://slirp.sourceforge.net/) for this. Slirp is described as follows on its homepage:

_Slirp emulates a PPP or SLIP connection over a normal terminal. This is an actual PPP or SLIP link, firewalled for people’s protection. It makes a quick way to connect your Palm Pilot over the Internet via your Unix or Linux box!!! You don’t need to mess around with your /etc/inetd.conf or your /etc/ppp/options on your system._

Slirp is a useful basis for VM networking because it can parse raw IP packets (coming from the emulated network adapter) and forward their contents to the network using the host operating system’s normal, unprivileged networking APIs. Therefore, Slirp can run in the host’s userspace and doesn’t need any special kernel support.

Both QEMU and VirtualBox don’t directly use the upstream Slirp code, but instead use patched versions where, for example, the feature for setting up port forwards by talking to a magic IP address is removed. Especially in VirtualBox, the Slirp code has been altered a lot.

This post describes an issue in VirtualBox and how it can be exploited. Some parts are specific to the host operating system; in those cases, this post focuses on the situation on Linux.

## The packet heap in VirtualBox

The VirtualBox version of Slirp uses a custom zone allocator for storing packet data, in particular, incoming ethernet frames. Each NAT network interface has its own zone (`zone_clust`) with `nmbclusters=1024+32*64=3072` chunks of size `MCLBYTES=2048`. The initial freelist of each zone starts at the high-address end of the zone and linearly progresses towards the low-address end.

The heap uses inline metadata; each chunk is prefixed with the following structure:

```
struct item {
    uint32_t magic; // (always 0xdead0001)
    uma_zone_t zone; // (pointer to the zone; uma_zone_t is struct uma_zone *)
    uint32_t ref_count;
    struct {
        struct type *le_next; // (next element)
        struct type **le_prev; // (address of previous le_next)
    } list; // (entry in the freelist or in used_items, the list of used heap chunks)
};
```

![](<Base64-Image-Removed>)

Chunks are freed through the methods `m_freem -> m_free -> mb_free_ext -> uma_zfree -> uma_zfree_arg -> slirp_uma_free`. The `uma_zfree_arg()` function takes pointers to the real zone structure and to the chunk data as arguments and checks some assertions before calling `slirp_uma_free()` as `zone->pfFree()`:

```
void uma_zfree_arg(uma_zone_t zone, void *mem, void *flags) {
    struct item *it;
    [...]
    it = &((struct item *)mem)[-1];
    Assert((it->magic == ITEM_MAGIC));
    Assert((zone->magic == ZONE_MAGIC && zone == it->zone));

    zone->pfFree(mem,  0, 0); // (zone->pfFree is slirp_uma_free)
    [...]
}
```

Unfortunately, `Assert()` [is `#define`‘d to do nothing in release builds](https://www.virtualbox.org/browser/vbox/trunk/include/iprt/assert.h) \- only “strict” builds check for the condition. The builds that are offered on the VirtualBox download page are normal, non-strict release builds.

Next, `slirp_uma_free()` is executed:

```
static void slirp_uma_free(void *item, int size, uint8_t flags) {
    struct item *it;
    uma_zone_t zone;
    [...]
    it = &((struct item *)item)[-1];
    [...]
    zone = it->zone;
    [...]
    LIST_REMOVE(it, list);
    if (zone->pfFini)
    {
        zone->pfFini(zone->pData, item, (int /*sigh*/)zone->size);
    }
    if (zone->pfDtor)
    {
        zone->pfDtor(zone->pData, item, (int /*sigh*/)zone->size, NULL);
    }
    LIST_INSERT_HEAD(&zone->free_items, it, list);
}
```

`slirp_uma_free()` grabs the zone pointer from the chunk header. Because `Assert()` is compiled out, there is no validation to ensure that this zone pointer points to the actual zone - an attacker who can overwrite the chunk header could cause this method to use an arbitrary zone pointer. Then, the member `pfFini` of the zone is executed, which, for an attacker who can point `it->zone` to controlled data, means that an arbitrary method call like this can be executed:

_`{controlled pointer}`_`({controlled pointer}, {pointer to packet data}, {controlled u32});`

Because the VirtualBox binary, at least for Linux, is not relocatable and has \`memcpy()\` in its PLT section, this can be used as a write primitive by using the static address of the PLT entry for `memcpy()` as function address:

`memcpy(dest={controlled pointer}, src={packet data}, n={controlled u32})`

This means that, even though the packet heap doesn’t contain much interesting data, a heap memory corruption that affects chunk headers could still be used to compromise the VirtualBox process rather easily.

## The Vulnerability

In [changeset 23155](https://github.com/VirtualBox/virtualbox/commit/cd68926f500fe93c6fe4a33992201039eac526e9), the following code was added at the top of `ip_input()`, the method that handles incoming IP packets coming from the VM, before any validation has been performed on the IP headers. `m` points to the buffer structure containing the packet data pointer and the actual length of the packet data, `ip` points to the IP header inside the untrusted packet data. `RT_N2H_U16()` performs an endianness conversion.

```
if (m->m_len != RT_N2H_U16(ip->ip_len))
    m->m_len = RT_N2H_U16(ip->ip_len);
```

This overwrites the trusted buffer length with the contents of the untrusted length field from the IP packet. This is particularly bad because all safety checks assume that m->m\_len is correct - these two added lines basically make all following length checks useless.

Later, in [changeset 59063](https://github.com/VirtualBox/virtualbox/commit/b25d7cade21993266954de30b015310f23b9774d), the following comment was added on top of those lines:

```
/*
* XXX: TODO: this is most likely a leftover spooky action at
* a distance from alias_dns.c host resolver code and can be
* g/c'ed.
*/
if (m->m_len != RT_N2H_U16(ip->ip_len))
    m->m_len = RT_N2H_U16(ip->ip_len);
```

One straightforward way to abuse this issue is to send a small `ICMP_ECHO` packet with a large `ip_len` to the address 10.0.2.3, causing Slirp to send back a larger `ICMP_ECHOREPLY` with out-of-bounds heap data. However, Slirp validates the correctness of the ICMP checksum, meaning that the attacker has to guess the 16-bit checksum of the out-of-bounds heap data that the attacker is trying to leak. While it is possible to bruteforce this checksum, it is inelegant.

An easier way to leak heap data is to use UDP with the help of a helper machine on the other side of the NAT, e.g. on the internet. UDP has a 16-bit checksum over packet data as well, but unlike ICMP, UDP treats the checksum value 0 as “don’t check the checksum”. Therefore, by sending a UDP packet with checksum 0 and a bogus length in the IP header, it is possible to reliably leak out-of-bounds heap data. Since `ip_len` can be bigger than the chunk size, this also permits leaking the headers (and contents) of following chunks, disclosing information about the heap state, the heap location and the location of the `struct uma_zone`.

The next step is to somehow use the bug to corrupt chunk headers. Most of the code only reads from incoming packets; however, when a packet with IP options arrives in `udp_input()` or `tcp_input()`, the IP payload (meaning the TCP or UDP packet header and everything following it) is moved over the IP options using `ip_stripoptions()`:

```
void ip_stripoptions(struct mbuf *m, [...])
{
    register int i;
    struct ip *ip = mtod(m, struct ip *);
    register caddr_t opts;
    int olen;
    NOREF(mopt); /** @todo do we really will need this options buffer? */

    olen = (ip->ip_hl<<2) - sizeof(struct ip);
    opts = (caddr_t)(ip + 1);
    i = m->m_len - (sizeof(struct ip) + olen);
    memcpy(opts, opts  + olen, (unsigned)i);
    m->m_len -= olen;

    ip->ip_hl = sizeof(struct ip) >> 2;
}
```

This means that, by sending a TCP or UDP packet with IP options and a bogus length that is bigger than a heap chunk, it is possible to move the packet payload of the following heap chunk over the corresponding heap chunk header.

## Exploitation: Going up to host userspace

In this part of the post, I’m going to show how it’s possible to break out of the VM and run arbitrary shell commands on the host system using `system()`.

Assuming that a sufficiently big portion of the packet heap is unused, the behavior of the allocator can be simplified by allocating all fragmented heap memory, leaving only a pristine freelist that linearly allocates downwards (as shown at the top of the post). Heap chunks can be allocated by sending IP packets with the “more fragments” bit set; such IP packets have to be stored in memory until either the remaining fragments have been received or the maximum number of pending fragments is reached. An attack that is optimized for maximum reliability would probably go a more complex route and use an approach that still works with an arbitrarily fragmented heap.

The first step is to place the command that should be given to `system()` in memory and determine at which address it was placed. To do this, assuming that the freelist grows downwards linearly, the attacker can first send an IP fragment containing the shell command (causing the IP fragment to be stored), then send a crafted UDP packet to leak data:

![](<Base64-Image-Removed>)

(Note: `le_prev` and `le_next` are now pointers on the list of used heap chunks (`free_items`), not the freelist, and therefore the `le_next` pointer points upwards.)

While the leaked data does not contain a pointer to the chunk containing the shell command, it contains pointers to the adjacent chunk headers, which can be used to calculate the address of the shell command.

The next big step is to figure out the address of `system()`. Because there is no PLT entry for `system()`, there is no fixed address the attacker can jump to to invoke the function. However, using the contents of the global offset table, an attacker can first compute the offsets between libc symbols and use them to identify the libc version, then use a GOT entry and the known offset of `system()` relative to the address the GOT entry points to in that libc version to compute the address of `system()`. Unfortunately, there seems to be no nice way to directly read from the GOT using the bug, so this has to be done in a somewhat ugly way.

It is possible to use the bug as a write primitive by calling `memcpy()` as described in the section “The packet heap in VirtualBox”. In general, functions can be called using the bug as follows:

First, the attacker places a fake `struct uma_zone` (zone header) in memory and determines the address of the fake `struct uma_zone`, just like the shell command was placed in memory. Next, the attacker sends a packet containing a fake `struct vmox_heap_item` (chunk header) and moves it over the real chunk header using an adjacent UDP packet with a bogus length field and with IP options:

![](<Base64-Image-Removed>)

The result is a chunk with an attacker-controlled header that points to the fake `struct uma_zone`:

![](<Base64-Image-Removed>)

Next, this chunk can be freed by sending a corresponding second IP fragment, causing the member `pfFini` of the fake `uma_zone` to be called with arguments `zone->pData` (attacker-controlled), `item` (the data directly behind the fake chunk header) and `zone->size` (again attacker-controlled).

In the case of `memcpy()`, one issue here is that the fake IP header must be valid; otherwise, the packet might not be recognized during fragment reassembly. Therefore, only the space that would normally be occupied by the ethernet header (14 bytes long) can be used to store the payload; to write larger payloads, multiple function calls must be made.

At this point, using the write primitive, it is possible to leak the GOT contents by overwriting memory as follows (red parts are modified):

![](<Base64-Image-Removed>)

First, a fake heap chunk header is placed at the start of the GOT, which is writable and at a fixed address. Because after the VirtualBox process has started, only library code is executed, the corruption of the start of the GOT is not a problem. The `le_next` pointer of the fake chunk header points to a legitimate chunk that is currently in a pristine area of the original freelist. Now, the attacker can overwrite the freelist head pointer `free_items.lh_first` in the zone header, causing the fake chunk in the GOT to be returned by a legitimate future allocation.

At this point, the attacker can send another UDP packet with a bogus length field in the IP header. This UDP packet will be placed at the start of the GOT, and out-of-bounds data behind the packet will leak - in other words, the remaining normal GOT entries.

At this point, the attacker can determine the location of `system()` and call `system()` with a fully controlled argument.

## Conclusion \[from the future\]

As I noted in the introduction, none of the relevant code seems to have changed much since I found this bug in 2017 - I think if you found a similar bug in the VirtualBox networking code today, it would likely still be exploitable in a similar way.

VirtualBox uses a separate memory region for packet memory allocations - that’s probably intended as a performance optimization. This implementation choice should also make it harder to exploit packet memory UAF bugs as a side effect, since no packets contain pointers, kind of like PartitionAlloc or kalloc\_type. However, it might still be possible to exploit a packet memory UAF as TOCTOU by making use of an already-validated length value or such.

This could have also made it harder to exploit packet memory linear OOB write bugs - but the choice of using inline metadata, and not protecting against corruption of this metadata at all, makes OOB write bugs in this allocator region highly exploitable.