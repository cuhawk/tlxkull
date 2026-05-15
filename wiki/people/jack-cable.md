---
title: Jack Cable
slug: jack-cable
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [jackhcable, cablej]
role: dual
primary_focus: ai-security
tags: [person, role/researcher, role/vendor-eng, focus/ai-security, focus/policy, focus/secure-by-design, focus/vdp, focus/electron, focus/responsible-disclosure]
inbound: []
---

## Identity

- **Real name:** Jack Cable (b. 2000-02-18).
- **Primary handle:** `jackhcable` (X/Twitter), `cablej` (GitHub).
- **Role:** CEO & co-founder of [Corridor](https://www.conviction.com/launches/corridor.html) — an "AI security architect" startup. Previously Senior Technical Advisor at CISA (Secure by Design + open-source software security), Election Security Technical Advisor at CISA, TechCongress Fellow (Senate HSGAC), and Security Architect at Krebs Stamos Group.
- **Track record:** 350+ vulnerabilities across Google, Facebook, Uber, Yahoo, DoD. 1st place in DoD's Hack the Air Force (2017, age 17). Top-100 all-time on HackerOne. Time Magazine 25 Most Influential Teens (2018). Helped stand up Stanford's bug bounty (2019, one of the first in higher ed).

## Focus areas

- AI application security — model-assisted codegen failure modes, prod-sec for AI startups
- Secure-by-design / shifting-left at the manufacturer level (policy + practice)
- Vulnerability disclosure law — CFAA / DMCA boundaries, VDP advocacy, safe-harbor design
- Electron / desktop-app security (Cluely case study)
- Open-source software security and supply-chain policy

## Online presence

- Blog: [cablej.io](http://cablej.io/) (TLS cert mismatch on `https://` as of 2026-05; the HTTP host is canonical)
- X / Twitter: [@jackhcable](https://x.com/jackhcable)
- GitHub: [github.com/cablej](https://github.com/cablej)
- LinkedIn: [in/jackcable](https://www.linkedin.com/in/jackcable/)
- Company: [Corridor](https://www.conviction.com/launches/corridor.html) — co-founded with Ashwin; Alex Stamos as CSO; early customers Cursor, Mercury, GreyNoise.
- CISA speaker page: [cisa.gov/speaker/jack-cable](https://www.cisa.gov/speaker/jack-cable)
- IST profile: [securityandtechnology.org/person/jack-cable/](https://securityandtechnology.org/person/jack-cable/)
- Wikipedia: [Jack Cable (software developer)](https://en.wikipedia.org/wiki/Jack_Cable_(software_developer))

## Key research / posts

- **Hacking Cluely — Electron app teardown** ([thread](https://x.com/jackhcable/status/1942636823525679182)) — unzipped the Cluely Electron app, found both standard and enterprise system prompts in plaintext, then chained no-sandbox + over-permissive `postMessage` exposure into a continuous screen-capture PoC. Cluely responded with a DMCA takedown filed by an employee (CEO publicly denied filing). Canonical 2025 example of "AI startup ships AI prod-sec mistakes" + "vendor weaponises copyright law against researchers".
- **The Year of the Vulnerability Disclosure Policy** ([talk, YouTube](https://www.youtube.com/watch?v=_SJ8Am0jvS0)) — argument that VDPs are the load-bearing legal primitive making web bug-bounty research possible under CFAA. Foundation for the "How To Not Get Sued" framing on CT Ep 136.
- **CISA Secure by Design Pledge** ([CyberScoop exit interview](https://cyberscoop.com/jack-cable-cisa-secure-by-design-exit-interview/), [The Record](https://therecord.media/cisa-jack-cable-interview-secure-by-design-pledge-update)) — led CISA's voluntary pledge; 250+ manufacturers including Google, Microsoft, AWS signed. No enforcement, peer-pressure-driven. Cable's argument: Salt Typhoon / Volt Typhoon prove the cost of decades-old preventable edge-device bugs.
- **Ransomwhere** ([github.com/cablej/ransomwhere](https://github.com/cablej/ransomwhere), [ransomwhe.re](https://ransomwhe.re/)) — first open, crowdsourced ransomware-payment tracker. Originated work that surfaced a payment-system workaround saving victims ~$27k (acknowledged by DHS Sec. Mayorkas).
- **Crossfeed** ([github.com/cisagov/crossfeed](https://github.com/cisagov/crossfeed)) — CISA's first passive, opt-out vuln-scanning program; scanned all 50 states + 2,500 counties before 2020 election. Built while Election Security Technical Advisor.
- **DIODB — Disclose.io database** ([github.com/disclose/diodb](https://github.com/disclose/diodb)) — open registry of org VDP / bounty policies (1.1k stars). The reference dataset behind "does this target have safe-harbor".
- **FileChangeMonitor** ([github.com/cablej/FileChangeMonitor](https://github.com/cablej/FileChangeMonitor)) — continuous JS-file change monitor; the prototype of the "diff their bundles, find their bugs" recon pattern.
- **Stratosphere** ([github.com/stanford-esrg/stratosphere](https://github.com/stanford-esrg/stratosphere)) — password-generation-style enumeration of publicly accessible cloud storage buckets. Stanford ESRG.
- **hack-your-government** ([github.com/cablej/hack-your-government](https://github.com/cablej/hack-your-government)) — curated registry of governments running VDPs. Policy-meets-research.
- **Written testimony to House Homeland Security Committee, May 2025** ([PDF](https://www.congress.gov/119/meeting/house/118140/witnesses/HHRG-119-HM00-Wstate-CableJ-20250528.pdf)) — as Corridor CEO; case for secure-by-design as national-security lever.

## CT podcast appearances

- [2025-08-21 Ep 136 — Hacking Cluely, AI Prod Sec, and How To Not Get Sued with Jack Cable](../sources/podcasts/ct/20250821_xi087VDy9G8_Hacking_Cluely_AI_Prod_Sec_and_How_To_Not_Get_Sued_with_Jack_Cable_Ep._136.en.vtt) — Cluely Electron teardown; AI-model codegen introduces vulns "20-30% of the time"; CFAA vs DMCA research-exemption boundary; VDP / safe-harbor advocacy. Companion HackerNotes recap: [blog.criticalthinkingpodcast.io/.../ep-136](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-136-hacking-cluely-ai-prod-sec-and-how-to-not-get-sued-with-jack-cable).

## Notes

- **Policy/research crossover.** Rare profile: a top-100 H1 hunter who also spent 3+ years inside CISA shaping federal vuln-disclosure and secure-by-design policy. Most of his published work sits at the seam — the bugs are arguments for the policy, the policy is scaffolding for more bugs to be found legally.
- **The "How To Not Get Sued" frame.** His standing recommendation to bounty hunters: local/desktop testing is mostly fine (DMCA security-research exemption); web testing without an explicit VDP or program scope is CFAA-exposed regardless of intent. When in doubt, check `disclose.io` (DIODB) first. Cluely DMCA episode is his lived case study for "even good-faith disclosure can attract retaliation; reduce blast radius preemptively."
- **AI prod-sec thesis (Corridor).** Models introduce a predictable class of bad-architecture decisions when generating code — e.g. "make the whole table public to fix an access bug" rather than wiring proper authz. Corridor's pitch is to enforce security properties *structurally during codegen* (Cursor, Mercury, GreyNoise as design-partner customers) rather than catch it in scans after the fact. Co-founder Ashwin (open-source maintainer / Georgetown Law) + CSO Alex Stamos (ex-Yahoo/Facebook/SentinelOne).
- **Electron-app review.** His Cluely teardown is the cleanest 2025 walkthrough of how to assess an Electron AI app: check `sandbox: true`, audit `contextIsolation`, enumerate `postMessage` handlers reachable from newly-opened windows, grep the unpacked ASAR for system prompts and API keys. Re-usable checklist for any Electron-shipped AI product.
- **DMCA-as-suppression pattern.** The Cluely takedown of his system-prompt screenshot — vendor claiming "proprietary source code" over content shipped to every installing user — is a teachable example. Cite it when arguing for stronger VDP safe-harbor language.
- **Collab graph.** Alex Stamos (Corridor CSO; ex-Krebs Stamos colleague), Chris Krebs (Krebs Stamos Group), Sen. Gary Peters' staff (TechCongress), Allan Friedman (CISA SBOM), Justin Gardner (CT host, Ep 136).
- **When to invoke this dossier:** any Electron / desktop AI-app target; any time a vendor threatens legal action over a disclosure; questions about VDP / safe-harbor / CFAA scope; AI codegen failure modes; secure-by-design policy framing in writeups.
