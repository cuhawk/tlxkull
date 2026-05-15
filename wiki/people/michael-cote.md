---
title: Michael Cote
slug: michael-cote
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [michaelpatrickcote]
role: vendor-eng
primary_focus: vrp-triage
tags: [person, role/vendor-eng, focus/vrp-triage, focus/cloud-security, focus/google-cloud]
inbound: []
---

# Michael Cote

## Identity

- **Real name:** Michael Cote (Michael Patrick Coté).
- **Role:** Cloud VRP Lead at Google. Runs Google Cloud's Vulnerability
  Rewards Program — panel decisions, reward framework, triage and
  reproduction workflow for cloud-tier reports.

## Focus areas

- Google Cloud VRP triage and panel adjudication.
- Reward-framework design (transparency, downgrade criteria, exceptional
  bonuses).
- Cloud-security report intake; cross-tenant / IAM / GCP product surface.

## Online presence

- [LinkedIn — michaelpatrickcote](https://www.linkedin.com/in/michaelpatrickcote/)
- [Google Bug Hunters program](https://bughunters.google.com/)

## Key research / posts

- [Google Cloud VRP: Enhancing Transparency and Impact in Our Rewards Program](https://bughunters.google.com/blog/google-cloud-vrp-enhancing-transparency-and-impact-in-our-rewards-program)
  — Co-authored with Sri Tulasiram (Head of Cloud Security Response).
  Announced the revised Cloud VRP framework after ~1,600 reports
  processed in the program's first year: clearer "exceptional"
  criteria for server-side bugs, more achievable bonus tiers, goal of
  speeding up triage / reproduction.
- [Google Cloud launches new Vulnerability Rewards Program](https://cloud.google.com/blog/products/identity-security/google-cloud-launches-new-vulnerability-rewards-program)
  — Co-authored launch post for the dedicated Cloud VRP (split from
  the general Google VRP).
- [VRP 2025 Year in Review (Google Security Blog)](https://blog.google/security/vrp-2025-year-in-review/)
  — Acknowledged contributor; Cloud VRP cohort summary for 2025.

## CT podcast appearances

- [2026-01-29 Ep 159 — Tips for crushing it on Google Cloud VRP With Michael Cote and Darby Hopkins](../sources/podcasts/ct/20260129_7u6xpVhEpBA_Tips_for_crushing_it_on_Google_Cloud_VRP_With_Michael_Cote_and_Darby_Hopkins_Ep._159.en.vtt)
  — Co-guest with Darby Hopkins. Walks through Cloud VRP scope,
  reward-panel logic, why reports get downgraded, what makes a report
  "exceptional", and concrete tips for hunters targeting Google Cloud
  surface ([Spotify](https://open.spotify.com/episode/2nMcihIKPSn7as5Fs0HzAX),
  [YouTube](https://www.youtube.com/watch?v=7u6xpVhEpBA)).

## Notes

- **Vendor-side, not a hunter.** Cote runs the panel, he doesn't
  submit. Useful as a primary source on what Google Cloud VRP actually
  pays for vs. discounts. When in doubt about whether a finding clears
  the bar, his public framing in the transparency blog + Ep 159 is the
  authoritative reference.
- **Cloud VRP is its own program.** Separate scope, separate panel,
  separate reward table from the general Google/Alphabet VRP. Submit
  cloud-product bugs (GCP services, cross-tenant, IAM, multi-tenant
  isolation) through the Cloud VRP path; don't conflate with main VRP.
- **Triage signal-to-noise.** Ep 159 theme is "avoid the downgrade":
  the panel rewards clearly demonstrated cross-tenant impact, sound
  reproduction steps, and severity backed by actual blast radius — not
  theoretical severity from a CVSS calculator. Bonus tier requires
  novelty + impact, not just impact.
- **BugSWAT participation.** Has attended Google's invite-only BugSWAT
  events (Mexico City cohort) where top researchers hunt GCP
  surface in person; useful context that Cote is on the inside of
  those triage rooms.
