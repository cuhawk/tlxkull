---
source: bughunters
source_url: https://bughunters.google.com/blog/project-rainl1tf
title: "Project Rain:L1TF - Google Bug Hunters"
description: "This blog shares a detailed overview of the L1TF vulnerability, a CPU vulnerability on some Intel CPUs (Skylake and older), and explains how it could be exploited and what mitigation strategies are possible."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/project-rainl1tf#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Project Rain:L1TF

![](https://storage.googleapis.com/bughunters-article-images/blogs/mathe.jpg)

Mathé Hertogh

VUSec - PhD Student

![](https://storage.googleapis.com/bughunters-article-images/blogs/evn.jpg)

Eduardo Vela Nava

Google - Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/dave.jpg)

Davey Quakkelaar

VUSec - PhD Student

![](https://storage.googleapis.com/bughunters-article-images/blogs/matteorizzo.jpg)

Matteo Rizzo

Google - Information Security Engineer

Published: Sep 19, 2025

Vulnerability Research

[RSS Feed](https://bughunters.google.com/feed/en)

# Project Rain:L1TF

This blog provides a detailed overview of the L1TF vulnerability, a CPU
vulnerability on some Intel CPUs (Skylake and older), how it could be exploited,
as well as different mitigation strategies. We also explain how Google responded
to this issue and the work we have done to fix this vulnerability together with
the Linux Kernel community as part of developing
[Address Space Isolation](https://lore.kernel.org/lkml/20250812173109.295750-1-jackmanb@google.com/T/#u).
This blog is written together with VUSec, the Systems and Network Security Group
at Vrije Universiteit Amsterdam, and a researcher from the University of
Birmingham who collaborated on the research of the
[L1TF Reloaded exploit](https://program.why2025.org/why2025/talk/DG7VSX/)
( [paper](https://openreview.net/forum?id=4tDNvQe2G0)) but had to remain
anonymous until last month in order to go through the double blind review
process, which is now over.

Researchers from the VUSec group invited Google to go to Amsterdam to discuss
research ideas like the one presented in this blog post, and some time later
VUSec proposed this research project, which Google sponsored with a
[sole-tenant](https://cloud.google.com/compute/docs/nodes/sole-tenant-nodes)
node in order to conduct the research safely without potentially affecting any
other customers. Once VUSec succeeded, they visited Google's offices in Zurich
where they presented their results. Google awarded a $151,515 USD reward for
their results, the highest reward tier for our
[Google Cloud VRP](https://cloud.google.com/blog/products/identity-security/google-cloud-launches-new-vulnerability-rewards-program)
and the first time researchers have been rewarded at this level.

## Background

This background section provides some general background about CPU
_microarchitecture_. This overview establishes context to help readers
understand how someone could exploit
[L1TF](https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00161.html)
to hypothetically conduct an attack, and mitigation strategies to fix the
vulnerability. It is not meant to be complete or comprehensive, but aims to be
understandable to readers with some knowledge about operating systems and
systems programming experience.

When we talk about CPU microarchitecture, we mean details that aren't defined by
the CPU developer manuals, but are hardware implementation details. These
details are often documented in performance optimization manuals and reverse
engineered for security, performance and reliability reasons.

### Caching

In order to improve computing performance, CPU architects strive to to reduce
the amount of time (measured in "clock cycles") that each operation takes. An
example of an operation in this context is "add the value of register rax with
the value of the register rbx and put the result in rax".

One of the most frequent operations the CPU needs to do is to read memory, and
unfortunately some memory is very slow to read. Even very modern DRAM (Dynamic
RAM) needs a lot of cycles to be read. As a solution, modern CPUs employ SRAM
(Static RAM) caches which are very fast to read (a few cycles) and are located
physically in the same chip package as the rest of the CPU, but are also much
smaller (measured in Megabytes) and consume much more power. We still use DRAM
because it is significantly cheaper than SRAM and occupies less space and power.

These SRAM caches are hierarchical, where the smallest cache is fastest to
access while the largest cache is slower to access (L1 cache is the fastest and
the Last-Level Cache/LLC is the slowest).

### Speculative execution

![](https://storage.googleapis.com/bughunters-article-images/blogs/rain_01.png)

_Fig. 1. Trace from [https://uica.uops.info/](https://uica.uops.info/) showing out of order execution of a_
_few assembly instructions._

Speculative execution is an optimization tackling the problem that some
instructions take very long to execute (like accessing memory that is not
cached). In order not to waste too much time, the CPU starts preparing some
future instructions ahead of their turn. If it later turns out that these
prepared instructions aren't necessary (for example, a memory access fails or
there is an error like a division by zero), then the CPU simply discards these
prepared results. In the illustration above you can see how the CPU "prepares"
some instructions for execution ahead of their turn (marked in yellow) but only
finalizes the result of their prepared execution in the right order (marked with
an R in green - the R stands for "retirement" which means completing the
instruction and removing it from the queue).

Usually one assembly instruction has one or more of these operations which are
called micro-operations. Note that all micro-operations that belong to one
instruction retire all at once. When all micro-operations in an instruction
retire it is said that the instruction is "architecturally" executed.

Speculative execution allows CPUs to work on available instructions even if
earlier ones are slow. However, this requires a steady stream of upcoming
instructions. The main obstacle is control flow (loops, conditions, function
calls), where the execution path, or "branch," often depends on results that
aren't yet calculated. To overcome this, CPUs employ branch prediction. Using
historical data (stored in microarchitectural buffers, often called Branch
Target Buffer or Branch History Table, among others) and heuristics, the CPU
predicts which path a branch will likely take and reads instructions from that
path preemptively.

Here is an example of a situation where the CPU needs to decide which
instructions to fetch next. In order to take advantage of out-of-order execution
the CPU needs to decide what instructions to fetch after the conditional branch
on `402009` before the result of the comparison is known.

```
  402000:  mov rax, [rsp-100]
  402005:  cmp rax, 100
  402009:  je 0x401000
  40200f:  mov rbx, [rsp-999]
  402017:  int3
```

These predictions are sophisticated guesses. If a guess is wrong (a
misprediction), the CPU simply detects the error, discards the preparation work
done based on the wrong path, and proceeds with the correct instructions. This
process of predicting branches and executing potentially needed instructions
ahead of time using out-of-order techniques is collectively termed "speculative
execution".

An example of the work the CPU may do if it speculates that the line on `40200f`
is the one likely to be executed, is to fetch data from the memory pointed at by
`rsp-999`.

### Hyperthreading

One more optimization that CPUs have is called "Hyperthreading", or
"Simultaneous multithreading" (SMT), where a CPU "thread" (the logical unit that
the operating system understands in order to execute code) shares some resources
with some other "threads." The operating system then can schedule a task on each
of these "hyperthreads" and from its point of view each hyperthread is a
different CPU independent from the others. In reality all the hyperthreads that
belong to the same core share most of these resources. Most x86 CPUs have 2
hyperthreads per "physical" core, in which case every thread has one sibling
thread.

![](https://storage.googleapis.com/bughunters-article-images/blogs/rain_02.png)

_Fig. 2. A diagram showing how the CPU schedules tasks and executes them on_
_hyperthreads that share some buffers._

This optimization better utilizes CPU resources, by executing more instruction
streams in parallel. When one thread is waiting, for example for a memory access
to complete, the other can still use the core's remaining execution resources
and make progress. It also makes it look like the CPU has twice as many cores,
all available to the operating system to schedule work on.

### Multitasking

One of the responsibilities of the Operating Systems (OS) is to schedule work on
the CPU. Scheduling generally works by "time sharing" a CPU across many
different tasks. A task can be a process, a thread, a VM or even work done on
the kernel (like processing network packets or user input).

The CPU runs code from one task until it is interrupted either voluntarily (for
example, if the task needs something from the operating system, it may interrupt
its own execution and transfer control back to the kernel) or involuntarily (for
example, by a timer). When the control is transferred back to the kernel, the
CPU automatically switches to a privileged mode (ring 0 on x86) if it was
running as a userspace process, and executes code at an address defined by the
kernel. If the kernel decides that another task should run now, then it will
switch to the other task for a while. When that task runs out of time, the
kernel can resume the previous task from where it had left off.

This time sharing of the CPU is what is known as multitasking. The operating
system is responsible for managing all the defined CPU state that is shared by
all the tasks (like registers). These are called "architectural buffers." The
CPU also has a lot of undefined and poorly documented shared state which the
operating system also has to clear when switching from one task to another
called "microarchitectural buffers." If the kernel does not flush these
microarchitectural buffers, then information from the previous task could leak
to the next task through those buffers or the previous task might be able to
somehow influence the behavior of the next task. Unfortunately, cleaning some of
these microarchitectural buffers is very slow, so task transitions can in turn
be very slow (both between workloads and between the workload and the underlying
kernel).

It is also worth noting that some of these shared buffers are also shared across
hyperthreads, so in some cases the only way to prevent the leakage of data
between tasks is to avoid using one hyperthread when its sibling is running
untrusted code, as we will discuss later on.

### Memory addressing

The CPU has a concept of virtual and physical addresses. This separation allows
the CPU to configure different permissions to memory ranges to different
processes and privilege levels, as well as to assemble "virtually" contiguous
memory that may be spread all across physical memory. Physical memory as its
name implies, simply corresponds to the physical location of memory in DRAM.

The mapping between virtual and physical addresses is configured by a data
structure called Page Tables. Usually software uses virtual addresses to refer
to locations in memory, and the CPU converts that virtual address to physical
addresses by doing a "translation." For example, for x86 CPUs, which support
what is referred to as "4-level paging," the virtual address is conceptually
split the following way:

```
virtual_addr = 0xFF_FF_00_11_22_33_44_55
pml4e_i = (virtual_addr >> 39) & 0b111_111_111
pdpte_i = (virtual_addr >> 30) & 0b111_111_111
pde_i = (virtual_addr >> 21) & 0b111_111_111
pte_i = (virtual_addr >> 12) & 0b111_111_111
pfn = pml4[pml4e_i]->pdpt[pdpte_i]->pd[pde_i]->pt[pte_i]->pfn
phys_addr = (pfn << 12) | (virtual_addr & 0b111_111_111_111)
```

![](https://storage.googleapis.com/bughunters-article-images/blogs/rain_03.png)

_Fig. 3. Pseudocode and table showing how to map a virtual address to the_
_corresponding physical address._

The name for each "level" isn't very important (in this case PML4, PDPT, PD,
PT), it suffices to say that it just dereferences an entry into a 4-dimensional
data structure to obtain the physical address. Besides the addresses, the tables
for each level also contain information about the memory range they refer to,
like flags (such as "present," which will be relevant later on), "writeable" or
"cacheable."

### Virtualization

Virtualization allows separating the responsibilities of the maintenance of a
physical machine from the responsibilities of building and deploying
applications through what is called a Virtual Machine (VM). Virtualization
allows application developers to have more control over the operating system
they interact with, while having the physical machine owner have control of the
operating system that they need in order to maintain the physical machine. This
is made possible by the CPU having features that allow it to keep track of one
or more second level operating systems (the outer one called host OS and the
inner ones guest OS) managed by a "hypervisor" (which runs on the host OS). This
is accomplished by having transitions between a "host" and a "guest" called "VM
Exit" and "VM Enter." A VM Enter is when the host OS hands over the execution to
the VM and the VM Exit is when the VM stops executing and control returns to the
host.

The CPUs lets the VMs (the "guests") define their own view of the memory
assigned to it by the host as if it was physical memory, and lets the host
define which memory the guest gets to use. This is accomplished through a
mechanism called extended page tables (EPT), second level address translation
(SLAT) or nested paging. This means that as far as the guest OS is concerned, it
is referencing physical memory, while in fact it is just virtual memory on the
host. The mechanism to do this is as follows:

- The Host configures a mapping between Host Physical Address and Host Virtual
Address.
- The Host configures a VM as owning a range of virtual address space.
- The Host launches the Guest VM, which sees the memory range provided by the
Host as physical memory (Guest Physical Memory).
- The Guest configures a mapping between Guest Physical Memory and Guest
Virtual Memory.

When the VM needs to dereference a memory address, the CPU first translates the
address from Guest Virtual Address (GVA) to Guest Physical Address (GPA) and
then to the Host Physical Address (HPA).

```
// --- Level 1: Guest Virtual Address (GVA) to Guest Physical Address (GPA) ---
// 1. Get the Guest Page Table Base (GPA) from the guest's CR3 register.
guest_page_table_base_gpa = read_guest_cr3()
// 2. Walk the guest's page tables.
gpa = walk_guest_page_tables(gva, guest_page_table_base_gpa)

// --- Level 2: Guest Physical Address (GPA) to Host Physical Address (HPA) ---
// 1. Get the Host EPT Base (HPA) from the EPT pointer.
host_ept_base_hpa = read_ept_pml4_register()
// 2. Walk the host's Extended Page Tables.
hpa = walk_host_ept(gpa, host_ept_base_hpa)
```

_Code 1. Pseudocode of how second level address translation works._

Virtualization creates significant cost savings because of economies of scale.
By separating concerns, the host OS manages resources of the VMs without
worrying about the workload and the host providers can specialize their
infrastructure and maintenance. By making the guest OS believe it is executing
directly on hardware it allows for a wider diversity of workloads (some of which
use more network, some use more CPU, some use RAM, some more disk, etc.). This
execution model makes it possible to minimize waste and maximize utilization by
sharing a single physical machine across multiple users. In addition, it allows
users to run an unmodified OS and run their applications as if they were running
on a physical machine. Cloud providers rely on virtualization as a business
model: a compute cloud is similar to a VM rental store, and typically, the guest
is considered untrusted from the host's perspective.

However, these improvements did not come without risks. When designing these
mechanisms, there were significant oversights which ultimately resulted in
having weaker security boundaries than originally intended. These weaker
boundaries were caused because the host shares some CPU resources with the
guests, and as a result it allows lower privilege levels (for example the guest
OS) to infer information about data stored in shared resources (like the data
caches) by other privilege levels (like the host OS or other guests).

## L1TF Reloaded Exploit

Now we are ready to talk about VUSec's exploit: "L1TF Reloaded." We will start
with a short high-level overview.

L1TF is a CPU vulnerability that allows an (attacker) VM to speculatively read
_any_ data residing in the (core-local) L1 data cache — including data the VM
shouldn't have access to. At a high level, L1TF Reloaded abuses this to obtain
an arbitrary RAM read primitive as follows. The attacker VM subsequently:

1. chooses the "secret" to be any byte in RAM it wants to leak;
2. performs a hypercall that tricks the host to perform a speculative
out-of-bounds memory access, putting the secret into the L1 cache;
3. triggers the L1TF vulnerability, to obtain _speculative_ access to the
secret, and _speculatively_ encodes it into the data cache;
4. decodes the secret from the data cache via timing side-channel analysis.

Using this arbitrary read primitive, the exploit built an end-to-end attack that
leaks data from the host OS to detect victim VMs running on the same machine.
From the guest OSes it leaks what processes those victims are running. And
lastly, as an example, from a victim Nginx web server, it leaks its private TLS
key — breaking that web server's HTTPS security.

Let's dive into the details.

### Half-Spectre: caching secret data

An important limitation of L1TF is that it can only leak data that is cached in
the L1 cache. Normally, this means that the attacker can only read secret data
that another VM or the host OS has recently read. One possibility is for the
attacker to force the host OS or other VMs to read secret data architecturally,
which will end up in the cache. This strategy is targeted by the deployed
L1TF-mitigations and therefore cannot be effectively exploited. We'll dive into
mitigations later on.

Instead, L1TF Reloaded exploits a microarchitectural (i.e. CPU implementation)
weakness: speculative execution. The CPU populates cache entries from memory
even during speculative execution. This means attackers don't actually need the
(more privileged) software code to load secret data using architecturally
retired instructions for it to end up in the cache. If it is possible to make
the host load the secret data during speculative execution then that data will
remain in the cache even after the CPU notices the misprediction and rolls back.

A snippet of code in the host that can be used to load secret data in the cache
in this way is called a "half-Spectre gadget" (also known as
" [cache load gadget](https://xenbits.xen.org/xsa/advisory-289.html)",
" [prefetch gadget](https://www.cc0x1f.net/publications/transient_sytematization.pdf)",
or " [MDS gadget](https://www.vusec.net/projects/kasper/)"), and looks something
like this:

```
if (idx < MAX) x = y[idx]
```

_Code 2. Example of a Half-spectre gadget_

This is code on the host OS and the attacker controls the value of idx. The
conditional branch could take long to evaluate (e.g. when the value of idx is
not cached), so the CPU speculatively executes what it believes to be the most
likely path. If the most likely path is the one where the bounds check succeeds,
then 'y\[idx\]' speculatively loads data from RAM into the L1 cache. Upon
resolution of the branch, and detection of a possible misprediction, the loaded
data will _stay_ in the L1 cache (i.e., the cache fill operation is not rolled
back). Assuming 'idx' to be a 64-bit integer, 'y\[idx\]' can reference any memory
address in the entire virtual address space of the host kernel.

For many host kernels, including Linux, this includes all of physical memory
(i.e. all RAM), due to the kernel's "direct map" (i.e. "physmap"). On x86\_64,
the Linux kernel linearly maps all physical memory (contiguously) in a region of
virtual memory known as the physmap or direct map. In other words, the memory at
physical address p is mapped at virtual address `physmap_base + p.` Most
heap-allocated kernel objects reside in the physmap, and that includes the `y`
array used in the Half-Spectre gadget. Hence, with the host physical address of
`y` known, the exploit can bring data at an arbitrary physical address into the
L1 cache by varying the value of idx.

VUSec found such a half-Spectre gadget in Linux' KVM subsystem (and a pretty
shallow one in the callstack, meaning it was very easy to reach), enabling them
to load any RAM data into the L1 cache.

### L1 Terminal Fault

The next step is to leak the secret data — which the attacker VM is not
authorized to access — out of the L1 cache. This is done by exploiting L1
Terminal Fault (L1TF).

It is caused by a logic error in the way Skylake and some other Intel CPUs
behave after a "terminal fault." Terminal faults are a type of page fault
triggered when referencing invalid memory. A terminal fault causes the address
translation process to be terminated immediately, without fully completing the
address translation. The problem is that, although the access failed, the CPU
may still load the referenced data from the L1 cache.

It is important to note that the "physical address" from the perspective of a
virtual machine does not correspond to the hardware physical address. The
concept of a "Guest Physical Address" and a "Host Physical Address" (HPA) that
are related but treated differently is the root cause of the vulnerability as we
will see below.

![](https://storage.googleapis.com/bughunters-article-images/blogs/rain_04.png)

_Fig. 4. Diagram showing how the L1TF vulnerability ends up reading unexpected_
_data._

To exploit the L1TF vulnerability, an attacker creates a VM and maps a guest
virtual address (GVA) to a guest physical address (GPA). However, this entry is
deliberately marked as "not present" or "reserved" within the guest's page
tables, which the attacker can do as the attacker has full control over their
own VM. Consequently, when the CPU attempts to access this address, a "terminal
fault" occurs, aborting the address translation process prematurely. This early
termination prevents the translation from proceeding to the extended page tables
(EPT) to derive the host physical address (HPA). The L1TF flaw arises because
this premature abortion inadvertently forwards the guest physical address to the
L1 cache resolution as if it were a host physical address, and allows it to read
any data present in the L1 cache whose host physical address is identical to the
faulting guest physical address manipulated by the attacker.

While the CPU ultimately discards all speculative operations following a page
fault, certain effects (like bringing data to the cache or evicting data from
the cache) remain un-undoable, despite the memory access itself not being
architecturally retired.

### Reading secret data

The attacking VM then can use that mistakenly fetched value from the L1 cache to
perform an operation that can't be undone by the CPU after the page fault. A
common operation is to make a change to the L1 cache itself. This is done
usually with a "dependent load," which makes a change in the cache that the
attacker can detect later on. For example (this code is fully in the attacker
VM):

```
char reload_buffer[64*256]; // Helper array consisting of 256 uncached cachelines
char *gva = GVA; // Non-present guest virtual address, mapped to attacker chosen host physical address
char secret = *gva; // Architecturally faults, but speculatively acquires a byte of secret host data (L1TF)
reload_buffer[64*secret]; // Speculatively cache the secret-th cacheline of reload_buffer
```

Only the first two instructions will execute architecturally, and the last
instruction will never be reached (due to the page fault). However, the last
instruction will still execute speculatively, and leave traces of its execution
in the cache. In particular, the `secret`-th cacheline of `reload_buffer` will
speculatively be cached. Shortly after that, the CPU will actually page fault
due to `*gva`, and control flow diverts to the guest's page fault handler. Over
there, the guest (i.e. the attacker), will measure the access latency to each of
the 256 cachelines of `reload_buffer`. Let's say 255 of them have access latency
of 200+ cycles, while only the 100th entry (at index 99) has a latency of 4
cycles. Then the attacker deduces: only cacheline 99 was cached, hence the
speculative load `reload_buffer[64*secret]` must have been on cacheline 99, so
`secret` must have had value 99 during speculative execution. This technique is
called Flush+Reload, and it is how the attacker turns _speculative_ data access
into _architectural_ data knowledge, via (cache timing) side-channel analysis.

We saw how the attacker can leak secret data by first putting them into the L1
cache via half-Spectre, then extracting them speculatively from the L1 cache by
means of L1TF, and finally leaking them through Flush+Reload.

```
if (idx < MAX) x = y[idx]
```

_Code 3. Example of a Half-spectre gadget, same as the one from the previous_
_section._

Doing this does require some addressing information, which we skimmed over so
far. For half-Spectre, the attacker needs to know _host virtual addresses_: the
gadget's base address (`y` above) and the location of the secret data within the
host's address space. Moreover, L1TF requires knowledge of the _host physical_
_address_ of the secret data, in order to speculatively fetch it from the L1
cache. The exploit therefore spends most of its time leaking such addressing
information in order to, in the end, find and leak (truly sensitive) secret
data.

The initial exploit phase leaks the gadget's base `y` in \*host physical memory
\*by brute-force search. First, we trigger the gadget with offset (`idx`) zero,
pulling `y[0]` into the L1 cache, and brute-forcing its host physical address: a
correct guess gives a measurable Flush+Reload signal. False positives can easily
be filtered out, via some a priori knowledge of the data patterns at `y[0]`, and
via failure of subsequent exploit steps.

The second exploit phase breaks the host kernel's KASLR by leaking the physmap's
base address (and thereby also deduces `y`'s _host virtual address_). In the
VUSec exploit, `y` was an array of
[struct kvm\_lapic](https://elixir.bootlin.com/linux/v6.16.1/source/arch/x86/kvm/lapic.h#L58)
structures, representing LAPICs (local advanced programmable interrupt
controller). The exploit leaks the pointer `y[0]` to the first LAPIC structure
and then brute forces its host physical address similar to before. Now both the
physmap virtual address of this LAPIC structure and its physical address are
known, so the exploit can compute the base virtual address of the physmap by
subtracting the two.

Now, the exploit can start "chasing" physmap pointers. Given a physmap pointer,
one finds its host physical address by subtracting the physmap's base address.
This is sufficient to compute the offset `idx` that loads the data behind the
pointer into the L1 cache, as well as to leak it from it with L1TF.

![](https://storage.googleapis.com/bughunters-article-images/blogs/rain_05.png)

_Fig. 5. Diagram showing how an attacker can chase through the pointers found in_
_structs to find the page tables of other tasks running on the host._

The exploit can now follow a chain of pointers to heap-allocated objects, which
are all mapped in the physmap, to find the location of the host's root page
table and then traverse the host's page tables to translate an arbitrary host
virtual address to a host physical address.
[struct kvm\_lapic](https://elixir.bootlin.com/linux/v6.16.1/source/arch/x86/kvm/lapic.h#L58)
contains a pointer to a
[struct kvm\_vcpu](https://elixir.bootlin.com/linux/v6.16.1/source/include/linux/kvm_host.h#L323)
which represents the vCPU that the LAPIC is associated with. This in turn
contains a pointer to a
[struct pid](https://elixir.bootlin.com/linux/v6.16.1/source/include/linux/pid.h#L55)
which represents the process ID of the vCPU task.
[struct pid](https://elixir.bootlin.com/linux/v6.16.1/source/include/linux/pid.h#L55)
is in a linked list of all tasks that use that PID. By traversing the list the
exploit can find the
[task\_struct](https://elixir.bootlin.com/linux/v6.16.1/source/include/linux/sched.h#L812)
for the vCPU task, which in Linux contains all the information about a running
task.
[task\_struct](https://elixir.bootlin.com/linux/v6.16.1/source/include/linux/sched.h#L812)
includes a pointer to the task's
[mm\_struct](https://elixir.bootlin.com/linux/v6.16.1/source/include/linux/mm_types.h#L933),
which keeps track of the task's address space. Importantly, the
[mm\_struct](https://elixir.bootlin.com/linux/v6.16.1/source/include/linux/mm_types.h#L933)
contains
[a pointer to the top-level page](https://elixir.bootlin.com/linux/v6.16.1/source/include/linux/mm_types.h#L960)
table for the vCPU task.

Through this top-level page table, the attacker can use L1TF to perform page
table walks (by leaking the pointers across each page table level) to translate
arbitrary host virtual addresses to physical addresses. On Skylake, the page
tables have a tree-like structure with 4 levels. Each page table has 512 entries
which contain some control bits for the mapping, and the physical address of the
next level page table or of the mapped page. To convert from host virtual to
host physical addresses, the attacker has to descend the tree (leaking wise)
until it reaches a page table entry which contains the mapped page's physical
address. In short, by leaking page table entries, the exploit now elevates its
capabilities, from only chasing physmap pointers, to chasing arbitrary host
kernel pointers.

An important matter to note is that the attacker's leakage primitive is not
perfect. Neither half-Spectre, nor L1TF, nor Flush+Reload is perfect, hence
combining them results in leakage that sometimes contains some errors (e.g.,
leaking a 0x79 byte as 0x00). Given that the exploit relies on following chains
of pointers through memory, the attack will fail if only a single error
transpired somewhere in the chain. Hence, VUSec implements what they call
'chasing-and-checking'. At a high level, this entails that after a number of
'chased' (i.e., leaked to dereference) pointers, VUSec's exploit again leaks a
known prior pointer in the chain and check whether it did not go off track due
to incorrect leakage. By doing so, the attacker ensures the chain is not broken.

### Leaking interesting secret data

To exfiltrate interesting data from a victim guest VM, a possible attack would
be to just dump all the RAM (which would include all data from all VMs running
on the machine). However, that would be very slow and would not be very useful
as the state of the RAM is likely to change over time. The attacker, because of
the aforementioned problem, cannot just leak all memory, must first find a way
to determine the location of interesting data to leak.

The attacker will instead search for other VMs that are co-scheduled on the same
physical machine and their data by means of their metadata available in known
structures of the host. Namely, all task\_structs on the system are in a global
linked list. Starting from the task\_struct of its own CPU, the attacker can
search for a task that corresponds to a particular VM's vCPU. Once the attacker
finds a task associated with a targeted victim VM, the attacker can search that
task's file descriptor table, which contains a descriptor associated with KVM's
vCPU object. That file descriptor contains a pointer to that task's
[kvm\_vcpu](https://elixir.bootlin.com/linux/v6.16.1/source/include/linux/kvm_host.h#L323),
from which the attacker can not only leak the root of the victim VM's EPTs (in
[kvm\_vcpu\_arch](https://elixir.bootlin.com/linux/v6.16.1/source/arch/x86/include/asm/kvm_host.h#L778)
->
[kvm\_mmu](https://elixir.bootlin.com/linux/v6.16.1/source/arch/x86/include/asm/kvm_host.h#L453)
->
[kvm\_mmu\_root\_info](https://elixir.bootlin.com/linux/v6.16.1/source/arch/x86/include/asm/kvm_host.h#L429)),
but also the value of the guest's cr3 register (in
[kvm\_vcpu\_arch](https://elixir.bootlin.com/linux/v6.16.1/source/arch/x86/include/asm/kvm_host.h#L778)),
which contains the physical address of the root of the guest's own page tables.
With knowledge of the guest VM's EPTs and page tables, the attacker can perform
a two-dimensional page table walk. Here, the exploit traverses both these sets
of page tables to translate any guest virtual address to a host physical address
– which can be read from by using L1TF.

However, the attacker does not yet know where in the victim VM's memory the
interesting data lies, and cannot know this if the attacker does not know the
pointers that are interesting to follow. Hence, the attacker first aims to break
KASLR in the guest, which can be done by using the guest's page tables to find
the location of the kernel text and the kernel's direct map. With the former, it
is now possible for the attacker to find and follow interesting pointers, while
with the latter, the attacker can skip the costly address translation process
for various pointers in the guest kernel.

The attacker starts following pointers from the guest kernel's init\_task, which
is a global variable located at a known offset from the start of the guest
kernel, from where it is possible to traverse the list of tasks to find one
dealing with interesting data. In the real-world demonstrated exploit, the
researchers targeted an Nginx web server process in the guest as an example.
After finding it in the list of tasks, it then went through the Nginx process's
[mm\_struct](https://elixir.bootlin.com/linux/v6.16.1/source/include/linux/mm_types.h#L933)
and found its root page table and the virtual address of the start of its heap
memory. With the found page tables, the attacker can translate the heap's
virtual address into its physical counterpart, enabling leakage with L1TF
onward.

In the example of Nginx, the attackers know that Nginx stores its private key at
a static location on the heap, surrounded by magic numbers that make discovering
them easy. Using L1TF and the chase-and-check techniques to verify their leakage
was correct, it leaks the key successfully.

See a video demo of the exploit at the end of this blog.

## Mitigations

Fortunately, not all Intel CPUs are affected by L1TF. Cascade Lake and more
modern CPUs are not vulnerable to this particular CPU vulnerability, as listed
on Intel's list of
[Affected Processors: Transient Execution Attacks & Related Security](https://www.intel.com/content/www/us/en/developer/topic-technology/software-security-guidance/processors-affected-consolidated-product-cpu-model.html#tab-blade-1-2).
However, for Skylake and earlier CPUs, multiple mitigations need to be
implemented by software at some performance cost to users.

Google deployed multiple mitigations at the time of the initial discovery of
L1TF back in 2018. And earlier this year, as a result of the L1TF Reloaded
research, we have also deployed Address Space Isolation on the affected
processors (we had already deployed ASI on some other processors to protect
against other vulnerabilities like
[Inception](https://comsec.ethz.ch/research/microarch/inception/)).

### Intel Mitigations

![](https://storage.googleapis.com/bughunters-article-images/blogs/rain_06.png)

_Fig. 6. Explanation of core scheduling to prevent sharing a physical core_
_between two virtual machines, by Intel._

Intel's
[official documentation](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/intel-analysis-l1-terminal-fault.html)
expected all hypervisors to flush the cache before VM Enter and to disable the
sibling hyperthread unless both virtual CPUs were running guest code at the same
time. This would involve enabling full flushing on every VM Exit/Enter
transition, and enabling core stunning in every VM Exit. This would be very
expensive, since every time there is a VM Exit, the sibling core would need to
be paused.

![](https://storage.googleapis.com/bughunters-article-images/blogs/rain_07.png)

_Fig. 7. Relative performance of different workloads with a sibling hyperthread_
_enabled or disabled, by Intel._

The guidance explained that data prefetchers and speculative execution may
reload data that has been removed, so hypervisors should minimize or eliminate
periods after a L1D cache flush where secret data is both mapped in and is
marked as cacheable. As
[explained in 2018](https://cloud.google.com/blog/products/gcp/protecting-against-the-new-l1tf-speculative-vulnerabilities),
Google ensured that an individual core is never concurrently shared between
distinct virtual machines. That isolation also ensured that, in the case that
different virtual machines were scheduled sequentially (from one VM to another),
the L1 data cache was completely flushed to ensure that no vulnerable state
remained.

### Fixing Cache Load Gadgets

While clearing the L1 cache between VMs protected against guest-to-guest
attacks, a guest-to-host attack was publicly discussed in early 2019, with the
description of Half-Spectre gadgets
( [https://www.openwall.com/lists/oss-security/2019/01/21/8](https://www.openwall.com/lists/oss-security/2019/01/21/8)).
The attack works by triggering secret loads through half Spectre v1 Bounds-Check
Bypass (BCB) gadgets, leading to speculative arbitrary memory load in the VMExit
code path. That is the same attack used
in the VUSec exploit and described as cache load gadgets.

As a result, efforts were made to find and remove these gadgets from the kernel.
After fixing these internally at Google, we upstreamed them to Linux in 2020.

- [\[PATCH v2 00/13\] KVM: x86: Extend Spectre-v1 mitigation - Marios Pomonis](https://lore.kernel.org/lkml/20191211204753.242298-1-pomonis@google.com/)
- [\[PATCH\] KVM: x86: Extend Spectre-v1 mitigation](https://lore.kernel.org/lkml/20191122184039.7189-1-pomonis@google.com/)

The mitigation involved mostly the use of the
[array\_index\_nospec helper](https://www.kernel.org/doc/Documentation/speculation.txt)
in Linux. A call to array\_index\_nospec(index, size) returns a sanitized index
value that is bounded to `[0, size)` even under cpu speculation conditions. This\
is done by creating a "bit mask" which is either all 0 or all 1, and the value\
of the mask depends on a bounding condition being true (a technique also\
implemented as "speculative load hardening"). This was done selectively where it\
was understood that users might be able to control the value of an offset;\
however, doing this everywhere would have had a\
[significant performance cost](https://llvm.org/docs/SpeculativeLoadHardening.html#:~:text=high%20performance%20cost).\
\
Over time, new gadgets were introduced, among them were the gadgets used by the\
VUSec exploit:\
\
- [kvm\_sched\_yield](https://elixir.bootlin.com/linux/v6.16.1/source/arch/x86/kvm/x86.c#L10041)\
  - Triggered when making a\
    [KVM\_HC\_SCHED\_YIELD hypercall](https://www.kernel.org/doc/html/v6.16/virt/kvm/x86/hypercalls.html#kvm-hc-sched-yield).\
- [\_\_pv\_send\_ipi](https://elixir.bootlin.com/linux/v6.16.1/source/arch/x86/kvm/lapic.c#L846)\
  - Triggered when making a\
    [KVM\_HC\_SEND\_IPI hypercall](https://www.kernel.org/doc/html/v6.16/virt/kvm/x86/hypercalls.html#kvm-hc-send-ipi).\
\
Both were fixed on\
[KVM: x86: use array\_index\_nospec with indices that come from guest](https://github.com/gregkh/linux/commit/c87bd4dd43a624109c3cc42d843138378a7f4548).\
\
### Address Space Isolation\
\
![](https://storage.googleapis.com/bughunters-article-images/blogs/rain_08.png)\
\
_Fig. 8. Comparison of how the page tables are mapped with and without Address_\
_Space Isolation._\
\
While essential, these gadget-hunting efforts are part of a reactive posture\
that the kernel community has been forced into. For years, we have been\
developing bespoke mitigations for each new, scarily-named hardware\
vulnerability, from Meltdown and Spectre to Retbleed and L1TF. Address Space\
Isolation (ASI) is Google's proposed long-term, proactive solution designed to\
fix this entire class of vulnerabilities at once. ASI's fundamental principle is\
simple: speculative execution is stopped on its track when it runs into a page\
translation fault. As a result, speculative execution in kernel context cannot\
leak data that is not mapped into the kernel's address space.\
\
Google has deployed ASI internally and has also been\
[working](https://lore.kernel.org/all/20250812173109.295750-1-jackmanb@google.com/)\
on it with the Linux Kernel community. Address Space Isolation separates memory\
addresses into "sensitive" (memory that may contain secrets) and "nonsensitive"\
(memory that can't directly be used to compromise co-scheduled processes or\
VMs). Note that sensitive data includes all userspace/guest data, so the vast\
majority of memory is protected. In terms of protecting KVM guest data this is\
conceptually similar to placing all guest memory within\
' [memfd\_secret](https://man7.org/linux/man-pages/man2/memfd_secret.2.html)'\
regions (which also removes the memory from the kernel page tables). However,\
ASI also protects userspace memory, and is flexible enough to also protect\
internal kernel data structures.\
\
When ASI is enabled, whenever there is a VM Exit, there is no sensitive data\
present in the memory address space of the kernel. However, when the kernel\
needs to access this data, a page fault, which occurs as sensitive data is not\
present in the restricted address space, triggers what we call an "ASI Exit".\
This transitions the kernel to its full address space and clears the CPU shared\
buffers (like the buffers used by the branch predictor) to prevent\
guest-influenced speculation before allowing access. When the kernel prepares\
for a VM Enter from this sensitive state, an ASI Enter is triggered. This\
reverts to the restricted address space and flushes CPU data buffers (e.g. L1\
Data Cache) to prevent sensitive data leaks. This prevents any information from\
leaking between Host and Guest state, while minimizing the number of times that\
a flush is necessary. This is efficient because the majority of the transitions\
in and out of the Guest do not need access to any sensitive data. In fact, our\
extensive performance testing with ASI and L1 Data Cache flush on ASI Entry has\
demonstrated a performance impact of less than 3% across almost all benchmarks,\
with an impact of less than 1% being common.\
\
_But that alone is not sufficient_, as the shared buffers are also shared\
between hyperthreads. So even if clearing is done before a VM Enter, it is still\
possible for the other hyperthread to read the data off the L1 cache before it\
happens. That is:\
\
1. Hyper thread 1 runs guest code\
2. Hyper thread 2 does ASI exit and triggers a half-spectre gadget\
3. Hyper thread 1 (still as guest) reads L1 data\
4. Hyper thread 2 does ASI enter, and clears L1 cache\
\
While a malicious VM could schedule tasks on hyperthread neighbors to achieve\
the necessary conditions, the additional hurdle lies in identifying a\
half-Spectre gadget capable of loading arbitrary data during an ASI exit. This\
is significantly more difficult, as the instances where ASI exits occur are\
exceedingly rare, and triggering one from within a VM is considerably more\
challenging and improbable than merely locating a VMExit path. An attacker\
would, furthermore, be required to cause an ASI Exit in conjunction that also\
allows them to trigger a half-Spectre gadget.\
\
We searched for half-Spectre gadgets within the kernel and we could not find one\
that a guest could trigger during an ASI exit. Nevertheless, for\
future-proofing, the sibling hyperthread must be paused, or "stunned," whenever\
an ASI exit occurs. This stunning process is inherently expensive, as any\
ongoing operations on the other hyperthread must be interrupted, and all\
associated state, including the L1 cache, must be flushed, thereby imposing a\
substantial performance overhead on workloads.\
\
We have spent a lot of effort identifying the most efficient way to implement\
stunning-during-ASI exit so that it imposes the minimum amount of performance\
cost to VMs as possible. This stunning-during-ASI exit functionality has been\
integrated into Google's internal kernel fork, and we intend to release it\
externally in a subsequent patch series once we deem it prepared and have\
finalized our testing and qualification processes on our systems.\
\
## Conclusion\
\
In this post, we set out to provide a detailed overview of the "L1TF Reloaded"\
exploit chain, demonstrating CPU exploits are real and how the barrier to\
develop one that can breach across VMs is becoming easier to cross. We show how\
the vulnerability could be used by an attacker and, most importantly, detailing\
the different mitigation strategies to protect against it. One key takeaway is\
that reactive security postures, like hunting for individual "gadgets," are not\
future proof or sufficient to protect against state-of-the-art CPU exploits and\
instead we need a holistic solution. Address Space Isolation isn't just a patch,\
it's a proactive, fundamental solution that severs the link between speculative\
execution and sensitive data, all while maintaining high performance and\
minimizing the cost that these vulnerabilities impose on users. Performance\
punitive mitigations can lead to weak adoption and leave security gaps behind\
which is why ASI being low overhead and comprehensive is critical.\
\
We also highlighted how important open collaboration is between industry and the\
research community. This collaboration allows industry to leverage the deep\
expertise of leading security research groups, like VUSec, to protect users.\
While also providing a safe environment for researchers to conduct cutting edge\
offensive security research on realistic environments without putting users at\
risk.\
\
## Acknowledgements\
\
The authors would like to acknowledge the invaluable feedback during the review\
of this blog:\
\
- The Rain Team: Thijs Raymakers, Mahesh Hari Sarma, Marius Muench (University\
of Birmingham), Herbert Bos, Erik van der Kouwe\
- The Google Team: Adam Krasuski, Brendan Jackman, Christoph Kern, Reiji\
Watanabe, KP Singh, Natalie Silvanovich, Andrés Lagar-Cavilla, Alexandra\
Sandulescu\
\
- ### Video demo of exploit\
\
\
\
L1TF Reloaded - YouTube\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
Tap to unmute\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
[L1TF Reloaded](https://www.youtube.com/watch?v=W9ctPp-luwA) [VUSec](https://www.youtube.com/channel/UC9WimJoKklmni4feJD9bdhw)\
\
\
\
\
\
\
\
VUSec1.17K subscribers\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
[Watch on](https://www.youtube.com/watch?v=W9ctPp-luwA)\
\
\
[Back to overview](https://bughunters.google.com/blog)\
\
Sign In - Google Accounts\
\
Sign inSign in with Google. Opens in new tab