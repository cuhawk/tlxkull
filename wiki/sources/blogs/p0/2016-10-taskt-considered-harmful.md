---
source: p0
source_url: https://projectzero.google/2016/10/taskt-considered-harmful.html
title: "task_t considered harmful - Project Zero"
description: "Posted by Ian Beer, Project ZeroThis post discusses a design issue at the core of the XNU kernel ..."
---

Posted by Ian Beer, Project Zero

This post discusses [a design issue at the core of the XNU kernel](https://bugs.chromium.org/p/project-zero/issues/detail?id=837) which powers iOS and MacOS. Apple have shipped two iterations of mitigations followed yesterday by a large refactor in MacOS 10.12.1/iOS 10.1. We’ll look at the bugs, how they can be exploited to escape sandboxes and escalate privileges, and how we can defeat each of the mitigations. Every step is accompanied by a working exploit.

## Some background on mach ports

Mach ports are multiple-sender, single-receiver message queues maintained by the kernel. Some special mach ports provide the same message-passing API to userspace but messages sent to them are handled synchronously by kernel message handlers. In this sense messages sent to these ports are quite a lot like syscalls.

Task ports are an example of this kind of port. They handle messages which allow senders to manipulate the virtual memory of a task and gain access to its threads. Each task (process) has its own task port. MIG is the name of the tool used to generate the serialization code used by these kernel-owned message ports.

## A low-level look at IOKit

When you create a new IOKit user client in userspace you normally call this method from IOKitLib:

kern\_return\_t

IOServiceOpen(

io\_service\_t service,

task\_port\_t owningTask,

uint32\_t type,

io\_connect\_t \*connect );

IOServiceOpen calls the MIG generated serialization code for the io\_service\_open\_extended IPC method and sends that serialized message to the provided IOService port. The mach\_msg mach trap notices that this port is owned by the kernel and calls the correct kernel MIG handler for this message rather than queuing it onto the port’s message queue.

The task port passed here is called owningTask; the same name is used throughout the userspace and kernel code. This name was the first thing which made me suspicious. OwningTask implies an ownership relationship which might lead kernel extension developers to believe that behind the scenes IOKit is actually maintaining an ownership relationship which will ensure that the lifetime of this userclient will always be dominated by the lifetime of the owningTask. This is a dangerous assumption, and this blog post is really the fallout from questioning this assumption. Let’s keep following the flow of this code into the kernel. Here’s a snippet from the kernel-side MIG deserialization code for io\_service\_open\_extended:

mig\_internal novalue \_Xio\_service\_open\_extended(

mach\_msg\_header\_t \*InHeadP,

mach\_msg\_header\_t \*OutHeadP)

{

...

owningTask = convert\_port\_to\_task(In0P->owningTask.name);

RetCode = is\_io\_service\_open\_extended(

              service,

              owningTask,

              In0P->connect\_type,

              In0P->ndr,

              (io\_buf\_ptr\_t)(In0P->properties.address),

              In0P->propertiesCnt, &OutP->result, &connection);

task\_deallocate(owningTask);

...

The kernel has already copied-in all the rights contained in the message so In0P->owningTask.name is actually a pointer to a struct ipc\_port and not the mach port’s name as seen from userspace.

Here’s convert\_port\_to\_task:

task\_t

convert\_port\_to\_task(

ipc\_port\_t port)

{

task\_t task = TASK\_NULL;

if (IP\_VALID(port)) {

    ip\_lock(port);

    if (ip\_active(port) &&

        ip\_kotype(port) == IKOT\_TASK)

    {

      task = (task\_t)port->ip\_kobject;

      assert(task != TASK\_NULL);

      task\_reference\_internal(task);

    }

    ip\_unlock(port);

}

return (task);

}

This checks that the port argument really is a task port object then takes a reference on the task by calling task\_reference and returns the task\_t pointer. task\_t is a typedef for a pointer to a struct task and as you can see from the code it’s a reference-counted object.

is\_is\_service\_open\_extended doesn’t do anything with owningTask other than passing it to ::newUserClient:

res = service->newUserClient(

    owningTask,

    (void \*) owningTask,

    connect\_type,

    propertiesDict,

    &client );

newUserClient is an IOService method which can be overridden by an IOService if they want to offer multiple userclient types. Otherwise the default implementation will look up the IOService’s IOUserClient subclass class name in the IOKit registry, allocate it via [IOKit’s reflection API](https://bugs.chromium.org/p/project-zero/issues/detail?id=221) and call its ::initWithTask method. The default implementation of ::initWithTask also doesn’t do anything with owningTask.

Having looked through the code this far it looks like it’s not the case that by default the owningTask is going to hold a reference on the userclient (which would prevent the userclient taking a reference on the task and causing a reference cycle.) In fact it’s clearly quite the opposite; the userclient must take a reference on the owningTask if it wishes to keep a reference to the owningTask - there’s no implicit ownership relationship at all.

## Checking the docs

There aren’t a whole lot of resources for writing OS X kernel extensions. Apple does publish a sample kext on their developer site called AppleSamplePCI which provides examples of various IOKit design patterns. Here’s the AppleSamplePCI.kext implementation of initWithTask:

bool SamplePCIUserClientClassName::initWithTask(

task\_t owningTask,

void\* securityID,

UInt32 type,

OSDictionary\* properties)

{

bool success = super::initWithTask(owningTask,

                                     securityID,

                                     type,

                                     properties);

fTask = owningTask;

fDriver = NULL;

return success;

}

The sample userclient stores the owningTask argument in the fTask member variable without taking a reference. Without that reference there’s no guarantee that the task struct pointed to by fTask hasn’t been freed after this method returns. Looking through the rest of the sample kext we can see that some external methods use the fTask pointer to create memory descriptors - if we can get the task struct pointed to by fTask to be freed these will be using a dangling pointer.

Opening up a handful of other OS X kexts in IDA it’s pretty clear that lots of them follow this anti-pattern of holding a task\_t pointer without taking a reference.

## Creating a dangling task\_t

Mach messages provide very flexible and powerful IPC building blocks. One of the neat things you can do is send other processes send-rights to mach ports for which you hold send or receive rights.

Because task ports give you complete control over other tasks the api to request the task port for another task (task\_for\_pid) is privileged but since all tasks have send rights to their own task ports if we have code execution in two tasks we can send a send-right to the second task’s task port to the first.

In this case we’ll use the [technique outlined by Robert Sesek](https://robert.sesek.com/2014/1/changes_to_xnu_mach_ipc.html) to create a shared mach port between a parent and forked child by stashing a send-right in the bootstrap\_port special port slot. After the fork the child can recover this stashed port, restore the bootstrap port and set up a bi-directional IPC channel over which it can send its task port back to the parent.

Triggering the UaF in the vulnerable anti-pattern looks like this:

- parent forks off a child

- child sends its task port back to its parent

- child spins

- parent receives child’s task port and creates a vulnerable IOKit userclient passing the child’s task port as owningTask

- parent destroys its send right to the child’s task port

- parent kills child, freeing the task struct of the child

- parent has a userclient with a dangling task struct pointer


## A first exploit

Looking through the IOKit drivers which had this bug, one jumped out as being particularly interesting - IOSurfaceRootUserClient. Here’s what the Apple developer docs have to say about IOSurface:

The IOSurface framework provides a framebuffer object suitable for sharing across process boundaries. It is commonly used to allow applications to move complex image decompression and draw logic into a separate process to enhance security.

In reality IOSurfaces are just wrappers around shared memory buffers. On OS X we can talk to the IOSurface kernel extension from inside the Safari renderer sandbox and the Chrome GPU sandbox, amongst others.

The IOSurfaceRootUserClient class has exactly the same anti-pattern as we saw in the AppleSamplePCI client where the userclient stores a copy of the owningTask pointer as a member variable without taking a reference. Some reversing tells us that external method 0 of IOSurfaceRootUserClient is create\_surface which takes a dictionary of key-value parameters used to create a shared memory object that other processes can map into their address spaces. By passing the following keys and values we can get IOSurfaceRootUserClient to wrap existing userspace pages in an IOSurface rather than allocating a new buffer:

IOSurfaceAddress:   base\_address

IOSurfaceAllocSize: size

IOSurfaceIsGlobal:  true

The IOSurface object actually just wraps an IOMemoryDescriptor which is allocated in IOSurface::allocate by calling:

IOMemoryDescriptor \*

IOMemoryDescriptor::withAddressRange(

mach\_vm\_address\_t address,

mach\_vm\_size\_t length,

IOOptionBits   options,

task\_t         task);

The final task\_t task argument to IOMemoryDescriptor::withAddressRange defines which task’s virtual memory the descriptor should be created for. IOSurface passes the member variable storing its copy of owningTask here, on which it doesn’t hold a reference! If we can get that task struct memory to be freed (by the original task exiting), reallocated (by another task starting) and used as the task struct for a more privileged task then this IOMemoryDescriptor will believe it’s wrapping a portion of the current process’s address space when it’s actually wrapping a portion of that other more privileged task’s virtual memory in the IOMemoryDescriptor which backs this IOSurface.

Setting IOSurfaceIsGlobal=true makes that surface available to other processes so that by calling external method 6 (lookup\_surface) on another IOSurfaceRootUserClient created with our own legitimate task port as the owningTask we can build a primitive which allows us to map arbitrary portions of other process’s address spaces into our own :-)

Since the IOMemoryDescriptor is actually creating shared memory mappings of those pages we can write to them and those writes will also be reflected in the other process. IOSurfaceRootUserClient doesn’t allow us to map executables pages from the victim but we can still map for example the \_\_DATA segment of libraries. This is made easier by the shared library cache being at the same virtual address in all processes.

## Putting the exploit together

We need a way to get the task struct reused by a more privileged process and then we need something to overwrite in the target to get code execution.

Task structs are allocated from their own kernel heap zone which greatly simplifies things. We can just kill the child and fork and exec a few suid-root binaries and they are very likely to re-use the same memory pointed to by the dangling task\_t.

For the overwrite target I chose to target the \_\_cleanup pointer in libc. This will be called when the process exits.  We can play a few tricks to block the binary just before it exits by setting its stderr file descriptor to a full pipe and forcing it to write an error message giving us plenty of time to exploit the bug in the parent process and overwrite the \_\_cleanup pointer before emptying the pipe in the parent. I chose to point the function pointer to a gadget which adds a large constant to RSP and returns. Doing this moves the stack pointer up into argv and since we exec’ed this binary I put a simple ROP stack there to call setuid(0) and execve /bin/bash. The ROP payload is prefixed with a large number of ret-slide gadgets so it should be stable across most versions of OS X.

You can download this [exploit](https://bugs.chromium.org/p/project-zero/issues/attachment?aid=237183) and check out the [original bug report](https://bugs.chromium.org/p/project-zero/issues/detail?id=831).

Since this bug also allows us to gain any entitlements we want as well as root it’s easy to use it to defeat kernel code signing on OS X and load an unsigned kernel extension. See the [exploit for CVE-2016-1757](https://projectzero.google/2016/03/race-you-to-kernel.html) for one way to do this.

Although this exploit uses fork and execve they aren’t actually required - the only prerequisite for triggering the bug is that you need code execution in two co-operating processes which can send mach messages to each other, and for this particular bug to be able to talk to IOSurface. Damien DeVille has a [blog post](http://ddeville.me/2015/02/interprocess-communication-on-ios-with-mach-messages) discussing ways of achieving this from within the app sandbox on iOS using application groups. It’s also not necessary to exec a suid-root binary: we could cause the freed task struct to be reused by another more privileged task by looking up a mach service via launchd or deliberately crashing and causing launchd to run the CrashReporter.

Many individual instances of this bug were fixed in OS X 10.11.6/iOS 9.3.3 and Apple shipped a mitigation to prevent passing other task’s task ports to certain IOKit methods.

## Stepping back

This use-after-free bug is quite fun but it obscures a far deeper and more concerning issue. If the IOSurfaceRootUserClient now calls task\_reference() on owningTask, and owningTask has to be the original creator of the userclient, is there still a bug?

Earlier this year [osxreverser@](https://twitter.com/osxreverser) and I both independently published research about a problem with the execve syscall. In that case there was a race condition due to the order in which execve performed certain operations when loading a suid binary which left a small race window between the new memory map being created and the old task port being invalidated.

There’s a far more fundamental problem: the execve syscall doesn’t actually create a new task struct, even when it executes a more privileged suid binary. It just modifies the existing task struct in-place and any objects which previously had a task\_t pointer now have one to a more privileged task.

This isn’t temporal memory safety - there’s no use-after-free involved. Lets look in detail at why that’s such a large problem for XNU.

## XNU’s Neither Unix Nor Mach

In a pure Mach microkernel invalidating the old task port would be sufficient to prevent any other process from maintaining control of a task across a privilege-escalating exec, but XNU isn’t a microkernel. Earlier we looked at the kernel function convert\_port\_to\_task which takes a mach task port and converts it into a task struct pointer. This pointer can then be used and passed around within the kernel without all the overhead of sending messages. For example when IOKit wants to manipulate the virtual memory of a process, rather than having to send a mach message to the mach\_vm MIG subsystem (which it could theoretically do) it instead directly calls the responsible kernel function.

Another way to think of this is that all the MIG subsystems which live in the kernel (IOKit, mach\_vm, tasks, threads, semaphores etc) are directly linked against each other. They can simply call the target functions rather than going via the MIG IPC layer. This is obviously massively faster, but comes at a cost.

## Every task\_t pointer is a potential security bug

The tradeoff is that now there’s no central point where access to a resource can be cut off. In the kernel they can’t just invalidate the task port when a privileged exec happens and expect that to work because the kernel-internal MIG subsystems don’t use task ports, they just translate between task ports and task struct pointers once at the user/kernel boundary. The kernel has no idea where all the kernel pointers to a task’s task struct are; it can’t hope to invalidate them.

This is a much bigger problem than the original reference counting bug. When a privilege-escalating exec takes place execve doesn’t create a new process; the task struct stays the same, just the privileges change. This means that every single task\_t pointer in the kernel is a potential security bug - there’s no locking mechanism to let you assert that the privileges of a task struct haven’t changed since you got access to it and just because kernel code got access to a task struct at one time doesn’t mean it should have access later.

## On the heap: rewriting the IOSurface exploit

We actually only need to slightly tweak the original IOSurface exploit to work even with the correct task\_reference(owningTask) call. Instead of the child passing its task port back to the parent we’ll instead create the IOSurfaceRootUserClient in the child (correctly using the child’s own task port) and pass that userclient port back to the parent.

The child can then execve a suid-root binary which will set the EUID of the task to 0 without freeing the task struct. The parent still has a send right to the IOSurfaceRootUserClient, and that userclient’s owningTask now has EUID 0. The parent can then proceed as before, blocking the child, mapping the target’s libc \_\_DATA segment, overwriting a function pointer and unblocking the child so that it tries to exit and executes the ROP stack. This new exploit also defeats the mitigation added in 10.11.6 which stops the creation of userclients with other task’s task ports.

Note that there are no failure cases for this exploit - there’s no race to win and no use-after-free which could go wrong. The [exploit](https://bugs.chromium.org/p/project-zero/issues/attachment?aid=256267) should work on all OS X versions <= 10.11.6.

This primitive is slightly less powerful than the use after free, which could break you out of very restrictive sandboxes, as you do need to call execve. These IOKit objects which store task\_t pointers on the heap are really just the top of the iceberg though.

## On the stack: exploiting task\_threads

Back closer to the user/kernel boundary as soon as convert\_port\_to\_task has converted a task port received from userspace into a task struct pointer, that task could exec a suid-root or entitled binary and increase its privileges. Even if that task struct pointer isn’t stored on the heap there could still be an exploitable bug. Once case of this is the kernel MIG task\_threads method:

kern\_return\_t

task\_threads(

task\_t target\_task,

thread\_act\_array\_t \*act\_list,

mach\_msg\_type\_number\_t \*act\_listCnt );

Given a send right to a task port this method returns send rights to the thread ports for each of the threads in that task. Here’s a snippet from MIG auto-generated code in the kernel:

target\_task = convert\_port\_to\_task(

    In0P->Head.msgh\_request\_port); // (1)

RetCode = task\_threads(

              target\_task,

              (thread\_act\_array\_t \*)&(OutP->act\_list.address),

              &OutP->act\_listCnt);

task\_deallocate(target\_task);

Here we see that the task port is converted into the underlying task struct pointer which is then stored in the target\_task local variable which lives for the duration of this function call.

Here’s the relevant code from task\_threads:

task\_threads(

    task\_t task,

    thread\_act\_array\_t \*threads\_out,

    mach\_msg\_type\_number\_t \*count)

{

    ...

    for (thread = (thread\_t)queue\_first(&task->threads);

         i < actual;

         ++i, thread = (thread\_t)queue\_next(&thread->task\_threads)) {

      thread\_reference\_internal(thread);

      thread\_list\[j++\] = thread;

    }

    ...

      for (i = 0; i < actual; ++i)

((ipc\_port\_t \*) thread\_list)\[i\] = convert\_thread\_to\_port(thread\_list\[i\]); // (2)

      }

    ...

}

This code iterates through the list of threads collecting the struct thread pointers then converts those struct threads to thread ports and returns. There are a handful of locks in the code but they’re not relevant.

What happens if that task is exec-ing a suid root binary at the same time?

The relevant parts of the exec code are these two points in ipc\_task\_reset and ipc\_thread\_reset:

void

ipc\_task\_reset(

    task\_t    task)

{

    ipc\_port\_t old\_kport, new\_kport;

    ipc\_port\_t old\_sself;

    ipc\_port\_t old\_exc\_actions\[EXC\_TYPES\_COUNT\];

    int i;

    new\_kport = ipc\_port\_alloc\_kernel();

    if (new\_kport == IP\_NULL)

      panic("ipc\_task\_reset");

    itk\_lock(task);

    old\_kport = task->itk\_self;

    if (old\_kport == IP\_NULL) {

      itk\_unlock(task);

      ipc\_port\_dealloc\_kernel(new\_kport);

      return;

    }

    task->itk\_self = new\_kport;

    old\_sself = task->itk\_sself;

    task->itk\_sself = ipc\_port\_make\_send(new\_kport);

ipc\_kobject\_set(old\_kport, IKO\_NULL, IKOT\_NONE); // (3)

This is followed by a call to ipc\_thread\_reset:

ipc\_thread\_reset(

    thread\_t  thread)

{

    ipc\_port\_t old\_kport, new\_kport;

    ipc\_port\_t old\_sself;

    ipc\_port\_t old\_exc\_actions\[EXC\_TYPES\_COUNT\];

    boolean\_t  has\_old\_exc\_actions = FALSE;

    int      i;

    new\_kport = ipc\_port\_alloc\_kernel();

    if (new\_kport == IP\_NULL)

      panic("ipc\_task\_reset");

    thread\_mtx\_lock(thread);

    old\_kport = thread->ith\_self;

    if (old\_kport == IP\_NULL) {

      thread\_mtx\_unlock(thread);

      ipc\_port\_dealloc\_kernel(new\_kport);

      return;

    }

thread->ith\_self = new\_kport; // (4)

Let's call the process which is doing the exec process B and the process calling task\_threads() process A and imagine the following interleaving of execution:

A:

target\_task = convert\_port\_to\_task(

    In0P->Head.msgh\_request\_port); // (1)

A gets pointer to process B's task struct on the stack

B:

ipc\_kobject\_set(old\_kport, IKO\_NULL, IKOT\_NONE); // (3)

B is execing a suid binary and invalidates the old task port so that it no longer has a task struct pointer

B:

thread->ith\_self = new\_kport; // (4)

B allocates new thread ports and sets them up

A:

((ipc\_port\_t \*) thread\_list)\[i\] = convert\_thread\_to\_port(thread\_list\[i\]); // (2)

A reads and converts the new thread port objects for B’s privileged threads giving A a privileged thread port

Send rights to a thread port give you complete register control. The exploit proceeds in a similar fashion to the previous two except that once it’s got the thread port it can directly point RIP to the gadget address rather than overwriting a function pointer. This race window is quite tight as is requires a very particular interleaving of execution but it does work. Check out the [exploit](https://bugs.chromium.org/p/project-zero/issues/attachment?aid=237182) and the [original bug report](https://bugs.chromium.org/p/project-zero/issues/detail?id=837).

## Mitigations round 2

The release of iOS 10/MacOS 10.12 brought another round of mitigations to defeat.

Firstly on the IOKit side userclient lifetime is now directly tied to that of the creating task. Secondly there’s a mitigation in ipc\_kobject server to detect when a MIG kernel method has raced an execve syscall and force the method to fail if a race was detected:

/\*

\\* Check if the port is a task port, if its a task port then

\\* snapshot the task exec token before the mig routine call.

\*/

ipc\_port\_t port = request->ikm\_header->msgh\_remote\_port;

if (IP\_VALID(port) && ip\_kotype(port) == IKOT\_TASK) {

task = convert\_port\_to\_task\_with\_exec\_token(port, &exec\_token);

}

(\*ptr->routine)(request->ikm\_header, reply->ikm\_header);

/\\* Check if the exec token changed during the mig routine \*/

if (task != TASK\_NULL) {

if (exec\_token != task->exec\_token) {

    exec\_token\_changed = TRUE;

}

task\_deallocate(task);

}

There are three flaws with this mitigation:

1. It only inspects the first argument, there are kernel MIG methods which take a task port in a different position.

2. It only checks for task ports, these issues also affect thread\_ports in a similar way

3. It only mitigates cases of the bug where we need to get the resources which are returned by the MIG call (eg ports.) There are plenty of other methods which actually directly modify the process state rather than returning new ports.


## Exploiting the 2nd round mitigations

Although we can no longer directly get a new thread port via task\_threads there are still some more roundabout ways to get it. We just need an API which modifies state rather than directly returning something useful (like a task port) to us.

task\_set\_exception\_port allows us to set a the exception port for a task. When an exception is raised (for example by accessing invalid memory) the kernel will send an exception message to the registered exception handler. Importantly for us that exception message contains the task and thread ports for the thread which caused the exception.

Like almost all places in the kernel with a task\_t on the stack this api has a vulnerable race condition. In process A we’ll keep calling task\_set\_exception\_ports() passing B’s task port while B execve’s a suid binary:

mig\_internal novalue \_Xtask\_set\_exception\_ports(

mach\_msg\_header\_t \*InHeadP,

mach\_msg\_header\_t \*OutHeadP) {

...

task = convert\_port\_to\_task(In0P->Head.msgh\_request\_port); // (1)

OutP->RetCode =

    task\_set\_exception\_ports(task,

                             In0P->exception\_mask,

                             In0P->new\_port.name,

                             In0P->behavior,

                             In0P->new\_flavor);

task\_deallocate(task);

...

kern\_return\_t

task\_set\_exception\_ports(

task\_t                task,

exception\_mask\_t      exception\_mask,

ipc\_port\_t            new\_port,

exception\_behavior\_t  new\_behavior,

thread\_state\_flavor\_t new\_flavor)

{

...

itk\_lock(task); // (2)

for (i = FIRST\_EXCEPTION; i < EXC\_TYPES\_COUNT; ++i) {

    if ((exception\_mask & (1 << i)) ) {

      old\_port\[i\] = task->exc\_actions\[i\].port;

task->exc\_actions\[i\].port = ipc\_port\_copy\_send(new\_port); // (3)

      task->exc\_actions\[i\].behavior = new\_behavior;

      task->exc\_actions\[i\].flavor = new\_flavor;

      task->exc\_actions\[i\].privileged = privileged;

    }

...

itk\_unlock(task);

...

Process B calls execve to exec a privileged suid binary:

ipc\_task\_reset(

task\_t  task)

{

...

itk\_lock(task); // (4)

...

ip\_lock(old\_kport);

ipc\_kobject\_set\_atomically(old\_kport, IKO\_NULL, IKOT\_NONE); // (5)

task->exec\_token += 1;

ip\_unlock(old\_kport);

ipc\_kobject\_set(new\_kport, (ipc\_kobject\_t) task, IKOT\_TASK);

for (i = FIRST\_EXCEPTION; i < EXC\_TYPES\_COUNT; i++) {

...

    if (!task->exc\_actions\[i\].privileged) {

      old\_exc\_actions\[i\] = task->exc\_actions\[i\].port;

task->exc\_actions\[i\].port = IP\_NULL; // (6)

    }

}

itk\_unlock(task); //(7)

We’re looking for the following interleaving:

A:

task = convert\_port\_to\_task(In0P->Head.msgh\_request\_port); // (1)

B:

itk\_lock(task); // (4)

ipc\_kobject\_set\_atomically(old\_kport, IKO\_NULL, IKOT\_NONE); // (5)

task->exc\_actions\[i\].port = IP\_NULL; // (6)

itk\_unlock(task); //(7)

A:

itk\_lock(task); // (2)

task->exc\_actions\[i\].port = ipc\_port\_copy\_send(new\_port); // (3)

This race condition is far easier to win than the task\_threads case as the locks make sure that everything lines up nicely for us. We just need to call task\_set\_exception\_ports in a loop and hope that (1) gets called by A just before B takes the task lock at (4). In practise the exploit wins the race in a few milliseconds.

The final trick is to actually make sure that if we win the race we force the child to cause an exception and send us its task and thread ports. We can do this by calling setrlimit(RLIMIT\_STACK) with a very small value just before execing the suid target. This means that the binary will be run with a tiny stack and will almost immediately segfault.

In the parent once the task\_set\_exception\_port call has failed we try to receive on the exception port with a short timeout. If a message is received then we won the race and that message contains the task and thread ports for an euid 0 process. In this case the exploit allocates some RWX memory in the task and copies a shellcode stub into there which does this:

struct rlimit lim = {0x1000000, 0x1000000};

setrlimit(RLIMIT\_STACK, lim);

setuid(0);

char\* argv\[2\] = {"/bin/bash", 0};

execve("/bin/bash", argv, 0);

This shellcode sets the stack size back to a large value, does a setuid(0) to prevent bash dropping privileges and executes a shell.

This [exploit](https://bugs.chromium.org/p/project-zero/issues/attachment?aid=256266) should work reliably on all versions of MacOS/OS X 10.12.0 and below.

## The final fix

This isn’t an easy bug class to fix. Due to the design of XNU there are task\_t pointers everywhere and the underlying issue affects more than just task\_t; threads suffer from the same issue. Apple decided to refactor the execve code to allocate new task and thread structures when loading a binary which should fix the underlying issue. This is a considerable amount of work, kudos to Apple for the engineering effort they put into fixing these bugs and I look forward to the release of the MacOS 10.12.1 XNU source to see the new code.