---
title: "Shift (disambiguation — tool, not a person)"
slug: shift
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [shiftplugin]
role: researcher
primary_focus: ai-tooling
tags: [person, disambiguation, tool/shift, focus/ai-tooling, focus/client-side]
inbound: []
---

# Shift — Disambiguation

> **This page exists because the name "Shift" is often mistaken for a CT
> podcast co-host. It is not. Shift is a tool. Joel Margolis's actual
> cohost replacement is Joseph Thacker (rez0).** See
> [rez0.md](rez0.md).

## Identity

- **What Shift actually is:** an AI-powered plugin for [Caido](../tools/caido/),
  marketed with the tagline "**Cursor of Hacking**" (analogy to Cursor,
  the AI-assisted code editor). Closed source, waitlist / paid product.
- **Builders (real people):**
  - Joseph Thacker — see [rez0.md](rez0.md)
  - Justin Gardner — see [justin-gardner.md](justin-gardner.md)
- **Common misconception:** Ep 100 of Critical Thinking (2024-12-05) was
  titled *"Farewell Joel, Hello Shift — Cursor of Hacking"*. Listeners
  who skim the title sometimes read "Hello Shift" as "we have a new
  cohost named Shift". The episode body makes clear that Shift is the
  AI tool being announced, not a person, and Joel's cohost seat is
  later filled by rez0 (announced Ep 106).

## Focus areas

- AI-assisted web hacking via Caido (LLM-driven match-and-replace,
  wordlist generation, context-aware tab naming).
- Cursor-style "Copilot for web app pentesting" UX paradigm — natural-
  language commands wrap proxy primitives.

## Online presence

- Tool site: [shiftplugin.com](https://shiftplugin.com/)
- Original launch waitlist: [shiftwaitlist.com](https://shiftwaitlist.com)
  (referenced in Ep 100 show notes)
- Tool announcement post: [Shift: AI-Powered Hacking — josephthacker.com](https://josephthacker.com/ai/2025/01/04/shift.html)
- Builder handles: [@rez0__](https://x.com/rez0__), [@rhynorater](https://x.com/rhynorater)

## Key research / posts

- **Joseph Thacker — *Shift: AI-Powered Hacking*** ([josephthacker.com/ai/2025/01/04/shift.html](https://josephthacker.com/ai/2025/01/04/shift.html))
  — Rez0's own launch writeup. Frames Shift as "a Copilot for web
  application testing" running inside Caido. Features called out:
  context-aware wordlist generation, AI-authored match-and-replace
  rules, custom memory/instructions/tab-naming logic.
- **CT Ep 100 show notes — Shift Announcement** at 01:28:20
  ([criticalthinkingpodcast.io](https://www.criticalthinkingpodcast.io/ep-100-8-fav-bugs-of-2024-farewell-joel-hello-shift-cursor-of-hacking/))
  — first public unveiling. Coincides with Joel's cohost farewell.

## CT podcast appearances

Shift (the tool) is referenced — not interviewed — across CT eps from
Ep 100 onward. It is **not a cohost**. The cohost seat after Joel was
filled by rez0 (Ep 106 announcement); gr3pme (Brandyn Murtagh) appears
recurrently from 2024-10 (Ep 91 guest) and into 2025 as a third-chair
regular.

- **2024-12-05 Ep 100 — 8 Fav Bugs of 2024, Farewell Joel, Hello Shift — Cursor of Hacking**:
  [local transcript](../sources/podcasts/ct/20241205_ANYtLQrT-F0_8_Fav_Bugs_of_2024_Farewell_Joel_Hello_Shift_-_Cursor_of_Hacking_Ep._100.en.vtt)
  — Shift's first on-air unveiling.

## Notes

- **Do not write CT episodes "with Shift as cohost".** The cohost is a
  human (rez0, sometimes gr3pme). Shift the tool is a recurring topic,
  not a seat at the table.
- **Move to `tools/` when written.** The proper home for Shift's
  practical notes (install, API surface, prompt patterns, gotchas) is
  `wiki/tools/shift/` — to be created when the user begins using the
  plugin. This `people/shift.md` page exists only to catch the naming
  confusion and route readers to the right places.
- **Cross-refs once tool page exists:**
  - `wiki/tools/shift/install.md` — Caido plugin install + auth.
  - `wiki/tools/shift/prompts.md` — useful prompts (wordlist, m&r rules).
  - Cross-link from `wiki/tools/caido/` index.
- **Provenance for this disambiguation:** Ep 100 transcript (local) +
  shiftplugin.com fetch + josephthacker.com launch post + Ep 106
  HackerNotes (cohost announcement = rez0).
