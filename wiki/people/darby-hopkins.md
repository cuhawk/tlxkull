---
title: Darby Hopkins
slug: darby-hopkins
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [darbyhopkins]
role: vendor-eng
primary_focus: vrp-triage
tags: [person, role/vendor-eng, focus/vrp-triage, focus/gcp, focus/program-policy, vendor/google]
inbound: []
---

## Identity

- **Real name:** Darby Hopkins.
- **Primary handle:** `darbyhopkins` (LinkedIn). No known public X/Twitter or GitHub presence as of 2026-05.
- **Role:** Technical Program Manager (TPM), Google Cloud Vulnerability Reward Program. Based in the Vienna, VA area. Works alongside Michael Cote (engineering side) on the Cloud panel that triages and rewards GCP-scoped reports.
- **Track record:** Vendor-side, not a hunter. Public footprint is panel/program work — policy rewrites, rewards-table maintenance, researcher communications. Co-presented the September 2025 Cloud VRP rewards-table rework on CT Ep 159.

## Focus areas

- Cloud VRP triage and panel process (Cloud panel cadence, unanimous-consensus rule, panel shopping)
- Rewards-table policy — severity buckets (S0/S1/S2, C0/C1) and product tiering (T1/T2/T3A/T3B)
- Report-quality rubric — the 1.2x bonus criteria and downgrade reasons
- Researcher experience / program comms (BugSWAT, blog posts, podcast appearances)

## Online presence

- LinkedIn: [in/darbyhopkins](https://www.linkedin.com/in/darbyhopkins/)
- Program account (team, not personal): [@GoogleVRP](https://x.com/googlevrp)
- Cloud VRP rules: [bughunters.google.com — Cloud VRP rules](https://bughunters.google.com/about/rules/google-friends/cloud-vulnerability-reward-program-rules)
- Cloud VRP launch post (program context): [Google Cloud Blog — Google Cloud launches new VRP](https://cloud.google.com/blog/products/identity-security/google-cloud-launches-new-vulnerability-rewards-program)

## Key research / posts

- **CT Ep 159 — Tips for crushing it on Google Cloud VRP** ([YouTube](https://www.youtube.com/watch?v=7u6xpVhEpBA), [Spotify](https://open.spotify.com/episode/2nMcihIKPSn7as5Fs0HzAX), [RSS.com](https://rss.com/podcasts/ctbbpodcast/2496509/)) — walkthrough of the September 2025 rewards-table rework with Michael Cote. Severity buckets keyed off attacker starting privilege, panel cadence (~15 reports/session, ~4 min each, unanimous consensus), and the "panel shopping" pattern where a Cloud-table mismatch gets routed to Abuse/OSS/VRP panels solely to maximize researcher payout. No exploit content — pure program meta.
- **HackerNotes Ep 159 — Maximizing Bounties on Google Cloud VRP** ([blog.criticalthinkingpodcast.io](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-159-maximizing-bounties-on-google-cloud-vrp)) — text recap of the same episode. Surfaces the privilege-escalation delta framing, the 1.2x quality multiplier vs 0.8x downgrade, and "service account impersonation is a consistent high-value attack pattern."

## CT podcast appearances

- [2026-01-29 Ep 159 — Tips for crushing it on Google Cloud VRP](../sources/podcasts/ct/20260129_7u6xpVhEpBA_Tips_for_crushing_it_on_Google_Cloud_VRP_With_Michael_Cote_and_Darby_Hopkins_Ep._159.en.vtt) — with Michael Cote.

## Notes

- **When to invoke this dossier:** any GCP-scoped report drafting; deciding whether to file under Cloud vs. Abuse/OSS/VRP; estimating expected reward from a privilege-escalation chain; understanding why a Cloud report got downgraded.
- **Downgrade levers she called out (Ep 159).** Uncommon starting permissions, user interaction beyond normal product use, limited customer-population blast radius, non-standard configuration. Write the report to defuse each one explicitly.
- **Quality bonus is real.** 1.2x multiplier for exceptional reports across a six-dimension rubric (clarity of effect, clear impact, attack preconditions, etc.). Worth optimizing the writeup — the multiplier compounds on top of base reward, not after caps.
- **Service-account chains.** Per the HackerNotes recap, map the *full* chain (start perms → end perms → data reachable). Partial discoveries can be re-rewarded retroactively once the full path lands, but only if the original report cleanly identifies it as a chain step.
- **Panel mechanics.** Two weekly panels, ~15 bugs / 60 min, unanimous consensus required. Complex cases get deferred — vague reports get deferred (or downgraded) rather than discussed deeply. Front-load the impact paragraph.
- **Vendor contact, not adversary.** TPM role means she is the policy/comms face of the Cloud panel rather than an engineer reviewing PoCs. Communications-channel changes (BugSWAT invites, panel turnaround comms) likely route through her.
- **Collab graph.** Michael Cote (Google Cloud VRP engineering counterpart, CT Ep 159 co-guest), Justin Gardner (CT host), broader Google Bug Hunters program staff.
