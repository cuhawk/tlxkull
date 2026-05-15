---
title: Jon Colston (mayonaise)
slug: jon-colston
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [mayonaise, colston3000]
role: hunter
primary_focus: recon
tags: [person, role/hunter, focus/recon, focus/data-science, focus/ssrf, focus/idor, focus/ads-tech]
inbound: []
---

## Identity

- **Real name:** Jon Colston
- **Primary handle:** `mayonaise` (HackerOne); `colston3000` (X/Twitter)
- **Role:** Full-time bug-bounty hunter since late 2018. Operates personal brand "Mayonaise Cybersecurity Research". 25+ years prior in startup analytics / digital marketing leadership; Las Vegas-based.
- **Reputation:** Ninth hacker to reach $1M lifetime earnings on HackerOne (announced 2020-06-29). 170+ valid vulnerabilities reported across enterprise + government programs. Held the record for most bounties earned by a single hacker at a live-hacking event (H1-2004, Verizon Media).
- **Handle origin:** Named after the song "Mayonaise" on Smashing Pumpkins' *Siamese Dream* — lyrics about overcoming long odds.

## Focus areas

- **Data-science-driven recon** — collect/organize endpoint and parameter data, mine for outliers, build target-specific wordlists from observed patterns rather than off-the-shelf lists.
- **Ad-tech / marketing platforms** — leverages prior digital-marketing background to find issues in publisher/advertiser pipelines that pure-engineering hunters miss.
- **SSRF + IDOR at scale** — these were his explicit focus during the Verizon Media H1-2004 record.
- **"Recipes & ingredients" methodology** — discrete recon/test atoms (a data source, an enumeration method, a sink probe) composed into reusable per-target blueprints.
- **"Conversion funnel" framing** — adapts marketing-funnel quantification (input volume → triage rate → submit rate → bounty rate) to bug-bounty pipeline tuning.

## Online presence

- Personal site: [colstonjon.com](https://www.colstonjon.com/)
- LinkedIn: [linkedin.com/in/jon-colston](https://www.linkedin.com/in/jon-colston/)
- X / Twitter: [@colston3000](https://x.com/colston3000)
- HackerOne profile: [hackerone.com/mayonaise](https://hackerone.com/mayonaise)
- HackerOne badges: [hackerone.com/mayonaise/badges](https://hackerone.com/mayonaise/badges)

No public technical blog or GitHub presence located as of 2026-05-15. Research output is podcast/interview-driven; primary writeups are private.

## Key research / posts

- **HackerOne Spotlight: Interview with mayonaise** — [hackerone.com/blog/hacker-spotlight-interview-mayonaise](https://www.hackerone.com/blog/hacker-spotlight-interview-mayonaise) — Methodology: spends 15-30 minutes per endpoint systematically, collects test-time data to identify suspicious patterns. Quote: *"Data is the digital image of the experiences you acquired while testing. As you become a more skilled bug hunter, you will be able to turn that data into information."*
- **Mayonaise Joins the Ranks of Seven-Figure-Earning Hackers** — [hackerone.com/blog/mayonaise-joins-ranks-seven-figure-earning-hackers](https://www.hackerone.com/blog/mayonaise-joins-ranks-seven-figure-earning-hackers) — H1's announcement of the $1M milestone (2020-06-29). Confirms Verizon Media as primary target program; SSRF + IDOR as primary classes; 170+ vulns.
- **Mayonaise Talks About His Recon Workflow** (YouTube interview) — [youtube.com/watch?v=SGLdv\_4Iy44](https://www.youtube.com/watch?v=SGLdv_4Iy44) — Recon workflow walkthrough, learning method, automation choices.
- **Critical Thinking HackerNotes Ep. 56 writeup** — [blog.criticalthinkingpodcast.io/p/jon-colston-mayonaise-bug-bounty-data-science](https://blog.criticalthinkingpodcast.io/p/jon-colston-mayonaise-bug-bounty-data-science) — Distilled CT episode: "recipes & ingredients" abstraction, signature *Mother of All Bugs* (MOAB) concept, working-backwards-from-the-bug method, conversion-funnel framing applied to bounty pipeline.
- **Dice — Bug Bounties: What It Takes to Succeed** — [dice.com/career-advice/bug-bounties-what-it-takes-succeed-get-paid](https://www.dice.com/career-advice/bug-bounties-what-it-takes-succeed-get-paid) — Career-side profile; reinforces the "digital marketing → data analytics → bug bounty" arc.

## CT podcast appearances

- [2024-02-01 Ep 56 — Using Data Science to win Bug Bounty - Mayonaise (aka Jon Colston)](../sources/podcasts/ct/20240201_4k1G63mhoek_Using_Data_Science_to_win_Bug_Bounty_-_Mayonaise_aka_Jon_Colston_Ep._56.en.vtt) — Cross-refs: [YouTube](https://www.youtube.com/watch?v=4k1G63mhoek) · [Spotify](https://open.spotify.com/episode/3An78VLPaa9K1wGGu0B9rY) · [criticalthinkingpodcast.io](https://www.criticalthinkingpodcast.io/episode-56-using-data-science-to-win-bug-bounty-mayonaise-aka-jon-colston/) · [RSS.com](https://rss.com/podcasts/ctbbpodcast/1325300/)

## Notes

- **Signature methodology — "recipes & ingredients":** Ingredients are atomic recon/test units (a data source like Shodan, a crawl pattern, a specific endpoint probe). Recipes are ordered compositions of ingredients that reliably surface a bug class on a specific target/technology. Once a recipe lands a bug, it becomes a reusable blueprint — applied across the program and adjacent programs. Maps cleanly onto TLX's skill-chain pattern (recon → js-harvest → js-index → chain-triage); each skill is effectively a Mayonaise-style ingredient.
- **Excel / pivot-table reputation:** Colleagues joke he "most likely invented the pivot table" — shorthand for an obsessive habit of dumping all test-time observations into tabular form and slicing them. The actionable lesson for TLX: persist *everything* observed during fuzz/recon (URLs, params, header diffs, response-size deltas) into queryable form, then look for outliers — that's the input to MOAB hunting.
- **MOAB ("Mother of All Bugs"):** His term for a single recon artifact that unlocks chained findings across an entire program family (e.g. one mis-scoped ad-tech endpoint that is reused across N publisher integrations → N reports). Working-backwards: start from "what would the highest-impact bug on this stack look like?" and reverse-engineer the recipe to reach it.
- **Conversion-funnel framing:** Treat bug-bounty pipeline as a marketing funnel — measure (a) hosts identified, (b) endpoints surfaced, (c) candidates worth manual review, (d) submissions, (e) accepted findings. Optimize the conversion rate between adjacent stages rather than just top-of-funnel volume. Direct analog to TLX's chain triage / DOM-reachability filtering — both are funnel-narrowing stages.
- **No public blog or GitHub:** Unlike most CT guests, his output is interview/podcast form. Treat the CT Ep 56 transcript as the canonical wiki source. If a `mayonaise.io` or other blog ever appears, ingest immediately — currently no such domain resolved (2026-05-15).
- **Why he matters to TLX:** philosophical match. The data-science-driven, "save everything → mine for outliers → compose into recipes" loop is exactly what TLX's per-target SQLite + Chroma snapshot + chain-triage pipeline is engineered to enable. Worth treating Ep 56 as a methodological reference when designing new skills or chain scorers.
