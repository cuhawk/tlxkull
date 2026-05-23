---
title: CCleaner Floxif (Piriform/Avast, Sep 2017)
slug: ccleaner-floxif
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, actor/axiom-group, technique/build-environment-compromise, technique/code-signing-abuse, technique/dga-c2, registry/msi]
inbound: []
---

# CCleaner Floxif (Piriform/Avast, Sep 2017)

## What happened

In mid-2017, attackers compromised the Piriform build environment
*after* Avast had announced the Piriform acquisition (Jul 2017, deal
closed) but *before* internal toolchain unification was complete. They
trojanised the 32-bit build of **CCleaner v5.33.6162** (released
2017-08-15) and **CCleaner Cloud v1.07.3191** (2017-08-24), both signed
with Piriform's real Symantec-issued code-signing certificate. The
malicious installers were served from Piriform's official CDN to
roughly **2.27 million users** over ~four weeks.

The stage-1 implant -- **Floxif** -- was a thin profiler: collect
hostname, IP, installed-software list, MAC, admin status; POST to a
hardcoded C2; on failure fall back to a domain-generation algorithm. It
looked like a noisy mass infection. Stage-2 changed the calculus: of
the 2.27M victims only **~40 specific PCs** received it, and the
list of targeted internal domains read like a Western tech-sector
hit-list -- Cisco, Samsung, Sony, Intel, VMware, HTC, Akamai,
Microsoft, Google, Oracle, Vodafone, Linksys, D-Link, Epson, MSI,
Singtel. Cisco Talos discovered it 2017-09-13 while beta-testing new
exploit-detection. Attribution: **Axiom Group / APT17 / "Group 72"**
(Chinese state-aligned), based on overlap with ShadowPad C2
infrastructure.

## Attack chain

1. **Initial access via TeamViewer.** Avast's later forensics
   identified the attacker entered Piriform's network through an
   exposed TeamViewer installation on a developer workstation using
   credentials reused from a prior breach. They pivoted by RDP and
   credential theft to the build server.
2. **Stage-1: Floxif in `CCleaner.exe`.** Injected into the legitimate
   32-bit `CCleaner.exe` binary at build time. Profiles the host and
   POSTs to `216.126.225.148`, using the same HTTPS headers as
   Piriform's own Speccy product so traffic blends with legitimate
   telemetry. On C2 failure, generates DGA domains and queries them.
2. **Targeting filter on the C2.** Server-side MySQL table mapped
   victim domain/hostname to a target list. Only victims matching the
   list received stage-2.
3. **Stage-2: `GeeSetup_x86.dll` + patched DLLs.** Delivered to ~40
   PCs. Drops a 32-bit patched `TSMSISrv.dll` (originally Corel's) or
   a 64-bit patched `EFACli64.dll` (originally Symantec's) into
   `%SystemRoot%\System32`. Both abuse a DLL-hijack-style auto-load
   path to gain persistence as a service DLL on next reboot.
4. **Possible stage-3 keylogger.** Avast later identified a likely
   third stage with keylogging capability found on the C2 but never
   confirmed deployed. The C2 was seized before they could enumerate
   exfil fully.
5. **Discovery.** Talos's behavioural detection caught the installer
   doing the POST handshake. Avast confirmed within hours and pushed a
   clean 5.34 release; the malicious cert was revoked.

## Lessons for bug hunters

- **Acquisitions are a transient soft window.** The two months around
  an acquisition are when both sides' security teams are reorganising,
  shared credentials are issued for "migration", and old VPN/RDP
  paths are still open. On any bug-bounty target that recently
  acquired, expect M&A-era misconfigurations: shared service accounts,
  test VPNs not torn down, build-cert sharing. See
  [[m-and-a-transient-attack-window]].
- **The legitimate cert is the prize, not the malware.** Floxif's
  novelty wasn't the implant; it was that 32-bit `CCleaner.exe` was
  signed by Piriform's real cert. Watch for targets that sign artifacts
  from a shared HSM or CI without per-build human approval -- one
  signing-pipeline compromise = limitless authenticated payloads.
- **Service-account / RDP / TeamViewer on developer workstations.**
  The breach started from a humble remote-access tool on one engineer's
  laptop. On bug-bounty targets, look for exposed `:5938` (TeamViewer)
  or RustDesk/AnyDesk relays, weak credentials, and developer-grade
  remote-access products on production-adjacent hosts.
- **DGA fallback as a network IOC.** Any binary that contacts a
  hardcoded C2 then *deterministically* tries DGA names on failure is
  trivially detectable in egress logs. Targets running outbound DNS
  monitoring should be alerting on this. If they don't, the gap is the
  bug.
- **"Same User-Agent as our other product" trick.** Floxif mimicked
  the Speccy User-Agent header. Probe similar masquerading in any
  vendor that ships multiple binaries with shared telemetry endpoints
  -- impersonating sibling-product traffic to slip past per-product
  egress allowlists is a real evasion gadget. See [[user-agent-tunnel]].

## Primary sources

- [Avast Threat Labs: "Avast Threat Labs analysis of CCleaner incident"
  (2017-09-25)](https://blog.avast.com/avast-threat-labs-analysis-of-ccleaner-incident)
  -- the vendor post-mortem confirming TeamViewer ingress and the
  staged target list.
- [Cisco Talos: "CCleanup: A Vast Number of Machines at Risk"
  (2017-09-18)](https://blog.talosintelligence.com/avast-distributes-malware/)
  -- discoverer's writeup, with stage-1 binary analysis, DGA, and
  C2 protocol.

## Related

- [[solarwinds-orion-sunburst]]
- [[shadowpad-netsarang]]
- [[asus-shadowhammer]]
- [[code-signing-cert-theft]]
- [[m-and-a-transient-attack-window]]
