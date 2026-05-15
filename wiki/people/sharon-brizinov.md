---
title: Sharon Brizinov
slug: sharon-brizinov
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [sharonbrizinov, sbrizinov]
role: researcher
primary_focus: ot-iot
tags: [person, role/researcher, focus/ot-iot, focus/ics, focus/embedded, focus/pwn2own, focus/protocol, org/claroty-team82]
inbound: []
---

# Sharon Brizinov

## Identity

- **Real name:** Sharon Brizinov
- **Primary handle:** `sharonbrizinov` (GitHub, LinkedIn, personal domain); `sbrizinov` referenced on X.
- **Nationality / base:** Israel
- **Role:** Director of Vulnerability Research at Claroty's Team82 (OT/IoT/XIoT research group).
- **Notoriety:** 200+ CVEs across ICS, IoT, embedded and cloud. Five-time Pwn2Own competitor (ICS 2020, ICS 2022, IoT 2022, ICS 2023, IoT 2023). DEF CON 27 ICS-CTF winner (black badge). SANS Difference Makers Researcher-of-the-Year. Speaker at DEF CON, Black Hat, BlueHat IL, HITCON, S4, Nexus, OTCEP, HackInParis, BSidesTLV.

## Focus areas

- ICS / OT protocols — OPC UA, EtherNet/IP, Siemens S7, Rockwell Logix, OpenVPN industrial wrappers
- PLC and engineering-workstation exploitation (Siemens, Rockwell, Schneider, GE)
- IoT/embedded device pwning — NAS, IP cameras, routers, smart speakers, intercoms, patient monitors
- Printer/embedded firmware extraction and post-RCE persistence (Lexmark series)
- Cloud-to-device pivot — abusing vendor "QuickConnect"-style relays to reach LAN devices from WAN
- Bug-bounty surface that overlaps OT — secrets-in-git, leaked-deleted-files, SaaS-side OT consoles

## Online presence

- [sharonbrizinov.com](https://sharonbrizinov.com/) — personal site; bio, talks, CVE index
- [CVE index](https://sharonbrizinov.com/cves)
- [Contact page](https://sharonbrizinov.com/contact)
- [GitHub — sharonbrizinov](https://github.com/sharonbrizinov) — 45 repos; pinned: [s3viewer](https://github.com/SharonBrizinov/s3viewer), [slack-anti-delete](https://github.com/SharonBrizinov/slack-anti-delete)
- [Medium — @sharon.brizinov](https://medium.com/@sharon.brizinov)
- [LinkedIn — sharonbrizinov](https://www.linkedin.com/in/sharonbrizinov/)
- [SANS profile](https://www.sans.org/profiles/sharon-brizinov/)
- [Claroty Team82 research blog](https://claroty.com/team82/research) — primary corporate outlet
- [Off-by-One Singapore talk page](https://offbyone.sg/conference/sharon-brizinov) — "Five years of hacking ICS/IoT in Pwn2Own"
- [Nexus Podcast appearance — Hacking and Securing PLCs](https://nexusconnect.io/podcasts/nexus-podcast-sharon-brizinov-on-hacking-plcs)
- [ICS Cyber Talks Podcast](https://icscybertalks.podbean.com/e/sharonb/)

## Key research / posts

Selected from claroty.com/team82 and personal outlets; emphasis on the chains the OT/IoT community references.

- [How I Made $64k from Deleted Files — A Bug Bounty Story (2025-04-22)](https://medium.com/@sharon.brizinov/how-i-made-64k-from-deleted-files-a-bug-bounty-story-c5bd3a6f5f9b) — automated clone+scan of thousands of public GitHub repos for secrets that survived in deleted commits / dangling blobs; bounty pipeline writeup. Cross-pollinated with the Truffle Security "Oops Commits" post (also 2025).
- [Bypassing Rockwell Logix Controllers' Trusted Slot (CVE-2024-6242)](https://www.darkreading.com/ics-ot-security/rockwell-plc-security-bypass-threatens-manufacturing-processes) — chassis-level "trusted slot" model on ControlLogix bypassed, letting a low-trust module reach high-trust PLCs over the backplane. 2024 Team82 work.
- [Pwn2Own Toronto 2023 — WAN-to-LAN Exploit Showcase (Part 1)](https://claroty.com/team82/research/pwn2own-wan-to-lan-exploit-showcase) — Team82's playbook for chaining a WAN-facing primitive into LAN-side device takeover across the 2023 contest.
- [Pivoting from WAN to LAN to Attack a Synology BC500 IP Camera (Part 2)](https://claroty.com/team82/research/pivoting-from-wan-to-lan-synology-bc500-ip-camera) — concrete WAN→LAN chain landing RCE on Synology's BC500 camera on stage at P2O Toronto 2023.
- [Synology NAS DSM Account Takeover — When Random is not Secure](https://claroty.com/team82/research/synology-nas-dsm-account-takeover-when-random-is-not-secure) — predictable PRNG state in DSM auth flow → full ATO; Pwn2Own-class bug on consumer NAS. Same family of randomness-failure bug class as several Meta SDK issues.
- [A Pain in the NAS — Exploiting Cloud Connectivity to PWN Synology DS920+](https://claroty.com/team82/research/a-pain-in-the-nas-exploiting-cloud-connectivity-to-pwn-your-nas-synology-ds920-edition) — impersonated the DS920+ to Synology's QuickConnect relay and redirected legitimate user traffic to attacker hardware. DEF CON 31 talk.
- [Chaining Five Vulnerabilities to Exploit Netgear Nighthawk RAX30 Routers (Pwn2Own Toronto 2022)](https://claroty.com/team82/research/chaining-five-vulnerabilities-to-exploit-netgear-nighthawk-rax30-routers-at-pwn2own-toronto-2022) — five-bug chain landing pre-auth RCE on consumer router at P2O Toronto 22.
- [Lexmark Printers Firmware Extraction — Part A](https://claroty.com/team82/research/lexmark-printers-firmware-extraction-part-a) — bootstrapping research on Lexmark fleet by extracting and unpacking firmware; baseline for downstream printer-network attacks (Lexmark is one of the most common printer brands inside hospital networks).
- [Evil PLC Attack — Weaponizing PLCs](https://claroty.com/team82/research/evil-plc-attack-weaponizing-plcs-to-attack-engineering-workstations) — flipping the threat model: a malicious PLC infects the engineering workstation that connects to it. DEF CON 30.
- [Exploiting URL Parsers — paper](https://claroty.com/team82/research/exploiting-url-parsing-confusion) — co-authored with Snyk; survey of parser-confusion bugs across 16 URL libs. Cross-cutting web/IoT relevance.
- [All Roads Lead to OpenVPN — Pwning Industrial Remote Access Clients](https://claroty.com/team82/research/all-roads-lead-to-openvpn-pwning-industrial-remote-access-clients) — vendor wrappers around OpenVPN reintroduced classic bugs; multiple industrial-RA clients popped.
- [Unboxing BusyBox — 14 vulnerabilities (with JFrog)](https://claroty.com/team82/research/jfrog-claroty-unboxing-busybox) — embedded-Linux userland mass-impact bugs.
- [Unpacking the Blackjack Group's Fuxnet Malware](https://claroty.com/team82/research/unpacking-the-blackjack-groups-fuxnet-malware) — reverse-engineering ICS-targeted destructive malware (2024).
- [OPC UA Deep Dive series](https://claroty.com/team82/research/opc-ua-deep-dive-history-of-the-opc-ua-protocol) — multi-part technical series following his P2O OPC-UA wins; protocol internals + attack surface.
- [Exploiting Cloud-Based Intercoms at Scale (BlueHat IL 2022)](https://claroty.com/team82/research/akuvox-e11-multiple-vulnerabilities-allow-network-attackers-full-takeover) — Akuvox E11 intercom: 13 vulns, cloud-side mass-takeover primitives.
- [Pwn2Own Miami 2022 — Prosys OPC UA SDK resource exhaustion](https://prosysopc.com/blog/pwn2own-resource-exhaustion-exploit/) — DoS-class OPC UA bug landed on stage; vendor postmortem.
- [Zero Day Initiative — Sonos One exploited three different ways at Pwn2Own Toronto 2023](https://www.thezdi.com/blog/2023/5/24/exploiting-the-sonos-one-speaker-three-different-ways-a-pwn2own-toronto-highlight) — ZDI roundup of the three winning Sonos chains at the contest Sharon's Team82 also competed in. (NCC Group's deeper Sonos kernel-exploit work was disclosed at Black Hat 2024 — separate team.)

## CT podcast appearances

- [2024-11-21 Ep. 98 — Team 82 Sharon Brizinov - The Live Hacking Polymath](../sources/podcasts/ct/20241121_CP3FxNPXh0g_Team_82_Sharon_Brizinov_-_The_Live_Hacking_Polymath_Ep._98.en.vtt)

## Notes

- Runs Team82, Claroty's research arm — one of the most prolific OT/IoT research outfits, with hundreds of disclosures to ICS vendors (Siemens, Rockwell, Schneider, GE, ABB) and consumer-IoT brands (Synology, Netgear, TP-Link, Akuvox, Lexmark). Most published work after ~2020 is co-authored with the team (Noam Moshe and others appear repeatedly) — read the byline.
- **LHE polymath** angle (CT podcast framing): unusual range for an OT specialist — bug-bounty (web/SaaS), embedded firmware RE, ICS protocol stacks, cloud relay abuse, and even consumer-grade tooling (slack-anti-delete, s3viewer). Same researcher delivering a Rockwell PLC bypass and a $64k secrets-from-deleted-commits payday in the same year is the headline.
- **Signature pattern:** cloud relay → on-device pivot. Vendor-provided "QuickConnect" / "MyCloud" / intercom-SaaS layers consistently underweight authn/authz on the device side. Synology DS920+, Akuvox E11, and several remote-access industrial wrappers all share this shape.
- **PLC tradecraft:** Evil-PLC and Trusted-Slot lines treat the controller as the attacker, not the victim — flips engineer-workstation trust model. Worth re-reading whenever a target ships a thick-client engineering tool that auto-fetches device config.
- **Bug-bounty crossover:** despite OT focus, ranks #1 in Israel's national VDP and runs HackerOne bounty work. The deleted-files-from-git pipeline is reusable tradecraft for our own recon — automated diffing of force-pushed / deleted blobs across public repos.
- **Tools to remember:** [opcua-network-fuzzer](https://github.com/claroty/opcua-network-fuzzer) (Claroty), [s3viewer](https://github.com/SharonBrizinov/s3viewer) for open-bucket triage during recon. ScanMySMS is his co-built SMS-phishing scanner (BSidesTLV 2024).
- **Writeup style:** long-form, vendor-coordinated, screenshot-and-protocol-trace-heavy. Slower cadence than a solo bounty hunter but each post is a self-contained tutorial on the protocol or device family. Treat Team82 posts as reference material for any OT-adjacent target.
