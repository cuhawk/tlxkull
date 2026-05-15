---
title: Eugene Lim (spaceraccoon)
slug: spaceraccoon
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [spaceraccoonsec, spaceraccoon, eugene1337]
role: dual
primary_focus: zero-day
tags: [person, role/dual, role/researcher, role/hunter, focus/zero-day, focus/iot, focus/reverse-engineering, focus/fuzzing, focus/llm-assisted, vendor/govtech-sg]
inbound: []
---

# Eugene Lim (spaceraccoon)

## Identity

- **Real name:** Eugene Lim
- **Primary handle:** `spaceraccoonsec` (also `spaceraccoon` on GitHub / HackerOne, `eugene1337` on LinkedIn)
- **Role:** Dual — Cybersecurity researcher + bug-bounty hunter + published author. Currently Lead Cybersecurity Engineer at Open Government Products (GovTech Singapore). Joined GovTech's Cybersecurity Group as a Cybersecurity Specialist (Advanced Cyber Attack Simulation) in 2020.
- **Based:** Singapore
- **Focus:** Vulnerability research methodology — code review, reverse-engineering, fuzzing, and increasingly LLM-assisted discovery. Strong IoT / embedded slant.

## Focus areas

- Zero-day discovery methodology (taught end-to-end in his book)
- IoT / embedded device reverse-engineering (TP-Link Tapo cameras, enterprise AV hardware, Crestron)
- Coverage-guided fuzzing and symbolic execution (Ghidra, Frida, angr)
- LLM-assisted vulnerability research ("negative-days" — catching patches before CVEs drop)
- Supply-chain attacks (GitHub Actions, build pipelines)
- Web app exploitation (Spring Boot, Webpack source recovery)

## Online presence

- [Blog — spaceraccoon.dev](https://spaceraccoon.dev) — canonical writeup index
- [About page](https://spaceraccoon.dev/about/) — bio, awards, links
- [X / Twitter — @spaceraccoonsec](https://twitter.com/spaceraccoonsec)
- [GitHub — @spaceraccoon](https://github.com/spaceraccoon) — 66+ repos, tooling and book code
- [LinkedIn — eugene1337](https://www.linkedin.com/in/eugene1337/)
- [HackerOne — spaceraccoon](https://hackerone.com/spaceraccoon) — ranked #2 globally at peak
- [Book site — fromdayzerotozeroday.com](https://fromdayzerotozeroday.com/)
- [Book at No Starch Press](https://nostarch.com/zero-day) — "From Day Zero to Zero Day" (2025)
- [Book code repo](https://github.com/spaceraccoon/from-day-zero-to-zero-day) — scripts + examples accompanying the book

## Key research / posts

- **[Discovering Vulnerabilities in Enterprise Audiovisual Hardware](https://spaceraccoon.dev/discovering-vulnerabilities-enterprise-audiovisual-hardware/)** (2026-05-01) — Chains an unauth API admin-credential leak (client-side auth check) into Crestron Terminal Protocol access, then root via command injection. Canonical IoT primitive-chaining example (CVE-2025-45619, CVE-2025-45620 on the PTC310UV2).
- **[Getting a Shell on the Tapo C260 Camera](https://spaceraccoon.dev/getting-shell-tapo-c260-webcam/)** (2026-03-06) — Reverse-engineered TP-Link cloud interaction to land RCE on the C260 (CVE-2026-0651/0652/0653).
- **[Reverse Engineering the Tapo C260 and Tapo Discovery Protocol v2](https://spaceraccoon.dev/reverse-engineer-tapo-c260-tdp-v2/)** (2026-01-02) — Companion piece: protocol RE that seeded the Tapo shell post above.
- **[Discovering Negative-Days with LLM Workflows](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/)** (2026-02-07) — Uses LLMs over public commit diffs to flag security patches *before* the CVE lands ("negative-days"). Productised as `vulnerability-spoiler-alert`.
- **[Ticket Tricking OpenSSL.org with Google Groups](https://spaceraccoon.dev/ticket-trick-openssl-google-groups/)** (2026-02-02) — Modern revival of the "ticket trick" technique against a high-profile target via Google Groups misconfiguration.
- **[Remote Code Execution in Three Acts: Chaining Exposed Actuators and H2 Database Aliases in Spring Boot 2](https://spaceraccoon.dev/remote-code-execution-in-three-acts-chaining-exposed-actuators-and-h2-database/)** (2020) — Foundational Spring Boot actuator + H2 alias RCE writeup; the de-facto reference for this chain.
- **[The InfoSecurity Challenge 2021 Full Writeup](https://spaceraccoon.dev/the-infosecurity-challenge-2021-full-writeup-battle-royale-for-30k/)** (2021) — CTF / live event writeup ($30k prize pool).
- **[vulnerability-spoiler-alert](https://github.com/spaceraccoon/vulnerability-spoiler-alert)** — AI-driven monitor of OSS commits that flags silent security patches; ships findings with an RSS feed.
- **[webpack-exploder](https://github.com/spaceraccoon/webpack-exploder)** — Recover original source from Webpacked React apps using sourcemaps. Useful upstream-of any JS taint pipeline (see `../tools/tlx/` source-recovery notes).
- **[manuka](https://github.com/spaceraccoon/manuka)** — Modular OSINT honeypot for blue teamers.
- **[spring-boot-actuator-h2-rce](https://github.com/spaceraccoon/spring-boot-actuator-h2-rce)** — Reference vulnerable app accompanying the Spring Boot RCE writeup.
- **["You Have One New Appwntment" — DEF CON talk](https://forum.defcon.org/node/241931)** — Hacking proprietary iCalendar properties; desktop / mail-client surface.

## CT podcast appearances

- [2025-05-01 Ep 120 — SpaceRaccoon - From Day Zero to Zero Day](../sources/podcasts/ct/20250501_7ppNXESTu6I_SpaceRaccoon_-_From_Day_Zero_to_Zero_Day_Ep.120.en.vtt)

## Notes

- **Book author.** "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" (No Starch Press, 2025, ISBN 9781718503946). Teaches the full vuln-research pipeline: target selection across codebases / protocols / file formats, taint analysis, binary RE with Ghidra+Frida+angr, coverage-guided fuzzing, symbolic execution, PoC construction. Companion repo on GitHub. Primary reason this dossier is `role: dual` — output is split roughly evenly between original research and pedagogy.
- **Methodology focus.** Posts are deliberately structured as *reusable workflows*, not one-off war stories. Reads more like teaching material than a brag list — fits the persona of an author who codified his own process.
- **GovTech engineer.** Day-job is offensive red-team simulation at GovTech Singapore / Open Government Products. Has a public preference for white-hat work — was the top hacker in the Singapore Government Bug Bounty Programme before joining the team that runs it.
- **Awards.** H1-213 Most Valuable Hacker (2019, with USAF/UK MoD/Verizon Media). H1-Elite Hall of Fame (2021, 1 of 5 picked from ~1M HackerOne users). Peak HackerOne global rank #2.
- **Recurring theme: chains.** "Individual vulnerabilities often chain well together — a low-severity file read primitive helps understand context to find a code execution path." This framing pervades both the IoT writeups (Tapo, Crestron) and the book's methodology chapters — useful prior when triaging long taint chains in `targets/<name>/chains/`.
- **LLM-assisted research direction.** `vulnerability-spoiler-alert` + the negative-days post mark his recent pivot toward AI-augmented vuln discovery; relevant to TLX's own `js_run_audit` + autoresearch-loop patterns.
- **No public Tencent / Alibaba writeups confirmed** as of this dossier — searches for that combination returned threat-actor infra rather than spaceraccoon's own research. Removed from this page; revisit if a future source surfaces one.
