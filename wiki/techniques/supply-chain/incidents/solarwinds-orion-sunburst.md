---
title: SolarWinds Orion SUNBURST (APT29/UNC2452)
slug: solarwinds-orion-sunburst
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, actor/apt29, technique/build-pipeline-compromise, technique/code-signing-abuse, language/csharp, registry/msi]
inbound: []
---

# SolarWinds Orion SUNBURST (APT29/UNC2452)

## What happened

Between September 2019 and December 2020, **APT29 / UNC2452 (Russian SVR
"Cozy Bear")** breached SolarWinds' internal network and patiently lived
inside the Orion product build environment. They deployed a custom
implant -- **SUNSPOT** -- on the build server that watched for
`MsBuild.exe` running the Orion solution and, at exactly the right
window of the build, swapped a single source file (`InventoryManager.cs`)
for a backdoored variant. The resulting build then shipped a trojanised
`SolarWinds.Orion.Core.BusinessLayer.dll` -- the **SUNBURST** backdoor
-- inside the legitimately signed Orion Platform updates 2019.4 HF 5,
2020.2 (no HF), and 2020.2 HF 1.

Roughly **18,000 SolarWinds customers** downloaded the trojanised
update. SUNBURST is a careful first-stage triage tool: it checks the
victim's domain against an exclusion list (security vendors, internal
SolarWinds names), waits 12-14 days, then beacons to an
algorithmically-generated `*.avsvmcloud.com` DNS-tunnel C2. Of those
18k, the actor selected **~100 high-value targets** -- US Treasury,
Commerce, DHS, DoJ, State, NIH, Microsoft, FireEye/Mandiant (whose
discovery exposed the campaign) -- for stage-2 **TEARDROP** / **RAINDROP**
in-memory Cobalt Strike loaders. FireEye disclosed publicly on
2020-12-13.

## Attack chain

1. **Build-environment compromise.** Initial vector never fully
   disclosed; SolarWinds confirmed attacker access to the development
   network months before injection. The actor mapped the Orion CI/CD,
   learned the build cadence, then deployed SUNSPOT.
2. **SUNSPOT in-build source swap.** SUNSPOT polls every second for
   `MsBuild.exe` processes whose command line references the Orion
   `.sln`. When matched, it replaces `InventoryManager.cs` on disk with
   an AES-encrypted backdoored copy, waits for the file to be compiled
   into the DLL, then restores the original. The legitimate code-signing
   pipeline then signs the malicious DLL with SolarWinds' real cert. The
   hash of the source file is verified to keep the build deterministic.
3. **SUNBURST DLL backdoor.** Embedded in the signed plugin. Dormant
   for 12-14 days post-install. Communicates by encoding C2 commands as
   subdomains of `avsvmcloud.com` (DNS-tunnel that blends into Orion's
   legitimate telemetry protocol "Orion Improvement Program"). Selects
   targets via domain-name hash matching against a blocklist; non-matches
   are killed.
4. **Stage-2 TEARDROP / RAINDROP.** For chosen victims, SUNBURST drops
   TEARDROP (memory-only PE loader using a custom XOR-rolled format) or
   RAINDROP (DLL variant) that loads Cobalt Strike BEACON. Then human
   operators pivot, abuse on-prem ADFS to forge SAML tokens (the
   "Golden SAML" technique), and access M365 mailboxes via OAuth token
   theft.
5. **Long discovery window.** Detected ~9 months after first deployed,
   only because FireEye noticed a second device registering to its MFA
   tied to a stolen security engineer credential, and traced the breach
   inward.

## Lessons for bug hunters

- **Build pipelines are an attack surface, not a black box.** Any
  bug-bounty target that publishes signed binaries has a CI/CD that
  can be tampered with. Look for CI config leaks (`.github/workflows/`,
  `Jenkinsfile`, `azure-pipelines.yml` in public repos), runner-token
  exposure, and the cardinal sin of running signing inside the same
  pipeline that pulls untrusted PRs. See [[github-actions-pwn-request]]
  and [[code-signing-cert-theft]].
- **In-build source swap is invisible to source review.** SUNSPOT
  modified files only during the compile window, then restored them.
  This pattern -- "the source on disk is one thing during `make`,
  another at rest" -- is reproducible with filesystem watchers in any
  CI. Probe for build environments that don't hash-verify intermediates
  or that allow non-CI processes on the build host.
- **Domain/cert hash blocklists as anti-analysis.** SUNBURST refused to
  run on hostnames containing "SolarWinds", security-vendor domain
  names, or known sandbox AD names. Watching for fingerprint-checks
  against a list of strings before activation is a malware-analysis
  smell that maps cleanly to bug-class fingerprinting in product code
  too -- search captured JS for similar "abort if customer matches X"
  toggles.
- **DNS as covert channel.** SUNBURST encoded C2 in DNS subdomains
  ([[dns-tunnel-c2]]). Look at your target's egress: do they allow
  arbitrary outbound DNS for their build network? If yes, that's a
  finding regardless of whether you find an active implant.
- **Golden SAML.** Once an attacker has the ADFS token-signing cert,
  every SAML SP downstream trusts forged assertions. SaaS targets
  whose SAML IdP is on-prem and whose token signing key is on a
  reachable host are a higher-value finding than the SAML protocol
  bugs themselves. See [[saml-token-signing-key-exposure]].

## Primary sources

- [Mandiant: "Highly Evasive Attacker Leverages SolarWinds Supply Chain
  to Compromise Multiple Global Victims With SUNBURST Backdoor"
  (2020-12-13)](https://www.mandiant.com/resources/blog/evasive-attacker-leverages-solarwinds-supply-chain-compromises-with-sunburst-backdoor)
  -- the original public disclosure with SUNBURST IOCs and behaviour.
- [CrowdStrike: "SUNSPOT Malware: A Technical Analysis" (2021-01-11)](https://www.crowdstrike.com/en-us/blog/sunspot-malware-technical-analysis/)
  -- deep reverse of the build-time injector, including the MsBuild
  process-poll loop and source-file swap mechanic.

## Related

- [[xz-utils-cve-2024-3094]]
- [[3cx-desktopapp]]
- [[ccleaner-floxif]]
- [[code-signing-cert-theft]]
- [[github-actions-pwn-request]]
