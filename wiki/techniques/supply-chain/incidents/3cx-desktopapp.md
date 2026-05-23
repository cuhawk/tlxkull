---
title: 3CX DesktopApp double supply chain (Lazarus, Mar 2023)
slug: 3cx-desktopapp
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, actor/lazarus, actor/labyrinth-chollima, technique/dll-sideload, technique/code-signing-abuse, technique/double-supply-chain]
inbound: []
---

# 3CX DesktopApp double supply chain (Lazarus, Mar 2023)

## What happened

In **March 2023**, **CrowdStrike Falcon Overwatch** and other EDR
vendors flagged unusual beaconing originating from the **signed 3CX
DesktopApp** on both **Windows (18.12.416, 18.12.407)** and **macOS
(18.11.1213, 18.12.402, 18.12.416)**. The trojanised installer was
served from 3CX's official update infrastructure, signed with 3CX's
real code-signing certs, and rolled out to a chunk of 3CX's claimed
**~600,000 enterprise customers / ~12 million daily users**.

Mandiant's investigation produced the headline finding: **3CX was
compromised because 3CX itself was the *victim* of a prior supply
chain attack.** In **April 2022**, a 3CX employee downloaded a
trojanised **X_TRADER** futures-trading installer from Trading
Technologies' official site (the X_TRADER product had been EOL since
2020 but the download was still live, signed with TT's then-valid
cert). The X_TRADER trojan, **VEILEDSIGNAL** (a modular HTTP backdoor),
gave **UNC4736 / Lazarus subcluster (LABYRINTH CHOLLIMA)** access to
the employee's box; they harvested 3CX corporate creds, pivoted into
3CX's Windows and macOS build environments, and modified the build
output to sideload malicious DLLs. Mandiant called this the first
publicly confirmed **software-to-software double supply chain**.

## Attack chain

1. **First-stage supply chain (X_TRADER → 3CX employee).** Trading
   Technologies' deprecated X_TRADER installer page served a
   trojanised .exe signed with TT's cert (the cert had been revoked in
   2022 but Windows still accepted it because it was timestamped
   before revocation). 3CX dev installed it on a personal laptop also
   used for corporate VPN access. VEILEDSIGNAL backdoor activates.
2. **Lateral movement into 3CX build infra.** Lazarus harvested
   credentials, accessed both the Windows and macOS build pipelines.
3. **Trojanised 3CX DesktopApp.** On Windows, the build was modified
   to ship a **side-loaded `ffmpeg.dll` + `d3dcompiler_47.dll`**
   alongside the legitimate 3CX exe. The exe loads `ffmpeg.dll` from
   its own directory (DLL search-order). `ffmpeg.dll` is a thin shim
   that decrypts a payload embedded in `d3dcompiler_47.dll` and
   executes it -- the **SUDDENICON** loader. On macOS, the
   `3CXDesktopApp` Mach-O was trojanised directly.
4. **SUDDENICON → C2 from GitHub-hosted .ico files.** After a 7-day
   sleep (to push past install-time AV scanning), SUDDENICON downloads
   an `.ico` file from a hardcoded GitHub repo. The .ico has trailing
   bytes containing AES-encrypted C2 URLs. C2 served the final stage.
5. **ICONIC / ICONICSTEALER infostealer.** Stage-3 payload deployed to
   a small subset of victims. Steals browser history, saved
   credentials, and system info. Hands-on-keyboard activity observed in
   a handful of cases -- this was a targeted-after-mass campaign.
6. **Discovery.** Multiple EDR vendors (CrowdStrike, SentinelOne,
   Sophos) flagged the signed 3CX app's beaconing on 2023-03-29. 3CX
   confirmed within 24h, revoked certs, shipped a clean release.

## Lessons for bug hunters

- **Code-signing timestamps + revoked certs.** Windows accepts a
  signed binary as valid if the cert was good at the *timestamp time*,
  even if revoked later, unless the user has explicitly enabled strict
  revocation checking. Targets shipping native installers should
  enforce per-build cert validity at install time. Test by replaying
  signed-but-revoked binaries through autoupdater paths. See
  [[code-signing-timestamp-bypass]].
- **DLL search-order hijack via legitimate DLL names.** `ffmpeg.dll`,
  `d3dcompiler_47.dll`, `version.dll`, `dwmapi.dll` are
  classic sideload targets. If a target's binary loads any of these
  from its install dir rather than `System32`, that's a foothold. On
  bug-bounty targets, audit installed product directories with
  Procmon for `NAME NOT FOUND` events on DLL loads -- those are the
  empty slots an attacker can fill via [[install-dir-write-acl]].
- **GitHub as C2 dead-drop.** ICONIC's `.ico` files were hosted in a
  public GitHub repo. GitHub-hosted dead-drops bypass corporate egress
  filters because GitHub is allow-listed. Targets that proxy outbound
  HTTP should be inspecting GitHub raw-content downloads too.
- **Sleep timers (7 days) defeat install-time AV.** Implants that
  delay activation past the install window are not theoretical; they
  break the standard "scan on install" defence model. When testing a
  product update, leave it running for >2 weeks before declaring it
  clean.
- **Software-to-software double supply chain is the future-normal.**
  Every vendor in your bug-bounty target's dev toolchain is part of
  the attack surface. Map the *internal* dev-tool stack (IDE plugins,
  Slack apps, CI plugins, OS update channels, third-party trading /
  market-data / dev-utility installers used by engineers). 3CX shows
  the second hop is the productive one.

## Primary sources

- [Mandiant / Google Cloud: "3CX Software Supply Chain Compromise
  Initiated by a Prior Software Supply Chain Compromise" (2023-04-20)](https://cloud.google.com/blog/topics/threat-intelligence/3cx-software-supply-chain-compromise)
  -- the X_TRADER → 3CX double-supply-chain reveal with VEILEDSIGNAL
  reverse and timeline.
- [CrowdStrike: "CrowdStrike Falcon Platform Detects and Prevents
  Active Intrusion Campaign Targeting 3CXDesktopApp Customers"
  (2023-03-29)](https://www.crowdstrike.com/en-us/blog/crowdstrike-detects-and-prevents-active-intrusion-campaign-targeting-3cxdesktopapp-customers/)
  -- discoverer's writeup with the DLL-sideload chain
  (`ffmpeg.dll` + `d3dcompiler_47.dll`), ICONIC stager, and LABYRINTH
  CHOLLIMA attribution.

## Related

- [[solarwinds-orion-sunburst]]
- [[asus-shadowhammer]]
- [[shadowpad-netsarang]]
- [[code-signing-timestamp-bypass]]
- [[dll-sideload-living-off-the-land]]
