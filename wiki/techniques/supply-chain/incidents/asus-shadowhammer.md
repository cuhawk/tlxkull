---
title: ASUS Live Update / Operation ShadowHammer (BARIUM, 2018)
slug: asus-shadowhammer
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, actor/barium-winnti, technique/code-signing-abuse, technique/mac-address-targeting, technique/build-server-compromise]
inbound: []
---

# ASUS Live Update / Operation ShadowHammer (BARIUM, 2018)

## What happened

Between **June and November 2018**, the **BARIUM / Winnti** group
(Chinese state-aligned, the same cluster behind [[ccleaner-floxif]] and
[[shadowpad-netsarang]]) compromised ASUS's build infrastructure for
the **ASUS Live Update Utility** -- the pre-installed updater that
ships on every consumer ASUS laptop. They trojanised at least two
versions of the utility, signed them with **two legitimate ASUS
code-signing certificates**, and served them from ASUS's official
update servers via the normal Live Update channel.

Kaspersky detected ~57,000 of *their own customers* installing the
malicious update; real-world prevalence was estimated >1 million users
worldwide. The novelty was the targeting filter: the implant carried a
**hardcoded list of ~600 MAC-address hashes** (MD5 of the adapter MAC).
On execution, it hashed the machine's NICs and compared. **Non-match =
no stage-2, no network activity, dormant forever.** Match = pull
stage-2 from `asushotfix.com` and run. Kaspersky disclosed it
2019-01-29 and made the MAC-check list searchable. The targets were
~600 specific machines whose identity ASUS could not enumerate -- the
campaign was personnel-level surgical inside a consumer-mass envelope.

## Attack chain

1. **Build-server compromise.** Exact vector not publicly disclosed by
   ASUS. Kaspersky's IOCs and 2018 timing overlap with BARIUM activity
   targeting Asian electronics OEMs. Two ASUS code-signing certs (the
   "AsusTeK Computer Inc." cert and a second one) were both used --
   indicating either dual-cert theft or build-server signing access
   without HSM PIN.
2. **Trojanised `setup.exe` for Live Update.** Implant inserted at the
   binary level (post-compile, pre-sign) so it didn't show in source
   review. Carried the ~600-entry MAC table and a backdoor stub.
3. **Distribution via legitimate update server.** Pushed through the
   normal Live Update auto-update path. The fact that the executable
   was signed with a valid ASUS cert meant Windows SmartScreen, AV
   signature DBs, and ASUS's own client-side update verification all
   passed it.
4. **Selective activation.** On boot, the implant queried local NIC
   MAC addresses, MD5-hashed each, and compared to the embedded table.
   - **Hash hit:** pull `idx.ico` from `asushotfix.com`, decrypt,
     execute stage-2.
   - **No hit:** silent. No callout, no persistence beyond what the
     legitimate updater already does. This is what kept it invisible
     for ~6 months.
5. **Discovery.** Kaspersky's machine-learning telemetry flagged the
   signed binary as a sibling of known Winnti samples. Skylight Cyber
   later brute-forced the MAC-hash list by reverse-engineering
   Kaspersky's offline checker tool, publishing the full ~600-entry
   plaintext list.

## Lessons for bug hunters

- **Auto-update mechanisms are themselves products.** Vendor-bundled
  updaters (Live Update, GeForce Experience, Dell SupportAssist, Lenovo
  Vantage) sit at SYSTEM, run on boot, and trust their vendor CDN
  blindly. Audit them as their own attack surface: pinning, TLS
  validation, signature checks, downgrade protection, request
  manipulability. Any updater that accepts a redirect to a non-vendor
  host is a finding. See [[oem-updater-attack-surface]].
- **MAC / hostname / domain-hash gating is a generic anti-analysis
  pattern.** If you find a binary in a target's product that hashes a
  local identifier and compares to an embedded table before running
  privileged code, that's a kill-switch / per-customer-gating mechanism
  -- often legitimate, sometimes a hidden feature, occasionally an
  implant. Always extract and brute-force the table.
- **Two valid certs, both reachable from one build network = single
  point of failure.** Targets that publish multiple products under
  multiple certs but share a signing pipeline have effectively one
  cert. Look for signing-key usage logs (or absence) in customer
  portals.
- **"Silent if not target" implants are detectable only by hash.** If
  a target's product has a code path that never executes on your test
  machine, that doesn't mean it's dead. Diff the binary against the
  prior version's hash, look for new strings/constants, and
  symbolically execute the dormant branch. See
  [[silent-branch-fingerprinting]].
- **Vendor offline checker tools leak the IOC.** Skylight extracted
  the MAC list by inverting Kaspersky's checker. Any defensive tool
  shipped to end-users that contains the indicator set is itself a
  research artefact -- inversion is in-scope.

## Primary sources

- [Kaspersky Securelist: "Operation ShadowHammer" (2019-03-25)](https://securelist.com/operation-shadowhammer/89992/)
  -- discoverer's writeup with binary analysis, MAC-filter mechanic,
  and infrastructure overlap with previous Winnti campaigns.
- [BleepingComputer / Skylight Cyber: "MAC Addresses Targeted by the
  ASUS Supply Chain Attack Now Available" (2019-03-28)](https://www.bleepingcomputer.com/news/security/mac-addresses-targeted-by-the-asus-supply-chain-attack-now-available/)
  -- reverse of the Kaspersky checker tool to extract the full
  ~600-entry MAC list, with methodology.

## Related

- [[ccleaner-floxif]]
- [[shadowpad-netsarang]]
- [[3cx-desktopapp]]
- [[code-signing-cert-theft]]
- [[oem-updater-attack-surface]]
