---
title: Jason Haddix (jhaddix)
slug: jason-haddix
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [jhaddix]
role: dual
primary_focus: recon
tags: [person, role/researcher, role/vendor-eng, focus/recon, focus/methodology, focus/ai-redteam, focus/training, vendor/arcanum, vendor/bugcrowd-alum]
inbound: []
---

# Jason Haddix (jhaddix)

## Identity

- **Real name:** Jason Haddix
- **Primary handle:** `Jhaddix`
- **Role:** Founder / CEO / Lead Instructor, Arcanum Information Security. Also a working hunter (currently around #59 on the Bugcrowd global leaderboard, was #1 in 2014, top-10 in 2013).
- **Career arc:** Lead Pentester at Redspin → Director of Penetration Testing at HP (2011-2015) → Director of Technical Operations, then Head of Trust & Security, then VP of Trust & Security at Bugcrowd (2015-2018) → Head of Security / CISO at Ubisoft → CISO at BuddoBot → Founder/CEO of Arcanum.
- **Public-facing posture:** Community figure first, vendor exec second. One of the small handful of names that defined the modern bug-bounty hunter playbook.

## Focus areas

- Reconnaissance methodology (subdomain enumeration, content discovery, asset attribution at scale)
- Bug-bounty methodology as a teachable, repeatable process (TBHM)
- Red-team operations and adversary emulation
- AI red-teaming — attacking LLMs, prompt-injection taxonomy, agentic-system pentesting
- Hacker training and career building

## Online presence

- [Personal site — jhaddix.com](https://www.jhaddix.com) — short bio, blog, contact
- [Arcanum Information Security — arcanum-sec.com](https://www.arcanum-sec.com) — his current company; trainings + consulting
- [X / Twitter — @Jhaddix](https://x.com/Jhaddix) — primary social channel
- [LinkedIn — Jason Haddix](https://www.linkedin.com/in/jhaddix) — career history
- [GitHub — @jhaddix](https://github.com/jhaddix) — TBHM + wordlists + gists
- [YouTube — /c/jhaddix](https://www.youtube.com/c/jhaddix) — talks, recon walkthroughs, AMAs
- [Bugcrowd blog author page](https://www.bugcrowd.com/blog/author/jhaddixbugcrowd-com/) — legacy posts from his VP era
- [Executive Offense newsletter (Beehiiv)](https://executiveoffense.beehiiv.com) — Arcanum AI security resource hub
- [Arcanum Discord](https://www.arcanum-sec.com) — community for course members (linked from arcanum-sec.com)

## Key research / posts

- **[The Bug Hunter's Methodology (tbhm)](https://github.com/jhaddix/tbhm)** — 4.3k stars. The canonical end-to-end methodology repo: recon → mapping → app analysis (XSS / SQLi / auth / authz / file upload / CSRF / privesc / mobile). Has shipped in multiple major versions (v1 through v4); v4 is the recon-focused edition. Cross-link: `../techniques/recon/`.
- **[The Bug Hunter's Methodology v4.0 — Recon Edition (NahamCon 2020)](https://www.youtube.com/watch?v=p4JgIu1mceI)** — Talk that re-defined modern recon: scoping → seed-set → enumeration → attribution → port/service → screenshot/visual review → content discovery. Covers 30+ tools and is the most-cited recon talk in bounty circles. Seeded `../techniques/recon/dns-wildcard-profile.md` and informs the wordlist-driven approach in `../techniques/recon/dns-ents-zone-walk.md`.
- **[DEF CON Red Team Village — The Bug Hunters Methodology](https://www.youtube.com/watch?v=qPlpN4BVnRY)** (2020) — DEF CON Safe Mode edition of the methodology; same content, different audience framing.
- **[Recon Like an Adversary (IWCON 2023)](https://www.youtube.com/watch?v=nGs8pWIj5k4)** — Adversary-framed update to TBHM recon. Heavier emphasis on threat-intel feeds, leaked-credential corpora, and unconventional sources (residential-proxy intel, BGP, CT logs). Seeded `../techniques/recon/threat-intel-creds-residential.md`.
- **[all.txt — every DNS enumeration wordlist, merged](https://gist.github.com/jhaddix/86a06c5dc309d08580a018c66354a056)** — The de-facto subdomain bruteforce wordlist. Roughly 25MB of merged sources. Every modern subdomain enum tool ships with this or a derivative.
- **[content_discovery_all.txt — content discovery masterlist](https://gist.github.com/jhaddix/b80ea67d85c13206125806f0828f4d10)** — Companion to all.txt for path/file enum; the canonical seed list for `gobuster`, `feroxbuster`, `ffuf`. Underpins `../techniques/recon/saas-preauth-config-enum.md`.
- **[Cloud Metadata Dictionary (SSRF)](https://gist.github.com/jhaddix)** — IMDS / metadata-service endpoint list for AWS / GCP / Azure / Aliyun / DO. Standard SSRF allowlist for any pentest.
- **[Attacking AI — Arcanum training](https://www.arcanum-sec.com/training/attacking-ai)** — Multi-day live course. Releases Arcanum's prompt-injection taxonomy + Jason's 7-point AI-system pentesting methodology. Built on real 2024-2025 client engagements.
- **[Attacking AI v1.1 (Antisyphon Anti-Cast)](https://www.youtube.com/watch?v=0MDfKTJQQyE)** — Free public excerpt of the Attacking AI course material. Watch this before paying for the full course to gauge fit.
- **[Arcanum Prompt Injection Taxonomy](https://www.arcanum-sec.com)** — Public artifact released alongside the AI training. Categorizes prompt-injection primitives by trust boundary, payload form, and delivery vector.
- **[Hackbots (Using Agent Frameworks) — Arcanum training](https://www.arcanum-sec.com/training-overview)** — Course on building autonomous bug-hunting agents on top of LLM frameworks. Direct conceptual ancestor of TLX's autoresearch loop.
- **[Red Blue Purple AI — Arcanum training](https://www.arcanum-sec.com/training-overview)** — Defender-side counterpart: AI tactics for red, blue, and purple team workflows. The "Defenders' Toolkit / red+blue" framing.
- **[Bug Bounty Hunter's Methodology — Application Analysis v1 (YouTube)](https://www.youtube.com/watch?v=fvQ8RWoK_Z0)** — Older but still-referenced application-analysis half of TBHM (pre-recon-only split).
- **[SecLists fork](https://github.com/jhaddix/SecLists)** — His pinned fork of Daniel Miessler's `SecLists`, periodically synced with his own wordlist additions.

## CT podcast appearances

- [2023-03-23 Ep 12 — Jason Haddix: From Hacker to CISO](../sources/podcasts/ct/20230323_OYlL67pj7Ek_Jason_Haddix_-_From_Hacker_to_CISO_Ep._12.en.vtt)
- [2024-03-21 Ep 63 — JHaddix Returns](../sources/podcasts/ct/20240321_5NBlyzV0Wbc_JHaddix_Returns_Ep._63.en.vtt)
- [2024-12-19 Ep 102 — Building Web Hacking Micro Agents with Jason Haddix](../sources/podcasts/ct/20241219_3y8dyeKmJQI_Building_Web_Hacking_Micro_Agents_with_Jason_Haddix_Ep._102.en.vtt)

## Notes

- **Community role first.** Jason's outsized influence is not from any single high-impact CVE; it is from packaging the hunter workflow into a teachable, repeatable form and giving it away. TBHM and `all.txt` are foundational artifacts of the modern bounty scene — most hunters under 30 in this industry learned recon from him whether they realize it or not.
- **Recon evangelism.** Pre-TBHM, recon was tribal knowledge. Post-TBHM, recon is a checklist. He treats the seed-set → enumeration → attribution → content-discovery pipeline as the leverage point: if you out-recon the next hunter, you find bugs they cannot. This wiki's `../techniques/recon/` tree is downstream of his framing.
- **Wordlist legacy.** `all.txt` and `content_discovery_all.txt` are the kind of artifact that's still being used in pipelines a decade after publication. Compare with PortSwigger's permanence in tooling — Jason's permanence is in wordlists.
- **Career-to-training pivot.** The Bugcrowd → Ubisoft → BuddoBot → Arcanum arc tracks the same pivot many top hunters make: from individual reward-driven hunting, through corporate security leadership, into independent training/consulting. Arcanum is the destination of that pivot: high-margin live training plus boutique consulting, with the social capital from the hunter-celebrity years driving lead-gen.
- **AI red-team second act.** Post-2023 he has been re-tooling the entire methodology for AI systems. The Attacking AI course, prompt-injection taxonomy, and Hackbots agent-framework training are a consistent thesis: the bug-bounty playbook applies to LLM and agentic systems, with a re-mapped sink/source/trust-boundary model. CT Ep 102 on micro-agents is the clearest articulation of how he views autonomous hunters in 2024-2025.
- **Style.** Generous with takes, dense with tool name-drops, weak on novel primitives. Reading him gets you the breadth of "what every hunter is doing right now"; reading James Kettle gets you the depth of "what one researcher invented this year". Both are necessary.
- **Don't confuse the man with the methodology.** TBHM is now a community artifact with many contributors; Jason curates rather than authors most recent updates. The Arcanum-hosted on-demand version (`arcanum-sec.com/training/the-bug-hunters-methodology`) is the paid edition with current videos.
