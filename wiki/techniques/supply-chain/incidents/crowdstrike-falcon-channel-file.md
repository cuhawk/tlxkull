---
title: CrowdStrike Falcon Channel File 291 outage (Jul 2024)
slug: crowdstrike-falcon-channel-file
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, surface/endpoint-agent, surface/kernel-driver, technique/config-as-code, technique/no-canary, vendor/crowdstrike]
inbound: []
---

# CrowdStrike Falcon Channel File 291 outage (Jul 2024)

## What happened

At **04:09 UTC on 2024-07-19** CrowdStrike pushed a Rapid Response
Content update -- `Channel File 291`, the "InterProcessCommunication
Template Instances" config -- to every Windows host running the
Falcon sensor at supported `csagent.sys` versions. The file caused
the Falcon driver to perform an **out-of-bounds read** during its
template-interpretation pass, which raised a structured exception in
kernel mode and triggered an immediate BSOD. The file was active for
**78 minutes** (pulled at 05:27 UTC) but the damage was permanent
per-host: machines that booted during the window would crash before
network code initialised, so they could not be remediated remotely.

~**8.5 million Windows hosts** crashed -- airlines (Delta cancelled
~7,000 flights), hospitals (multiple US emergency rooms went
paper-only), broadcast TV (Sky News UK off-air), London Stock
Exchange data feeds, and an estimated 25% of global airport
check-in. **Not malicious.** A textbook "vendor with kernel-load
trust pushes config without canarying" failure -- the supply-chain
class is: a control plane shipped by one vendor can take down the
entire downstream fleet, no CVE, no exploit, just a config flag in
the wrong place.

## Attack chain

(read here as "failure chain" -- replicable by any attacker who
compromises a vendor's content-pipeline signing key.)

1. **IPC Template Type schema declared 21 input fields.**
   `csagent.sys`'s content interpreter, however, only ever passed
   **20** fields when calling out to the template. The 21st field was
   read from one slot past the end of the input array.
2. **Content Validator missed the mismatch.** CrowdStrike's
   pre-deploy validator was supposed to reject any template instance
   whose field count exceeded what the sensor would supply, but a
   logic bug allowed Channel File 291 (which provided non-wildcard
   matching criteria in the 21st field) to pass.
3. **No runtime bounds check.** The content interpreter dereferenced
   the 21st field via pointer arithmetic on an `IMAGE_REL_BASED_DIR64`
   relocation without checking that the array was large enough -- a
   classic OOB read in C++.
4. **Kernel-mode exception -> BSOD.** Because `csagent.sys` runs at
   ring 0, the read access violation could not be caught by user-mode
   SEH. Windows raised `KERNEL_SECURITY_CHECK_FAILURE` and rebooted.
5. **Crash-on-boot loop.** The bad channel file was loaded *during*
   the kernel driver's early init. Affected hosts crashed before the
   sensor's update channel could pull a newer version; recovery
   required boot to Safe Mode and manual deletion of
   `C:\Windows\System32\drivers\CrowdStrike\C-00000291-*.sys`.
6. **No canary / no staged rollout.** Rapid Response Content was
   deployed to **100% of hosts simultaneously**. CrowdStrike's own RCA
   admits there was no canary fleet, no per-region staggering, no
   "halt on first 1% BSOD" telemetry signal.

## Lessons for bug hunters

- **"Config as code" pushed to kernel drivers is a class of
  supply-chain risk.** Most EDR vendors (CrowdStrike, SentinelOne,
  Microsoft Defender, Carbon Black) ship signed-but-not-versioned
  content files that the kernel driver interprets. If you can find
  *any* primitive that causes the interpreter to misbehave (OOB read,
  type confusion, integer overflow), you have a kernel-mode crash or
  worse. RCA-style bug reports against EDR content pipelines are a
  high-payout category.
- **Vendor signing-key compromise = fleet-wide RCE.** The blast
  radius of a vendor whose content gets to ring 0 is identical to
  the blast radius of an attacker who steals their signing key.
  Programs that publish such artefacts should include the
  build/signing infrastructure in scope. See
  [[ci-signing-key-blast-radius]].
- **Always check canary policy in scoping conversations.** A target
  whose program rewards demonstrations of "config push reaches all
  customers in <N minutes without staging" can be a separate report
  class.
- **Userland != kernel-land.** OOB-read in a userland sensor at
  worst kills the agent process; in `csagent.sys` it kills the OS.
  Pay attention to which DLLs/SYSes your target's agent loads and
  what privilege they hold.
- **Force-update channels disable customer remediation.** If your
  target has a "we override your local pin" content channel, document
  it -- it changes the customer's risk model and is worth a writeup
  in itself.

## Primary sources

- [CrowdStrike: External Technical Root Cause Analysis -- Channel File 291 (PDF, 2024-08-06)](https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf)
  -- the 12-page CrowdStrike-authored RCA naming the 21-vs-20 field
  mismatch and the validator bug.
- [Sonar: What Code Issues Caused the CrowdStrike Outage?](https://www.sonarsource.com/blog/what-code-issues-caused-the-crowdstrike-outage)
  -- independent C++ deep-dive with the disassembly of the OOB read
  in the content interpreter.

## Related

- [[ci-signing-key-blast-radius]]
- [[xz-utils-cve-2024-3094]]
- [[mimecast-cert-solarwinds-cluster]]
