---
title: Sam Curry (samwcyo)
slug: sam-curry
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [samwcyo]
role: hunter
primary_focus: enterprise
tags: [person, role/hunter, focus/enterprise, focus/api, focus/iot, focus/collaboration]
inbound: []
---

# Sam Curry (samwcyo)

## Identity

- **Real name:** Sam Curry (b. 1999, Omaha NE).
- **Primary handle:** `samwcyo` (X, GitHub). HackerOne handle: `zlz`.
- **Role:** Bug-bounty hunter, security researcher, founder of Palisade
  Security (security consulting, founded ~2018).
- Earned first bounty at 15, crossed US$500k by 18. April 2021 donated a
  $50k Yuga Labs bounty toward an infant heart-surgery fund.

## Focus areas

- Connected-vehicle telematics / OEM SSO chains (Hyundai, Kia, Subaru,
  BMW, Mercedes, Ferrari, Porsche).
- Enterprise web/API auth bypass and IDOR at scale (Apple, Starbucks,
  Cox, points.com).
- Group recon-heavy chains: long, collaborative auth/SSO traversals
  involving 3-7 hunters per writeup.
- Web cache / path-normalization quirks (Rocket League, Starbucks `/bff/proxy/`).
- Mass-assignment + dealer/admin-portal abuse on B2B-flavored OEM portals.

## Online presence

- Blog: [samcurry.net](https://samcurry.net)
- X / Twitter: [@samwcyo](https://x.com/samwcyo)
- GitHub: [samwcyo](https://github.com/samwcyo)
- HackerOne: [hackerone.com/zlz](https://hackerone.com/zlz)
- Bugcrowd profile / interview:
  [Hacker Spotlight - Sam "zlz" Curry](https://www.bugcrowd.com/blog/hacker-spotlight-sam-zlz-curry/)
- Wikipedia: [Sam Curry](https://en.wikipedia.org/wiki/Sam_Curry)

## Key research / posts

- **[Web Hackers vs. The Auto Industry](https://samcurry.net/web-hackers-vs-the-auto-industry)**
  (2023-01-03, w/ Neiko Rivera, Brett Buerhaus, Maik Robert, Ian Carroll,
  Justin Rhinehart, Shubham Shah).
  Across ~16 OEMs (Ferrari, BMW, Rolls Royce, Porsche, Mercedes, Toyota,
  Nissan, Honda, etc.): SSO/dealer-portal auth bypass + mass-assignment
  + email-verification skips chained to remote-control of millions of
  vehicles and full internal-app access at BMW/Mercedes. Foundational
  car-telematics writeup; signature collab piece.
- **[Hacking Hyundai/Genesis (thread + writeup)](https://x.com/samwcyo/status/1597695432544907265)**
  (2022-11). Email-verification bypass in OEM mobile app yields full
  account takeover and lock/unlock/start/honk on every 2012+ vehicle.
  Companion to the auto-industry post.
- **[Hacking Kia: Remote Control via License Plate](https://samcurry.net/hacking-kia)**
  (2024-09-20, w/ Neiko Rivera, Justin Rhinehart, Ian Carroll, Kenneth
  Lugo). Self-register dealer account → resolve VIN from plate → mass-assign
  attacker as primary owner; ~30s from plate to remote unlock/start/track.
- **[Hacking Subaru STARLINK](https://samcurry.net/hacking-subaru)**
  (2025-01-23, w/ Shubham Shah). Unauthenticated employee password reset +
  client-side 2FA bypass on admin panel → location history + remote
  vehicle commands across US/CA/JP. Patched in 24h.
- **[Hacking Millions of Modems (Cox)](https://samcurry.net/hacking-millions-of-modems)**
  (2024-06-03, solo). ~700 internal Cox APIs with replayable
  authorization; leaked frontend crypto key → arbitrary command exec on
  any customer modem + PII retrieval. Disclosed Mar 4, patched Mar 5.
- **[We Hacked Apple for 3 Months](https://samcurry.net/hacking-apple)**
  (2020-10-07, w/ Brett Buerhaus, Ben Sadeghipour, Samuel Erb, Tanner
  Barnes). 55 vulns (11 critical, 29 high) on Apple infra; centerpiece
  was a wormable stored XSS in iCloud Mail propagating via contacts on
  message read. Reconnaissance-heavy methodology benchmark.
- **[Hacking Starbucks — ~100M customer records](https://samcurry.net/hacking-starbucks)**
  (2020-06-20, w/ Justin Gardner, Noah Pearson). Path-traversal on
  `/bff/proxy/` reached an internal Microsoft Graph instance and dumped
  customer PII. Canonical secondary-context path traversal case study.
- **[Leaked Secrets and Unlimited Miles — points.com](https://samcurry.net/points-com)**
  (2023-08-03, w/ Ian Carroll, Shubham Shah). Flask session signed with
  literal secret `"secret"` granted admin on the platform backing most
  airline/hotel loyalty programs; 22M customer records + arbitrary points
  transfer.
- **[Hacking ClubWPT Gold](https://samcurry.net/hacking-clubwpt-gold)**
  (2025-10-12, w/ Shubham Shah). Exposed `.git` → source disclosure →
  hardcoded staging creds + unauthenticated 2FA-bypass endpoint → prod
  admin panel with KYC docs (driver's licenses, passports).
- **[Cracking My Windshield — Tesla $10k](https://samcurry.net/cracking-my-windshield-and-earning-10000-on-the-tesla-bug-bounty-program)**
  (2019). Early-career Tesla bug-bounty writeup; often-referenced for
  the storytelling style.
- **[Rocket League Path Normalization + Cache Poisoning](https://samcurry.net/abusing-http-path-normalization-and-cache-poisoning-to-steal-rocket-league-accounts)**
  HTTP cache-deception / path normalization yielding account takeover —
  Sam's recurring web-cache theme.
- **[Don't Force Yourself to Become a Bug Bounty Hunter](https://samcurry.net/dont-force-yourself-to-become-a-bug-bounty-hunter)**
  Career/methodology essay frequently cited in onboarding threads.

## CT podcast appearances

- [2024-04-04 Ep 65 — Motivation and Methodology with Sam Curry & Zlz](../sources/podcasts/ct/)
  (co-guest with Brett Buerhaus / @zlz).

## Notes

- **Signature shape:** long, recon-heavy, multi-hunter chains targeting
  enterprise/OEM control planes. Typical chain: subdomain enum →
  dealer/employee portal → SSO or email-verification skip → mass-assign
  primary-owner / dealer role → telematics command exec. The work scales
  one bug into "every car/modem/account at this company".
- **Recurring collaborators:** Brett Buerhaus (`zlz`), Shubham Shah,
  Ian Carroll, Justin Rhinehart, Neiko Rivera, Maik Robert. Sam +
  Brett is the most common co-byline; auto-industry-class research
  typically draws the wider crew.
- **Methodology cues to copy:** treat OEM/B2B-flavored side portals
  (dealer/employee/fleet) as the soft-tissue around hardened consumer
  apps; check email-verification flows for client-side trust; assume
  every internal `/bff/` or `/api/proxy/` style path is path-traversable
  until disproven; pull JS for embedded keys and admin endpoints before
  doing anything else.
- **Voice:** narrative, screenshot-heavy, vendor-praising-on-fix.
  Disclosures usually well-coordinated; many patched in 24-48h.

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/sam-curry/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

<!-- sources:auto:start -->
## Ingested blog posts

- [about](../sources/blogs/personal/sam-curry/about.md)
- [feed rss](../sources/blogs/personal/sam-curry/feed-rss.md)
- [hacking apple](../sources/blogs/personal/sam-curry/hacking-apple.md)
- [hacking clubwpt gold](../sources/blogs/personal/sam-curry/hacking-clubwpt-gold.md)
- [hacking kia](../sources/blogs/personal/sam-curry/hacking-kia.md)
- [hacking millions of modems](../sources/blogs/personal/sam-curry/hacking-millions-of-modems.md)
- [hacking subaru](../sources/blogs/personal/sam-curry/hacking-subaru.md)
- [points com](../sources/blogs/personal/sam-curry/points-com.md)
- [web hackers vs the auto industry](../sources/blogs/personal/sam-curry/web-hackers-vs-the-auto-industry.md)

<!-- sources:auto:end -->
