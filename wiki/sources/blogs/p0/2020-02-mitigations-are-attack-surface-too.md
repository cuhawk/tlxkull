---
source: p0
source_url: https://projectzero.google/2020/02/mitigations-are-attack-surface-too.html
title: "Mitigations are attack surface, too - Project Zero"
description: "Posted by Jann Horn, Project ZeroIntroductionThis blog post discusses a bug leading to memory cor..."
---

Posted by Jann Horn, Project Zero

Introduction

This blog post discusses [a bug](https://crbug.com/project-zero/1962) leading to memory corruption in Samsung's Android kernel (specifically the kernel of the Galaxy A50, A505FN - I haven't looked at Samsung's kernels for other devices). I will describe the bug and how I wrote a (very unreliable) exploit for it. I will also describe how [a second vulnerability](https://crbug.com/project-zero/1657), which had long been fixed in the upstream kernel, the upstream stable releases, and the Android common kernel, but not in Samsung's kernel, aided in its exploitation.

If you want to look at the corresponding source code yourself, you can download Samsung's kernel sources for the A505FN from [here](https://opensource.samsung.com/uploadList?menuItem=mobile&classification1=mobile_phone&searchValue=SM-A505FN). The versions seem to be sorted such that the newer ones are at the top of the list; A505FNXXS3ASK9 is the newest one at the time of writing, corresponding to the November 2019 security patch level.

# Vendor-specific kernel modifications

On Android, it is normal for vendors to add device-specific code to the kernel. This code is a frequent source of security vulnerabilities. Android has been reducing the security impact of such code by locking down which processes have access to device drivers, which are often vendor-specific. Modern Android phones access hardware devices through dedicated helper processes, which form the Hardware Abstraction Layer (HAL).

(As an aside: Linux supports secure, direct hardware access from userspace to PCI devices via [Virtual Function I/O](https://www.kernel.org/doc/html/latest/driver-api/vfio.html) (since [Linux 3.6](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=cba3345cc494ad286ca8823f44b2c16cae496679)), and to USB devices via [/dev/bus/usb/](https://www.kernel.org/doc/html/latest/driver-api/usb/usb.html#the-usb-character-device-nodes). If more OEMs used these mechanisms instead of out-of-tree drivers, this would improve their device security. It would also help with the issue of maintaining those drivers, since these mechanisms use stable userspace APIs instead of kernel APIs that have no such guarantees.)

Unfortunately, it is more difficult to generically lock down the attack surface that is created when vendors modify core kernel functionality.

For example, Samsung's kernel adds extra "protection" to credential structures: struct cred is made read-only with the assistance of hypervisor code (CONFIG\_RKP\_KDP, "Protection for cred structure"), and transitions to UID 0 are subject to special checks based on the path of the current executable (CONFIG\_SEC\_RESTRICT\_SETUID, “Restrict changing root privilege except allowed process”). But none of these modifications actually prevent an attacker who has sufficient control over the kernel to modify credential structures from reading or modifying user data directly. For example, an attacker could:

- In order to directly gain access to resources that are supposed to be inaccessible to the attacker:


  - modify file-system-internal data structures to give themselves access to inodes that wouldn't be accessible normally (as demonstrated further down in this blogpost)

  - directly read secrets from kernel memory


- In order to gain control over processes that have interesting privileges or access to interesting data, such as an email application, a messenger app, the zygote or system\_server - since virtually all user data is accessible to at least one userspace context:

  - modify userspace code that is present in the page cache through the direct mapping (also known as "physmap" among security folks)

  - modify the saved register state of other userspace processes that are stored in the kernel

  - modify userspace pointers that are saved in the kernel and will later be used to write to userspace

  - modify memory management state such that victim-process-owned pages will become accessible to an attacker process

Of course, this is a non-exhaustive list. In other words, Samsung's protection mechanisms won't provide meaningful protection against malicious attackers trying to hack your phone, they only block straightforward rooting tools that haven't been customized for Samsung phones. My opinion is that such modifications are not worth the cost because:

- They make it more difficult to rebase onto a new upstream kernel, which should be happening more often than it currently does

- They add additional attack surface


# Samsung's "Process Authenticator" (PROCA)

## The subsystem

The Samsung kernel on the A50 contains an extra security subsystem (named "PROCA", short for "Process Authenticator", with code in security/proca/) to track process identities. By combining several logic issues in this subsystem (which, on their own, can already cause a mismatch between the tracking state and the actual process state) with a brittle code pattern, it is possible to cause memory unsafety by winning a race condition.

PROCA seems to track information about process identities based on ASN.1-encoded signatures attached to their executable files. It might be making that information available to a hypervisor, but that's just speculation on my part. The ASN.1-encoded signatures are loaded from the extended attribute user.pa ; the extended attribute security.five also plays a role. I believe that offsets into PROCA's data structures are exposed to something outside the kernel through the GAFINFO structure in drivers/staging/samsung/sec\_gaf\_v5.c - this might be for a hypervisor, but if so, I haven't yet figured out where that hypervisor code is on the A50 or how that hypervisor can protect accesses to PROCA's data structures against concurrency, given that GAFINFO doesn't contain any information about where locks are located.

There are only a small number of files in the /system and /vendor filesystems that have a user.pa attribute:

- /vendor/bin/hw/wpa\_supplicant

- /vendor/bin/vendor.samsung.security.wsm@1.0-service

- /system/app/SecurityLogAgent/SecurityLogAgent.apk

- /system/app/Bluetooth/oat/arm64/Bluetooth.odex

- /system/app/Bluetooth/Bluetooth.apk

- /system/priv-app/Fast/oat/arm64/Fast.odex

- /system/priv-app/Fast/Fast.apk

- /system/bin/apk\_signer

- /system/bin/dex2oat

- /system/bin/patchoat

- /system/bin/vold

- /system/framework/oat/arm64/services.odex

- /system/framework/services.jar


(The signatures can be decoded on a Linux machine after mounting the filesystems from a factory image with a command like "getfattr -e base64 -n user.pa system/bin/dex2oat \| grep -F 'user.pa=' \| sed 's\|^user.pa=0s\|\|' \| openssl asn1parse"; the ASN.1 structure can be seen in security/proca/proca\_certificate.asn1.)

The main data structure of PROCA is the per-process struct proca\_task\_descr, which looks as follows (lightly edited output from pahole):

struct proca\_task\_descr {

struct task\_struct \*       task;                /\\* 0 0x8 \*/

struct proca\_identity {

    void \*             certificate;           /\* 0x8 0x8 \*/

    long unsigned int  certificate\_size;           /\* 0x10 0x8 \*/

    struct proca\_certificate {

      char \*     app\_name;                           /\* 0x18 0x8 \*/

      long unsigned int app\_name\_size;                /\* 0x20 0x8 \*/

      char \*     five\_signature\_hash;                 /\* 0x28 0x8 \*/

      long unsigned int five\_signature\_hash\_size;     /\* 0x30 0x8 \*/

    } parsed\_cert;                                  /\* 0x18 0x20 \*/

    struct file \*      file;           /\* 0x38 0x8 \*/

} proca\_identity;                               /\* 0x8 0x38 \*/

struct hlist\_node {

    struct hlist\_node \* next;                       /\* 0x40 0x8 \*/

    struct hlist\_node \* \* pprev;                    /\* 0x48 0x8 \*/

} pid\_map\_node;                                 /\\* 0x40 0x10 \*/

struct hlist\_node {

    struct hlist\_node \* next;                       /\* 0x50 0x8 \*/

    struct hlist\_node \* \* pprev;                    /\* 0x58 0x8 \*/

} app\_name\_map\_node;                            /\* 0x50 0x10 \*/

};

One instance of struct proca\_task\_descr exists for each running process that is currently executing an executable with the user.pa extended attribute.

Instances of struct proca\_task\_descr are addressed through g\_proca\_table, which is a global instance of struct proca\_table, a container structure for two hash tables with locks:

struct proca\_table {

unsigned int hash\_tables\_shift;

DECLARE\_HASHTABLE(pid\_map, PROCA\_TASKS\_TABLE\_SHIFT);

spinlock\_t pid\_map\_lock;

DECLARE\_HASHTABLE(app\_name\_map, PROCA\_TASKS\_TABLE\_SHIFT);

spinlock\_t app\_name\_map\_lock;

};

While the kernel maintains both hash tables, it only ever performs lookups in the pid\_map \- the app\_name\_map is either unused or used solely for lookups from hypervisor code.

## Two logic bugs

pid\_map uses numeric PIDs as lookup keys (where PID has the kernel meaning "per-task/per-thread ID", not the userspace meaning "per-thread-group ID"). The following cases are the most interesting ones where this map is modified:

- When a task creates a child that doesn't share the parent's virtual memory mappings (CLONE\_VM is unset), five\_hook\_task\_forked() posts a TASK\_FORKED work item onto the g\_hook\_workqueue. When this work item is asynchronously processed, if a struct proca\_task\_descr exists for the parent's PID, a copy is created for the child's PID. The kernel's hashtable implementation allows multiple entries with the same key, so if an entry for the child's PID already exists in the table, this adds another entry.

- When a task goes through execve() (more specifically, in search\_binary\_handler()), five\_hook\_file\_processed() collects some information about the binary being executed, then posts a FILE\_PROCESSED work item onto the g\_hook\_workqueue. When this work item is asynchronously processed, an item may be inserted into or deleted from the pid\_map depending on the pre-execve() state and the new executable.

- When a struct task\_struct is freed, proca\_task\_free\_hook() synchronously removes the table entry for its PID.


This means that the state of the PROCA subsystem can easily get out of sync with the actual state of the system. One problem is that the point where PROCA believes that an execution has occurred (the security hook in search\_binary\_handler()) is before the "point of no return" in the execve() path: The execution may still abort at a later point, leaving the original executable running, but letting PROCA believe that a new executable is now running. If PROCA was actually used to make authentication decisions, this might allow an attacker to impersonate a privileged executable while actually running attacker-owned code.

But the more interesting logic bug is that PIDs can be reused long before the proca\_task\_free\_hook() is triggered: On Linux, the PID of a task is available for reallocation once the task has been reaped (transitioned from Zombie to Dead), but the task is only freed (triggering the hook) once all refcounted references to the task\_struct are gone. While most well-behaved kernel code only takes short-lived references to it, the binder driver takes long-term references to it - in one place in the upstream code, in two places in the version in Android's common kernel tree and Samsung's kernel (because of some priority boosting logic that doesn't exist upstream). This is a potential correctness issue for PROCA, since it means that after a PROCA-authenticated task has died, a new process that reuses the PID might incorrectly be considered authenticated; but more importantly, in combination with the following brittle code, it causes a memory safety problem.

## A memory safety bug

There is some suspicious locking (dropping and re-acquiring a lock in the middle of an operation) in proca\_table\_remove\_by\_pid() (at the bottom of security/proca/proca\_table.c), the helper used by proca\_task\_free\_hook() to look up and, if successful, remove an entry from the pid\_map:

void proca\_table\_remove\_task\_descr(struct proca\_table \*table,

        struct proca\_task\_descr \*descr)

{

\[...\]

spin\_lock\_irqsave(&table->pid\_map\_lock, irqsave\_flags);

hash\_del(&descr->pid\_map\_node);

spin\_unlock\_irqrestore(&table->pid\_map\_lock, irqsave\_flags);

\[... same thing for app\_name\_map ...\]

}

struct proca\_task\_descr \*proca\_table\_get\_by\_pid(

          struct proca\_table \*table, pid\_t pid)

{

struct proca\_task\_descr \*descr;

struct proca\_task\_descr \*target\_task\_descr = NULL;

unsigned long hash\_key;

unsigned long irqsave\_flags;

hash\_key = calculate\_pid\_hash(table, pid);

spin\_lock\_irqsave(&table->pid\_map\_lock, irqsave\_flags);

hlist\_for\_each\_entry(descr, &table->pid\_map\[hash\_key\], pid\_map\_node) {

    if (pid == descr->task->pid) {

target\_task\_descr = descr;

      break;

    }

}

spin\_unlock\_irqrestore(&table->pid\_map\_lock, irqsave\_flags);

return target\_task\_descr;

}

struct proca\_task\_descr \*proca\_table\_remove\_by\_pid(

          struct proca\_table \*table, pid\_t pid)

{

struct proca\_task\_descr \*target\_task\_descr = NULL;

target\_task\_descr = proca\_table\_get\_by\_pid(table, pid);

proca\_table\_remove\_task\_descr(table, target\_task\_descr);

return target\_task\_descr;

}

As you can see, proca\_table\_remove\_by\_pid() first performs the table lookup while holding the pid\_map\_lock, looking for an item with a matching PID. Then, it grabs a raw pointer to the item (without incrementing a reference counter or anything like that), drops the lock, takes the lock again, and removes the element from the hash table. This pattern is only safe if it is guaranteed that there can't be two concurrent calls to proca\_table\_remove\_by\_pid() for the same PID. However, this function is called only when the last reference to a task has been dropped, which, as explained above, can be delayed to a time at which the PID has already been reused. Therefore, this function can be called concurrently for a single PID, and when that happens, this bug can cause a proca\_task\_descr to be torn down and released a second time. The following operations will happen on the already-freed proca\_task\_descr in that case:

- two hash\_del() calls in proca\_table\_remove\_task\_descr()

- destroy\_proca\_task\_descr():

  - deinit\_proca\_identity():


    - deinit\_proca\_certificate() calls kfree() on two members

    - fput(identity->file) unless the file is NULL

    - kfree(identity->certificate)


  - kfree() on the proca\_task\_descr

There are several ways one might try to exploit this. I decided to exploit it as a use-after-free list unlink (via hash\_del()) and ignore the double-free aspect.

## Becoming authenticated

As a first step, we'll want to make PROCA track one of our attacker-controlled processes. As far as I can tell, this probably isn't supposed to be possible because PROCA only tracks processes that run specific binaries that are marked with special attributes, presumably based on the idea that they run trusted code; but we can make PROCA track our own processes using the logic bugs.

One way to do this would be to cause an execution to abort after the security hook in search\_binary\_handler() (e.g. because something goes wrong while looking up the interpreter), but I couldn't find an easy way to do this in practice. Therefore, I decided to use the second logic bug described in the section " [Two logic bugs](https://projectzero.google/2020/02/mitigations-are-attack-surface-too.html#twologicbugs)", reusing a PID while it is still being tracked:

- Let the attacker-owned process P1 create a child P2 that shares P1's file descriptor table.

- Let P2 open /dev/binder, causing the resulting file's struct binder\_proc to hold a reference to P2.

- Let P2 execute /system/bin/dex2oat --blah. dex2oat is a file we're allowed to execute from app context (and also from adb shell context) that comes with a user.pa extended attribute, so at this point P2 is tracked by PROCA.

- dex2oat is called with invalid arguments, so P2 prints some usage information and exits, turning into a Zombie.

- P1 reaps P2 with waitpid(), so P2 becomes Dead. However, the /dev/binder file (which is referenced from a file descriptor table shared with P1 and therefore wasn't closed when P2 exited) still references P2, so P2's task\_struct won't be freed, and the associated entry isn't removed from the pid\_map.

- P1 keeps forking children until there is a child P3 which has the same PID as P2. At this point, P3 is tracked by PROCA because its PID has an entry in the pid\_map. (If there is hypervisor code involved with PROCA, we don't know how it feels about this, considering that {proca\_task\_descr}->task still points to P2; but the kernel code doesn't care.)


## Basic race scenario

To cause the race between two concurrent proca\_table\_remove\_by\_pid() calls, we need to have two tasks with the same PID that are freed concurrently. The usual last reference to a task comes through its struct pid, whose lifetime is subject to an unusual flavor of RCU semantics. Since we don't want the freeing to happen whenever the kernel decides to run RCU callbacks, we'll have to create different counted references to the tasks.

(Irrelevant sidenote: struct pid's refcount does not have RCU semantics, instead the reference from a living task does. This means that you can, while being in an RCU read-side critical section without any extra locks and without elevating any refcounts, unconditionally increment the refcount of any struct pid as long as you got the pointer to it from a task\_struct in the same RCU read-side critical section. This is a pattern that you don't see much in the Linux kernel.)

One helpful reference-counted pointer to a task exists in binder's struct binder\_thread: When a binder\_thread is created, it takes a reference to the calling task, and when it is destroyed via ioctl(..., BINDER\_THREAD\_EXIT, ...), it synchronously drops a reference on the task. At first I thought that I could only use this for one side of the race: BINDER\_THREAD\_EXIT only allows us to free binder\_thread instances whose PID matches the caller's PID, so it seemed like it was impossible to call this twice in parallel for the same PID. For this reason, in my original crasher, I triggered the inner side of the race by closing a binder file descriptor, triggering the file's ->release() handler, which posts the work item binder\_deferred\_work onto the global workqueue. When this item is processed, the binder\_proc's task reference is dropped.

But actually, there is a way to use BINDER\_THREAD\_EXIT for both sides of the race: We can create a binder\_thread whose ->pid does not match the PID of its associated task (->task->pid) if we can change the task's ->pid at a later point. That is possible by calling execve() from a non-leader thread - in other words, from a thread other than the one thread the process had when it last went through execve() or was created by fork(). When this happens, the calling thread steals the ->pid of the leader. (Essentially, on Linux, when a thread that isn't the main thread calls execve(), that thread first halts all its sibling threads, then assumes the identity of the main thread. This is implemented in de\_thread() in fs/exec.c.)

So, to trigger the race, we need to:

1. Let task A (with PID P1) call BINDER\_THREAD\_EXIT to start freeing a task with PID P1.

2. Somehow stall the execution of thread A in the middle of the race window, while the pid\_map\_lock is dropped.

3. Let task B (with PID P2) call BINDER\_THREAD\_EXIT to free a task with PID P1, using a binder\_thread whose ->pid doesn't match ->task->pid. After this step, the proca\_task\_descr that task A is currently operating on has been freed.

4. Reallocate the proca\_task\_descr's memory as something else with controlled data.

5. Let task A continue deleting the already-freed object (UAF followed by double-free).


## Widening the race window

To create a sufficiently large race window while task A is between the two locked regions, we can abuse preemption, similar to the mremap() issue I have [written about before](https://projectzero.google/2019/01/taking-page-from-kernels-book-tlb-issue.html) (see section "Locks and preemption") and [gave a talk about](https://youtube.com/watch?v=MIJL5wLUtKE) (in case you want the long video version). However, unlike the mremap() issue, we are holding a spinlock here until we reach the spot where we want to preempt the task. This is very helpful: On CONFIG\_PREEMPT systems, if the scheduler wants to preempt a task while that task is holding a spinlock, it sets a flag on the task that causes the task to move off the CPU as soon as it's done with the spinlocked region. (Actually, I think that in this case, the flag can't even be set in the middle of the spinlocked region because interrupts are disabled, too, so I think the scheduler IPI is actually only going to be delivered when we reach spin\_unlock\_irqrestore(). But that doesn't really matter here.)

Since the unlocked region is very short, we'll want to instead make the spinlocked region before it as big as we can, and then try to preempt task A in the middle of it. What task A does while holding the lock is a simple hash table lookup:

hash\_key = calculate\_pid\_hash(table, pid);

spin\_lock\_irqsave(&table->pid\_map\_lock, irqsave\_flags);

hlist\_for\_each\_entry(descr, &table->pid\_map\[hash\_key\], pid\_map\_node) {

    if (pid == descr->task->pid) {

      target\_task\_descr = descr;

      break;

    }

}

spin\_unlock\_irqrestore(&table->pid\_map\_lock, irqsave\_flags);

Hash tables are supposed to be more or less constant-time under normal conditions, but in the worst case, they deteriorate into linked lists and have O(n) lookup time instead of ~O(1). (This was presented as [the hashDoS attack at 28C3](https://fahrplan.events.ccc.de/congress/2011/Fahrplan/events/4680.en.html), with a focus on Denial of Service attacks, but it can also be used for various other tricks, including [leaking addresses encoded in the lookup key](https://bugzilla.mozilla.org/show_bug.cgi?id=1312001) or to widen race windows.) Since calculate\_pid\_hash() doesn't have any secret parameters, we can easily determine which PIDs will fall into the same list bucket as the one we're using for the race, and fill the hash table bucket with lots of proca\_task\_descr instances whose truncated PID hash collides while the PID itself doesn't collide, forcing lookups for the target PID to walk through a large number of non-matching entries first.

# An unfixed infoleak from September 2018

## Figuring out where preemption occurred

At this point, we can repeatedly preempt task A, and one of those preemptions will happen directly at the spin\_unlock\_irqrestore(). However, we need to figure out which of the preemption events happens in that spot so that we know when to run the inner side of the race. One way to do this would be to just observe scheduling latency, and that should work if we make the hash bucket sufficiently big - but there is a nicer way.

Back in September 2018, I reported [a security bug](https://crbug.com/project-zero/1657) in the /proc/$pid/stack interface and sent a patch that restricts this interface to root. That patch was quickly applied to mainline, the upstream stable trees, and the Android common kernel. Someone even assigned a CVE identifier to it, [CVE-2018-17972](https://nvd.nist.gov/vuln/detail/CVE-2018-17972). But in the Android ecosystem, that doesn't mean that it actually makes its way into device kernels - and at least on this Samsung phone, it still hadn't landed in a build with security patch level "1 November 2019". (The patch is now present in the newest kernel image, with security updates from February 2020.)

Therefore, we can still use /proc/$pid/stack in our PoC. This file intentionally allows normal users to dump kernel stack traces of any tasks they own; it contains a symbolized stack trace, like this (with the marker 0xffffffffffffffff at the end):

a50:/ $ cat /proc/$$/stack

\[<0000000000000000>\] \_\_switch\_to+0xbc/0xd8

\[<0000000000000000>\] sigsuspend+0x3c/0x74

\[<0000000000000000>\] SyS\_rt\_sigsuspend+0xa0/0xf8

\[<0000000000000000>\] \_\_sys\_trace+0x68/0x68

\[<0000000000000000>\] 0xffffffffffffffff

This means that every time we have preempted task A, we can read its /proc/$pid/stack and check whether it contains "proca\_table\_get\_by\_pid+"; and when it does, we're in the race window.

(While using /proc/$pid/stack this way makes it easier to write exploits for kernel race conditions, this is not the security bug that caused the interface to be restricted to root upstream; that security bug will be described in the next section.)

## Bypassing PAN using the direct mapping of a user page

On Linux, the kernel's direct mapping area (also known as "physmap" among security folks) maps almost all memory as RW, including pages that are mapped into userspace as part of normal anonymous memory mappings. If we can locate such a page in the direct mapping, we have a known kernel address at which we can arbitrarily read/write data directly from userspace.

The security bug in the /proc/$pid/stack interface was that it performs stack tracing on a task that might be running concurrently, starting with the saved frame pointer from when the task was last scheduled off a CPU - which means that if the stack changed in the meantime, the kernel's stack tracer can end up interpreting random stack data as stack frames. To make things worse, when the stack tracer was unable to symbolize a saved instruction pointer, it would simply print out the raw value as a hexadecimal number. You can easily reproduce this as follows on an Android phone affected by the bug:

130\|a50:/ $ cat /dev/zero > /dev/null &

\[1\] 8559

a50:/ $ while true; do grep ' 0x' /proc/8559/stack \| grep -v 0xffffffffffffffff; done

\[<0000000000000000>\] 0x285ab42995

\[<0000000000000000>\] 0xffffff8009b63b80

\[<0000000000000000>\] 0x285ab42995

\[<0000000000000000>\] 0x285ab42995

\[<0000000000000000>\] 0x285ab42995

\[<0000000000000000>\] 0x285ab42995

\[<0000000000000000>\] 0x285ab42995

\[<0000000000000000>\] 0x285ab42995

\[<0000000000000000>\] 0x285ab42995

\[<0000000000000000>\] 0x285ab42995

\[<0000000000000000>\] 0xffffffc874325280

\[<0000000000000000>\] 0xffffffc874325280

\[<0000000000000000>\] 0xffffffc874325280

\[<0000000000000000>\] 0xffffffc874325280

\[<0000000000000000>\] 0x80000000

If we could specifically target things like e.g. the kernel-virtual address of a userspace-owned page with this, that would be very helpful for exploit writing.

After a few days spent on figuring out stack frame layouts, I found that this can be done by alternating the following two syscalls:

1. Call getcwd() on a non-present page and let it block on the mmap semaphore.


   - We need to let another thread perform VMA allocations and deallocations in a loop to create contention on the mmap semaphore.

   - The process will be scheduled away when attempting to acquire the mmap semaphore that has already been taken in write mode. When this happens, cpu\_switch\_to() in arch/arm64/kernel/entry.S saves the callee-saved registers, including the frame pointer, into {task}->thread.cpu\_context.

   - The frame pointer that was saved when scheduling away ({task}->thread.cpu\_context.fp) points to a stack frame whose saved link register is in the same location as where X1 is stored during the other syscall.


3. Call process\_vm\_readv() with an output pointer that points to a non-present page.

   - A page fault will be taken in the middle of copyout(), saving the complete register state in the exception frame.

   - The saved X1 in the exception frame contains the kernel address at which the task's page is mapped by the kernel. Since process\_vm\_readv() lets us control the offset of the access, we can use the low 12 bits of the address as a marker that tells us whether the stack tracing operation raced in the right way and leaked the page pointer.

See [addr\_leak.c in our bugtracker](https://bugs.chromium.org/p/project-zero/issues/attachmentText?aid=424516) for the call stacks and frame sizes.

Similarly, we can leak the address of the struct file associated with a pipe using sched\_yield() and pipe-to-pipe splice(). The stack layouts for this look as follows (entry-from-EL0 exception frames not shown, since they look the same for all syscalls):

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjgIsB_s600_7nlkTunFyHfeUZYkecgO5D6yu6ggbxHt0QPkyQ6fCOvteY6bZltJpTpGsERXwfHw63HrSGe67RCOPDPV4_7jDztNb9Ikr9rfX1rzDoDuOysIGFOj5y6v6ZFPDUAx-HtvMFkWyrfL.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjgIsB_s683_7nlkTunFyHfeUZYkecgO5D6yu6ggbxHt0QPkyQ6fCOvteY6bZltJpTpGsERXwfHw63HrSGe67RCOPDPV4_7jDztNb9Ikr9rfX1rzDoDuOysIGFOj5y6v6ZFPDUAx-HtvMFkWyrfL.png)

In this case, since we can't specify an arbitrary offset here as a signal to distinguish the target value, I determined the correct file\* by performing an otherwise identical operation on two different pipe files and filtering out any numbers that show up in the stack traces in both cases.

# Spraying the heap

The proca\_task\_descr in which the UAF occurs is allocated using kzalloc(), so it must be in one of the kmalloc-\* slabs. The slab is selected based on the size of the object; a proca\_task\_descr is 0x60==96 bytes big, which on an X86 desktop system would mean that the allocation lands in the kmalloc-96 slab. But such a slab doesn't exist on ARM64; the smallest slab there is kmalloc-128, which is used for all kmalloc() allocations up to 128 bytes.

Normally, to spray allocations through the slab allocator, a primitive is used that allocates a memory chunk with a size that falls within the right size bucket, fills it with attacker-controlled data, and then keeps a reference to the allocation around somehow so that the allocation won't be freed again immediately. However, instead, by relying on the allocation pattern of the SLUB allocator, we can combine two primitives instead: One to allocate some memory, fill it, then free it again immediately afterwards, the other to reallocate that memory and keep a reference to it around while leaving most of it uninitialized. We can e.g. do this by alternating calls to recvmsg() with the payload in the control message and calls to signalfd(): recvmsg() allocates a temporary buffer for the control message, copies the control message into it and frees the buffer, then signalfd() reallocates the 128-byte heap chunk as an 8-byte allocation and leaves the rest of it uninitialized.

Because the UAF will happen on a proca\_task\_descr that was allocated from the g\_hook\_workqueue, whose scheduling we can't control, we don't know on which CPU's slab it was allocated. On top of that, because we need to slowly create dummy proca\_task\_descr instances to fill up the hash bucket after creating the to-be-UAFed allocation, a significant amount of time passes between the allocation of the proca\_task\_descr and the UAF. My PoC attempts to perform reallocations on all CPU cores to avoid missing percpu slabs, but it still doesn't work very reliably, and I didn't want to invest more time into investigating this in detail. (I'm not sure whether this is the only major source of unreliability, or whether there are other parts of the exploit that are unreliable.)

# Getting arbitrary read/write

At this point, we have everything we need for an (unreliable, because the heapspray doesn't work great) proof-of-concept that can gain arbitrary kernel read/write.

We can trigger the race, reallocating the freed buffer using the heapspray. The sprayed fake proca\_task\_descr can be used to perform a linked list unlink operation on two arbitrary addresses, causing them to point to each other. As one side of the unlink operation, we can use a pointer to the ->private\_data member of a pipe file whose address we've leaked; as the other side, we can use the kernel mapping of the userspace-owned page whose kernel address we've leaked. With this, we have direct, full control over the struct pipe\_inode\_info used by this pipe file. By controlling the pipe\_buffer instances to which the pipe\_inode\_info points, we can cause the pipe code to read from and write to arbitrary addresses, as long as they're in the direct mapping and the access range doesn't cross page boundaries.

At this point, extending that to full arbitrary read/write is rather easy; we can overwrite all sorts of pointers to data that the kernel will hand back to us.

# Doing something useful with the read/write

Normally we could stop at this point; arbitrary kernel read/write clearly means that all user data reachable by userspace and the kernel is compromised (unless the files are encrypted and the user hasn't entered the corresponding PIN yet). However, because of Samsung's attempts to prevent exploits from succeeding (such as CONFIG\_RKP\_KDP), I felt it was necessary to demonstrate that it is possible to access sensitive data using this arbitrary kernel read/write without doing anything particularly complex. Therefore, I wrote some code that can perform path walks through the dentry cache using the arbitrary read/write (just like the kernel would do it on the fastpath), look up an inode based on its path in a filesystem, and then install its ->i\_mapping as the ->f\_mapping of an attacker-owned instance of struct file. The PoC uses this to dump the contents of the accounts database at /data/system\_ce/0/accounts\_ce.db, which contains sensitive authentication tokens. The code for this is fairly straightforward and never touches any credential structures.

# Conclusion

Linux kernel code has quite a few sharp edges - and modifications to such a codebase, in particular in a fork without any review from upstream maintainers, can easily introduce subtle issues, even if those modifications are for implementing "security" features.

In my opinion, some of the custom features that Samsung added are unnecessary, and can be removed without any loss of value. I can't tell what PROCA is supposed to do, but e.g., SEC\_RESTRICT\_SETUID seems to be designed to restrict an attacker who has already gained arbitrary kernel read/write - which to me seems futile, and engineering resources would have been better spent preventing an attacker from getting to that point in the first place.

I believe that device-specific kernel modifications would be better off either being upstreamed or moved into userspace drivers, where they can be implemented in safer programming languages and/or sandboxed, and at the same time won't complicate updates to newer kernel releases.

That I was able to reuse an infoleak bug here that was fixed over a year ago shows, [once again](https://projectzero.google/2019/11/bad-binder-android-in-wild-exploit.html), that the way Android device branches are currently maintained is a security problem. While I have criticized some Linux distributions in the past for not taking patches from upstream in a timely manner, the current situation in the Android ecosystem is worse. Ideally, all vendors should move towards using, and frequently applying updates from, [supported upstream kernels](http://www.kroah.com/log/blog/2018/08/24/what-stable-kernel-should-i-use/).