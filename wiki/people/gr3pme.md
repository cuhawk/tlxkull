---
title: Gr3pme (Brandyn Murtagh)
slug: gr3pme
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [gr3pme, blmsec]
role: dual
primary_focus: ai-assisted
tags: [person, role/dual, role/host, role/hunter, focus/ai-assisted, focus/threat-modeling, focus/note-taking, focus/client-side]
inbound: []
---

## Identity

- **Real name:** Brandyn Murtagh.
- **Primary handle:** `gr3pme` (X/Twitter, HackerOne, GitHub primary). Secondary GitHub: `blmsec`.
- **Role:** Dual — full-time bug-bounty hunter and Critical Thinking podcast co-host (announced Ep 143, 2025-10-09). Joined the show after a year as a recurring guest and CT mentee graduate.
- **Track record:** Went from first paid bug to a HackerOne Live Hacking Event invite in ~9 months while still working part-time (Ep 91, 2024-10). Holds OSWE / OSCP / CRT. Went full-time in 2025; CT cohost slot followed within a year.

## Focus areas

- AI-assisted bug-bounty methodology — LLM-in-the-loop for recon, code review, hypothesis generation
- AI red-teaming — prompt-injection payloads, LLM router attacks, AI-coding-agent vuln-finding eval
- Threat modeling as primary discovery method (over class-specific hunting)
- Note-taking / target-mapping discipline (Notion-based; templated)
- Client-side gadgets and OAuth/redirect chains (per Ep 91 findings)

## Online presence

- X / Twitter: [@gr3pme](https://x.com/gr3pme)
- HackerOne: [hackerone.com/gr3pme](https://hackerone.com/gr3pme)
- HackerOne hacktivity: [hackerone.com/gr3pme/hacktivity](https://hackerone.com/gr3pme/hacktivity?type=user)
- GitHub (primary): [github.com/gr3pme](https://github.com/gr3pme)
- GitHub (secondary): [github.com/blmsec](https://github.com/blmsec)
- CT cohost feed: [criticalthinkingpodcast.io](https://www.criticalthinkingpodcast.io/)
- CT author page (HackerNotes): [blog.criticalthinkingpodcast.io](https://blog.criticalthinkingpodcast.io/)

## Key research / posts

- **AI_Prompts_payloads** ([github.com/gr3pme/AI_Prompts_payloads](https://github.com/gr3pme/AI_Prompts_payloads)) — payloads collection for AI red-teaming. Working-set rather than polished release; mirrors what he uses in live LLM-feature testing.
- **effectivePrompts** ([github.com/gr3pme/effectivePrompts](https://github.com/gr3pme/effectivePrompts)) — curated prompts he uses to drive AI-assisted code review and bug-hunting hypotheses.
- **Threat-modeling-first methodology** ([x.com/gr3pme/status/1844071496643379514](https://x.com/gr3pme/status/1844071496643379514)) — public thread sketching his approach: map all functionality, brainstorm attack vectors per surface, then hunt — rather than grepping for a single class.
- **Note-taking template** (Ep 145 HackerNotes; template shared via CT) — see [Ep 145 page](https://www.criticalthinkingpodcast.io/episode-145-gr3pmes-secret-bug-bounty-note-taking-methodology/). Notion-based dossier per target: tech stack, brainstorming/risk, high-signal greps, error oracles, attack paths & gadgets.
- **PROMISQROUTE / CVE-Genie / WebSocket Turbo Intruder discussion** ([HackerNotes Ep 142](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-142-gr3pme-s-full-time-hunting-journey-update-insane-ai-research-and-some-light-news)) — covered model-router prompt-injection, automated CVE-to-PoC frameworks, and the Meta Messenger $111k path-traversal-to-DLL-hijack chain. Sets his "insane AI research" framing.

## CT podcast appearances

- [2024-10-03 Ep 91 — Zero to LHE in 9 Months (feat gr3pme)](../sources/podcasts/ct/20241003_5WIRyMA0FfM_Zero_to_LHE_in_9_Months_feat_gr3pme_Ep._91.en.vtt)
- [2025-10-02 Ep 142 — Gr3pme's Full-Time Hunting Journey Update, Insane AI Research, And Some Light News](../sources/podcasts/ct/20251002_l6O_ez2CTOo_Gr3pme_s_Full-Time_Hunting_Journey_Update_Insane_AI_Research_And_Some_Light_News_Ep._142.en.vtt)
- [2025-10-09 Ep 143 — New Cohost + Client-Side Gadgets LHE / Meta Instant Global Admin in Entra](../sources/podcasts/ct/20251009_XbP0qP03ZRM_New_Cohost_+_Client-Side_Gadgets_LHE_Meta_Instant_Global_Admin_in_Entra_Ep._143.en.vtt) — *announced as cohost*.
- [2025-10-23 Ep 145 — Gr3pme's Secret: Bug Bounty Note Taking Methodology](../sources/podcasts/ct/20251023_rbDdiM1L2Bo_Gr3pme_s_Secret_-_Bug_Bounty_Note_Taking_Methodology_Ep._145.en.vtt)

## Notes

- **Mentee-to-cohost arc.** Gr3pme is the canonical CT mentee success story: appeared on Ep 91 as the "Zero to LHE in 9 Months" case study, returned as recurring AI-research guest through 2025, made cohost at Ep 143. Joel Margolis ([joel-margolis.md](./joel-margolis.md)) left late 2024, Shift ([shift.md](./shift.md)) joined Ep 100, gr3pme rounds out the post-teknogeek trio with Justin Gardner ([justin-gardner.md](./justin-gardner.md)) and Rez0 ([rez0.md](./rez0.md)).
- **Signature 1 — AI-assisted, not AI-native.** Unlike Rez0 whose subspecialty is *hacking* AI features, gr3pme's signature is *using* AI to hunt classical bugs faster: LLMs for code review, hypothesis generation, prompt-payload libraries, prompt templates. The AI_Prompts_payloads + effectivePrompts repos are the public artifacts. Distinguishes him from AI-security researchers proper.
- **Signature 2 — Obsessive note-taking.** Ep 145 is built around his Notion template. Treats notes as a *living target dossier*, not a writeup. Sections: tech stack, threat-model brainstorm, high-signal greps, "error oracle" endpoints (info leaks not immediately useful but logged), attack paths & gadgets. The combination of threat-modeling + persistent note-store is what lets him return to a target across sessions and chain partial gadgets into full bugs.
- **Target-selection style.** Hunts services he personally uses (familiarity → faster feature mapping), products tied to recent purchases (he has legitimate credentials), and regionally-specific services (smaller competitor pool). Not a recon-volume hunter; deep-target by design.
- **Findings flavor.** Ep 91 examples: stored XSS via emoji-character injection bypassing payment-field length limits → ATO; 0-interaction ATO via "oracle endpoint" leaking invitation tokens; OAuth `response_type`-confusion driving `redirect_uri` SSRF chain. Pattern: information-leak + state-dependent endpoint → ATO. Maps to wiki techniques in `oauth/` and `client-side/` (link when those pages land).
- **Tools used.** Notion (notes), Caido (proxy + replay — standard CT toolchain), Claude / LLMs (code review + hypothesis), grep (per handle). No public custom tooling stack beyond the two AI prompt repos; the methodology *is* the tooling.
- **When to invoke this dossier.** Reach for gr3pme's note-taking template before starting a new target dossier in `targets/<name>/`. Reach for his prompt-payload repo when designing LLM-feature recon. Treat his CT appearances as the canonical "how a part-timer becomes a full-timer" reference for budget/time-allocation questions.
