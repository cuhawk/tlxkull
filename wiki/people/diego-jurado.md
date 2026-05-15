---
title: Diego Jurado
slug: diego-jurado
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [djurado, djurado9, 0d4rujd, djuradopallares]
role: dual
primary_focus: ai-hacking
tags: [person, role/dual, focus/ai-hacking, focus/agent-driven, focus/web, focus/xss, focus/xxe, focus/access-control, vendor/xbow]
inbound: []
---

# Diego Jurado

## Identity

- Real name: **Diego Jurado Pallarés**. Spanish hunter, based in Spain.
- Current role: **Security Researcher / Engineer at XBOW** — the autonomous AI bug-bounty agent. Acts as a researcher embedded in the agent loop ("human in the loop"): triages agent output, designs new solver capabilities, and authors the public writeups for findings the agent surfaces.
- Pre-XBOW career: offensive security at **Activision Blizzard King**, then continued on the **Microsoft / Xbox** gaming-security team after the acquisition. Has also done **Synack Red Team** work.
- Bug-bounty track record: part-time hunter since 2020 on HackerOne under `djurado`. 2023 recap — **Top 11 HackerOne World Leaderboard**, **Top 3 Highest Critical Reputation**, **~770 reports / ~430 criticals**, and **HackerOne Ambassador World Cup Champion 2023 with Team Spain**.

## Focus areas

- **Agent-driven bug hunting** — building and operating XBOW's coordinator + solver architecture; deciding which classes of bug the agent should learn next.
- **Hallucination control in offensive LLMs** — validation harnesses (headless browser confirmation for XSS, real-DTD exfil for XXE) so the agent only reports bugs it actually fired.
- **Classic web at scale** — XSS, XXE, SSRF, access control / IDOR, account-takeover chains. Strong on HackerOne / Bugcrowd-style web targets.
- **Account-takeover chaining** — multi-step chains that combine an API downgrade or JSONP gadget with a same-origin XSS to land ATO, rather than single-bug submissions.
- **Salesforce / AEM / enterprise SaaS quirks** — Aura component parameter abuse, AEM dispatcher bypass.

## Online presence

- HackerOne: [hackerone.com/djurado](https://hackerone.com/djurado) — primary platform profile (badges: [hackerone.com/djurado/badges](https://hackerone.com/djurado/badges)).
- Bugcrowd: [bugcrowd.com/djurado](https://bugcrowd.com/djurado/achievements).
- X / Twitter: [@djurado9](https://x.com/djurado9).
- GitHub: [github.com/0d4rujd](https://github.com/0d4rujd) (handle `djurado` on the profile header). Bio: "Ethical Hacker, Red Teamer and Bug Hunter".
- LinkedIn: [linkedin.com/in/djuradopallares](https://www.linkedin.com/in/djuradopallares).
- Employer: [xbow.com](https://xbow.com) — XBOW research blog hosts his public writeups.
- DEF CON 32 (2024) Bug Bounty Village talk: [Leveraging AI for Smarter Bug Bounties](https://media.defcon.org/DEF%20CON%2032/DEF%20CON%2032%20villages/DEF%20CON%2032%20-%20Bug%20Bounty%20Village%20-%20Diego%20Jurado%20-%20Leveraging%20AI%20for%20Smarter%20Bug%20Bounties%20-%20updated.pdf).
- Thinkst Citation speaker page: [citation.thinkst.com/speaker/95632](https://citation.thinkst.com/speaker/95632).

## Key research / posts

- **[Finding XSS in Salesforce Aura Components: How XBOW Got Creative](https://xbow.com/blog/xbow-salesforce-xss)** (2025-07-07) — XBOW discovered an XSS in Salesforce Aura by combining `aura.tag` with `aura.format=JSON`; the server keeps `text/html` despite the JSON format, and an SVG `onload` payload renders. Wiki tie-in: a Salesforce-Aura technique entry under `../techniques/xss/salesforce-aura-format-content-type-mismatch.md` when seeded.
- **[CVE-2025-49493: XXE in Akamai CloudTest](https://xbow.com/blog/xbow-akamai-cloudtest-xxe)** (2025-06-24) — Agent-discovered XXE in CloudTest SOAP endpoints; exploited via externally-hosted malicious DTD to exfiltrate `/etc/passwd`. Classic out-of-band XXE, useful as a reference shape for `../techniques/xxe/oob-dtd-exfil.md`.
- **[Stored Cross-Site Scripting (XSS) in 2FAuth](https://xbow.com/blog/xbow-2fauth-xss)** (2024-12-13) — Stored XSS in the open-source 2FAuth project; one of XBOW's early public OSS findings.
- **[LabsAI EDDI path traversal](https://xbow.com/blog/xbow-eddi-path)** (2024-12-02) — Path traversal in the EDDI conversational-AI project.
- **[Leveraging AI for Smarter Bug Bounties](https://media.defcon.org/DEF%20CON%2032/DEF%20CON%2032%20villages/DEF%20CON%2032%20-%20Bug%20Bounty%20Village%20-%20Diego%20Jurado%20-%20Leveraging%20AI%20for%20Smarter%20Bug%20Bounties%20-%20updated.pdf)** (DEF CON 32 Bug Bounty Village, 2024) — Public talk on integrating LLMs into a bounty workflow; the conceptual prelude to his XBOW work.
- **HackerOne 2023 recap on LinkedIn** — [linkedin.com/posts/djuradopallares_my-bug-bounty-2023-recap...](https://www.linkedin.com/posts/djuradopallares_my-bug-bounty-2023-recap-at-hackerone-as-activity-7147688732421259264-852M) — Self-reported 2023 stats; primary source for the "Top 11 / Top 3 critical / ~430 crits" numbers above.

## CT podcast appearances

- [2025-08-04 Ep 134 — XBOW: AI Hacking Agent and Human in the Loop with Diego Djurado](../sources/podcasts/ct/) — Walkthrough of XBOW's architecture: a **coordinator** does recon and endpoint discovery, then spawns isolated **solvers** (each a goal-conditioned AI pentester with its own attack VM, headless browser, InteractSH exfil server, payload host, and scope-enforcing network monitor). Discusses hallucination handling (validate-then-report — e.g. confirm XSS only after headless-browser execution, not on payload reflection), reported scale (15 RCEs in 3 months, 32 SQLi in 90 days), and where humans still matter (complex chains, business logic). Episode pages: [criticalthinkingpodcast.io/episode-134-xbow-ai-hacking-agent-and-human-in-the-loop-with-diego-djurado](https://www.criticalthinkingpodcast.io/episode-134-xbow-ai-hacking-agent-and-human-in-the-loop-with-diego-djurado/); HackerNotes: [blog.criticalthinkingpodcast.io/p/hackernotes-ep-134-xbow-ai-hacking-agent-and-human-in-the-loop-with-diego-jurado](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-134-xbow-ai-hacking-agent-and-human-in-the-loop-with-diego-jurado); YouTube: [youtube.com/watch?v=rvA8IbyogJ0](https://www.youtube.com/watch?v=rvA8IbyogJ0); Spotify: [open.spotify.com/episode/4UIyQgPAUFixM0cX4gfOQH](https://open.spotify.com/episode/4UIyQgPAUFixM0cX4gfOQH); CTBB announce: [x.com/ctbbpodcast/status/1952311244184285218](https://x.com/ctbbpodcast/status/1952311244184285218).

## Notes

- **Dual identity matters.** Diego is both a top-tier human hunter (H1 Top 11 / Ambassador Cup champion) **and** an XBOW engineer. When he speaks about XBOW he is not a vendor mouthpiece — the agent is judged against the bar of someone who personally knows what a 430-critical year looks like.
- **Architecture take-away worth re-using.** XBOW's coordinator/solver split (one orchestrator doing recon + endpoint enumeration, multiple solvers each with their own attack box, headless browser, exfil server, and scope monitor) maps directly onto how our TLX skill chain decomposes a target (`recon` → `js-harvest` → `js-index` → per-chain `opus-deep-audit`/`autoresearch-loop`). The "isolated attack VM per solver" pattern is a defense in our context against one agent's tooling state polluting another's evidence — relevant if we ever fan out `autoresearch-loop` in parallel.
- **Validation-before-report.** The hallucination-control rule he describes (headless browser must actually execute the XSS; XXE must actually exfil bytes) is the same rule we enforce via `browser-confirm` + `mock_confirm` before a finding moves out of `undetermined`. Cite him as external precedent when defending the cost of the dynamic-confirmation step.
- **Style** — concise, finding-led writeups on the XBOW blog; lets the chain speak rather than narrating discovery. Useful as a writeup-style reference for `report-finding`.
- **Cross-refs (when seeded)** — `../techniques/xss/salesforce-aura-format-content-type-mismatch.md`, `../techniques/xxe/oob-dtd-exfil.md`, `../tools/agents/xbow-coordinator-solver.md`, `../techniques/ato/api-downgrade-jsonp-aem-dispatcher-chain.md`.
