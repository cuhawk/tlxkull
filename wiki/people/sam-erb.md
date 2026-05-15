---
title: Sam Erb (erbbysam)
slug: sam-erb
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [erbbysam]
role: dual
primary_focus: server-side
tags: [person, role/dual, focus/server-side, focus/recon, focus/dns, focus/ctf, focus/google-vrp]
inbound: []
---

# Sam Erb (erbbysam)

## Identity

- **Real name:** Samuel Erb.
- **Primary handle:** `erbbysam` (X, GitHub, HackerOne, Keybase).
- **Role:** Dual — Google security engineer + part-time bug-bounty hunter.
- **Accolades:** HackerOne MVH, H1-Elite member, 2x DEF CON Black Badge
  winner (DC23 & DC24 Badge Challenge with team Council of Nine),
  3x DEF CON Packet Hacking Village speaker.

## Focus areas

- Server-side web vulns (SSRF, auth, vhost / virtual-host confusion).
- Large-scale internet reconnaissance: DNS dataset mining, TLS-cert
  SAN/CN harvesting across IPv4 space.
- DEF CON-style cryptography / cipher / CTF puzzles (route transposition,
  Vigenère, etc.).
- Tooling for searching massive datasets cheaply (binary search over
  reversed-and-sorted text).
- Deep-systems hunter — favors understanding how the target is built
  before fuzzing.

## Online presence

- Blog: [blog.erbbysam.com](https://blog.erbbysam.com/)
- Landing page: [erbbysam.com](https://erbbysam.com)
- X / Twitter: [@erbbysam](https://x.com/erbbysam)
- GitHub: [erbbysam](https://github.com/erbbysam)
- HackerOne: [hackerone.com/erbbysam](https://hackerone.com/erbbysam)
- Keybase: [keybase.io/erbbysam](https://keybase.io/erbbysam)
- Team site: [Council of Nine — co9.io](https://co9.io/)
- DEF CON Black Badge Hall of Fame:
  [defcon.org/html/links/dc-black-badge.html](https://defcon.org/html/links/dc-black-badge.html)

## Key research / posts

- **[DNSGrep — Quickly Searching Large DNS Datasets](https://blog.erbbysam.com/index.php/2019/02/09/dnsgrep/)**
  (2019-02-09). Reverse-and-sort domains then binary-search Rapid7's
  10GB+ fdns/rdns dumps; query time 11 min → 2 ms. Source:
  [github.com/erbbysam/DNSGrep](https://github.com/erbbysam/DNSGrep).
- **[Why I broke your subdomain recon pipeline last night](https://blog.erbbysam.com/index.php/2022/01/15/why-i-broke-your-subdomain-recon-pipeline-last-night/)**
  (2022-01-15). Moved `tls.bufferover.run` / `dns.bufferover.run` to
  freemium after commercial recon vendors freeloaded — broke half the
  industry's subdomain pipelines overnight.
- **[Hunting Certificates & Servers](https://github.com/erbbysam/Hunting-Certificates-And-Servers)**
  (DEF CON 27 PHV, 2019). Scan IPv4 for TLS certs, index CN+SAN fields
  for asset discovery.
  [Slides PDF](https://cdn.shopify.com/s/files/1/0177/9886/files/phv2019-serb.pdf).
- **[Trials, Tribulations & VHost Misconfigurations](https://github.com/erbbysam/virseccon2020_presentation)**
  (VirSecCon 2020). Practical vhost-confusion bug class with Docker lab
  ([docker-vuln-vhosts](https://github.com/erbbysam/docker-vuln-vhosts)).
- **[H1-212 CTF writeup](https://blog.erbbysam.com/index.php/2017/11/17/ctf/)**
  (2017-11-17). HackerOne's NYC live-hacking qualifier CTF solution.
- **[Crossing the KASM — a webapp pentest story](https://forum.defcon.org/node/242001)**
  (DEF CON talk, w/ Justin Gardner / Rhynorater). Multi-stage server-side
  chain against a KASM-style remote-browser webapp.

## CT podcast appearances

- [2023-12-07 Ep 48 — MVH, DEFCON Black Badge, Googler — Sam Erb](../sources/podcasts/ct/20231207_1tKV5HaUXxg_MVH_DEFCON_Black_Badge_Googler_Sam_Erb_Ep._48.en.vtt)

## Notes

- 2x DEF CON Black Badge with Council of Nine (DC23, DC24 Badge
  Challenge) — H1 dubbed him "cipher master." Black Badge = lifetime
  free DEF CON entry.
- HackerOne MVH + inducted into H1-Elite
  ([H1 announcement, 2024-08](https://x.com/Hacker0x01/status/1820620135947726951)).
- Day-job: security engineer at Google. Hunts on the side and tends to
  pick deep-systems targets (auth servers, virtual-hosting layers,
  recon-infra) rather than client-side / DOM bugs.
- Recurring theme: build the dataset / tooling first, then mine it for
  bugs. DNSGrep + bufferover.run powered a generation of subdomain
  recon pipelines.
- Co-presents with Justin Gardner (Rhynorater); collab style is paired
  deep-dive on a single complex webapp rather than mass-hunting.
- Engineering background heavily shapes his methodology — see
  Critical Thinking Ep 48 for his explicit framing of
  "understand-how-it's-built before you break it."
