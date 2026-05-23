---
title: ShadowPad in NetSarang Xshell/Xmanager (Winnti, Jul 2017)
slug: shadowpad-netsarang
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, actor/winnti, actor/bronze-atlas, technique/build-server-compromise, technique/dga-c2, technique/dns-txt-activation, technique/modular-backdoor]
inbound: []
---

# ShadowPad in NetSarang Xshell/Xmanager (Winnti, Jul 2017)

## What happened

On **2017-07-18**, **NetSarang** -- a Korean vendor of SSH/SFTP/X11
client software for Windows administrators (**Xshell**, **Xmanager**,
**Xftp**, **Xlpd**) -- shipped a signed build of its full product line
containing a multi-stage backdoor inside `nssock2.dll`, the shared
networking library. The implant, named **ShadowPad** by Kaspersky on
2017-08-04, sat dormant on every installed system until activated by
a specific DNS TXT response from one of the attacker's DGA-generated
domains. Once activated, ShadowPad is a fully modular backdoor with
plugins for file I/O, process control, registry, keylog, and arbitrary
code download/exec.

NetSarang's products are widely used by sysadmins and devops engineers
worldwide -- Xshell in particular is the dominant non-PuTTY SSH client
in Asian enterprises. Kaspersky discovered the implant only because a
**Hong Kong financial-services customer** noticed unusual DNS lookups
from a server running the new Xshell build and asked for help. The
backdoor was traced to NetSarang's official signed installer.
Attribution: **Winnti / Bronze Atlas / APT41** (Chinese state-aligned).
ShadowPad later became Winnti's shared modular framework, recurring in
**[[ccleaner-floxif]]** (Sep 2017) and many subsequent campaigns.
NetSarang's installation base was small relative to CCleaner but
selectively positioned -- sysadmin tooling on jump hosts and bastions.

## Attack chain

1. **Build-environment compromise at NetSarang.** Vector not publicly
   confirmed. The trojanised `nssock2.dll` was signed with NetSarang's
   real cert, so either the cert was used in-band (signing pipeline
   compromise) or the attacker had reached the build server. Affected
   versions: Xmanager Enterprise 5.0 Build 1232, Xmanager 5.0 Build
   1045, Xshell 5.0 Build 1322, Xftp 5.0 Build 1218, Xlpd 5.0 Build
   1220 -- one coordinated build pass across the product line.
2. **Dormant stage-1 in `nssock2.dll`.** On startup, decrypts a small
   shellcode blob (custom XOR) that initialises the C2 stub. It does
   nothing observable: no immediate network beacon.
3. **DGA-driven DNS-TXT activation.** Generates a domain name based
   on the current month + a day-range bucket (1-10, 11-20, 21+) -- so
   only three lookups per month, low-volume by design. Queries DNS TXT
   for the generated domain. The attackers had pre-registered domains
   for **July-December 2017** at campaign time.
4. **Activation triggered only by a valid TXT record.** A normal NXDOMAIN
   keeps the implant dormant. If the attacker's DNS returns a specially
   crafted TXT, it decrypts to a key + intermediate C2 URL. ShadowPad's
   full second stage downloads from the intermediate.
5. **Modular plugin framework.** Stage-2 is a plugin host. Plugins load
   on demand, providing file/process/registry/keylog/network capabilities.
   The plugin protocol is the same one later seen across Winnti
   campaigns -- ShadowPad is a *platform*, NetSarang was its public
   debut.
6. **Discovery.** Hong Kong customer's DNS-monitoring saw lookups to
   a suspicious domain. Kaspersky reversed `nssock2.dll`, identified
   stage-1, hooked the C2, and disclosed publicly on 2017-08-15.
   NetSarang issued an emergency clean rebuild within 48h.

## Lessons for bug hunters

- **Dormant-by-default backdoors are invisible to behavioural EDR.**
  ShadowPad emitted *no* network traffic until activated by a TXT
  response. Any malware sandbox that doesn't simulate attacker DNS
  will mark the binary clean. On bug-bounty targets, look for product
  features that are gated behind an obscure DNS lookup / TXT record /
  remote feature-flag -- those gates are also exfil channels and
  often unauthenticated. See [[remote-feature-flag-trust]].
- **DNS TXT as C2.** Three lookups per month is hard to flag on
  volume. Targets that don't monitor *content* of DNS TXT in
  outbound responses (not just queries) are deaf to this class. Test
  egress: can you exfil 200 bytes via a single TXT response to a domain
  the target's resolver queries? Usually yes. See [[dns-txt-c2]].
- **Shared network libraries are high-value targets.** `nssock2.dll`
  is loaded by every NetSarang product. One DLL = one cert sig =
  full product line. On bug-bounty targets, identify the shared base
  library (often `*.network.dll`, `libsupport.so`, `core.dylib`) and
  ask: who signs it, where does it come from, can I push a build?
- **DGA with low-cardinality buckets.** ShadowPad's DGA produced only
  ~3 domains per month -- cheap to register and easy to maintain. Most
  defensive DGA-detection tools watch for high-volume sequential
  lookups; a low-and-slow DGA bypasses them. If you find low-cardinality
  DGA in a target's product, it's either malware or a buggy update
  mechanism; both are interesting.
- **Sysadmin tooling is the bastion.** Xshell users are sysadmins
  running it on jump hosts that have privileged access to the rest of
  the fleet. Compromising the SSH-client tooling = compromising every
  destination it touches. On bug-bounty targets, pay attention to any
  developer-tool / admin-tool / IDE-plugin in the engineer toolchain
  -- compromise there is far higher-leverage than a customer-facing
  bug. See [[admin-tooling-attack-surface]].

## Primary sources

- [Kaspersky GReAT: "ShadowPad: popular server management software hit
  in supply chain attack" (2017-08-15)](https://securelist.com/shadowpad-in-corporate-networks/81432/)
  -- the original public disclosure with reverse engineering of
  `nssock2.dll`, DGA mechanics, and C2 architecture.
- [Kaspersky technical PDF: "ShadowPad technical description"
  (2017-08-15)](https://d2538mqrb7brka.cloudfront.net/wp-content/uploads/sites/43/2017/08/07172148/ShadowPad_technical_description_PDF.pdf)
  -- detailed binary-level walk of stage-1 decryption, DNS-TXT
  activation, modular plugin protocol, and IOC list.

## Related

- [[ccleaner-floxif]]
- [[asus-shadowhammer]]
- [[solarwinds-orion-sunburst]]
- [[dns-txt-c2]]
- [[admin-tooling-attack-surface]]
- [[remote-feature-flag-trust]]
