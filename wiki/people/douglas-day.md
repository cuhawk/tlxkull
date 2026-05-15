---
title: Douglas Day
slug: douglas-day
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [archangeldday, the_arch_angel, archangel, arch_angel, douglasday, dday]
role: hunter
primary_focus: collaboration
tags: [person, role/hunter, focus/collaboration, focus/authz, focus/business-logic, focus/lhe]
inbound: []
---

# Douglas Day

## Identity

- Real name: Douglas Day
- Primary handle: `ArchAngelDDay` (X) / `the_arch_angel` (HackerOne)
- Role: full-time bug bounty hunter; member of HackerOne's Hacker Advisory Board
- Background: formerly Sr Security Engineer at Elastic (and prior AppSec at New Relic); went full-time bounty 2024-07-05
- Reputation: top-grossing hacker on HackerOne; "Most Valuable Hacker" at an H1 LHE; nicknamed "The King of Collaboration" on Critical Thinking Ep. 35

## Focus areas

- Collaboration / LHE team play
- Authorization & business-logic flaws (privilege escalation, IDOR, role-mixing)
- Endpoint discovery via match-and-replace tactics
- Vendor / third-party widget abuse (Intercom widget ATO)
- Mapping methodology — disassembly then reassembly of app surface

## Online presence

- X / Twitter: [https://x.com/ArchAngelDDay](https://x.com/ArchAngelDDay)
- HackerOne (primary): [https://hackerone.com/the_arch_angel](https://hackerone.com/the_arch_angel)
- HackerOne (legacy): [https://hackerone.com/archangel](https://hackerone.com/archangel)
- Bugcrowd: [https://bugcrowd.com/arch_angel](https://bugcrowd.com/arch_angel)
- GitHub: [https://github.com/douglasday](https://github.com/douglasday)
- LinkedIn: [https://www.linkedin.com/in/douglas-day-39baa8108/](https://www.linkedin.com/in/douglas-day-39baa8108/)
- Personal blog: [https://dday.us/](https://dday.us/)

## Key research / posts

- "H1 Vendor ATO via Intercom widget" — [https://dday.us/2021/11/03/h1vendorATO.html](https://dday.us/2021/11/03/h1vendorATO.html) — abuse of an embedded Intercom support widget on a vendor surface to pivot to account takeover; canonical reference for third-party-widget attack surface.
- "Map Your Hacking" — [http://dday.us/2021/10/09/Mapyourhacking.html](http://dday.us/2021/10/09/Mapyourhacking.html) — methodology piece: explicitly map every component / role / boundary of the target before fuzzing.
- "100 Very Short Bug Bounty Rules" thread — [https://twitter.com/ArchAngelDDay/status/1661924038875435008](https://twitter.com/ArchAngelDDay/status/1661924038875435008) — terse heuristics for hunters; widely cited starter-pack.
- CVSS frustrations thread — [https://x.com/archangeldday/status/1416531839607480320](https://x.com/archangeldday/status/1416531839607480320) — both-sides-of-the-table take on triage scoring.
- SecurityWeek "Hacker Conversations" interview — [https://www.securityweek.com/hacker-conversations-professional-hacker-douglas-day/](https://www.securityweek.com/hacker-conversations-professional-hacker-douglas-day/) — his hacker-definition + disassembly/reassembly framing.
- shomik.substack interview — [https://shomik.substack.com/p/a-peek-behind-the-hacker-curtain](https://shomik.substack.com/p/a-peek-behind-the-hacker-curtain) — career arc, privilege-escalation patterns, AI/LLM-in-workflow.
- HackerOne interview video — [https://www.youtube.com/watch?v=-w43BKLz6us](https://www.youtube.com/watch?v=-w43BKLz6us)
- BugBountyExplained podcast appearance — [https://www.bugbountyexplained.com/going-full-time-bug-bounty-privilege-escalation-bugs-and-more-with-douglas-day/](https://www.bugbountyexplained.com/going-full-time-bug-bounty-privilege-escalation-bugs-and-more-with-douglas-day/)

## CT podcast appearances

- [2023-09-07 Ep 35 — Douglas Day: The King of Collaboration](../sources/podcasts/ct/20230907_Yz5i9BcnuNY_Douglas_Day_-_The_King_of_Collaboration_Ep._35.en.vtt)

## Notes

- **Collab-first methodology.** Douglas's defining edge at LHEs is aggressive partnering: he treats other top hunters not as competitors but as multipliers, splitting bounties to combine surface coverage with deep-context exploit chaining. Ep. 35 is the canonical reference for *how* he picks partners and structures the split.
- **Disassemble → reassemble.** From the SecurityWeek interview: ~99% of his hacking time is the "reassembly" stage — taking a fully-mapped system and producing workflows / data shapes its designers never intended. This is the conceptual frame behind the "Map Your Hacking" post.
- **Endpoint discovery via match-and-replace.** Burp/Caido match-and-replace rules to rewrite responses (e.g. flip permission booleans, surface hidden UI routes) — surfaces endpoints that a normal crawl will miss because they're gated client-side.
- **Vendor-widget surface.** The Intercom ATO writeup is a recurring inspiration for the "embedded third-party widget = forgotten attack surface" pattern; worth cross-referencing whenever a target embeds Intercom, Zendesk, Drift, etc.
- **Auth/authz heavy.** Privilege escalation, role mixing, MFA edge cases — his bread and butter. Less client-side / XSS than peers.
- **Voice.** Pragmatic, work-life-balance honest; "justify the hobby that doesn't generate income" was a recurring Ep. 35 thread. Treat his rules-of-thumb as heuristics, not laws.
