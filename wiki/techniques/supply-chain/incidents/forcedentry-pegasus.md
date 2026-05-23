---
title: FORCEDENTRY -- NSO Pegasus 0-click iMessage (CVE-2021-30860, Sep 2021)
slug: forcedentry-pegasus
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/mobile, vendor/apple, technique/zero-click-imessage, technique/image-parser, technique/jbig2, actor/nso-pegasus, cve/CVE-2021-30860]
inbound: []
---

# FORCEDENTRY -- NSO Pegasus 0-click iMessage (CVE-2021-30860, Sep 2021)

## What happened

In **August 2021** Citizen Lab recovered an active 0-click iMessage
exploit from the iPhone of a **Saudi activist** infected with NSO
Group's Pegasus spyware. The exploit -- branded **FORCEDENTRY** by
Citizen Lab -- bypassed Apple's **BlastDoor** iMessage sandbox by
exploiting an integer overflow in CoreGraphics' **JBIG2** image
decoder, reachable when iMessage processed an inbound attachment with
a `.gif` extension that was actually a PDF. Apple patched it on
**13 September 2021** as **CVE-2021-30860** in iOS 14.8.

In **December 2021** Google Project Zero published a deep-dive on the
sandbox-escape stage and called it "one of the most technically
sophisticated exploits we have ever seen". The exploit uses JBIG2's
generic-refinement segments -- a per-pixel boolean combinator opcode
set -- to **emulate a custom CPU inside the decompressor**. With
~70,000 segment commands NSO built registers, a 64-bit ALU, and a
comparator, then ran the entire sandbox-escape program as a
single-pass JBIG2 decode. No JavaScript, no scripting language --
arbitrary computation expressed as image data.

## Attack chain

1. **Delivery: iMessage `.gif` that's actually a PDF.** iMessage
   trusts the file extension less than the magic header; the
   attachment routed through CoreGraphics' PDF/image rendering pipe.
   BlastDoor was intended to isolate this -- the JBIG2 stage broke out
   of it.
2. **CoreGraphics JBIG2 integer overflow (CVE-2021-30860).** A
   `JBIG2Bitmap` allocation underflowed via crafted segment headers,
   letting subsequent generic-refinement operations write outside the
   intended bitmap.
3. **OOB write -> arbitrary R/W in the decoder process.** Refinement
   ops can copy adjacent bytes within configurable rectangles; with
   careful heap layout the attacker reads and writes arbitrary
   addresses inside the JBIG2 decoder's address space.
4. **Build a virtual machine in JBIG2.** ~70,000 segment commands
   define logic gates (AND, OR, XOR, NOT via bit-plane combinators)
   that implement registers, an adder, and conditional branching. The
   entire follow-on exploit -- BlastDoor sandbox escape + privilege
   bump -- runs as boolean-circuit emulation inside the decompressor's
   single decode pass.
5. **Sandbox escape + Pegasus implant load.** The emulated program
   completes the BlastDoor escape and stages Pegasus core, which then
   pivots into the kernel via a separate (not publicly attributed)
   chain.

## Lessons for bug hunters

- **Image / document decoders are full RCE surfaces.** JBIG2 is
  obscure but every PDF reader supports it; same risk in JPEG2000,
  HEIC, AVIF, WebP, TIFF, OpenEXR. If your target ingests user
  uploads anywhere -- profile pictures, attachments, document
  previews, OCR pipelines, screenshot tools -- the underlying decoder
  is the surface. See [[operation-triangulation]] for the TrueType
  sibling.
- **Format-internal Turing-completeness is a generic primitive.** Any
  format that defines per-element conditional / combinator operations
  (PDF actions, ICC profiles, font hinting, JBIG2 refinement, SVG
  filters) can be coerced into a VM if you have memory-write inside
  the parser. Worth investigating on any bounty with file-upload
  surface.
- **Sandbox-bypass via parser logic, not parser bugs.** BlastDoor
  worked correctly. The bypass was that CoreGraphics decoded the
  attachment in a process whose sandbox profile still allowed enough
  to stage the next link. Look for "this is sandboxed" claims in your
  target -- they're usually narrower than the threat model implies.
- **0-click means probing must be hands-off / passive.** Standard
  recon (clicking links, hitting endpoints) won't find this class.
  For mobile-app bounties: review the attachment ingestion pipeline,
  fuzz the parsers locally with libFuzzer + AFL++ against open-source
  reimplementations of the format, then report crash repros.
- **Apple's MessageProtection sandbox (BlastDoor) and Lockdown Mode
  exist because of this class.** Lockdown disables most attachment
  preview pipelines -- a target offering "high-risk user" mode is
  signaling where they think their RCE surface is.

## Primary sources

- [Citizen Lab: "FORCEDENTRY: NSO Group iMessage Zero-Click Exploit Captured in the Wild" (13 Sep 2021)](https://citizenlab.ca/research/forcedentry-nso-group-imessage-zero-click-exploit-captured-in-the-wild/)
- [Google Project Zero: "A deep dive into an NSO zero-click iMessage exploit: Remote Code Execution" (Ian Beer & Samuel Gross, 15 Dec 2021)](https://googleprojectzero.blogspot.com/2021/12/a-deep-dive-into-nso-zero-click.html)

## Related

- [[operation-triangulation]]
- [[bybit-safewallet-ui]]
- [[xz-utils-cve-2024-3094]]
