---
title: Sean Yeoh
slug: sean-yeoh
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [seanyeoh, sean-yeoh]
role: vendor-eng
primary_focus: recon
tags: [person, role/vendor-eng, vendor/assetnote, focus/recon, focus/devops, focus/n-day]
inbound: []
---

# Sean Yeoh

## Identity

- Real name: Sean Yeoh.
- Lead Architecture and DevOps engineer at
  [Assetnote](https://www.assetnote.io/) (now part of Searchlight
  Cyber following the January 2025 acquisition).
- Long-running collaborator of Shubham Shah on Assetnote's
  recon-tooling and n-day analysis output. See
  [shubham-shah.md](shubham-shah.md).
- Background spans Rails/devops engineering, Kubernetes admin, and
  bug-bounty research. Previously won Cyber Security Challenge
  Australia CTFs and lectures Advanced Web Application Security and
  Software Security Assessment at UNSW.
- Based in Australia.

## Focus areas

- **Recon infrastructure** — building the engine behind Assetnote's
  ASM platform: continuous asset discovery, fingerprinting at scale,
  pipeline architecture.
- **Content discovery** — co-author of the contextual / API-aware
  content-discovery thesis that produced
  [kiterunner](https://github.com/assetnote/kiterunner).
- **N-day reverse engineering** — pre-auth deserialization and
  managed-file-transfer software analysis (WS_FTP work with Shubs).
- **DevOps / platform** — message brokers, event-driven architecture,
  bottleneck removal, build pipelines.
- **Desktop / macOS** — historic Zoom-on-macOS RCE chain work
  (HITB GSEC SG 2019).

## Online presence

- Company / research hub:
  [assetnote.io/resources/research](https://www.assetnote.io/resources/research)
- X / Twitter: [@seanyeoh](https://twitter.com/seanyeoh)
- GitHub: [github.com/sean-yeoh](https://github.com/sean-yeoh)
  (Ruby on Rails, Phlex components, Tailwind/Alpine — devops side)
  and team contributions under
  [github.com/assetnote](https://github.com/assetnote)
- LinkedIn:
  [linkedin.com/in/sean-yeoh-17b566a6](https://www.linkedin.com/in/sean-yeoh-17b566a6/)
- HITB GSEC SG 2019 speaker page:
  [gsec.hitb.org/sg2019/speakers/sean-yeoh](https://gsec.hitb.org/sg2019/speakers/sean-yeoh/)

## Key research / posts

- **Advisory: Progress WS_FTP RCE (CVE-2023-40044)** (2023-09-30)
  with Shubham Shah —
  [assetnote.io](https://www.assetnote.io/resources/research/advisory-progress-ws-ftp-rce-cve-2023-40044).
  Pre-auth deserialization in the WS_FTP Ad Hoc Transfer component;
  CVSS 10.0; ~3,000 internet-exposed hosts at disclosure time. Sean
  led the reverse-engineering side of the file-transfer-suite work.
- **Contextual Content Discovery: You've forgotten about the API
  endpoints** (2021-04-05) with James Hebden, Patrick Mortensen,
  Jordan Macey, Michael Gianarakis, and Shubham Shah —
  [assetnote.io](https://www.assetnote.io/resources/research/contextual-content-discovery-youve-forgotten-about-the-api-endpoints).
  Introduces Kiterunner. Collated ~67k OpenAPI/Swagger specs into a
  schema-aware brute-forcer that fires the correct method, headers,
  path, and parameters per route — finding API routes that
  path-only wordlist tools miss. Tool:
  [github.com/assetnote/kiterunner](https://github.com/assetnote/kiterunner).
- **Zero To RCE In Two Days – Exploiting Zoom on macOS**
  (HITB GSEC SG 2019, 2019-08-29) —
  [gsec.hitb.org](https://gsec.hitb.org/sg2019/speakers/sean-yeoh/).
  COMMSEC talk on chaining bugs in the Zoom macOS client into RCE.
  Pre-Assetnote era; demonstrates desktop-app reverse-engineering
  depth that later showed up in WS_FTP work.

(Assetnote's research-page bylines rarely surface in the listing
view; Sean is most visible as co-author on the WS_FTP and Kiterunner
work above. Other Assetnote n-day output is led by Shubham Shah,
Adam Kues, and Dylan Pindur — see
[shubham-shah.md](shubham-shah.md) for the broader catalog.)

## CT podcast appearances

- [2023-07-27 Ep 29 — Sean Yeoh: Live Chat with an AssetNote Engineer](../sources/podcasts/ct/20230727_nEQPTLDKfmM_Sean_Yeoh_-_Live_Chat_with_an_AssetNote_Engineer_Ep._29.en.vtt)
  — live-recorded episode. Sean discusses the engineering side of
  running Assetnote: message brokers and event-driven architecture,
  preventing bottlenecks, database choice, and how reconnaissance
  infrastructure (subdomain/IP enumeration pipelines) is built and
  scaled. Less hunter-war-stories, more "what does the platform
  team behind the research output actually do".

## Notes

- **The engineer behind the recon engine.** Where Shubham is the
  research-and-bounty face of Assetnote, Sean is the platform side:
  the person who keeps the asset-discovery pipelines, fingerprinters,
  and Kiterunner-class tooling actually running at internet scale.
  The "recon-first lineage" called out in
  [shubham-shah.md](shubham-shah.md) only works because someone
  builds and operates the system underneath — Sean is that someone.
- **Crosses the platform/research line.** Despite the "DevOps lead"
  title, Sean shows up as a co-author on Assetnote's deepest
  reverse-engineering output (WS_FTP CVE-2023-40044). The Zoom-macOS
  HITB talk shows the RE chops predate Assetnote. Useful pattern:
  the people who build the recon platform also do the n-day work
  that validates it.
- **Collaboration with Shubs.** Multi-year pairing. Most public
  Assetnote artifacts that touch both "scale up the surface" and
  "find the bug" have both names on them (Kiterunner; WS_FTP
  advisory). Treat the two pages as a unit when reading Assetnote
  research lineage.
- **Open-source footprint is Rails-flavored.** Personal GitHub is
  heavy on Rails / Phlex / Tailwind / Alpine.js components
  (`shadcn_phlexcomponents`, `sb_admin_2_rails`, `tailwind-alpinejs`)
  — not security tooling. The security output ships under the
  [assetnote](https://github.com/assetnote) org instead.
- **Searchlight Cyber transition.** Per the January 2025
  acquisition, Sean's work now feeds Searchlight's CTEM platform;
  Assetnote's Brisbane team joined Searchlight intact. Research
  output continues under the Assetnote brand.
