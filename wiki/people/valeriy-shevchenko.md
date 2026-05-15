---
title: Valeriy Shevchenko (bsysop / krevetk0)
slug: valeriy-shevchenko
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [bsysop, krevetk0]
role: hunter
primary_focus: race-conditions
tags: [person, role/hunter, focus/race-conditions, focus/ssrf, focus/auth, focus/recon]
inbound: []
---

# Valeriy Shevchenko

## Identity

- Real name: Valeriy Shevchenko
- Primary handle: **bsysop** (X/GitHub); **krevetk0** (Medium, HackerOne)
- Role: hunter (independent bug-bounty researcher since 2016)
- Day job: Security Engineer at Semrush (Feb 2023 – present). Previously
  pentester at Cobalt.io; co-founder of Darknotice.
- Recognized as a U.S. DoD Most Valuable Researcher (2024). Acknowledged
  by 20+ companies including Amazon, PayPal, Best Buy, Salesforce, N26,
  Mozilla.

## Focus areas

- Race conditions / TOCTOU (per CT Ep. 167 framing — "stealing bugs" is
  about competitive dynamics in bounty programs, not the bug class
  itself, but Justin Gardner framed his guest slot around timing-attack
  research)
- SSRF chains (FFmpeg HLS, Sentry, blind SSRF chaining)
- Auth / credential stuffing as a bug-bounty methodology
- Recon at scale on enterprise SaaS (Atlassian Cloud, Jenkins)
- Self-XSS → critical via downstream consumers

## Online presence

- [Medium blog (krevetk0)](https://krevetk0.medium.com/)
- [HackerOne — krevetk0](https://hackerone.com/krevetk0)
- [HackerOne — bsysop](https://hackerone.com/bsysop)
- [GitHub — bsysop](https://github.com/bsysop)
- [LinkedIn](https://www.linkedin.com/in/valeriyshevchenko/)
- [BSides Berlin speaker page](https://bsides.berlin/Valeriy_Shevchenko.html)
- [The Org — Semrush](https://theorg.com/org/semrush/org-chart/valeriy-shevchenko)

## Key research / posts

- [Hacking Hackers for fun and profit](https://krevetk0.medium.com/hacking-hackers-for-fun-and-profit-784e6c7897e8)
  (2023-01-09) — planted a Blind XSS payload in his LinkedIn "skills"
  field; it fired inside a third-party recruiter/scraper tool, exposing
  PII of other security professionals. Lesson: self-XSS is critical when
  a downstream automated consumer ingests the field.
- [How I accidentally hacked many companies using N/A vulnerability in Atlassian Cloud](https://krevetk0.medium.com/how-i-accidentally-hacked-many-companies-using-n-a-vulnerability-in-atlassian-cloud-d4ff8e7dbef1)
  (2021-11-19) — $15k bounty; turned an Atlassian "won't fix" into a
  multi-tenant chain.
- [Credential stuffing in Bug bounty hunting](https://krevetk0.medium.com/credential-stuffing-in-bug-bounty-hunting-7168dc1d3153)
  (2021-07-13) — methodology piece on using leaked-creds dumps as a
  legitimate bug-bounty primitive (in-scope programs only).
- [$10,000 for a vulnerability that doesn't exist](https://krevetk0.medium.com/10-000-for-a-vulnerability-that-doesnt-exist-9dbc63684e94)
  (2021-01-07) — report that triaged on perceived impact rather than
  reproducible PoC; lesson on framing.
- [From CRLF to Account Takeover](https://krevetk0.medium.com/from-crlf-to-account-takeover-a94d7aa0d74e)
  (2020-06-03) — header-injection chain to full ATO.
- [Broke limited scope with a chain of bugs](https://krevetk0.medium.com/broke-limited-scope-with-a-chain-of-bugs-ef734ac430f5)
  (2020-03-09).
- [Critical vulnerabilities in Pulse Secure and Fortinet SSL VPNs in the Wild Internet](https://krevetk0.medium.com/critical-vulnerabilities-in-pulse-secure-and-fortinet-ssl-vpns-in-the-wild-internet-3991ea9e6481)
  (2019-09-02) — early mass-scan disclosure work on Pulse/Fortinet CVEs.
- [Jenkins RCE PoC or simple pre-auth remote code execution on the Server](https://krevetk0.medium.com/jenkins-rce-poc-or-simple-pre-auth-remote-code-execution-on-the-server-d18b868a77cb)
  (2019-08-19).
- [Two Easy RCE in Atlassian Products](https://krevetk0.medium.com/two-easy-rce-in-atlassian-products-e8480eacdc7f)
  (2019-08-09).
- [SSRF Vulnerability due to Sentry misconfiguration](https://krevetk0.medium.com/ssrf-vulnerability-due-to-sentry-misconfiguration-5e758bdb4e44)
  (2019-05-27).
- [SSRF vulnerability via FFmpeg HLS processing](https://krevetk0.medium.com/ssrf-vulnerability-via-ffmpeg-hls-processing-f3823c16f3c7)
  (2019-04) — classic FFmpeg HLS playlist abuse for blind SSRF.

## Notable tooling (GitHub)

- [servicenow](https://github.com/bsysop/servicenow) — ServiceNow
  widget-simple-list misconfiguration scanner (Python, 65★).
- [CrowdAssist](https://github.com/bsysop/CrowdAssist) — JS helper (22★).
- [IpLogger](https://github.com/bsysop/IpLogger).
- Forks of `blind-ssrf-chains`, `jwt-hack`, `Awesome-Red-Teaming` —
  signals interest areas.

## CT podcast appearances

- [2026-03-26 Ep 167 — Stealing Bugs with Valeriy Shevchenko](../sources/podcasts/ct/) —
  program management, anchor programs, and "theft" dynamics in bug
  bounty (i.e. duplicate-stealing, program rotation, the social/economic
  layer of the bounty game). Despite the title, the episode is more
  about competitive ecosystem dynamics than a specific bug class.

## Notes

- The "Stealing Bugs" episode title is metaphorical, not technical —
  refers to competitive dynamics around dupes and triage, not collision
  attacks. The `primary_focus: race-conditions` frontmatter reflects the
  framing requested at ingest; if a closer listen of the transcript
  reveals a different center of gravity, update via wiki-ingest.
- Strong portfolio bias toward enterprise SaaS (Atlassian, Jenkins,
  Sentry, ServiceNow) and infrastructure (FFmpeg, SSL VPNs). Less
  client-side / DOM-XSS volume than CT regulars.
- Two-handle pattern is intentional: `krevetk0` for HackerOne + Medium
  presence, `bsysop` for GitHub + X + community ops. Both reference him.
- Russian / Ukrainian background; based in EU per Semrush HQ. No public
  geopolitical commentary on his channels.
- No published research found specifically on race conditions /
  collision attacks as of 2026-05-15 — the focus tag is forward-looking
  based on Ep 167 framing rather than back-catalog evidence.
