---
title: NotPetya / M.E.Doc update channel (Sandworm, Jun 2017)
slug: notpetya-medoc
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, actor/sandworm, technique/update-server-compromise, technique/wiper, technique/eternalblue, technique/mimikatz]
inbound: []
---

# NotPetya / M.E.Doc update channel (Sandworm, Jun 2017)

## What happened

On **2017-06-27**, Russian GRU **Unit 74455 ("Sandworm")** launched
**NotPetya**, a wiper masquerading as ransomware, against Ukraine.
Initial delivery: a backdoored auto-update of **M.E.Doc**, the
Ukrainian tax-accounting software used by ~80% of Ukrainian
businesses. The attackers had compromised M.E.Doc's update server
(`upd.me-doc.com.ua`) months earlier and used the update channel to
push the wiper as a normal M.E.Doc patch. Once inside a network,
NotPetya self-propagated via **EternalBlue (MS17-010)**, **EternalRomance**,
and credential theft via a bundled **Mimikatz** module that pulled
LSASS credentials and re-used them over PsExec / WMI.

The wiper destroyed the MBR + MFT of every reachable machine and
displayed a ransom note. There was **no actual recovery key** -- the
"installation ID" shown to victims was random data, not a key
identifier. ~80% of infections were Ukrainian, but lateral spread
through multinational corporate networks crippled **Maersk** (~$300M
loss, 17 port terminals offline), **Merck** (~$870M), **FedEx/TNT**
(~$400M), **Mondelez** (~$150M), **Reckitt Benckiser** (~$130M).
White House total estimate: **~$10 billion globally** -- the most
expensive cyberattack on record at the time.

## Attack chain

1. **M.E.Doc update server compromise.** Sandworm gained admin access
   to `upd.me-doc.com.ua` using stolen credentials (vector consistent
   with credential reuse / weak admin auth). They modified the NGINX
   config to proxy update requests to an actor-controlled host, and
   modified `ZvitPublishedObjects.dll` (a .NET assembly inside M.E.Doc)
   to include backdoor methods that ran arbitrary downloaded code under
   the M.E.Doc updater service.
2. **Three trojanised updates as recon.** ESET later identified
   backdoored M.E.Doc updates on 2017-04-14, 2017-05-15, 2017-06-22.
   The April/May versions exfiltrated EDRPOU codes (Ukrainian unique
   business registry IDs), SMTP credentials, and proxy settings,
   letting the actor map and pre-fingerprint every customer of M.E.Doc.
3. **2017-06-27: NotPetya drop.** The backdoor downloaded and executed
   the wiper. Initial execution privilege = the M.E.Doc updater's, which
   ran as a high-privilege Windows service.
4. **Lateral spread.** Mimikatz module dumped LSASS credentials.
   PsExec + WMI used to push the wiper to every Windows host reachable
   on SMB. **EternalBlue / EternalRomance** SMB exploits hit unpatched
   hosts. One unpatched VPN connection from a Ukrainian branch was
   enough to bridge into a multinational's full corporate AD --
   Maersk's case was a single workstation in Odessa.
5. **Wipe + fake ransom.** Overwrites MBR with a custom Petya-style
   bootloader, then on reboot encrypts MFT with no recoverable key.
   The ransom address is a single Bitcoin wallet for the whole
   campaign -- intentionally non-scalable, confirming wiper intent.

## Lessons for bug hunters

- **Auto-updaters with admin/SYSTEM trust are always-on RCE
  primitives.** Any target's update channel that lacks (a) HTTPS pin,
  (b) signature verification of payload, (c) authenticated origin
  binding is a single-vendor catastrophe waiting. Test with a
  modified-cert MitM through a controlled proxy on shadow accounts.
  See [[update-channel-hijack]].
- **Backdoor-the-server, not the binary.** NotPetya never trojanised
  M.E.Doc's source. The attacker owned the *delivery server* and
  modified `nginx.conf` to proxy update requests. Bug-bounty
  parallel: when a target serves binaries from S3 / CloudFront / a
  Linux VM, the bucket policy / origin server config is the supply
  chain. Public S3 write, weak IAM, exposed origin = the path. See
  [[s3-bucket-takeover-supply-chain]].
- **EternalBlue's lesson is patch lag, not the exploit.** Six weeks
  after MS17-010, Maersk had unpatched DCs. Probe targets for
  internal-only services exposed via VPN/proxy that are running old
  Windows or unpatched Linux SMB-equivalents (NetBIOS, Samba). The
  bounty is in the audit gap: "internal" services with external paths.
- **Mimikatz + PsExec is still the canonical Windows lateral-move
  primitive.** Targets that allow LSASS access (no Credential Guard)
  and unrestricted SMB internally are vulnerable to any post-foothold
  attacker. Domain-account password hygiene = bug-bounty finding when
  combined with a foothold primitive.
- **The "ransomware" framing is misdirection.** A wiper disguised as
  ransomware is a real adversary technique. When investigating a
  destructive event in a target's incident-response disclosure, check
  whether the decryption key is mathematically recoverable. If not,
  that's a clue to wiper intent and attribution.

## Primary sources

- [Cisco Talos: "The MeDoc Connection" (2017-07-05)](https://blog.talosintelligence.com/the-medoc-connection/)
  -- the discovery writeup, with NGINX config tamper, backdoored
  `ZvitPublishedObjects.dll`, and credential-theft IOCs.
- [Andy Greenberg / WIRED: "The Untold Story of NotPetya, the Most
  Devastating Cyberattack in History" (2018-08-22)](https://www.wired.com/story/notpetya-cyberattack-ukraine-russia-code-crashed-the-world/)
  -- long-form reconstruction including Maersk's near-total recovery
  from a single surviving DC in Ghana.

## Related

- [[solarwinds-orion-sunburst]]
- [[kaseya-vsa-revil]]
- [[update-channel-hijack]]
- [[eternalblue-ms17-010]]
- [[s3-bucket-takeover-supply-chain]]
