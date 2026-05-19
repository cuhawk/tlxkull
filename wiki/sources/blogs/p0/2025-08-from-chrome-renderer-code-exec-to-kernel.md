---
source: p0
source_url: https://projectzero.google/2025/08/from-chrome-renderer-code-exec-to-kernel.html
title: "From Chrome renderer code exec to kernel with MSG_OOB - Project Zero"
description: "IntroductionIn early June, I was reviewing a new Linux kernel feature when I learned about the MS..."
---

## Introduction

In early June, I was reviewing a new Linux kernel feature when I learned about the `MSG_OOB` feature supported by stream-oriented UNIX domain sockets. I reviewed the implementation of `MSG_OOB`, and discovered [a security bug](https://project-zero.issues.chromium.org/issues/423023990) (CVE-2025-38236) affecting Linux >=6.9. I reported the bug to Linux, and it [got fixed](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=32ca245464e1479bfea8592b9db227fdc1641705). Interestingly, while the `MSG_OOB` feature is not used by Chrome, it was exposed in the Chrome renderer sandbox. (Since then, sending `MSG_OOB` messages [has been blocked in Chrome renderers](https://chromium-review.googlesource.com/c/chromium/src/+/6711812) in response to this issue.)

The bug is pretty easy to trigger; the following sequence results in UAF:

```
char dummy;
int socks[2];
socketpair(AF_UNIX, SOCK_STREAM, 0, socks);
send(socks[1], "A", 1, MSG_OOB);
recv(socks[0], &dummy, 1, MSG_OOB);
send(socks[1], "A", 1, MSG_OOB);
recv(socks[0], &dummy, 1, MSG_OOB);
send(socks[1], "A", 1, MSG_OOB);
recv(socks[0], &dummy, 1, 0);
recv(socks[0], &dummy, 1, MSG_OOB);
```

I was curious to explore how hard it is to actually exploit such a bug from inside the Chrome Linux Desktop renderer sandbox on an x86-64 Debian Trixie system, escalating privileges directly from native code execution in the renderer to the kernel. Even if the bug is reachable, how hard is it to find useful primitives for heap object reallocation, delay injection, and so on?

The exploit code [is posted on our bugtracker](https://project-zero.issues.chromium.org/423023990#attachment67577205); you may want to reference it while following along with this post.

## Backstory: The feature

Support for using `MSG_OOB` with `AF_UNIX` stream sockets was added in 2021 with [commit 314001f0bf92 (“af\_unix: Add OOB support”, landed in Linux 5.15)](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=314001f0bf92). With this feature, it is possible to send a single byte of “out-of-band” data that the recipient can read ahead of the rest of the data. The feature is very limited - out-of-band data is always a single byte, and there can only be a single pending byte of out-of-band data at a time. (Sending two out-of-band messages one after another causes the first one to be turned into a normal in-band message.) This feature is used almost nowhere except in Oracle products, as discussed on [an email thread](https://lore.kernel.org/netdev/bef45d8e-35b7-42e4-bf6c-768da5b6d8f2@oracle.com/) from 2024 where removal of the feature was proposed; yet it is enabled by default when `AF_UNIX` socket support is enabled in the kernel config, and it wasn’t even possible to disable `MSG_OOB` support until [commit 5155cbcdbf03 (“af\_unix: Add a prompt to CONFIG\_AF\_UNIX\_OOB”)](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5155cbcdbf03f207095f9a3794942a25aa7e5f58) landed in December 2024.

Because the Chrome renderer sandbox allows stream-oriented UNIX domain sockets and didn’t filter the `flags` arguments of `send()`/`recv()` functions, this esoteric feature was usable inside the sandbox.

When a message (represented by a socket buffer / `struct sk_buff`, short SKB) is sent between two connected stream-oriented sockets, the message is added to the `->sk_receive_queue` of the receiving socket, which is a linked list. An SKB has a length field `->len` describing the length of data contained within it (counting both data in the SKB’s “head buffer” as well as data indirectly referenced by the SKB in other ways). An SKB also contains some scratch space that can be used by the subsystem currently owning the SKB (`char cb[48]` in `struct sk_buff`); UNIX domain sockets access this scratch space with the helper `#define UNIXCB(skb)	(*(struct unix_skb_parms *)&((skb)->cb))`, and one of the things they store in there is a field `u32 consumed` which stores the number of bytes of the SKB that have already been read from the socket. UNIX domain sockets count the remaining length of an SKB with the helper `unix_skb_len()`, which returns `skb->len - UNIXCB(skb).consumed`.

`MSG_OOB` messages (sent with something like `send(sockfd, &message_byte, 1, MSG_OOB)`, which goes through `queue_oob()` in the kernel) are also added to the `->sk_receive_queue` just like normal messages; but to allow the receiving socket to access the latest out-of-band message ahead of the rest of the queue, the `->oob_skb` pointer of the receiving socket is updated to point to this message. When the receiving socket receives an OOB message with something like `recv(sockfd, &received_byte, 1, MSG_OOB)` (implemented in `unix_stream_recv_urg()`), the corresponding socket buffer stays on the `->sk_receive_queue`, but its `consumed` field is incremented, causing its remaining length (`unix_skb_len()`) to become 0, and the `->oob_skb` pointer is cleared; the normal receive path will have to deal with this when encountering the remaining-length-0 SKB.

This means that the normal `recv()` path (`unix_stream_read_generic()`), which runs when `recv()` is called without `MSG_OOB`, must be able to deal with remaining-length-0 SKBs and must take care to clear the `->oob_skb` pointer when it deletes an OOB SKB. `manage_oob()` is supposed to take care of this. Essentially, when the normal receive path obtains an SKB from the `->sk_receive_queue`, it calls `manage_oob()` to take care of all the fixing-up required to deal with the OOB mechanism; `manage_oob()` will then return the first SKB that contains at least 1 byte of remaining data, and `manage_oob()` ensures that this SKB is no longer referenced as `->oob_skb`. `unix_stream_read_generic()` can then proceed as if the OOB mechanism didn’t exist.

## Backstory: The bug, and what led to it

In mid-2024, a userspace API inconsistency was discovered, where `recv()` could spuriously return 0 (which normally signals end-of-file) when trying to read from a socket with a receive queue that contains a remaining-length-0 SKB left behind by receiving an OOB SKB. [The fix for this issue](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=93c99f21db36) introduced two closely related security issues that can lead to UAF; it was marked as fixing a bug introduced by the original `MSG_OOB` implementation, but luckily was actually only backported to Linux 6.9.8, so the buggy fix did not land in older LTS kernel branches.

After the buggy fix, `manage_oob()` looked as follows:

```
static struct sk_buff *manage_oob(struct sk_buff *skb, struct sock *sk,
                                  int flags, int copied)
{
        struct unix_sock *u = unix_sk(sk);

        if (!unix_skb_len(skb)) {
                struct sk_buff *unlinked_skb = NULL;

                spin_lock(&sk->sk_receive_queue.lock);

                if (copied) {
                        skb = NULL;
                } else if (flags & MSG_PEEK) {
                        skb = skb_peek_next(skb, &sk->sk_receive_queue);
                } else {
                        unlinked_skb = skb;
                        skb = skb_peek_next(skb, &sk->sk_receive_queue);
                        __skb_unlink(unlinked_skb, &sk->sk_receive_queue);
                }

                spin_unlock(&sk->sk_receive_queue.lock);

                consume_skb(unlinked_skb);
        } else {
                struct sk_buff *unlinked_skb = NULL;

                spin_lock(&sk->sk_receive_queue.lock);

                if (skb == u->oob_skb) {
                        if (copied) {
                                skb = NULL;
                        } else if (!(flags & MSG_PEEK)) {
                                if (sock_flag(sk, SOCK_URGINLINE)) {
                                        WRITE_ONCE(u->oob_skb, NULL);
                                        consume_skb(skb);
                                } else {
                                        __skb_unlink(skb, &sk->sk_receive_queue);
                                        WRITE_ONCE(u->oob_skb, NULL);
                                        unlinked_skb = skb;
                                        skb = skb_peek(&sk->sk_receive_queue);
                                }
                        } else if (!sock_flag(sk, SOCK_URGINLINE)) {
                                skb = skb_peek_next(skb, &sk->sk_receive_queue);
                        }
                }

                spin_unlock(&sk->sk_receive_queue.lock);

                if (unlinked_skb) {
                        WARN_ON_ONCE(skb_unref(unlinked_skb));
                        kfree_skb(unlinked_skb);
                }
        }
        return skb;
}
```

After this change, syzbot (the public syzkaller instance operated by Google) [reported](https://lore.kernel.org/netdev/00000000000083b05a06214c9ddc@google.com/) that a use-after-free occurs in the following scenario, as described by [the fix commit for the syzbot-reported issue](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5aa57d9f2d53):

```
  1. send(MSG_OOB)
  2. recv(MSG_OOB)
     -> The consumed OOB remains in recv queue
  3. send(MSG_OOB)
  4. recv()
     -> manage_oob() returns the next skb of the consumed OOB
     -> This is also OOB, but unix_sk(sk)->oob_skb is not cleared
  5. recv(MSG_OOB)
     -> unix_sk(sk)->oob_skb is used but already freed
```

In other words, the issue is that when the receive queue looks like this (shown with the oldest message at the top):

- SKB 1: `unix_skb_len()=0`
- SKB 2: `unix_skb_len()=1  <--OOB pointer`

and a normal `recv()` happens, then `manage_oob()` takes the `!unix_skb_len(skb)` branch, which deletes the SKB with remaining length 0 and skips forward to the following SKB; but it then doesn’t go through the `skb == u->oob_skb` check as it otherwise would, which means it doesn’t clear out the `->oob_skb` pointer before the SKB is consumed by the normal receive path, creating a dangling pointer that will lead to UAF on a subsequent `recv(... MSG_OOB)`.

This issue was fixed, making the checks for remaining-length-0 SKBs and `->oob_skb` in `manage_oob()` independent:

```
static struct sk_buff *manage_oob(struct sk_buff *skb, struct sock *sk,
                                  int flags, int copied)
{
        struct sk_buff *read_skb = NULL, *unread_skb = NULL;
        struct unix_sock *u = unix_sk(sk);

        if (likely(unix_skb_len(skb) && skb != READ_ONCE(u->oob_skb)))
                return skb;

        spin_lock(&sk->sk_receive_queue.lock);

        if (!unix_skb_len(skb)) {
                if (copied && (!u->oob_skb || skb == u->oob_skb)) {
                        skb = NULL;
                } else if (flags & MSG_PEEK) {
                        skb = skb_peek_next(skb, &sk->sk_receive_queue);
                } else {
                        read_skb = skb;
                        skb = skb_peek_next(skb, &sk->sk_receive_queue);
                        __skb_unlink(read_skb, &sk->sk_receive_queue);
                }

                if (!skb)
                        goto unlock;
        }

        if (skb != u->oob_skb)
                goto unlock;

        if (copied) {
                skb = NULL;
        } else if (!(flags & MSG_PEEK)) {
                WRITE_ONCE(u->oob_skb, NULL);

                if (!sock_flag(sk, SOCK_URGINLINE)) {
                        __skb_unlink(skb, &sk->sk_receive_queue);
                        unread_skb = skb;
                        skb = skb_peek(&sk->sk_receive_queue);
                }
        } else if (!sock_flag(sk, SOCK_URGINLINE)) {
                skb = skb_peek_next(skb, &sk->sk_receive_queue);
        }

unlock:
        spin_unlock(&sk->sk_receive_queue.lock);

        consume_skb(read_skb);
        kfree_skb(unread_skb);

        return skb;
}
```

But a remaining issue is that when this function discovers a remaining-length-0 SKB left behind by `recv(..., MSG_OOB)`, it skips ahead to the next SKB _and assumes that it is not also a remaining-length-0 SKB_. If this assumption is broken, `manage_oob()` can return a pointer to the second remaining-length-0 SKB, which is bad because the caller `unix_stream_read_generic()` does not expect to see remaining-length-0 SKBs:

```
static int unix_stream_read_generic(struct unix_stream_read_state *state,
                                    bool freezable)
{
[...]
        int flags = state->flags;
[...]
        int skip;
[...]
        skip = max(sk_peek_offset(sk, flags), 0); // 0 if MSG_PEEK isn't set

        do {
                struct sk_buff *skb, *last;
[...]
                last = skb = skb_peek(&sk->sk_receive_queue);
                last_len = last ? last->len : 0;

again:
#if IS_ENABLED(CONFIG_AF_UNIX_OOB)
                if (skb) {
                        skb = manage_oob(skb, sk, flags, copied);
                        if (!skb && copied) {
                                unix_state_unlock(sk);
                                break;
                        }
                }
#endif
                if (skb == NULL) {
[...]
                }

                while (skip >= unix_skb_len(skb)) {
                        skip -= unix_skb_len(skb);
                        last = skb;
                        last_len = skb->len;
                        skb = skb_peek_next(skb, &sk->sk_receive_queue);
                        if (!skb)
                                goto again;
                }
[...]
                /* Mark read part of skb as used */
                if (!(flags & MSG_PEEK)) {
                        UNIXCB(skb).consumed += chunk;
[...]
                        if (unix_skb_len(skb))
                                break;

                        skb_unlink(skb, &sk->sk_receive_queue);
                        consume_skb(skb); // frees the SKB

                        if (scm.fp)
                                break;
                } else {
```

If `MSG_PEEK` is not set (which is the only case in which SKBs can actually be freed), `skip` is always 0, and the `while (skip >= unix_skb_len(skb))` loop condition should always be false; but when a remaining-length-0 SKB unexpectedly gets here, the condition turns into `0 >= 0`, and the loop skips ahead to the first SKB that does not have remaining length 0. That SKB could be the `->oob_skb`; in which case this again bypasses the logic in `manage_oob()` that is supposed to set `->oob_skb` to NULL before the current `->oob_skb` can be freed.

So the remaining bug can be triggered by first doing the following twice, creating two remaining-length-0 SKBs in the `->sk_receive_queue`:

```
send(socks[1], "A", 1, MSG_OOB);
recv(socks[0], &dummy, 1, MSG_OOB);
```

If another OOB SKB is then sent with `send(socks[1], "A", 1, MSG_OOB)`, the `->sk_receive_queue` will look like this:

- SKB 1: `unix_skb_len()=0`
- SKB 2: `unix_skb_len()=0`
- SKB 3: `unix_skb_len()=1  <--OOB pointer`

Now, `recv(socks[0], &dummy, 1, 0)` will trigger the bug and free SKB 3 while leaving `->oob_skb` pointing to it; making it possible for subsequent `recv()` syscalls with `MSG_OOB` to use the dangling pointer.

## The initial primitive

This bug yields a dangling `->msg_oob` pointer. Pretty much the only way to use that dangling pointer is the `recv()` syscall with `MSG_OOB`, either with or without `MSG_PEEK`, which is implemented in `unix_stream_recv_urg()`. (There are other codepaths that touch it, but they’re mostly just pointer comparisons, with the exception of the `unix_ioctl()` handler for `SIOCATMARK`, which is blocked in Chrome’s seccomp sandbox.)

`unix_stream_recv_urg()` does this:

```
static int unix_stream_recv_urg(struct unix_stream_read_state *state)
{
        struct socket *sock = state->socket;
        struct sock *sk = sock->sk;
        struct unix_sock *u = unix_sk(sk);
        int chunk = 1;
        struct sk_buff *oob_skb;

        mutex_lock(&u->iolock);
        unix_state_lock(sk);
        spin_lock(&sk->sk_receive_queue.lock);

        if (sock_flag(sk, SOCK_URGINLINE) || !u->oob_skb) {
[...]
        }

        // read dangling pointer
        oob_skb = u->oob_skb;

        if (!(state->flags & MSG_PEEK))
                WRITE_ONCE(u->oob_skb, NULL);

        spin_unlock(&sk->sk_receive_queue.lock);
        unix_state_unlock(sk);

        // read primitive
        // ->recv_actor() is unix_stream_read_actor()
        chunk = state->recv_actor(oob_skb, 0, chunk, state);

        if (!(state->flags & MSG_PEEK))
                UNIXCB(oob_skb).consumed += 1; // write primitive

        mutex_unlock(&u->iolock);

        if (chunk < 0)
                return -EFAULT;

        state->msg->msg_flags |= MSG_OOB;
        return 1;
}
```

At a high level, the call to `state->recv_actor()` (which goes down the call path `unix_stream_read_actor -> skb_copy_datagram_msg -> skb_copy_datagram_iter -> __skb_datagram_iter(cb=simple_copy_to_iter)`) gives a read primitive: it is trying to copy one byte of data referenced by the `oob_skb` to userspace, so by replacing the memory pointed to by `oob_skb` with controlled, repeatedly writable data, it is possible to repeatedly cause `copy_to_user(<userspace pointer>, <kernel pointer>, 1)` with arbitrary kernel pointers. As long as `MSG_PEEK` is set, this can be repeated; only when `MSG_PEEK` is clear, the `->msg_oob` pointer is cleared.

The only _write_ primitive this bug yields is the increment `UNIXCB(oob_skb).consumed += 1` that happens when `MSG_PEEK` is not set. In the build I’m looking at, the `consumed` field that is incremented is located 0x44 bytes into the `oob_skb`, an object which is effectively allocated with an alignment of 0x100 bytes. This means that, if the write primitive is applied to a 64-bit length value or a pointer, it would have to do an increment at offset 4 relative to the 8-byte aligned overwrite target, and it would effectively increment the 64-bit pointer/length by 4 GiB.

## My exploit for this issue

### Discarded strategy for using the write primitive: Pointer increment

It would be possible to free the `sk_buff` and reallocate it as some structure containing a pointer at offset 0x40. The write primitive would effectively increment this pointer by 4 GiB (because it would increment by 1 at an offset 4 bytes into the pointer). But this would fundamentally rely on the machine having significantly more than 4 GiB of RAM, which feels gross and a bit like cheating.

### Overall strategy

Since this issue relatively straightforwardly leads to a semi-arbitrary read (subject to usercopy hardening restrictions), but the write primitive is much more gnarly, I decided to go with the general approach of: first get the read primitive working; then use the read primitive to assist in exploiting the write primitive. This way, ideally everything after the read primitive bootstrapping can be made reliable with enough work.

### Dealing with per-cpu state

Lots of things in this exploit rely on per-cpu kernel data structures and will fail if a task is migrated between CPUs at the wrong time. In some places in the exploit, I repeatedly check which CPU the exploit is running on with `sched_getcpu()`, and retry if the CPU number changed; though I was too lazy to do that everywhere perfectly, and this could be done even better by relying more directly on the [“restartable sequences” subsystem](https://git.kernel.org/pub/scm/libs/librseq/librseq.git/tree/doc/man/rseq.2).

Note that the Chrome sandbox policy forbids `__NR_getcpu`; but that has no effect at all on `sched_getcpu()`, in particular on x86-64, because [there are two faster alternatives to the getcpu() syscall that glibc prefers to use instead](https://sourceware.org/git/?p=glibc.git;a=blob;f=sysdeps/unix/sysv/linux/sched_getcpu.c;hb=e85dbd8604aedf4f3a30c6c9c2f0efc18183f270):

- The kernel’s rseq subsystem maintains a `struct rseq` in userspace for each thread, which contains the `cpu_id` that the thread is currently running on; if rseq is available, glibc will read from the rseq struct.
- On x86-64, the [vDSO](https://man7.org/linux/man-pages/man7/vdso.7.html) contains a pure-userspace implementation of the `getcpu()` syscall which relies on either [the `RDPID` instruction](https://www.felixcloutier.com/x86/rdpid) or, if that is not available, [the `LSL` instruction](https://www.felixcloutier.com/x86/lsl) to determine the ID of the current CPU without having to perform a syscall. (This is implemented in `vdso_read_cpunode()` in the kernel sources, which is compiled into the vDSO that is mapped into userspace.)

### Setting up the read primitive - mostly boring spraying

On the targeted Debian kernel, `struct sk_buff` is in the `skbuff_head_cache` SLUB cache, which normally uses order-1 unmovable pages. I had trouble finding a good reallocation primitive that also uses order-1 pages (though `maple_node` might have been an option); so I went for reallocation as a pipe page (order-0 unmovable), though that means that the reallocation will go through the buddy allocator and requires the order-0 unmovable list to become empty so that an order-1 page is split up.

This is not very novel, so I will only describe a few interesting aspects of the strategy here - if you want a better understanding of how to free a SLUB page and reallocate it as something else, there are plenty of existing writeups, including [one I wrote a while ago (section “Attack stage: Freeing the object’s page to the page allocator”)](https://projectzero.google/2021/10/how-simple-linux-kernel-memory.html#:~:text=Attack%20stage%3A%20Freeing%20the%20object%27s%20page%20to%20the%20page%20allocator), though that one does not discuss the buddy allocator.

To make it more likely for a reallocation of an order-1 page as an order-0 page to succeed, the exploit starts by allocating a large number of order-0 unmovable pages to drain the order-0 and order-1 unmovable freelists. Most ways of allocating large amounts of kernel memory are limited in the sandbox; in particular, the default file descriptor table size soft limit (RLIMIT\_NOFILE) is 4096 on Debian (Chrome leaves this limit as-is), and I can neither use `setrlimit()` to bump that number up (due to seccomp) nor create subprocesses with separate file descriptor tables. (A real exploit might be able to work around this by exploiting several renderer processes, though that seems like a pain.) The one primitive I have for allocating large amounts of unmovable pages are page tables: by creating a gigantic anonymous VMA (read-only to avoid running into Chrome’s `RLIMIT_DATA` restrictions) and then triggering read faults all over this VMA, an unlimited number of page tables can be allocated. I use this to spam around 10% of total RAM with page tables. (To figure out how much RAM the machine has, I’m testing whether `mmap()` works with different sizes, relying on the `OVERCOMMIT_GUESS` behavior of `__vm_enough_memory()`; though that doesn’t actually work precisely in the sandbox due to the `RLIMIT_DATA` limit. A cleaner and less noisy way might be to actually fill up RAM and use `mincore()` to figure out how large the working set can get before pages get swapped out or discarded.)

Afterwards, I create 41 UNIX domain sockets and use them to spam 256 SKB allocations each; since each SKB uses 0x100 bytes, this allocates a bit over 2.5 MiB of kernel memory. That is enough to later flush a slab page out of both SLUB’s per-cpu partial list as well as the page allocator’s per-cpu freelist, all the way into the buddy allocator.

Then I set up a SLUB page containing a dangling pointer, try to flush this page all the way into the buddy allocator, and reallocate it as a pipe page by using 256 pipes to each allocate 2 pages (which is the minimum size that a pipe always has, see `PIPE_MIN_DEF_BUFFERS`). This allocates 256 _2_ 4KiB = 2 MiB worth of order-0 pages.

At this point, I have probably reallocated the SKB as a pipe page; but I don’t know in which pipe the SKB is located, or at which offset. To figure that out, I store fake SKBs in the pipe pages that point to different data; then, by triggering the bug with `recv(..., MSG_OOB|MSG_PEEK)`, I can read one byte at the pointed-to location and narrow down where in which pipe the SKB is. I don’t know the addresses of any kernel objects yet; but the X86-64 implementation of `copy_to_user()` is symmetric and also works if you pass a userspace pointer as the source, so I can simply use userspace data pointers in the crafted SKBs for now. (SMAP is not an issue here - SMAP is disabled for all memory accesses in `copy_to_user()`. On x86-64, `copy_to_user()` is actually implemented as a wrapper around `copy_user_generic()`, which is a helper that accepts both kernel and userspace addresses as source and destination.)

Afterwards, I have the ability to call `copy_to_user(..., 1)` on arbitrary kernel pointers through `recv(..., MSG_OOB|MSG_PEEK)` using the controlled SKB.

### Properties of the read primitive

One really cool aspect of a `copy_to_user()`-based read primitive on x86-64 is that it doesn’t crash even when called on invalid kernel pointers - if the kernel memory access fails, the `recv()` syscall will simply return an error (`-EFAULT`).

The main limitation is that usercopy hardening (`__check_object_size()`) will catch attempts to read from some specific memory ranges:

- Ranges that wrap around - not an issue here, only ranges of length 1 can be used anyway.
- Addresses `<=16` \- not an issue here.
- The kernel stack of the current process, if some other criteria are met. Not an issue here - even if I want to read from a kernel stack, I’ll probably want to read the kernel stack of another thread, which isn’t protected.
- The kernel `.text` section - all of `.data` and such is accessible, just `.text` is restricted. When targeting a specific kernel build, that’s not really relevant.
- `kmap()` mappings - those don’t exist on x86-64.
- Freed vmalloc allocations, or ranges that straddle the bounds of a vmalloc allocation. Not an issue here.
- Ranges in the direct mapping, or in the kernel image address range, that straddle the bounds of a high-order folio. Not an issue here, only ranges of length 1 can be used anyway.
- Ranges in the direct mapping, or in the kernel image address range, that are used as SLUB pages in non-kmalloc slab caches, at offsets not allowed by usercopy allowlisting (see `__check_heap_object()`). This is the most annoying part.

(There might be other ways of using this bug to read memory with different constraints, like by using the `frag_iter->len` read in `__skb_datagram_iter()` to influence an offset from which known data is subsequently read, but that seems like a pain to work with.)

### Locating the kernel image

To break KASLR of the kernel image at this point, there are lots of options, partially thanks to `copy_to_user()` not crashing on access to invalid addresses; but one nice option is to read an Interrupt Descriptor Table (IDT) entry through the read-only IDT mapping at the fixed address `0xfffffe0000000000` (`CPU_ENTRY_AREA_RO_IDT_VADDR`), which yields the address of a kernel interrupt handler.

### Using the read primitive to observe allocator state and other things

From here on, my goal is to use the read primitive to assist in exploiting the write primitive; I would like to be able to answer questions like:

- What is the mapping between `struct page *`/`struct ptdesc *`/`struct slab *` and the corresponding region in the direct mapping? (This is easy and just requires reading some global variables out of the `.data`/`.bss` sections.)
- At which address will the next `sk_buff` allocation be?
- What is the current state of this particular page?
- Where are my page tables located, and which physical address does a given virtual address map to?

Because usercopy hardening blocks access to objects in specialized slabs, reading the contents of a `struct kmem_cache` is not possible, because a `kmem_cache` is allocated from a specialized slab type which does not allow usercopy. But there are many important pieces of kernel memory that are readable, so it is possible to work around that:

- The kernel `.data`/`.bss` sections, which contain things like pointers to `kmem_cache` instances.
- The vmemmap region, which contains all instances of `struct page`/`struct folio`/`struct ptdesc`/`struct slab` (these types all together effectively form a `union`) which describe the status of each page. These also contain things like a SLUB freelist head pointer; a pointer to the `kmem_cache` associated with a given SLUB page; or an intrusive linked list element tying together the root page tables of all processes.
- Kernel stacks of other threads (located in vmalloc memory).
- Per-CPU memory allocations (located in vmalloc memory), which are used in particular for memory allocation fastpaths in SLUB and the page allocator; and also the metadata describing where the per-cpu memory ranges are located.
- Page tables.

So to observe the state of the SLUB allocator for a given slab cache, it is possible to first read the corresponding `kmem_cache*` from the kernel `.data`/`.bss` section, then scan through all per-cpu memory for objects that look like a `struct kmem_cache_cpu` (with a `struct slab *` and a freelist pointer pointing into the corresponding direct mapping range), and check which `kmem_cache` the `struct slab`’s `kmem_cache*` points to to determine whether the `kmem_cache_cpu` is for the right slab cache. Afterwards, the read primitive can be used to read the slab cache’s per-cpu freelist head pointer out of the `struct kmem_cache_cpu`.

To observe the state of a `struct page`/`struct slab`/…, the read primitive can be used to simply read the page’s refcount and mapcount (which contains type information). This makes it possible to observe things like “has this page been freed yet or is it still allocated” and “as what type of page has this page been reallocated”.

To locate the page table root of the current process, it is similarly not possible to directly go through the `mm_struct` because that is allocated from a specialized slab type which does not allow usercopy (except in the `saved_auxv` field). But one way to work around this is to instead walk the global linked list of all root page tables (`pgd_list`), which stores its elements inside `struct ptdesc`, and search for a `struct ptdesc` which has a `pt_mm` field that points to the `mm_struct` of the current process. The address of this `mm_struct` can be obtained from the per-cpu variable `cpu_tlbstate.loaded_mm`. Afterwards, the page tables can be walked through the read primitive.

### Finding a reallocation target: The magic of `CONFIG_RANDOMIZE_KSTACK_OFFSET`

Having already discarded the “bump a pointer by 4 GiB” and “reallocate as a maple tree node” strategies, I went looking for some other allocation which would place an object such that incrementing the value at address 0x…44 leads to a nice primitive. It would be nice to have something there like an important flags field, or a length specifying the size of a pointer array, or something like that. I spent a lot of time looking at various object types that can be allocated on the kernel heap from inside the Chrome sandbox, but found nothing great.

Eventually, I realized that I had been going down the wrong path. Clearly trying to target a heap object was foolish, because there is something much better: It is possible to reallocate the target page as the topmost page of a kernel stack!

That might initially sound like a silly idea; but Debian’s kernel config enables `CONFIG_RANDOMIZE_KSTACK_OFFSET=y` and `CONFIG_RANDOMIZE_KSTACK_OFFSET_DEFAULT=y`, **causing each syscall invocation to randomly shift the stack pointer down by up to 0x3f0 bytes, with 0x10 bytes granularity**. That is supposed to be a security mitigation, but works to my advantage when I already have an arbitrary read: instead of having to find an overwrite target that is at a 0x44-byte distance from the preceding 0x100-byte boundary, I effectively just have to find an overwrite target that is at a 0x4-byte distance from the preceding 0x10-byte boundary, and then keep doing syscalls and checking at what stack depth they execute until I randomly get lucky and the stack lands in the right position.

With that in mind, I went looking for an overwrite target on the stack, strongly inspired by [Seth’s exploit that overwrote a spilled register containing a length used in `copy_from_user`](https://projectzero.google/2022/12/exploiting-CVE-2022-42703-bringing-back-the-stack-attack.html). Targeting a normal `copy_from_user()` directly wouldn’t work here - if I incremented the 64-bit length used inside `copy_from_user()` by 4 GiB, then even if the copy failed midway through due to a userspace fault, `copy_from_user()` would try to `memset()` the remaining kernel memory to zero.

I discovered that, on the codepath `pipe_write -> copy_page_from_iter -> copy_from_iter`, the 64-bit length variable `bytes` of `copy_page_from_iter()` is stored in register `R14`, which is spilled to the stack frame of `copy_from_iter()`; and this stack spill is in a stack location where I can clobber it.

When userspace calls `write()` on a pipe, the kernel constructs an iterator (`struct iov_iter`) that encapsulates the userspace memory range passed to `write()`. (There are different types of iterators that can encapsulate a single userspace range, a set of userspace ranges, or various types of kernel memory.) Then, `pipe_write()` (which is called `anon_pipe_write()` in newer kernels) essentially runs a loop which allocates a new `pipe_buffer` slot in the pipe, places a new page allocation in this pipe buffer slot, and copies up to a page worth of data (`PAGE_SIZE` bytes) from the `iov_iter` to the pipe buffer slot’s page using `copy_page_from_iter()`. `copy_page_from_iter()` effectively receives two length values: The number of bytes that fit into the caller-provided page (`bytes`, initially set to `PAGE_SIZE` here) and the number of bytes available in the `struct iov_iter` encapsulating the userspace memory range (`i->count`). The amount of data that will actually be copied is limited by both.

If I manage to increment the spilled register `R14` which contains `bytes` by 4 GiB while `copy_from_iter()` is busy copying data into the kernel, then after `copy_from_iter()` returns, `copy_page_from_iter()` will effectively no longer be bounded by `bytes`, only by `i->count` (based on the length userspace passed to `write()`); so it will do a second iteration, which copies into out-of-bounds memory behind the pipe buffer page. If userspace calls `write(fd, buf, 0x3000)`, and the overwrite happens in the middle of copying bytes 0x1000-0x1fff of the userspace buffer into the second pipe buffer page, then bytes 0x2000-0x2fff will be written out-of-bounds behind the second pipe buffer page, at which point `i->count` will drop to 0, terminating the operation.

### Reallocating a SLUB page as a stack page, with arb-read assistance

So to get the ability to increment-after-free a value in a stack page, I again start by draining the low-order page allocator caches. But this time, the arb-read can be used to determine when an object at the right in-page offset is at the top of the SLUB freelist for the `sk_buff` slub cache; and the arb-read can also determine whether I managed to allocate an entire slab page worth of objects, with no other objects mixed in. Then, when flushing the page out of the SLUB allocator, the arb-read helps to verify that the page really has been freed (its refcount field should drop to 0); and afterwards, the page is flushed out of the page allocator’s per-cpu freelist.

Then, to reallocate the page, I run a loop that first allocates a pipe page, then checks the refcount field of the target page. If the refcount of the target page goes up, I probably found the target page, and can exit the loop; otherwise, I free the pipe page again, reallocate it as a page table to drain the page away, and try again. (Directly allocating as a page table would be cumbersome because page tables have RCU lifetime, so once a page has been allocated as a page table, it is hard to reallocate it. Keeping drained pages in pipe buffers might not work well due to the low file descriptor table size, and each pipe FD pair potentially only being able to reference two pages.)

Once I have reallocated the target page as a pipe buffer, I free it again, then free three more pages (from other helper pipes), and then create a new thread with the `clone()` syscall. If everything goes well, `clone()` will allocate four pages for the new kernel stack: First the three other pages I freed last, and then the target page as the last page of the stack. By walking the page tables, I can verify that the target page really got reused as the last page of the target stack.

### Remaining prerequisites for using the write primitive

At this point, I have the write primitive set up such that I can trigger it on a specific stack memory location. The write primitive essentially first reads some surrounding (stack) memory (in `unix_stream_read_actor()` and its callees `skb_copy_datagram_msg -> skb_copy_datagram_iter`) and expects that memory to have a certain structure before incrementing the value at a specific stack location.

I also know what stack allocation I want to overwrite.

The remaining issues are:

1. I need to ensure that an OOB `copy_from_user()` behind a pipe buffer page will overwrite some data that helps in compromising the kernel.
2. I need to be able to detect at what stack depth `pipe_write()` is running, and depending on that either try again or proceed to trigger the bug.
3. The UAF reads preceding the UAF increment need to see the right kind of data to avoid crashing.
4. `copy_from_iter()` needs to take enough time to allow me to increment a value in its stack frame.

### Selecting an OOB overwrite target

Page tables have several nice properties here:

- It is easy for me to cause allocation of as many page tables as I want.
- I can easily determine the physical and kernel-virtual addresses of page tables that the kernel has allocated for my process (by walking the page tables with the arb read).
- They are order-0 unmovable allocations, just like pipe buffers, so the page allocator will allocate them in the same 2MiB pageblocks.

So I am choosing to use the OOB `copy_from_user()` to overwrite a page table.

This requires that I can observe where my pipe buffer pages are located; for that, I again use the SLUB per-cpu freelist observing trick, this time on the `kmalloc-cg-192` slab cache, to figure out where a newly created pipe’s `pipe_inode_info` is located. From there, I can walk to the pipe’s `pipe_buffer` array, which contains pointers to the pages used by the pipe.

With the ability to observe both where my page tables are located and where pipe buffer pages are allocated, I can essentially alternatingly allocate page tables and pipe buffer pages until I get two that are adjacent.

### Detecting `pipe_write()` stack depth

To run `pipe_write()` with a `write()` syscall such that I can reliably determine at which depth the function is running and decide whether to go ahead with the corruption, without having to race, I can prepare a pipe such that it initially only has space for one more `pipe_buffer`, and then call `write()` with a length of 0x3000. This will cause `pipe_write()` to first store 0x1000 bytes in the last free `pipe_buffer` slot, then wait for space to become available again. From another thread, it is possible to detect when `pipe_write()` has used the last free `pipe_buffer` slot by repeatedly calling `poll()` on the pipe: When `poll()` stops reporting that the pipe is ready for writing (`POLLOUT`), `pipe_write()` must have used up the last free `pipe_buffer` slot.

At that point, I know that the syscall entry part of the kernel stack is no longer changing. To check whether the syscall is executing at a specific depth, it is enough to check whether the return address for the return from `x64_sys_call` to `do_syscall_64` is at the expected position on the kernel stack using the arb read - it can’t be a return address left from a preceding syscall because the same stack location where that return address is stored is always clobbered by a subsequent call to `syscall_exit_to_user_mode` at the end of a syscall.

If the stack randomization is the correct one, I can then do more setup and resume `pipe_write()` by using `read()` to clear pipe buffer entries; otherwise, I will use `read()` to clear pipe buffer entries, let `pipe_write()` run to completion, and try again.

### Letting the reads in the increment primitive see the right data

The increment primitive happens on this call graph:

```
unix_stream_recv_urg
  [read dangling pointer from ->oob_skb]
  unix_stream_read_actor [called as state->recv_actor]
    [UAF read UNIXCB(skb).consumed]
    skb_copy_datagram_msg
      skb_copy_datagram_iter
        __skb_datagram_iter
          skb_headlen
            [UAF read skb->len]
            [UAF read skb->data_len]
          skb_frags_readable
            [UAF read skb->unreadable]
          skb_shinfo [for reading nr_frags]
            skb_end_pointer
              [UAF read skb->head]
              [UAF read skb->end]
          skb_walk_frags
            skb_shinfo [for reading frag_list]
            [forward iteration starting at skb_shinfo(skb)->frag_list along ->next pointers]
  [UAF increment of UNIXCB(oob_skb).consumed]
```

A promising aspect here is that this codepath first does all the reads; then it does a linked list walk through attacker-controlled pointers with `skb_walk_frags()`; and then it does the write. `skb_walk_frags()` is defined as follows:

```
#define skb_walk_frags(skb, iter)	\
	for (iter = skb_shinfo(skb)->frag_list; iter; iter = iter->next)
```

and is used like this in `__skb_datagram_iter()`:

```
	skb_walk_frags(skb, frag_iter) {
		int end;

		WARN_ON(start > offset + len);

		end = start + frag_iter->len;
		if ((copy = end - offset) > 0) {
			if (copy > len)
				copy = len;
			if (__skb_datagram_iter(frag_iter, offset - start,
						to, copy, fault_short, cb, data))
				goto fault;
			if ((len -= copy) == 0)
				return 0;
			offset += copy;
		}
		start = end;
	}
```

So if I run `recv(..., MSG_OOB)` on the UNIX domain socket while the dangling `->oob_skb` pointer points to data I control, and craft that fake SKB such that its `skb_shinfo(skb)->frag_list` points to another fake SKB with `->len=0` and a `->next` pointer pointing back to itself, I can cause the syscall to get stuck in an infinite loop. It will keep looping until I replace the `->next` pointer with NULL, at which point it will perform just the UAF increment.

This is great news: instead of needing to ensure that the stack contains the right data for the UAF reads and the overwrite target for the UAF increment at the same time, I can first place controlled data on the stack, and then afterwards separately place the overwrite target on the stack.

To place controlled data on the stack, I initially considered using `select()` or `poll()`, since I know that those syscalls copy large-ish amounts of data from userspace onto the stack; however, those have the disadvantage of immediately validating the supplied data, and it would be hard to make them actually stay in the syscall, rather than immediately returning out of the syscall with an error and often clobbering the on-stack data array in the process. Eventually I discovered that `sendmsg()` on a **datagram-oriented UNIX domain socket** works great for this: `___sys_sendmsg()`, which implements the `sendmsg()` syscall, will import the destination address pointed to by `msg->msg_name` into a stack buffer (`struct sockaddr_storage address`), then call into the protocol-specific `->sendmsg` handler - in the case of datagram-oriented UNIX domain sockets, `unix_dgram_sendmsg()`. This function coarsely validates the structure of the destination address (checking that it specifies the `AF_UNIX` family and is no larger than `struct sockaddr_un`), then waits for space to become available in the socket’s queue before doing anything else with the destination address. This makes it possible to place 108 bytes of controlled data on a kernel stack, and that data will stay there until the syscall can continue or bail out when space becomes available in the socket queue or the socket is shut down. I actually need a bit more data on the stack, but luckily the `struct iovec iovstack[UIO_FASTIOV]` is directly in front of the `address`, and unused elements at the end of the `iovstack` are guaranteed to be zeroed thanks to `CONFIG_INIT_STACK_ALL_ZERO=y`, which happens to be exactly what I need.

It would be helpful to be able to reliably wait for the `sendmsg()` syscall to enter the kernel and copy the destination address onto the kernel stack before inspecting the state of its stack; this is luckily possible by supplying a single-byte “control message” via `msg->msg_control` and `msg->msg_controllen`, which will mostly be ignored because it is too small to be a legitimate control message, but will be copied onto the kernel stack in `____sys_sendmsg()` after the destination address has been copied onto the stack. It is possible to detect from userspace when this kernel access to `msg->msg_control` happens by pointing it to a userspace address which is not yet populated with a page table entry, then polling [`mincore()`](https://man7.org/linux/man-pages/man2/mincore.2.html) on this userspace address.

So now my strategy is roughly:

1. In a loop, call `sendmsg()` on the thread with the stack the dangling `->oob_skb` pointer points to to place a fake SKB on the stack until the fake SKB lands at the right stack offset thanks to `CONFIG_RANDOMIZE_KSTACK_OFFSET`, and have that fake SKB’s `skb_shinfo(skb)->frag_list` point to a second fake SKB with a `->next` pointer that refers back to itself. (This second fake SKB can be placed anywhere I want, so I’m putting it in a userspace-owned page, so that userspace can directly write into it.)
2. On a second thread, use `write()` on a UNIX domain socket to use the dangling `->oob_skb` pointer, which will start looping endlessly, following the `->next` pointer.
3. On the thread that called `sendmsg()` before, now call `write(..., 0x3000)` on a pipe with one free `pipe_buffer` slot in a loop until the syscall handler lands at the right stack offset thanks to `CONFIG_RANDOMIZE_KSTACK_OFFSET`.
4. Let the pipe `write()` continue, and wait until it is in the middle of copying data from userspace memory to a pipe buffer page.
5. Set the `->next` pointer in the second fake SKB to `NULL`, so that the `write()` on the UNIX domain socket stops looping, performs the UAF increment, and returns.
6. Wait for the pipe `write()` to finish, at which point the page table behind the pipe data page should have been overwritten with controlled data.

### Slowing down `copy_from_iter()`

I need to slow down a `copy_from_iter()` call. There are several strategies for this that don’t work (or don’t work well) in a Chrome renderer sandbox:

- **userfaultfd**: not accessible in the Chrome _Desktop_ renderer sandbox, and nowadays usually anyways nerfed such that only root can use it to intercept usercopy operations
- [**FUSE**](https://projectzero.google/2016/06/exploiting-recursion-in-linux-kernel_20.html#:~:text=pause%20the%20kernel%20thread): not accessible in the Chrome Desktop renderer sandbox
- [**causing lots of major page faults**](https://static.sched.com/hosted_files/lsseu2019/04/LSSEU2019%20-%20Exploiting%20race%20conditions%20on%20Linux.pdf#page=30): I’m not sure if there is some indirect way to get a file descriptor to a writable on-disk file; but either way, this seems like it would be a pain from a renderer.

But as long as only a single userspace memory read needs to be delayed, there is another option: I can create a very large anonymous VMA; fill it with mappings of the 4KiB zeropage; ensure that no page is mapped at one specific location in the VMA (for example with `madvise(..., MADV_DONTNEED)`, which zaps page table entries in the specified range); and then have one thread run an `mprotect()` operation on this large anonymous VMA while another thread tries to access the part of the userspace region where no page is currently mapped. The `mprotect()` operation will keep the VMA write-locked while it walks through all the associated page table entries, modifies the page table entries as required, and performs TLB flushes if necessary; so a concurrent page fault in this VMA will have to wait until the `mprotect()` has finished. One limitation of this technique is that the part of the accessed userspace range that causes the slowdown will be filled with zeroes; but that can just be a single byte at the start or end of the range being copied, so it’s not a major limitation.

Based on some rough testing on my machine, if `mprotect()` has to iterate through 128 MiB of page tables populated with zeropage mappings, it takes something like 500-1000ms depending on which way the page table entries are changed.

### Page table control

Putting all this together, I can overwrite the contents of a page table with controlled data. I’m using that controlled write to place a new entry in the page table that points back to the page table, effectively creating a userspace mapping of the page table; and then I can use this to map arbitrary kernel memory writably into userspace.

My exploit demonstrates its ability to modify kernel memory with this by using it to overwrite the UTS information printed by `uname`.

## Takeaway: Chrome sandbox attack surface

One thing that stood out to me about this is that I was able to use a somewhat large number of kernel interfaces in this exploit; in particular:

| interface | usecase |
| --- | --- |
| anonymous VMA creation | page table allocations |
| `madvise()` | fast VMA splitting and merging |
| `AF_UNIX``SOCK_STREAM` sockets | triggering the bug; SKB allocation and freeing |
| `sched_getcpu()` (via syscall-less fastpaths) | interacting with per-cpu kernel structures |
| `eventfd()` | synchronization between threads |
| `pipe()` | allocation and freeing of order-0 unmovable pages with controlled contents |
| `pipe()` | stack overwrite target |
| `AF_UNIX``SOCK_DGRAM` sockets | placing controlled data on the stack |
| `sendmsg()` | placing controlled data on the stack |
| `mprotect()` | slowing down `copy_from_user()` |
| `munmap()` | TLB flushing |
| `madvise(..., MADV_DONTNEED)` | zapping PTEs for slowing down subsequent `copy_from_user()` or subsequently detecting `copy_from_user()` |
| `mincore()` | detecting `copy_from_user()` |
| `clone()` | racing operations on multiple threads; reallocating pages as kernel stack |
| `poll()` | detecting progress of concurrent `pipe_write()` |

Some of these are obviously needed to implement necessary features of the sandboxed renderer; others seem like unnecessary attack surface. I hope to look at this more systematically in the future.

## Takeaway: Esoteric kernel features in core interfaces are an issue for browser sandboxes

One thing I’ve noticed, not just with this issue, but several issues before that, is that core kernel subsystems (which are exposed in renderer sandbox policies and such) sometimes have flags that trigger esoteric ancillary features that are unintentionally exposed by Chrome’s renderer sandbox. Such features seem to often be more buggy than the core feature that the policy intended to expose. Examples of this from Chrome’s past include:

- `futex()` was broadly exposed in the sandbox, making it possible to reach [a bug in Priority Inheritance futexes](https://issues.chromium.org/issues/40079619) from the renderer sandbox.
- `memfd_create()` [was exposed in the sandbox without checking its flags](https://chromium-review.googlesource.com/c/chromium/src/+/6712032), making it possible to create HugeTLB mappings using the `MFD_HUGETLB` flag. There have been several bugs in HugeTLB, which is to my knowledge almost exclusively used by some server applications that use large amounts of RAM, such as databases.
- `pipe2()` [was exposed in the sandbox without checking its flags](https://chromium-review.googlesource.com/c/chromium/src/+/4128252), making it possible to create “notification pipes” using the `O_NOTIFICATION_PIPE` flag, which behave very differently from normal pipes and are used exclusively for posting notifications from the kernel “keys” subsystem to userspace.

## Takeaway: probabilistic mitigations against attackers with arbitrary read

When faced with an attacker who already has an arbitrary read primitive, probabilistic mitigations that randomize something differently on every operation can be ineffective if the attacker can keep retrying until the arbitrary read confirms that the randomization picked a suitable value or even work to the attacker’s advantage by lining up memory locations that could otherwise never overlap, as done here using the kernel stack randomization feature.

Picking per-syscall random stack offsets at boottime might avoid this issue, since to retry with different offsets, the attacker would have to wait for the machine to reboot or try again on another machine. However, that would break the protection for cases where the attacker wants to line up two syscalls that use the same syscall number (such as different `ioctl()` calls); and it could also weaken the protection in cases where the attacker just needs to know what the randomization offset for some syscall will be.

Somewhat relatedly, [Blindside](https://www.vusec.net/projects/blindside/) demonstrated that this style of attack can be pulled off without a normal arbitrary read primitive, by “exploiting” a real kernel memory corruption bug during speculative execution in order to leak information needed for subsequently exploiting the same memory corruption bug for real.

## Takeaway: syzkaller fuzzing and complex data structures

The first memory corruption bug described in this post was introduced in late June 2024, and discovered by syzkaller in late August 2024. Hitting that bug required 6 syscalls: One to set up a socket pair, four `send()`/`recv()` calls to set up a dangling pointer, and one more `recv()` call to actually trigger UAF by accessing the dangling pointer.

Hitting the second memory corruption bug, which I found by code review, required 8 syscalls: One to set up a socket pair, six `send()`/`recv()` calls to set up a dangling pointer, and one more `recv()` to cause UAF.

This was not a racy bug; in a KASAN build, running the buggy syscall sequence once would be enough to get a kernel splat. But when a fuzzer chains together syscalls more or less at random, the chance of running the right sequence of syscalls drops exponentially with each syscall required…

The most important takeaway from this is that data structures with complex safety rules (in this case, rules about the ordering of different types of SKBs in the receive queues of UNIX domain stream sockets) don’t just make it hard for human programmers to keep track of safety rules, they also make it hard for fuzzers to construct inputs that explore all relevant state patterns. This might be an area for fuzzer improvement - perhaps fuzzers could reach deeper into specific subsystems by generating samples that focus on interaction with a single kernel subsystem, or by monitoring whether additional syscalls chained to the end of a base sample cause additional activity in a particular subsystem.

## Takeaway: `copy_from_user()` delays don’t require FUSE or userfaultfd

FUSE and userfaultfd are the most effective and reliable ways to inject delays on `copy_from_user()` calls because they can set up separate delays for multiple memory regions, provide precise control over the timing of the injected delay, don’t require large allocations or slow preparation, and allow placing arbitrary data in the page that is eventually installed. However, applying `mprotect()` to a large anonymous VMA filled with zeropage mappings (with 128 MiB of page tables) turns out to be sufficient to delay kernel execution by around a second. In the past, I have pushed for restricting userfaultfd because of how it can delay operations like `copy_from_user()`, but perhaps userfaultfd was not actually significantly more useful in this regard than `mprotect()`.

## Takeaway: Usercopy hardening

The hardening checks I encountered when calling `copy_to_user()` on arbitrary kernel addresses were a major annoyance, but could be worked around, since access to almost anything except type-specific SLUB pages is allowed. That said, I’m not sure how important improving these checks is - trying to protect against an attacker who can pass arbitrary kernel pointers to `copy_to_user()` might be futile, and guarding against out-of-bounds/use-after-free `copy_to_user()` or such is the major focus of this hardening.

## Conclusions

Even in somewhat constrained environments, it is possible to pull off moderately complex Linux kernel exploits.

Chrome’s Linux desktop renderer sandbox exposes kernel attack surface that is never legitimately used in the sandbox. This needless functionality doesn’t just allow attackers to exercise vulnerabilities they otherwise couldn’t; it also exposes kernel interfaces that are useful for exploitation, enabling heap grooming, delay injection and more. The Linux kernel contributes to this issue by exposing esoteric features through the same syscalls as commonly-used core kernel functionality. I hope to do a more in-depth analysis of Chrome’s renderer sandbox on Linux in a follow-up blogpost.