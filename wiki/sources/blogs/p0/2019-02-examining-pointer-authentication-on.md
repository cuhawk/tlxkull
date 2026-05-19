---
source: p0
source_url: https://projectzero.google/2019/02/examining-pointer-authentication-on.html
title: "Examining Pointer Authentication on the iPhone XS - Project Zero"
description: "Posted by Brandon Azad, Project ZeroIn this post I examine Apple's implementation of Pointer Auth..."
---

Posted by Brandon Azad, Project Zero

In this post I examine Apple's implementation of Pointer Authentication on the A12 SoC used in the iPhone XS, with a focus on how Apple has improved over the ARM standard. I then demonstrate a way to use an arbitrary kernel read/write primitive to forge kernel PAC signatures for the A keys, which is sufficient to execute arbitrary code in the kernel using JOP. The technique I discovered was (mostly) fixed in iOS 12.1.3. In fact, this fix first appeared in the 16D5032a beta while my research was still ongoing.

# ARMv8.3-A Pointer Authentication

Among the most exciting security features introduced with ARMv8.3-A is Pointer Authentication, a feature where the upper bits of a pointer are used to store a Pointer Authentication Code (PAC), which is essentially a cryptographic signature on the pointer value and some additional context. Special instructions have been introduced to add an authentication code to a pointer and to verify an authenticated pointer's PAC and restore the original pointer value. This gives the system a way to make cryptographically strong guarantees about the likelihood that certain pointers have been tampered with by attackers, which offers the possibility of greatly improving application security.

(Proper terminology dictates that the security feature is called Pointer Authentication while the cryptographic signature that is inserted into the unused bits of a pointer is called the Pointer Authentication Code, or PAC. However, popular usage has already confused these terms, and it is common to see Pointer Authentication referred to as PAC. Usually this usage is unambiguous, so for brevity I will often refer to Pointer Authentication as PAC as well.)

There are many great articles describing Pointer Authentication, so I'll only go over the rough details here. Interested readers can refer to [Qualcomm's whitepaper](https://www.qualcomm.com/media/documents/files/whitepaper-pointer-authentication-on-armv8-3.pdf), [Mark Rutland's slides](https://events.static.linuxfound.org/sites/events/files/slides/slides_23.pdf) from the 2017 Linux Security Summit, [this LWN article](https://lwn.net/Articles/718888/) by Jonathan Corbet, and the [ARM A64 Instruction Set Architecture](https://static.docs.arm.com/ddi0596/a/DDI_0596_ARM_a64_instruction_set_architecture.pdf) for further details.

The key insight that makes Pointer Authentication viable is that, although pointers are 64 bits, most systems have a virtual address space that is much smaller, which leaves unused bits in a pointer that can be used to store additional data. In the case of Pointer Authentication, these bits will be used to store a short authentication code over both the original 64-bit pointer value and a 64-bit context value.

Systems are allowed to use an implementation-defined algorithm to compute PACs, but the standard recommends the use of a block cipher called QARMA. According to the whitepaper, QARMA is "a new family of lightweight tweakable block ciphers" designed specifically for pointer authentication. QARMA-64, the variant used in the standard, takes as input a secret 128-bit key, a 64-bit plaintext value (the pointer), and a 64-bit tweak (the context), and produces as output a 64-bit ciphertext. The truncated ciphertext becomes the PAC that gets inserted into the unused extension bits of the pointer.

The architecture provides for 5 secret 128-bit Pointer Authentication keys. Two of these keys, APIAKey and APIBKey, are used for instruction pointers. Another two, APDAKey and APDBKey, are used for data pointers. And the last key, APGAKey, is a special "general" key that is used for signing larger blocks of data with the PACGA instruction. Providing multiple keys allows for some basic protection against pointer substitution attacks, in which one authenticated pointer is substituted with another.

The values of these keys are set by writing to special system registers. The registers containing the Pointer Authentication keys are inaccessible from EL0, meaning that a userspace process cannot read or change them. However, the hardware provides no other key management features: it's up to the code running at each exception level to manage the keys for the next lower exception level.

ARMv8.3-A introduces three new categories of instructions for dealing with PACs:

- PAC\* instructions generate and insert the PAC into the extension bits of a pointer. For example, PACIA X8, X9 will compute the PAC for the pointer in register X8 under the A-instruction key, APIAKey, using the value in X9 as context, and then write the resulting PAC'd pointer back in X8. Similarly, PACIZA is like PACIA except the context value is fixed to 0.

- AUT\* instructions verify a pointer's PAC (along with the 64-bit context value). If the PAC is valid, then the PAC is replaced with the original extension bits. Otherwise, if the PAC is invalid (indicating that this pointer was tampered with), then an error code is placed in the pointer's extension bits so that a fault is triggered if the pointer is dereferenced. For example, AUTIA X8, X9 will verify the PAC'd pointer in X8 under the A-instruction key using X9 as context, writing the valid pointer back to X8 if successful and writing an invalid value otherwise.

- XPAC\* instructions remove a pointer's PAC and restore the original value without performing verification.


In addition to these general Pointer Authentication instructions, a number of specialized variants were introduced to combine Pointer Authentication with existing operations:

- BLRA\* instructions perform a combined authenticate-and-branch operation: the pointer is validated and then used as the branch target for BLR. For example, BLRAA X8, X9 will authenticate the PAC'd pointer in X8 under the A-instruction key using X9 as context and then branch to the resulting address.

- LDRA\* instructions perform a combined authenticate-and-load operation: the pointer is validated and then data is loaded from that address. For example, LDRAA X8, X9 will validate the PAC'd pointer X9 under the A-data key using a context value of 0 and then load the 64-bit value at the resulting address into X8.

- RETA\* instructions perform a combined authenticate-and-return operation: the link register LR is validated and then RET is performed. For example, RETAB will verify LR using the B-instruction key and then return.


# A known limitation: signing gadgets

Before we start our analysis of PAC, I should mention a known limitation: PAC can be bypassed if an attacker with read/write access can coerce the system into executing a signing gadget. Signing gadgets are instruction sequences that can be used to sign arbitrary pointers. For example, if an attacker can trigger the execution of a function that reads a pointer from memory, adds a PAC, and writes it back, then they can use this function as a signing oracle to forge PACs for arbitrary pointers.

# Weaknesses against kernel attackers

As discussed in the Qualcomm whitepaper, ARMv8.3 Pointer Authentication was designed to provide some protection even against attackers with arbitrary memory read or arbitrary memory write capabilities. But it's important to understand the limitations of the design under the attack model we're considering: a kernel attacker who already has read/write and is looking to execute arbitrary code by forging PACs on kernel pointers.

Looking at the specification, I identified three potential weaknesses in the design when protecting against kernel attackers with read/write: reading the PAC keys from memory, signing kernel pointers in userspace, and signing A-key pointers using the B-key (or vice versa). We'll discuss each in turn.

## Reading PAC keys from kernel memory

First let's consider what is perhaps the most obvious type of attack: just reading the PAC keys from kernel memory and then manually computing PACs for arbitrary kernel pointers. Here's an excerpt from the subsection of the whitepaper on attackers who can read arbitrary memory:

Pointer Authentication is designed to resist memory disclosure attacks. The PAC is computed using a cryptographically strong algorithm, so reading any number of authenticated pointers from memory would not make it easier to forge pointers.

The keys are stored in processor registers, and these registers are not accessible from usermode (EL0). Therefore, a memory disclosure vulnerability would not help extract the keys used for PAC generation.

While true, this description applies specifically to attacking a userspace program, not attacking the kernel itself. Recent iOS devices do not appear to be running a hypervisor (EL2) or secure monitor (EL3), meaning the kernel running at EL1 must manage its own PAC keys. And since the system registers that store them during normal operation will be cleared when the core goes to sleep, this means that the PAC keys must at some point be stored in kernel memory. Thus an attacker with kernel memory access could probably read the keys and use them to manually compute authentication codes for arbitrary pointers.

Of course, this approach assumes that we know what algorithm is being used under the hood to generate PACs so that we can implement it ourselves in userspace. Knowing Apple, there's a good chance they're use a custom algorithm in place of QARMA. If that's the case, then knowing the PAC keys wouldn't be sufficient to forge PACs: either we'd have to reverse engineer the silicon and determine the algorithm, or we'd have to find a way to reuse the existing machinery to forge pointers on our behalf.

## Cross-EL PAC forgeries

Along the latter line of analysis, one possible way to do that would be to forge PACs for kernel pointers by executing the corresponding PAC\* instructions in userspace. While this may sound naive, there are a few reasons this could work.

While unlikely, it's possible that Apple has decided to use the same PAC keys for EL0 and EL1, in which case we could forge a kernel PACIA signature (for example) by literally executing a PACIA instruction on the kernel pointer from userspace. You can see that the ARM pseudocode describing the implementation of PAC\* instructions makes no distinction between whether this instruction was executed at EL0 or EL1.

Here's the pseudocode for AddPACIA(), which describes the implementation of PACIA-like instructions:

// AddPACIA()

// ==========

// Returns a 64-bit value containing X, but replacing the pointer

// authentication code field bits with a pointer authentication code, where the

// pointer authentication code is derived using a cryptographic algorithm as a

// combination of X, Y, and the APIAKey\_EL1.

bits(64) AddPACIA(bits(64) X, bits(64) Y)

    boolean TrapEL2;

    boolean TrapEL3;

    bits(1)  Enable;

    bits(128) APIAKey\_EL1;

    APIAKey\_EL1 = APIAKeyHi\_EL1<63:0>:APIAKeyLo\_EL1<63:0>;

    case PSTATE.EL of

        when EL0

            boolean IsEL1Regime = S1TranslationRegime() == EL1;

            Enable = if IsEL1Regime then SCTLR\_EL1.EnIA else SCTLR\_EL2.EnIA;

            TrapEL2 = (EL2Enabled() && HCR\_EL2.API == '0' &&

                       (HCR\_EL2.TGE == '0' \|\| HCR\_EL2.E2H == '0'));

            TrapEL3 = HaveEL(EL3) && SCR\_EL3.API == '0';

        when EL1

            Enable = SCTLR\_EL1.EnIA;

            TrapEL2 = EL2Enabled() && HCR\_EL2.API == '0';

            TrapEL3 = HaveEL(EL3) && SCR\_EL3.API == '0';

        ...

    if Enable == '0' then return X;

    elsif TrapEL2 then TrapPACUse(EL2);

    elsif TrapEL3 then TrapPACUse(EL3);

    else return AddPAC(X, Y, APIAKey\_EL1, FALSE);

And here's the pseudocode implementation of AddPAC():

// AddPAC()

// ========

// Calculates the pointer authentication code for a 64-bit quantity and then

// inserts that into pointer authentication code field of that 64-bit quantity.

bits(64) AddPAC(bits(64) ptr, bits(64) modifier, bits(128) K, boolean data)

    bits(64) PAC;

    bits(64) result;

    bits(64) ext\_ptr;

    bits(64) extfield;

    bit selbit;

    boolean tbi = CalculateTBI(ptr, data);

    integer top\_bit = if tbi then 55 else 63;

    // If tagged pointers are in use for a regime with two TTBRs, use bit<55> of

    // the pointer to select between upper and lower ranges, and preserve this.

    // This handles the awkward case where there is apparently no correct

    // choice between the upper and lower address range - ie an addr of

    // 1xxxxxxx0... with TBI0=0 and TBI1=1 and 0xxxxxxx1 with TBI1=0 and

    // TBI0=1:

    if PtrHasUpperAndLowerAddRanges() then

        ...

    else selbit = if tbi then ptr<55> else ptr<63>;

    integer bottom\_PAC\_bit = CalculateBottomPACBit(selbit);

    // The pointer authentication code field takes all the available bits in

    // between

    extfield = Replicate(selbit, 64);

    // Compute the pointer authentication code for a ptr with good extension bits

    if tbi then

        ext\_ptr = ptr<63:56>:extfield<(56-bottom\_PAC\_bit)-1:0>:ptr<bottom\_PAC\_bit-1:0>;

    else

        ext\_ptr = extfield<(64-bottom\_PAC\_bit)-1:0>:ptr<bottom\_PAC\_bit-1:0>;

    PAC = ComputePAC(ext\_ptr, modifier, K<127:64>, K<63:0>);

    // Check if the ptr has good extension bits and corrupt the pointer

    // authentication code if not;

    if !IsZero(ptr<top\_bit:bottom\_PAC\_bit>) && !IsOnes(ptr<top\_bit:bottom\_PAC\_bit>) then

        PAC<top\_bit-1> = NOT(PAC<top\_bit-1>);

    // Preserve the determination between upper and lower address at bit<55>

    // and insert PAC

    if tbi then

        result = ptr<63:56>:selbit:PAC<54:bottom\_PAC\_bit>:ptr<bottom\_PAC\_bit-1:0>;

    else

        result = PAC<63:56>:selbit:PAC<54:bottom\_PAC\_bit>:ptr<bottom\_PAC\_bit-1:0>;

    return result;

Operationally, there are no significant differences between executing PACIA at EL0 and EL1, which means that if Apple has used the same PAC keys for both exception levels, we can simply execute PACIA in userspace to sign kernel pointers.

Of course, it seems highly unlikely that Apple has left such an obvious hole in their implementation. Even so, the symmetry between EL0 and EL1 means that we could potentially forge kernel PACIA signatures by reading the kernel's PAC keys, replacing the userspace PAC keys for one thread in our process with the kernel PAC keys, and then we could indeed forge kernel pointers by executing PACIA in userspace in that thread. This would be useful if Apple is using an unknown algorithm in place of QARMA, since we could reuse the existing signing machinery without having to reverse engineer it.

## Cross-key PAC forgeries

Another symmetry that we could potentially leverage to produce PAC forgeries is between the different PAC keys: PACIA, PACIB, PACDA, and PACDB all reduce to the same implementation under the hood, just using different keys. Thus, if we can replace one PAC key with another, we can turn signing gadgets for one key into signing gadgets for another key.

This would be useful if, for example, the PAC algorithm is unknown and there is something that prevents us from setting the userspace PAC keys equal to the kernel PAC keys so that we can perform cross-EL forgeries. While this forgery strategy is much less powerful, since we'd need to rely on the existence of PAC signing gadgets (which are a known limitation of PAC), this technique would free us from the restriction that the signing gadget use the same key that we're trying to forge, potentially diversifying the set of available gadgets.

# Finding an entry point for kernel code execution

Now that we have some theoretical ideas of how we might try and defeat PAC on A12 devices, let's look at the other end and figure out how we could use a PAC bypass to execute arbitrary code in the kernel.

The traditional way to get kernel code execution via read/write is the iokit\_user\_client\_trap() strategy described by Stefan Esser in [Tales from iOS 6 Exploitation](https://conference.hitb.org/hitbsecconf2013kul/materials/D2T2%20-%20Stefan%20Esser%20-%20Tales%20from%20iOS%206%20Exploitation%20and%20iOS%207%20Security%20Changes.pdf). This strategy involves patching the vtable of an IOUserClient instance so that calling the userspace function IOConnectTrap6(), which invokes iokit\_user\_client\_trap() in the kernel, will call an arbitrary function with up to 7 arguments. To see why this works, here's the implementation of iokit\_user\_client\_trap() from XNU 4903.221.2:

kern\_return\_t iokit\_user\_client\_trap(struct iokit\_user\_client\_trap\_args \*args)

{

    kern\_return\_t result = kIOReturnBadArgument;

    IOUserClient \*userClient;

    if ((userClient = OSDynamicCast(IOUserClient,

            iokit\_lookup\_connect\_ref\_current\_task((mach\_port\_name\_t)

                (uintptr\_t)args->userClientRef)))) {

        IOExternalTrap \*trap;

        IOService \*target = NULL;

        trap = userClient->getTargetAndTrapForIndex(&target, args->index);

        if (trap && target) {

            IOTrap func;

            func = trap->func;

            if (func) {

                result = (target->\*func)(args->p1, args->p2, args->p3,

                                         args->p4, args->p5, args->p6);

            }

        }

        iokit\_remove\_connect\_reference(userClient);

    }

    return result;

}

If we can patch the IOUserClient instance such that getTargetAndTrapForIndex() returns controlled values for trap and target, then the invocation of target->func below will call an arbitrary kernel function with up to 7 controlled arguments (target plus p1 through p6).

To see how this strategy would work on A12 devices, let's examine the changes to this function introduced by PAC. This is easiest to understand by looking at the disassembly:

iokit\_user\_client\_trap

    PACIBSP

    ...        ;; Call iokit\_lookup\_connect\_ref\_current\_task() on

    ...        ;; args->userClientRef and cast the result to IOUserClient.

loc\_FFFFFFF00808FF00

    STR        XZR, \[SP,#0x30+var\_28\]  ;; target = NULL

    LDR        X8, \[X19\]               ;; x19 = userClient, x8 = ->vtable

    AUTDZA     X8                      ;; validate vtable's PAC

    ADD        X9, X8, #0x5C0          ;; x9 = pointer to vmethod in vtable

    LDR        X8, \[X8,#0x5C0\]         ;; x8 = vmethod getTargetAndTrapForIndex

    MOVK       X9, #0x2BCB,LSL#48      ;; x9 = 2BCB\`vmethod\_pointer

    LDR        W2, \[X20,#8\]            ;; w2 = args->index

    ADD        X1, SP, #0x30+var\_28    ;; x1 = &target

    MOV        X0, X19                 ;; x0 = userClient

    BLRAA      X8, X9                  ;; PAC call ->getTargetAndTrapForIndex

    LDR        X9, \[SP,#0x30+var\_28\]   ;; x9 = target

    CMP        X0, #0

    CCMP       X9, #0, #4, NE

    B.EQ       loc\_FFFFFFF00808FF84    ;; if !trap \|\| !target

    LDP        X8, X11, \[X0,#8\]        ;; x8 = trap->func, x11 = func virtual?

    AND        X10, X11, #1

    ORR        X12, X10, X8

    CBZ        X12, loc\_FFFFFFF00808FF84       ;; if !func

    ADD        X0, X9, X11,ASR#1       ;; x0 = target

    CBNZ       X10, loc\_FFFFFFF00808FF58

    MOV        X9, #0                  ;; Use context 0 for non-virtual func

    B          loc\_FFFFFFF00808FF70

loc\_FFFFFFF00808FF58

    ...        ;; Handle the case where trap->func is a virtual method.

loc\_FFFFFFF00808FF70

    LDP        X1, X2, \[X20,#0x10\]     ;; x1 = args->p1, x2 = args->p2

    LDP        X3, X4, \[X20,#0x20\]     ;; x3 = args->p3, x4 = args->p4

    LDP        X5, X6, \[X20,#0x30\]     ;; x5 = args->p5, x6 = args->p6

    BLRAA      X8, X9                  ;; PAC call func(target, p1, ..., p6)

    MOV        X21, X0

loc\_FFFFFFF00808FF84

    ...        ;; Call iokit\_remove\_connect\_reference().

loc\_FFFFFFF00808FF8C

    ...        ;; Epilogue.

    RETAB

As you can see, there are several places where PACs are authenticated. The first, which was omitted from the assembly for brevity, happens when performing the dynamic cast to IOUserClient. Then userClient's vtable is validated and a PAC-protected call to getTargetAndTrapForIndex() is made. After that, the trap->func field is read without validation, and finally the value func is validated with context 0 and called.

This is actually about the best case we could reasonably hope for as attackers. If we can find a legitimate user client that provides an implementation of getTargetAndTrapForIndex() that returns a pointer to an IOExternalTrap residing in writable memory, then all we have to do is replace trap->func with a PACIZA'd function pointer (that is, a pointer signed under APIAKey with context 0). That means only a partial PAC bypass, such as the ability to forge just PACIZA pointers, would be sufficient.

A quick search through the kernelcache revealed a unique IOUserClient class, IOAudio2DeviceUserClient, that fit these criteria. Here's a decompilation of its getTargetAndTrapForIndex() method:

IOExternalTrap \*IOAudio2DeviceUserClient::getTargetAndTrapForIndex(

        IOAudio2DeviceUserClient \*this, IOService \*\*target, unsigned int index)

{

    ...

    \*target = (IOService \*)this;

    return &this->IOAudio2DeviceUserClient.traps\[index\];

}

The traps field is initialized in the method IOAudio2DeviceUserClient::initializeExternalTrapTable() to a heap-allocated IOExternalTrap object:

this->IOAudio2DeviceUserClient.trap\_count = 1;

this->IOAudio2DeviceUserClient.traps = IOMalloc(sizeof(IOExternalTrap));

Thus, all we need to do to call an arbitrary kernel function is create our own IOAudio2DeviceUserClient connection, forge a PACIZA pointer to the function we want to call, overwrite the userClient->traps\[0\].func field with the PACIZA'd pointer, and invoke IOConnectTrap6() from userspace. This will give us control of all arguments except X0, which is explicitly set to this by IOAudio2DeviceUserClient's implementation of getTargetAndTrapForIndex().

To gain control of X0 alongside X1 through X6, we'll need to replace IOAudio2DeviceUserClient's implementation of getTargetAndTrapForIndex() in the vtable. This means that, in addition to forging the PACIZA pointer to the function we want to call, we'll also need to create a fake vtable consisting of PACIA'd pointers to the virtual methods, and we'll need to replace the existing vtable pointer with a PACDZA'd pointer to the fake vtable. This requires a significantly broader PAC forgery capability.

However, even if we only manage to produce PACIZA forgeries, there's still a way to gain control of X0: JOP gadgets. A quick search through the kernelcache revealed the following gadget that sets X0:

MOV         X0, X4

BR          X5

This gives us a way to call arbitrary kernel functions with 4 fully controlled arguments using just a single forged pointer: use iokit\_user\_client\_trap() to call a PACIZA'd pointer to this gadget with X1 through X3 set how we want them for the function call, X4 set to our desired value for X0, and X5 set to the target function we want to call.

# Analyzing PAC on the A12

Now that we know how we can use PAC forgery to call arbitrary kernel functions, let's begin analyzing Apple's implementation of PAC on the A12 SoC for weaknesses. Ideally we'll find a way to perform both PACIA and PACDA forgeries, but as previously discussed, even the ability to forge a single PACIZA pointer will be sufficient to call arbitrary kernel functions with up to 4 arguments.

To actually perform my analysis, I used the [voucher\_swap](https://bugs.chromium.org/p/project-zero/issues/detail?id=1731#c10) exploit to get kernel read/write on an iPhone XR running iOS 12.1.1 build 16C50.

## Finding where PAC keys are set

My first step was to identify where in the kernel's code the PAC keys were being set. Unfortunately, IDA does not display names for the special registers used to store the PAC keys, so I had to do a bit of digging.

Searching for "APIAKey" in the [LLVM repository mirror on GitHub](https://github.com/llvm-mirror/llvm/) revealed that the registers used to store the APIAKey are called APIAKeyLo\_EL1 and APIAKeyHi\_EL1, and the registers for other keys are similarly named. Furthermore, the file [AArch64SystemOperands.td](https://github.com/llvm-mirror/llvm/blob/efea7114d4f7bc56ab90df04037bdb7cd7d4f8c3/lib/Target/AArch64/AArch64SystemOperands.td#L1289) declares the codes for these registers. This allows us to easily search for these registers in IDA. For example, to find where APIAKeyLo\_EL1 is set, I searched for the string "#0, c2, c1, #0". This brought me to what I identified as part of common\_start, from [osfmk/arm64/start.s](https://opensource.apple.com/source/xnu/xnu-4903.221.2/osfmk/arm64/start.s.auto.html):

\_WriteStatusReg(TCR\_EL1, sysreg\_restore);               // 3, 0, 2, 0, 2

PPLTEXT\_\_set\_\_TTBR0\_EL1(x25 & 0xFFFFFFFFFFFF);

\_WriteStatusReg(TTBR1\_EL1, (x25 + 0x4000) & 0xFFFFFFFFFFFF);    // 3, 0, 2, 0, 1

\_WriteStatusReg(MAIR\_EL1, 0x44F00BB44FF);               // 3, 0, 10, 2, 0

if ( x21 )

    \_WriteStatusReg(TTBR1\_EL1, cpu\_ttep);               // 3, 0, 2, 0, 1

\_WriteStatusReg(VBAR\_EL1, ExceptionVectorsBase + x22 - x23);    // 3, 0, 12, 0, 0

do

    x0 = \_ReadStatusReg(S3\_4\_C15\_C0\_4);                 // ????

while ( !(x0 & 2) );

\_WriteStatusReg(S3\_4\_C15\_C0\_4, x0 \| 5);                 // ????

\_\_isb(0xF);

\_WriteStatusReg(APIBKeyLo\_EL1, 0xFEEDFACEFEEDFACF);     // 3, 0, 2, 1, 2

\_WriteStatusReg(APIBKeyHi\_EL1, 0xFEEDFACEFEEDFACF);     // 3, 0, 2, 1, 3

\_WriteStatusReg(APDBKeyLo\_EL1, 0xFEEDFACEFEEDFAD0);     // 3, 0, 2, 2, 2

\_WriteStatusReg(APDBKeyHi\_EL1, 0xFEEDFACEFEEDFAD0);     // 3, 0, 2, 2, 3

\_WriteStatusReg(S3\_4\_C15\_C1\_0, 0xFEEDFACEFEEDFAD1);     // ????

\_WriteStatusReg(S3\_4\_C15\_C1\_1, 0xFEEDFACEFEEDFAD1);     // ????

\_WriteStatusReg(APIAKeyLo\_EL1, 0xFEEDFACEFEEDFAD2);     // 3, 0, 2, 1, 0

\_WriteStatusReg(APIAKeyHi\_EL1, 0xFEEDFACEFEEDFAD2);     // 3, 0, 2, 1, 1

\_WriteStatusReg(APDAKeyLo\_EL1, 0xFEEDFACEFEEDFAD3);     // 3, 0, 2, 2, 0

\_WriteStatusReg(APDAKeyHi\_EL1, 0xFEEDFACEFEEDFAD3);     // 3, 0, 2, 2, 1

\_WriteStatusReg(APGAKeyLo\_EL1, 0xFEEDFACEFEEDFAD4);     // 3, 0, 2, 3, 0

\_WriteStatusReg(APGAKeyHi\_EL1, 0xFEEDFACEFEEDFAD4);     // 3, 0, 2, 3, 1

\_WriteStatusReg(SCTLR\_EL1, 0xFC54793D);                 // 3, 0, 1, 0, 0

\_\_isb(0xF);

\_WriteStatusReg(CPACR\_EL1, 0x300000);                   // 3, 0, 1, 0, 2

\_WriteStatusReg(TPIDR\_EL1, 0);                          // 3, 0, 13, 0, 4

This is very interesting, since it looks like common\_start sets the PAC keys to constant values every time a core starts up! Thinking that perhaps this was an artifact of the decompilation, I checked the disassembly:

common\_start+A8

    LDR        X0, =0xFEEDFACEFEEDFACF ;; x0 = pac\_key

    MSR        #0, c2, c1, #2, X0      ;; APIBKeyLo\_EL1

    MSR        #0, c2, c1, #3, X0      ;; APIBKeyHi\_EL1

    ADD        X0, X0, #1

    MSR        #0, c2, c2, #2, X0      ;; APDBKeyLo\_EL1

    MSR        #0, c2, c2, #3, X0      ;; APDBKeyHi\_EL1

    ADD        X0, X0, #1

    MSR        #4, c15, c1, #0, X0     ;; ????

    MSR        #4, c15, c1, #1, X0     ;; ????

    ADD        X0, X0, #1

    MSR        #0, c2, c1, #0, X0      ;; APIAKeyLo\_EL1

    MSR        #0, c2, c1, #1, X0      ;; APIAKeyHi\_EL1

    ADD        X0, X0, #1

    MSR        #0, c2, c2, #0, X0      ;; APDAKeyLo\_EL1

    MSR        #0, c2, c2, #1, X0      ;; APDAKeyHi\_EL1

...

pac\_key

    DCQ 0xFEEDFACEFEEDFACF      ; DATA XREF: common\_start+A8↑r

No, common\_start really was initializing all the PAC keys to constant values. This was quite surprising: clearly Apple knows that using constant PAC keys breaks all of PAC's security guarantees. So I figured there must be some other place the PAC keys were being initialized to their true runtime values.

But after much searching, this appeared to be the only location in the kernelcache that was setting the A keys and the general key. Still, it did appear that the B keys were being set in a few more places:

machine\_load\_context+A8

    LDR        X1, \[X0,#0x458\]

    ...

    MSR        #0, c2, c1, #2, X1      ;; APIBKeyLo\_EL1

    MSR        #0, c2, c1, #3, X1      ;; APIBKeyHi\_EL1

    ADD        X1, X1, #1

    MSR        #0, c2, c2, #2, X1      ;; APDBKeyLo\_EL1

    MSR        #0, c2, c2, #3, X1      ;; APDBKeyHi\_EL1

Call\_continuation+10

    LDR        X5, \[X4,#0x458\]

    ...

    MSR        #0, c2, c1, #2, X5      ;; APIBKeyLo\_EL1

    MSR        #0, c2, c1, #3, X5      ;; APIBKeyHi\_EL1

    ADD        X5, X5, #1

    MSR        #0, c2, c2, #2, X5      ;; APDBKeyLo\_EL1

    MSR        #0, c2, c2, #3, X5      ;; APDBKeyHi\_EL1

Switch\_context+11C

    LDR        X3, \[X2,#0x458\]

    ...

    MSR        #0, c2, c1, #2, X3      ;; APIBKeyLo\_EL1

    MSR        #0, c2, c1, #3, X3      ;; APIBKeyHi\_EL1

    ADD        X3, X3, #1

    MSR        #0, c2, c2, #2, X3      ;; APDBKeyLo\_EL1

    MSR        #0, c2, c2, #3, X3      ;; APDBKeyLo\_EL1

Idle\_load\_context+88

    LDR        X1, \[X0,#0x458\]

    ...

    MSR        #0, c2, c1, #2, X1      ;; APIBKeyLo\_EL1

    MSR        #0, c2, c1, #3, X1      ;; APIBKeyHi\_EL1

    ADD        X1, X1, #1

    MSR        #0, c2, c2, #2, X1      ;; APDBKeyLo\_EL1

    MSR        #0, c2, c2, #3, X1      ;; APDBKeyHi\_EL1

These are the only other places in the kernel that set PAC keys, and they all follow the same pattern: a 64-bit load from offset 0x458 into some data structure (later identified as structthread), then setting the APIBKey to that value concatenated with itself, and setting the APDBKey to that value plus one concatenated with itself.

Furthermore, all of these locations deal specifically with context switching between threads; conspicuously absent from this list is any indication that the PAC keys are changed when transitioning between exception levels, either on kernel entry (e.g. via a syscall) or on kernel exit (via ERET\*). This would be a strong indication that the PAC keys are indeed shared between userspace and the kernel.

(I subsequently learned that [@ProteasWang](https://twitter.com/ProteasWang) discovered the same thing I did: a GitHub gist called [pac-set-key.md](https://gist.github.com/Proteas/fc5b795f89095a9d90f3a53ef2b8aa4f) lists only the previously mentioned locations.)

If my understanding was correct, this seemed to suggest three disturbing and, frankly, highly unlikely things. First, contrary to all rules of cryptography, it appeared that the kernel was using constant values for the A keys and the general key. Second, the keys seemed to be effectively 64-bits, since the first and second halves of the 128-bit key are the same. And third, the PAC keys appeared to be shared between userspace and the kernel, meaning userspace could forge kernel PAC signatures. Could Apple's implementation really be that broken? Or was something else going on?

## Observing runtime behavior

In order to find out, I conducted a simple experiment: I read the value of a global PACIZA'd function pointer in the \_\_DATA\_CONST.\_\_const section over many different boots, recording the value of the kASLR slide each time. Since the number of possible kernel slide values is relatively small, it shouldn't be too long before I get two separate boots with the kernel at the exact same location in memory, meaning that the original, non-PAC'd value of the pointer would be the same both times. Then, if the A keys really are constant, the value of the PACIZA'd pointer should be the same in both boots, since the signing algorithm is deterministic and the pointer and context values being signed are the same both times.

As a target, I chose to read sysclk\_ops.c\_gettime, which is a pointer to the function rtclock\_gettime(). The results of this experiment over 30 trials are listed below, with colliding runs highlighted:

slide = 000000000ce00000, c\_gettime = b2902c70147f2050

slide = 0000000023200000, c\_gettime = 61e2c2f02abf2050

slide = 0000000023000000, c\_gettime = d98e57f02a9f2050

slide = 0000000006e00000, c\_gettime = 0b9613700e7f2050

slide = 000000001ce00000, c\_gettime = c3822bf0247f2050

slide = 0000000004600000, c\_gettime = 00d248f00bff2050

slide = 000000001fe00000, c\_gettime = 6aa61ef0277f2050

slide = 0000000013400000, c\_gettime = fda847701adf2050

slide = 0000000015a00000, c\_gettime = c5883b701d3f2050

slide = 000000000a200000, c\_gettime = bbe37ef011bf2050

slide = 0000000014200000, c\_gettime = a8ff9f701bbf2050

slide = 0000000014800000, c\_gettime = 20e538701c1f2050

slide = 0000000019800000, c\_gettime = 66f61b70211f2050

slide = 000000001c200000, c\_gettime = 24aea37023bf2050

slide = 0000000006c00000, c\_gettime = 5a9b42f00e5f2050

slide = 000000000e200000, c\_gettime = 128526f015bf2050

slide = 000000001fa00000, c\_gettime = 4cf2ad70273f2050

slide = 000000000a200000, c\_gettime = 6ed3177011bf2050

slide = 000000000ea00000, c\_gettime = 869d0f70163f2050

slide = 0000000015800000, c\_gettime = 9898c2f01d1f2050

slide = 000000001d400000, c\_gettime = 52a343f024df2050

slide = 000000001d600000, c\_gettime = 7ea2337024ff2050

slide = 0000000023e00000, c\_gettime = 31d3b3f02b7f2050

slide = 0000000008e00000, c\_gettime = 27a72cf0107f2050

slide = 000000000fa00000, c\_gettime = 2b988f70173f2050

slide = 0000000011000000, c\_gettime = 86c7a670189f2050

slide = 0000000011a00000, c\_gettime = 3d8103f0193f2050

slide = 000000001c200000, c\_gettime = 56d444f023bf2050

slide = 000000001fe00000, c\_gettime = 82fa3970277f2050

slide = 0000000008c00000, c\_gettime = 89dcda70105f2050

As you can see, even though by all accounts the IA key is the same, PACIZAs for the same pointer generated across different boots are somehow different.

The most straightforward solution I could think of was that iBoot or the kernel might be overwriting pac\_key with a random value each boot before common\_start runs, so that the PAC keys really are different each boot. Even though pac\_key resides in \_\_TEXT\_EXEC.\_\_text, which is protected against writes by KTRR, it's still possible to modify \_\_TEXT\_EXEC.\_\_text before KTRR lockdown is performed. However, reading pac\_key at runtime showed it still contained the value 0xfeedfacefeedfacf, so something else must be going on.

I next performed an experiment to determine whether the PAC keys really were shared between userspace and the kernel, as the code suggested. I executed the PACIZA instruction in userspace on the address of the rtclock\_gettime() function, and then compared against the PACIZA'd sysclk\_ops.c\_gettime pointer read from kernel memory. These two values differed despite the fact that the PAC keys should be the same in userspace and the kernel, so once again it appeared that the A12 was conjuring some sort of dark magic.

Still not quite believing that pac\_key wasn't being modified at runtime, I tried enumerating the B-key values of all threads on the system to see whether they really matched the 0xfeedfacefeedfacf value suggested by the code. Looking at the code for Switch\_context in [osfmk/arm64/cswitch.s](https://opensource.apple.com/source/xnu/xnu-4903.221.2/osfmk/arm64/cswitch.s.auto.html), I determined that the value used as a seed to compute the B keys was being loaded from offset 0x458 of structthread, the Mach struct representing a thread. This field is not present in the public XNU sources, so I decided to name it pac\_key\_seed. My experiment consisted of walking the global thread list and dumping each thread's pac\_key\_seed.

I found that all kernel threads were indeed using the 0xfeedfacefeedfacf PAC key seed, while threads for userspace processes were using different, random seeds:

pid   0  thread ffffffe00092c000  pac\_seed feedfacefeedfacf

pid   0  thread ffffffe00092c550  pac\_seed feedfacefeedfacf

pid   0  thread ffffffe00092caa0  pac\_seed feedfacefeedfacf

...

pid 258  thread ffffffe003597520  pac\_seed 51c6b449d9c6e7a3

pid 258  thread ffffffe003764aa0  pac\_seed 51c6b449d9c6e7a3

Thus, it did seem like the PAC keys for kernel threads were being initialized the same each boot, and yet the PAC'd pointers were different across boots. Something fishy was going on.

## Bypass attempts

I next turned my attention to bypassing PAC using the weaknesses identified in the section "Weaknesses against kernel attackers".

Since executing the same PACIZA instruction on the same pointer value with the same PAC keys across different boots was producing different results, there must be some unidentified source of per-boot randomness. This basically spelled doom for the "implement QARMA-64 in userspace and compute PACs manually" strategy, but I decided to try it anyway. Unsurprisingly, this did not work.

Next I looked at whether I could set my own thread's PAC keys equal to the kernel PAC keys and forge kernel pointers in userspace. Ideally this would mean I'd set my IA key equal to the kernel's IA key, namely 0xfeedfacefeedfad2. However, as previously discussed, there's only one place in the kernel that appears to set the A keys, common\_start, and yet userspace and kernel PAC codes are different anyway.

So I decided to combine this approach with the PAC cross-key symmetry weakness and instead set my thread's IB key equal to the kernel's IA key, which should allow me to forge kernel PACIZA pointers by executing PACIZB in userspace.

Unfortunately, the naive way of doing this, by overwriting the pac\_key\_seed field in the current thread, would probably crash or panic the system, since changing PAC keys during a thread's lifetime will break the thread's existing PAC signatures. And PAC signatures are checked all the time, most frequently when returning from a function via RETAB. This means that the only way to guarantee that changing a thread's PAC keys doesn't crash it or trigger a panic is to ensure that the thread does not call or return from any functions while the keys have been changed.

The easiest way to do this is to spawn a thread that infinite loops in userspace executing PACIZB and storing the result to a global variable. Then we can overwrite the thread's pac\_key\_seed and force the thread off-core using contention; once the looping thread is rescheduled, its B keys will be set via Switch\_context and the forgery will be executed.

However, once again, the result of this experiment was unsuccessful:

gettime       = fffffff0161f2050

kPACIZA       = faef2270161f2050

uPACIZA       = 138a8670161f2050

uPACIZB forge = d7fd0ff0161f2050

It seemed that the A12 manages to break either cross-EL PAC symmetry or cross-key PAC symmetry.

To gain a bit more insight, I devised a test specifically for cross-key PAC symmetry. This meant setting my thread's IB key equal to the DB key and checking whether the outputs of PACIZB and PACDZB looked similar, indicating that the same PAC was generated. Since the IB and DB keys are generated from the same seed and cannot be set independently, this actually involved 2 trials: first with seed value 0x11223344, and next with seed value 0x11223345:

IB = 0x11223344  uPACIZB = 0028180100000000

DB = 0x11223345  uPACDZB = 00679e0100000000

IB = 0x11223345  uPACIZB = 003ea80100000000

DB = 0x11223346  uPACDZB = 0023c58100000000

The highlighted rows show the result of executing PACDZB and PACIZB on the same value from userspace with the same keys. On a standard ARMv8.3 implementation of Pointer Authentication, we'd expect most of the bits of the PAC to agree. However, the two PACs seem unrelated, suggesting that the A12 does indeed manage to break cross-key PAC symmetry.

## Implementation theories

With all three weaknesses suggested by the original design demonstrably not applicable to the A12, it was time to try and work out what was really going on here.

It's clear that Apple had considered the fact that Pointer Authentication as defined in the standard would do little to protect against kernel attackers with read/write, and thus they decided to implement a more robust defense. It's impossible to know what exactly they did without a concerted reverse engineering effort, but we can speculate based on the observed behavior.

My first thought was that Apple had decided to implement a secure monitor again, like it had done on prior devices with Watchtower to protect against kernel patches. If the secure monitor could trap transitions between exception levels and trap writes to the PAC key registers, it could hide the true PAC keys from the kernel and implement other shenanigans to break PAC symmetries. However, I couldn't find evidence of a secure monitor inside the kernelcache.

Another alternative is that Apple has decided to move the true PAC keys into the A12 itself, so that even the most powerful software attacker doesn't have the ability to read the keys. The keys could be generated randomly on boot or set via special registers by iBoot. Then, the keys that are fed to QARMA-64 (or whatever algorithm is actually being used to generate PACs) would be some combination of the random key, the standard key set via special registers, and the current exception level.

For example, the A12 could theoretically store 10 random 128-bit PAC keys, one for each pair of an exception level (EL0 or EL1) and a standard PAC key (IA, IB, DA, DB, or GA). Then the PAC key used for any particular operation could be the XOR of the random PAC key corresponding to the operation (e.g. IB-EL0 for a PACIB instruction in userspace) with the standard PAC key set via the standard registers (e.g. APIBKey). Such a design wouldn't come without challenges (for example, you'd need a non-volatile place to store the random keys for when the core sleeps), but it would cleanly break the cross-EL and cross-key symmetries and prevent the keys from ever being disclosed, completely mitigating the three previously identified weaknesses.

While I couldn't figure out the true implementation, I decided to assume the most robust design for the rest of my research: that the true keys are random and stored in the SoC itself. That way, any bypass strategy I found would be all but guaranteed to work regardless of the actual implementation.

## PAC EL-impersonation

With zero leads for systematic weaknesses, I decided it was time to investigate PAC signing gadgets.

The very first PACIA instruction occurs in a function I identified as vm\_shared\_region\_slide\_page(), and specifically as an inlined copy of vm\_shared\_region\_slide\_page\_v3(). This function is present in the XNU sources, and has the following interesting comment in its main loop:

uint8\_t\* rebaseLocation = page\_content;

uint64\_t delta = page\_entry;

do {

    rebaseLocation += delta;

    uint64\_t value;

    memcpy(&value, rebaseLocation, sizeof(value));

    delta = ( (value & 0x3FF8000000000000) >> 51) \* sizeof(uint64\_t);

    // A pointer is one of :

    // {

    //     uint64\_t pointerValue : 51;

    //     uint64\_t offsetToNextPointer : 11;

    //     uint64\_t isBind : 1 = 0;

    //     uint64\_t authenticated : 1 = 0;

    // }

    // {

    //     uint32\_t offsetFromSharedCacheBase;

    //     uint16\_t diversityData;

    //     uint16\_t hasAddressDiversity : 1;

    //     uint16\_t hasDKey : 1;

    //     uint16\_t hasBKey : 1;

    //     uint16\_t offsetToNextPointer : 11;

    //     uint16\_t isBind : 1;

    //     uint16\_t authenticated : 1 = 1;

    // }

    bool isBind = (value & (1ULL << 62)) == 1;

    if (isBind) {

        return KERN\_FAILURE;

    }

    bool isAuthenticated = (value & (1ULL << 63)) != 0;

    if (isAuthenticated) {

        // The new value for a rebase is the low 32-bits of the threaded value

        // plus the slide.

        value = (value & 0xFFFFFFFF) + slide\_amount;

        // Add in the offset from the mach\_header

        const uint64\_t value\_add = s\_info->value\_add;

        value += value\_add;

    } else {

        // The new value for a rebase is the low 51-bits of the threaded value

        // plus the slide. Regular pointer which needs to fit in 51-bits of

        // value. C++ RTTI uses the top bit, so we'll allow the whole top-byte

        // and the bottom 43-bits to be fit in to 51-bits.

        ...

    }

    memcpy(rebaseLocation, &value, sizeof(value));

} while (delta != 0);

The part about the "pointer" containing authenticated, hasBKey, and hasDKey bits suggests that this code is dealing with authenticated pointers, although all the code that actually performs PAC operations has been removed from the public sources. Furthermore, the other comment about C++ RTTI suggests that this code is specifically for rebasing userspace code. This means that the kernel would have to be aware of, and maybe perform PAC operations on, userspace pointers.

Looking at the decompilation of this loop in IDA, we can see that there are many operations not present in the public source code:

slide\_amount = si->slide;

offset = uservaddr - rebaseLocation;

do

{

    rebaseLocation += delta;

    value = \*(uint64\_t \*)rebaseLocation;

    delta = (value >> 48) & 0x3FF8;

    if ( value & 0x8000000000000000 )       // isAuthenticated

    {

        value = slide\_amount + (uint32\_t)value + slide\_info\_entry->value\_add;

        context = (value >> 32) & 0xFFFF;   // diversityData

        if ( value & 0x1000000000000 )      // hasAddressDiversity

            context = (offset + rebaseLocation) & 0xFFFFFFFFFFFF

                    \| (context << 48);

        if ( si->UNKNOWN\_FIELD && !(BootArgs->bootFlags & 0x4000000000000000) )

        {

            daif = \_ReadStatusReg(ARM64\_SYSREG(3, 3, 4, 2, 1));// DAIF

            if ( !(daif & 0x80) )

                \_\_asm { MSR             #6, #3 }

            \_WriteStatusReg(S3\_4\_C15\_C0\_4,

                \_ReadStatusReg(S3\_4\_C15\_C0\_4) & 0xFFFFFFFFFFFFFFFB);

            \_\_isb(0xFu);

            key\_bits = (value >> 49) & 3;

            switch ( key\_bits )

            {

                case 0:

                    value = ptrauth\_sign...(value, ptrauth\_key\_asia, &context);

                    break;

                case 1:

                    value = ptrauth\_sign...(value, ptrauth\_key\_asib, &context);

                    break;

                case 2:

                    value = ptrauth\_sign...(value, ptrauth\_key\_asda, &context);

                    break;

                case 3:

                    value = ptrauth\_sign...(value, ptrauth\_key\_asdb, &context);

                    break;

            }

            \_WriteStatusReg(S3\_4\_C15\_C0\_4, \_ReadStatusReg(S3\_4\_C15\_C0\_4) \| 4);

            \_\_isb(0xFu);

            ml\_set\_interrupts\_enabled(~(daif >> 7) & 1);

        }

    }

    else

    {

        ...

    }

    memmove(rebaseLocation, &value, 8);

}

while ( delta );

It appears that the kernel is attempting to sign pointers on behalf of userspace. This is interesting because, as previously discussed, the A12 breaks cross-EL symmetry, which should mean that the kernel's signatures on userspace pointers will be invalid in userspace.

It's unlikely that this freshly-introduced code is broken, so there must be some mechanism by which the kernel instructs the CPU to sign with userspace pointers instead. Searching for other instances of PAC\* instructions like this, a pattern begins to emerge: whenever the kernel signs pointers on behalf of userspace, it wraps the PAC instructions by clearing and setting a bit in the S3\_4\_C15\_C0\_4 system register:

MRS         X8, #4, c15, c0, #4 ; S3\_4\_C15\_C0\_4

AND         X8, X8, #0xFFFFFFFFFFFFFFFB

MSR         #4, c15, c0, #4, X8 ; S3\_4\_C15\_C0\_4

ISB

...         ;; PAC stuff for userspace

MRS         X8, #4, c15, c0, #4 ; S3\_4\_C15\_C0\_4

ORR         X8, X8, #4

MSR         #4, c15, c0, #4, X8 ; S3\_4\_C15\_C0\_4

ISB

Also, kernel code that sets/clears bit 0x4 of S3\_4\_C15\_C0\_4 is usually accompanied by code that disables interrupts and checks bit 0x4000000000000000 of BootArgs->bootFlags, as we see in the excerpt from vm\_shared\_region\_slide\_page\_v3() above.

We can infer that bit 0x4 of S3\_4\_C15\_C0\_4 controls whether PAC\* instructions in the kernel use the EL0 keys or the EL1 keys: when this bit is set the kernel keys are used, otherwise the userspace keys are used. It makes sense that you'd need to disable interrupts while this bit is cleared, since otherwise the arrival of an interrupt may cause other kernel code to execute while the EL0 PAC keys are still in use, causing PAC validation failures that would panic the kernel.

## PAC-enable bits in SCTLR\_EL1

Another thing I noticed while investigating system registers was that previously reserved bits of SCTLR\_EL1 were now being used to enable/disable PAC instructions for certain keys.

While looking at the exception vector for syscall entry, Lel0\_synchronous\_vector\_64, I noticed some additional code referencing bootFlags and setting certain bits of SCTLR\_EL1 that are marked as reserved in the ARM standard:

ADRP        X0, #const\_boot\_args@PAGE

ADD         X0, X0, #const\_boot\_args@PAGEOFF

LDR         X0, \[X0,#(const\_boot\_args.bootFlags - 0xFFFFFFF0077A21B8)\]

AND         X0, X0, #0x8000000000000000

CBNZ        X0, loc\_FFFFFFF0079B3320

MRS         X0, #0, c1, c0, #0                  ;; SCTLR\_EL1

TBNZ        W0, #0x1F, loc\_FFFFFFF0079B3320

ORR         X0, X0, #0x80000000                 ;; set bit 31

ORR         X0, X0, #0x8000000                  ;; set bit 27

ORR         X0, X0, #0x2000                     ;; set bit 13

MSR         #0, c1, c0, #0, X0                  ;; SCTLR\_EL1

Also, these bits are conditionally cleared on exception return:

TBNZ        W1, #2, loc\_FFFFFFF0079B3AE8        ;; SPSR\_EL1.M\[3:0\] & 0x4

...

LDR         X2, \[X2,#thread.field\_460\]

CBZ         X2, loc\_FFFFFFF0079B3AE8

...

MRS         X0, #0, c1, c0, #0                  ;; SCTLR\_EL1

AND         X0, X0, #0xFFFFFFFF7FFFFFFF         ;; clear bit 31

AND         X0, X0, #0xFFFFFFFFF7FFFFFF         ;; clear bit 27

AND         X0, X0, #0xFFFFFFFFFFFFDFFF         ;; clear bit 13

MSR         #0, c1, c0, #0, X0                  ;; SCTLR\_EL1

While these bits are documented as reserved (with value 0) by ARM, I did find a reference to one of them in the XNU 4903.221.2 sources, in [osfmk/arm64/proc\_reg.h](https://opensource.apple.com/source/xnu/xnu-4903.221.2/osfmk/arm64/proc_reg.h.auto.html):

// 13           PACDB\_ENABLED            AddPACDB and AuthDB functions enabled

#define SCTLR\_PACDB\_ENABLED             (1 << 13)

This suggested that bit 13 at least is related to enabling PAC for the DB key. Since the only SCTLR\_EL1 bits that are both (a) not mentioned in the file and (b) not set automatically via SCTLR\_RESERVED are 31, 30, and 27, I speculated that these bits controlled the other PAC keys. (Presumably, leaving the reference to SCTLR\_PACDB\_ENABLED in the code was an oversight.) My guess is that bit 31 controls PACIA, bit 30 controls PACIB, bit 27 controls PACDA, and bit 13 controls PACDB.

To test this theory, I executed the following sequence of PAC instructions in the debugger, both before and after setting the field at offset 0x460 of the current thread:

pacia  x0, x1

pacib  x2, x3

pacda  x4, x5

pacdb  x6, x7

Before executing these instructions, I set each register Xn to the value 0x11223300 \| n. Here's the result before setting field\_460, with the PACs highlighted:

x0 = 0x001d498011223300    # PACIA

x1 = 0x0000000011223301

x2 = 0x0035778011223302    # PACIB

x3 = 0x0000000011223303

x4 = 0x0062860011223304    # PACDA

x5 = 0x0000000011223305

x6 = 0x001e6c8011223306    # PACDB

x7 = 0x0000000011223307

And here's the result after:

x0 = 0x0000000011223300    # PACIA

x1 = 0x0000000011223301

x2 = 0x0035778011223302    # PACIB

x3 = 0x0000000011223303

x4 = 0x0000000011223304    # PACDA

x5 = 0x0000000011223305

x6 = 0x0000000011223306    # PACDB

x7 = 0x0000000011223307

This seems to confirm our theory: before setting field\_460, the PAC instructions worked as expected, but after setting field\_460, all except PACIB have been effectively turned into NOPs. Using this fact for exploitation is tricky, since overwriting field\_460 in a kernel thread does not seem to disable PAC in that thread due to additional checks. Nonetheless, the existence of these PAC-enable bits in SCTLR\_EL1 was interesting in its own right.

# The (non-)existence of signing gadgets

At this point, since we have no systematic weaknesses against Apple's more robust design, we're looking for a signing gadget usable only via read/write. That means we're looking for a sequence of code that will read a pointer from memory, sign it, and write it back to memory. But we can't yet call arbitrary kernel addresses, so we also need to ensure that this code path is actually triggerable, either during the course of normal kernel operation, or by using our iokit\_user\_client\_trap() call primitive to call a kernel function to which there already exists a PACIZA'd pointer.

Apple has clearly tried to scrub the kernelcache of any obvious signing gadgets. All occurrences of the PACIA instruction are either unusable or wrapped by code that switches to the userspace PAC keys (via S3\_4\_C15\_C0\_4), so there's no way we can convince the kernel to perform a PACIA forgery using only read/write.

This left just PACIZA. While there were many more occurrences of the PACIZA instruction, most of them were useless since the result wasn't written to memory. Additionally, gadgets that actually did load and store the pointer were almost always preceded by AUTIA, which would fail if the pointer we were signing didn't already have a valid PAC:

LDR         X10, \[X9,#0x30\]!

CBNZ        X19, loc\_FFFFFFF007EBD330

CBZ         X10, loc\_FFFFFFF007EBD330

MOV         X19, #0

MOV         X11, X9

MOVK        X11, #0x14EF,LSL#48

AUTIA       X10, X11

PACIZA      X10

STR         X10, \[X9\]

Thus, it appeared I was out of luck.

# The fourth weakness

After giving up on signing gadgets and pursuing a few other dead ends, I eventually wondered: What would actually happen if PACIZA was used to sign an invalid pointer validated by AUTIA? I'd assumed that such a pointer would be useless, but I decided to look at the ARM pseudocode to see what would actually happen.

To my surprise, the standard revealed a funny interaction between AUTIA and PACIZA. When AUTIA finds that an authenticated pointer's PAC doesn't match the expected value, it corrupts the pointer by inserting an error code into the pointer's extension bits:

// Auth()

// ======

// Restores the upper bits of the address to be all zeros or all ones (based on

// the value of bit\[55\]) and computes and checks the pointer authentication

// code. If the check passes, then the restored address is returned. If the

// check fails, the second-top and third-top bits of the extension bits in the

// pointer authentication code field are corrupted to ensure that accessing the

// address will give a translation fault.

bits(64) Auth(bits(64) ptr, bits(64) modifier, bits(128) K, boolean data,

              bit keynumber)

    bits(64) PAC;

    bits(64) result;

    bits(64) original\_ptr;

    bits(2) error\_code;

    bits(64) extfield;

    // Reconstruct the extension field used of adding the PAC to the pointer

    boolean tbi = CalculateTBI(ptr, data);

    integer bottom\_PAC\_bit = CalculateBottomPACBit(ptr<55>);

    extfield = Replicate(ptr<55>, 64);

    if tbi then

        ...

    else

        original\_ptr = extfield<64-bottom\_PAC\_bit-1:0>:ptr<bottom\_PAC\_bit-1:0>;

    PAC = ComputePAC(original\_ptr, modifier, K<127:64>, K<63:0>);

    // Check pointer authentication code

    if tbi then

        ...

    else

        if ((PAC<54:bottom\_PAC\_bit> == ptr<54:bottom\_PAC\_bit>) &&

            (PAC<63:56> == ptr<63:56>)) then

            result = original\_ptr;

        else

            error\_code = keynumber:NOT(keynumber);

result = original\_ptr<63>:error\_code:original\_ptr<60:0>;

    return result;

Meanwhile, when PACIZA is adding a PAC to a pointer, it actually signs the pointer with corrected extension bits, and then corrupts the PAC if the extension bits were originally invalid. From the pseudocode for AddPAC() above:

    ext\_ptr = extfield<(64-bottom\_PAC\_bit)-1:0>:ptr<bottom\_PAC\_bit-1:0>;

PAC = ComputePAC(ext\_ptr, modifier, K<127:64>, K<63:0>);

// Check if the ptr has good extension bits and corrupt the pointer

// authentication code if not;

if !IsZero(ptr<top\_bit:bottom\_PAC\_bit>)

        && !IsOnes(ptr<top\_bit:bottom\_PAC\_bit>) then

PAC<top\_bit-1> = NOT(PAC<top\_bit-1>);

Critically, PAC\* instructions will corrupt the PAC of a pointer with invalid extension bits by flipping a single bit of the PAC. While this will certainly invalidate the PAC, this also means that the true PAC can be reconstructed if we can read out the value of a PAC\*-forgery on a pointer produced by an AUT\* instruction! So sequences like the one above that consist of an AUTIA followed by a PACIZA can be used as signing gadgets even if we don't have a validly signed pointer to begin with: we just have to flip a single bit in the forged PAC.

# A complete A-key forgery strategy for 16C50

With the existence of a single PACIZA signing gadget, we can begin our construction of a complete forgery strategy for the A keys on A12 devices running build 16C50.

## Stage 1: PACIZA-forgery

A bit of sleuthing reveals that the gadget we found is part of the function sysctl\_unregister\_oid(), which is responsible for unregistering a sysctl\_oid struct from the global sysctl tree. (Once again, this function does not have any PAC-related code in the public sources, but these operations are present on PAC-enabled devices.) Here's a listing of the relevant parts of this function from IDA:

void sysctl\_unregister\_oid(sysctl\_oid \*oidp)

{

    sysctl\_oid \*removed\_oidp = NULL;

    sysctl\_oid \*old\_oidp = NULL;

    BOOL have\_old\_oidp;

    void \*\*handler\_field;

    void \*handler;

    uint64\_t context;

    ...

    if ( !(oidp->oid\_kind & 0x400000) )         // Don't enter this if

    {

        ...

    }

    if ( oidp->oid\_version != 1 )               // Don't enter this if

    {

        ...

    }

    sysctl\_oid \*first\_sibling = oidp->oid\_parent->first;

    if ( first\_sibling == oidp )                // Enter this if

    {

        removed\_oidp = NULL;

        old\_oidp = oidp;

        oidp->oid\_parent->first = old\_oidp->oid\_link;

        have\_old\_oidp = 1;

    }

    else

    {

        ...

    }

    handler\_field = &old\_oidp->oid\_handler;

    handler = old\_oidp->oid\_handler;

    if ( removed\_oidp \|\| !handler )             // Take the else

    {

        ...

    }

    else

    {

        removed\_oidp = NULL;

        context = (0x14EF << 48) \| ((uint64\_t)handler\_field & 0xFFFFFFFFFFFF);

        \*handler\_field = ptrauth\_sign\_unauthenticated(

                ptrauth\_auth\_function(handler, ptrauth\_key\_asia, &context),

                ptrauth\_key\_asia,

                0);

        ...

    }

    ...

}

If we can get this function called with a crafted sysctl\_oid that causes the indicated path to be taken, we should be able to forge arbitrary PACIZA pointers.

There aren't any existing global PACIZA'd pointers to this function, so we can't call it directly using our iokit\_user\_client\_trap() primitive, but as luck would have it, there are several global PACIZA'd function pointers that themselves call into it. This is because several kernel extensions register sysctls that they need to unregister before they're unloaded; these kexts often have a module termination function that calls sysctl\_unregister\_oid(), and the kmod\_info struct describing the kext contains a PACIZA'd pointer to the module termination function.

The best candidate I could find was l2tp\_domain\_module\_stop(), which is part of the com.apple.nke.lttp kext. This function will perform some deinitialization work before calling sysctl\_unregister\_oid() on the global sysctl\_\_net\_ppp\_l2tp object. Thus, we can PACIZA-sign an arbitrary pointer by overwriting the contents of sysctl\_\_net\_ppp\_l2tp, calling l2tp\_domain\_module\_stop() via the existing global PACIZA'd pointer, and then reading out sysctl\_\_net\_ppp\_l2tp's oid\_handler field and flipping bit 62.

## Stage 2: PACIA/PACDA forgery

While this lets us PACIZA-forge any pointer we want, it'd be nice to be able to perform PACIA/PACDA forgeries as well, since then we could implement the full bypass described in the section "Finding an entry point for kernel code execution". To do that, I next looked into whether our PACIZA primitive could turn any of the PACIA instructions in the kernelcache into viable signing gadgets.

The most likely candidate for both PACIA and PACDA was an unknown function sub\_FFFFFFF007B66C48, which contains the following instruction sequence:

MRS         X9, #4, c15, c0, #4 ; S3\_4\_C15\_C0\_4

AND         X9, X9, #0xFFFFFFFFFFFFFFFB

MSR         #4, c15, c0, #4, X9 ; S3\_4\_C15\_C0\_4

ISB

LDR         X9, \[X2,#0x100\]

CBZ         X9, loc\_FFFFFFF007B66D24

MOV         W10, #0x7481

PACIA       X9, X10

STR         X9, \[X2,#0x100\]

...

LDR         X9, \[X2,#0xF8\]

CBZ         X9, loc\_FFFFFFF007B66D54

MOV         W10, #0xCBED

PACDA       X9, X10

STR         X9, \[X2,#0xF8\]

...

MRS         X9, #4, c15, c0, #4 ; S3\_4\_C15\_C0\_4

ORR         X9, X9, #4

MSR         #4, c15, c0, #4, X9 ; S3\_4\_C15\_C0\_4

ISB

...

PACIBSP

STP         X20, X19, \[SP,#var\_20\]!

...         ;; Function body (mostly harmless)

LDP         X20, X19, \[SP+0x20+var\_20\],#0x20

AUTIBSP

MOV         W0, #0

RET

What makes sub\_FFFFFFF007B66C48 a good candidate is that the PACIA/PACDA instructions occur before the stack frame is set up. Ordinarily, calling into the middle of a function will cause problems when the function returns, since the function's epilogue will tear down a frame that was never set up. But since this function's stack frame is set up after our desired entry points, we can use our kernel call primitive to jump directly to these instructions without causing any problems.

Of course, we still have another issue: the PACIA and PACDA instructions use registers X9 and X10, while our kernel call primitive based on iokit\_user\_client\_trap() only gives us control of registers X1 through X6. We'll need to figure out how to get the values we want into the appropriate registers.

In fact, we already found a solution to this very problem earlier: JOP gadgets.

Searching through the kernelcache, just three kexts seem to hold the vast majority of non-PAC'd indirect branches: FairPlayIOKit, LSKDIOKit, and LSKDIOKitMSE. These kexts even stand out in IDA's navigator bar as islands of red in a sea of blue, since IDA cannot create functions out of many of the instructions in these kexts:

[![](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgusbU_s600_ULRTU1PIWyMb883liCSLf7ZjRti02tfQELmC8Vx_rhEcNjYpmGX8vUR4-r7WUvkCLdL0qWFEUU-EdrEWMzV_qS6oi-WsBIrqdhJKexFAtRSZZj4H0ueFUkHfd9YFsvV5qDj6Mnvi.png)](https://projectzero.google/images/oldblog/blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgusbU_s1400_ULRTU1PIWyMb883liCSLf7ZjRti02tfQELmC8Vx_rhEcNjYpmGX8vUR4-r7WUvkCLdL0qWFEUU-EdrEWMzV_qS6oi-WsBIrqdhJKexFAtRSZZj4H0ueFUkHfd9YFsvV5qDj6Mnvi.png)

It seems that these kexts use some sort of obfuscation to hide control flow and make reverse engineering more difficult. Many jumps in this code are performed indirectly through registers. Unfortunately, in this case the obfuscation actually makes our job as attackers easier, since it gives us a plethora of useful JOP gadgets not protected by PAC.

For our specific use case, we have control of PC and X1 through X6, and we're trying to set X2 to some writable memory region, X9 to the pointer we want to sign, and X10 to the signing context, before jumping to the signing gadget. I eventually settled on executing the following JOP program to accomplish this:

X1 = MOV\_X10\_X3\_\_BR\_X6

X2 = KERNEL\_BUFFER

X3 = CONTEXT

X4 = POINTER

X5 = MOV\_X9\_X0\_\_BR\_X1

X6 = PACIA\_X9\_X10\_\_STR\_X9\_X2\_100

MOV         X0, X4

BR          X5

MOV         X9, X0

BR          X1

MOV         X10, X3

BR          X6

PACIA       X9, X10

STR         X9, \[X2,#0x100\]

...

And with that, we now have a complete bypass strategy that allows us to forge arbitrary PAC signatures using the A keys.

# Timeline

After sharing my original kernel read/write exploit on December 18, 2018, I reported the proof-of-concept PAC bypass built on top of voucher\_swap on December 30. This POC could produce arbitrary A-key PAC forgeries and call arbitrary kernel functions with 7 arguments, just like on non-PAC devices.

Apple quickly responded suggesting that the latest iOS 12.1.3 beta, build 16D5032a, should mitigate the issue. As this build also fixed the voucher\_swap bug, I couldn't test this directly, but I did inspect the kernelcache manually and found that Apple had mitigated the sysctl\_unregister\_oid() gadget used to produce the first PACIZA forgery.

This build was released on December 19, near the beginning of my research into PAC and long before I reported the bypass to Apple. Thus, like the case with the voucher\_swap bug, I suspect that another researcher found and reported this issue first.

# Apple's fix

In order to fix the sysctl\_unregister\_oid() gadget (and other AUTIA-PACIA gadgets), Apple has added a few instructions to ensure that if the AUTIA fails, then the resulting invalid pointer will be used instead of the result of PACIZA:

LDR         X10, \[X9,#0x30\]!            ;; X10 = old\_oidp->oid\_handler

CBNZ        X19, loc\_FFFFFFF007EBD4A0

CBZ         X10, loc\_FFFFFFF007EBD4A0

MOV         X19, #0

MOV         X11, X9                     ;; X11 = &old\_oidp->oid\_handler

MOVK        X11, #0x14EF,LSL#48         ;; X11 = 14EF\`&oid\_handler

MOV         X12, X10                    ;; X12 = oid\_handler

AUTIA       X12, X11                    ;; X12 = AUTIA(handler, 14EF\`&handler)

XPACI       X10                         ;; X10 = XPAC(handler)

CMP         X12, X10

PACIZA      X10                         ;; X10 = PACIZA(XPAC(handler))

CSEL        X10, X10, X12, EQ           ;; X10 = (PAC\_valid ? PACIZA : AUTIA)

STR         X10, \[X9\]

With this change, we can no longer PACIZA-forge a pointer unless we already have a PACIA forgery with a specific context.

# Brute-force strategies

While this does mitigate the fast, straightforward strategy outlined above, with enough time it is still susceptible to brute forcing. Now, I couldn't test this explicitly without an exploit for iOS 12.1.3, but I was able to simulate how long it might take using my exploit on iOS 12.1.2.

The problem is that even though we don't have an existing PACIA-forgery for the pointer we want to PACIZA-forge, we can use our kernel call primitive to execute this gadget repeatedly with different guesses for the valid PAC. Unlike most other instances in which authenticated pointers are used, guessing incorrectly here won't actually trigger a panic: we can just read out the result to see whether we guessed correctly (in which case the oid\_handler field will have a PAC added) or incorrectly (in which case oid\_handler will look like the result of a failed AUTIA).

Looking back at the list of PAC'd pointers generated in my very first experiment in the subsection "Observing runtime behavior", I compared the extension bits of all the pointers to determine that the PAC was masked into the bits 0xff7fff8000000000. This means the A12 is using a 24-bit PAC, or about 16 million possibilities.

In my experiments, I found that invoking l2tp\_domain\_module\_stop() and l2tp\_domain\_module\_start() 256 times took about 13.2 milliseconds. Thus, exhaustively checking all 16 million possible PACs should take around 15 minutes. And unless there were other changes I didn't notice, once a single PACIZA forgery is produced, the rest of the A-key bypass strategy should still be possible.

(Initializing/deinitializing the module more than about 4096 times started to produce noticeable slowdowns; I didn't identify the source of this slowness, but I do suspect that with effort it should be possible to work around it.)

# Conclusion

In this post we put Apple's implementation of Pointer Authentication on the A12 SoC used in the iPhone XS under the microscope, describing observed behavior, theorizing about how deviations from the ARM reference might be implemented under the hood, and analyzing the system for weaknesses that would allow a kernel attacker with read/write capabilities to forge PACs for arbitrary pointers. This analysis culminated with a complete bypass strategy and proof-of-concept implementation that allows the attacker to perform arbitrary A-key forgeries on an iPhone XS running iOS 12.1.2. Such a bypass is sufficient for achieving arbitrary kernel code execution through JOP. This strategy was partially mitigated with the release of iOS 12.1.3 beta 16D5032a, although there are indications that it might still be possible to bypass the mitigation via a brute-force approach.

Despite these flaws, PAC remains a solid and worthwhile mitigation. Apple's hardening of PAC in the A12 SoC, which was clearly designed to protect against kernel attackers with read/write, meant that I did not find a systematic break in the design and had to rely on signing gadgets, which are easy to patch via software. As with any complex new mitigation, loopholes are not uncommon in the first few iterations. However, given the fragility of the current bypass technique (relying on, among other things, the single IOUserClient class that allows us to overwrite its IOExternalTrap, one of a very small number of usable PACIZA gadgets, and a handful of non-PAC'd JOP gadgets introduced by obfuscation), I believe it's possible for Apple to harden their implementation to the point that strong forgery bypasses become rare.

Furthermore, PAC shows promise as a tool to make data-only kernel attacks trickier and less powerful. For example, I could see Apple adding something akin to a \_\_security\_critical attribute that enables PAC for C pointers that are especially prone to being hijacked during exploits, such as ipc\_port's ip\_kobject field. Such a mitigation wouldn't end any bug classes, since sophisticated attackers could find other ways of leveraging vulnerabilities into kernel read/write primitives, but it would raise the bar and make simple exploit strategies like those used in voucher\_swap much harder (and hopefully less reliable) to pull off.