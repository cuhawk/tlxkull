---
title: Justin Gardner (Rhynorater)
slug: justin-gardner
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [rhynorater]
role: dual
primary_focus: client-side
tags: [person, role/host, role/hunter, focus/client-side, focus/oauth, focus/source-review, focus/postmessage]
inbound: []
---

## Identity

- **Real name:** Justin Gardner
- **Primary handle:** `rhynorater`
- **Role:** Co-host of the Critical Thinking — Bug Bounty Podcast and full-time HackerOne bug-bounty hunter. Advisor to Caido. Hacker at CRIT (Critical Research) Software. HackerOne Ambassador (Eastern US).
- **Location:** Richmond, Virginia (previously Yokohama, Japan).
- **Track record:** 450+ vulnerabilities reported, top ~35 on the HackerOne all-time leaderboard, two-time Live Hacking Event MVH (2021, 2022), DEFCON 2022 main-stage speaker, full-time hunter since March 2020, OSCP since 2018.

## Focus areas

- Client-side web (DOM XSS, postMessage, browser quirks) — see [../techniques/dom-xss/SUMMARY.md](../techniques/dom-xss/SUMMARY.md)
- OAuth / SSO flow abuse — see [../techniques/oauth/SUMMARY.md](../techniques/oauth/SUMMARY.md)
- postMessage exploitation — see [../techniques/postmessage/SUMMARY.md](../techniques/postmessage/SUMMARY.md)
- Source-code review / whitebox 0-day hunting
- AI-assisted hacking and tooling (Caido plugins, micro-agents)

## Online presence

- Blog: [rhynorater.github.io](https://rhynorater.github.io/)
- About: [rhynorater.github.io/aboutme](https://rhynorater.github.io/aboutme/)
- X / Twitter: [@Rhynorater](https://x.com/Rhynorater)
- GitHub: [github.com/Rhynorater](https://github.com/Rhynorater)
- HackerOne: [hackerone.com/rhynorater](https://hackerone.com/rhynorater)
- LinkedIn: [in/rhynorater](https://www.linkedin.com/in/rhynorater/)
- Podcast: [criticalthinkingpodcast.io](https://www.criticalthinkingpodcast.io/) (alt: [ctbb.show](https://ctbb.show))
- Bugcrowd spotlight: [Researcher Spotlight: Ambassador Justin Gardner](https://www.bugcrowd.com/blog/researcher-spotlight-ambassador-justin-gardner/)

## Key research / posts

- **postMessage Braindump** ([rhynorater.github.io/postMessage-Braindump](https://rhynorater.github.io/postMessage-Braindump)) — treat postMessage listeners as APIs: enumerate them, drop into the debugger, and trace user-controlled data into sinks (e.g. unsafe `setAttribute`). Seed of the wiki's postMessage methodology — see [../techniques/postmessage/SUMMARY.md](../techniques/postmessage/SUMMARY.md).
- **CVE-2020-13379 — Grafana unauthenticated full-read SSRF** ([rhynorater.github.io/CVE-2020-13379-Write-Up](https://rhynorater.github.io/CVE-2020-13379-Write-Up)) — chained URL-parameter injection in Grafana's avatar route with open redirects on Gravatar/WordPress image services to escalate a string-concat bug into unauth SSRF.
- **AWS Metadata Identity-Credentials Research** ([rhynorater.github.io/AWS-Metadata-Identity-Credentials](https://rhynorater.github.io/AWS-Metadata-Identity-Credentials)) — dissects the lesser-known `identity-credentials/ec2` metadata endpoint; useful for SSRF-to-AWS escalation paths but tightly scoped to EC2 Instance Connect host-key ops, limited blast radius.
- **Hacker Healthcare** ([rhynorater.github.io/Hacker-Healthcare](https://rhynorater.github.io/Hacker-Healthcare)) — non-technical: how full-time US bug-bounty hunters get health insurance. Cited often when advising new full-timers.
- **Beginners Resources** ([rhynorater.github.io/Beginners-Resources](https://rhynorater.github.io/Beginners-Resources)) — the canonical "where do I start" link he hands out; still kept up to date.
- **CVE-2018-15473 OpenSSH user-enum exploit** ([github.com/Rhynorater/CVE-2018-15473-Exploit](https://github.com/Rhynorater/CVE-2018-15473-Exploit)) — threaded Python PoC, 500+ stars; the standard reference implementation for that CVE.
- **rebindMultiA** ([github.com/Rhynorater/rebindMultiA](https://github.com/Rhynorater/rebindMultiA)) — multi-A-record DNS rebinding helper used in SSRF / IoT chains.
- **waybacktool** ([github.com/Rhynorater/waybacktool](https://github.com/Rhynorater/waybacktool)) — Wayback Machine endpoint enumeration + liveness check; recon staple.

## CT podcast appearances

Host of every CT episode (170+ as of 2026-05). Notable solo/deep technical episodes: **Ep 151** (Client-side Advanced Topics w/ Rhynorater), **Ep 137** (AI-Assisted Whitebox Review), **Ep 102** (Building Web Hacking Micro Agents). See also Ep 8 (PostMessage Exploits and CSS Injection), Ep 18/19 (Source Review — Audit Code Earn Bounties), Ep 43 (Caido — The Up-And-Coming HTTP Proxy), Ep 138 (Caido Tools and Workflows).

## Notes

- **Signature move:** vulnerability *escalation* — refuses to ship low-severity reports as-is; converts reflected XSS into ATO, postMessage into cross-origin read, etc. Bugcrowd spotlight calls this out explicitly.
- **Client-side specialism:** drives much of the wiki's postMessage and DOM-XSS coverage. Episodes 8 and 26 (Client-side Quirks and Browser Hacks) align with [../techniques/postmessage/SUMMARY.md](../techniques/postmessage/SUMMARY.md) and [../techniques/dom-xss/SUMMARY.md](../techniques/dom-xss/SUMMARY.md).
- **Source-code review preacher:** Eps 18/19 are the canonical CT pitch for whitebox auditing as a bounty multiplier; he revisited the same theme in the AI-assisted whitebox review era (Ep 137).
- **Tooling philosophy:** prefers fast, scriptable Unix-style tools (TomNomNom suite — `waybackurls`, `unfurl`, `gron`, `meg`; gobuster, massdns, gowitness, Burp, amass/subfinder). He's now Caido-first as a proxy (advisor + heavy plugin promoter) — see [../tools/caido/notes.md](../tools/caido/notes.md).
- **Companies:** Critical Research (CRIT) — his consultancy / research vehicle. Caido — advisor. HackerOne — Ambassador (Eastern US).
- **Languages:** Fluent Japanese, intermediate Italian (relevant context for live-event collab and recon on JP/IT targets).
- **Off-hacking:** Volleyball, BJJ, real-estate investing — surfaces occasionally on the podcast.
- **Collab patterns:** Co-hosts with Joseph Thacker (`rez0`) and Brandyn Murtagh (`gr3pme`); frequent guest pairings with Inhibitor181, Corben Leo, Shubham Shah, Gal Nagli, Inti De Ceukelaire (per CT guest history).
