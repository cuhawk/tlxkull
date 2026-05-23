---
title: Operation Triangulation -- iOS iMessage 0-click (disclosed Jun 2023)
slug: operation-triangulation
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/mobile, vendor/apple, technique/zero-click-imessage, technique/font-parser, technique/mmio-bypass, actor/nation-state]
inbound: []
---

# Operation Triangulation -- iOS iMessage 0-click (disclosed Jun 2023)

## What happened

In **June 2023** Kaspersky disclosed a multi-year iOS implant campaign
they branded **Operation Triangulation**, found while triaging
anomalous network traffic from senior-staff iPhones on their corporate
Wi-Fi. The implant arrived as an invisible iMessage attachment -- a
PDF that the receiver never opened, never previewed, never interacted
with -- and ended up as root on the device with full RAM scrape, mic
access, keychain dump, and command-and-control. Infections were traced
back to **2019**, so the chain ran in the wild for ~4 years before
discovery.

Apple subsequently shipped patches across iOS 15.7.7 / 16.5.1 / 16.6
for a **four-CVE chain**. The most striking finding was
**CVE-2023-38606**: the kernel exploit used **undocumented MMIO
registers** in Apple-silicon SoCs (A12-A16) to disable the hardware
Page Protection Layer (PPL). The MMIO addresses are not referenced
anywhere in XNU, IOKit, or any public Apple SDK -- they appear to be
debug / factory-test interfaces left enabled in shipping hardware. The
attacker, presumed nation-state, knew about and used them. Kaspersky
released the chain in talks at 37C3 and on Securelist.

## Attack chain

1. **iMessage attachment delivery.** PDF disguised with a TrueType
   font containing a malicious `ADJUST` instruction --
   **CVE-2023-41990**. BlastDoor (the iMessage attachment sandbox) was
   bypassed because the font is parsed by the system font engine,
   reachable via `com.apple.fontd` / WebKit fonts handler before user
   interaction.
2. **NSExpression / NSPredicate language as stage-1 runtime.** The
   exploit's second stage is written in Apple's
   `NSExpression`/`NSPredicate` query language, used here as a
   Turing-complete interpreter to mount a JIT-spray against
   JavaScriptCore and patch its environment. Exotic primitive -- the
   stage runs entirely in obscure framework code, not user JS.
3. **WebKit JavaScriptCore RCE -- CVE-2023-32434.** The patched
   JS environment loads a ~11,000-line JS exploit that uses the
   `DollarVM` ($vm) debugging feature to read/write JSC heap and
   invoke native API. Yields ROP-ish user-space RCE.
4. **Kernel privilege escalation -- CVE-2023-32435** (XNU integer
   overflow) followed by **CVE-2023-38606** (the hardware MMIO bypass).
   The MMIO trick writes undocumented physical registers (around
   `0x206f00000`) that disable PPL's read-only enforcement on kernel
   page tables, letting the exploit patch arbitrary kernel memory.
5. **`ADJUST_RUNNER` persistence + C2.** The implant phones home over
   HTTPS to a chain of staging domains, dumps keychain, location,
   microphone, mic-on-trigger, and supports plugin loading.

## Lessons for bug hunters

- **Parsers reachable pre-interaction = your highest-leverage attack
  surface on any mobile platform.** Font parsers, image decoders, PDF
  renderers, message previewers (iMessage, RCS, WhatsApp, Signal media
  preview) all process attacker content with zero user gesture. See
  [[forcedentry-pegasus]] for the JBIG2 sibling.
- **Undocumented hardware features exist.** Vendor SoCs ship with
  debug / factory MMIO regions enabled in production silicon. On any
  embedded / mobile bounty: enumerate `/proc/iomem` (Linux),
  `IOService` browser (macOS/iOS), or device-tree dumps for
  unreferenced ranges, then attempt access.
- **Query / template languages embedded in OS frameworks are runtimes.**
  `NSExpression` / `NSPredicate` join Excel formulas, JSONLogic, jq,
  yaml-anchor-bombs as overlooked execution surfaces. If a target
  ingests user-controlled `NSPredicate` strings (some macOS apps do via
  filter UIs / Spotlight queries), treat it as RCE primitive.
- **JIT debugging hooks (`$vm` in JSC, `%DebugPrint` in v8) survive
  into release builds more often than expected.** Search any
  JavaScript engine for `--allow-natives-syntax`-like switches that
  attacker code can flip.
- **Long dwell-time + targeted-trigger payloads defeat synthetic
  scanning.** The chain inspected target characteristics before
  detonating; a generic security crawler hitting the same iMessage
  pipeline would have seen nothing. Stateful, instrumented capture is
  the only way to find these classes.

## Primary sources

- [Securelist: "Operation Triangulation: The last (hardware) mystery" (Kaspersky GReAT, 27 Dec 2023)](https://securelist.com/operation-triangulation-the-last-hardware-mystery/111669/)
- [Wikipedia consolidated chain reference -- Operation Triangulation](https://en.wikipedia.org/wiki/Operation_Triangulation)

## Related

- [[forcedentry-pegasus]]
- [[bybit-safewallet-ui]]
- [[ronin-bridge]]
