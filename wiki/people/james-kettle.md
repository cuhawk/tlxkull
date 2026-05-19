---
title: James Kettle (albinowax)
slug: james-kettle
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [albinowax, james.kettle]
role: researcher
primary_focus: server-side
tags: [person, role/researcher, vendor/portswigger, focus/http-smuggling, focus/desync, focus/cache, focus/server-side]
inbound: []
---

# James Kettle (albinowax)

## Identity

- **Real name:** James Kettle
- **Primary handle:** `albinowax`
- **Role:** Director of Research at PortSwigger (vendor of Burp Suite)
- **Based:** England
- **Focus:** Invents novel techniques to hack websites, then implements them into Burp Scanner. Widely regarded as the single most influential server-side web security researcher of the last decade.

## Focus areas

- HTTP request smuggling / desync (server-side and browser-powered)
- Web cache poisoning and cache deception
- HTTP/2 protocol attacks and parser differentials
- Race conditions (single-packet attack)
- Web timing attacks
- Scanner research: hunting unknown vulnerability classes via differential probing

## Online presence

- [PortSwigger research profile](https://portswigger.net/research/james-kettle) — canonical publication index
- [Personal site — jameskettle.com](https://jameskettle.com)
- [X / Twitter — @albinowax](https://x.com/albinowax)
- [GitHub — @albinowax](https://github.com/albinowax)
- [PortSwigger GitHub org](https://github.com/PortSwigger) — most of his tooling ships under this org
- [Param Miner (Burp extension)](https://github.com/PortSwigger/param-miner) — hidden parameter and header discovery; the de-facto tool for cache poisoning recon
- [Turbo Intruder (Burp extension)](https://github.com/PortSwigger/turbo-intruder) — high-speed HTTP engine; underpins the single-packet attack
- [HTTP Request Smuggler (Burp extension)](https://github.com/PortSwigger/http-request-smuggler) — automated desync detection
- [Backslash Powered Scanner](https://github.com/PortSwigger/backslash-powered-scanner) — differential injection scanner that finds unknown bug classes
- [ActiveScan++](https://github.com/PortSwigger/active-scan-plus-plus) — extends Burp Scanner with bleeding-edge checks
- [Collaborator Everywhere](https://github.com/PortSwigger/collaborator-everywhere) — passive OOB probe injector
- BlackHat USA speaker (multi-year): 2019 HTTP Desync, 2021 HTTP/2, 2022 Browser-Powered Desync, 2023 Smashing the State Machine, 2024 Listen to the Whispers

## Key research / posts

- **[HTTP Desync Attacks: Request Smuggling Reborn](https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn)** (2019) — Revived a near-dead bug class by demonstrating practical CL.TE / TE.CL exploitation on real CDNs and load balancers; spawned an entire industry sub-discipline. Seeded server-side desync technique notes; see `../techniques/server-side/hop-by-hop-smuggling.md` and `../techniques/server-side/akamai-edge-smuggling.md`.
- **[Practical Web Cache Poisoning](https://portswigger.net/research/practical-web-cache-poisoning)** (2018) — Showed unkeyed headers (`X-Forwarded-Host`, etc.) can be weaponised to poison shared caches at scale; turned cache poisoning from a theory paper into a routine bounty bug. Linked from `../techniques/server-side/web-cache-deception.md`.
- **[Web Cache Entanglement: Novel Pathways to Poisoning](https://portswigger.net/research/web-cache-entanglement)** (2020) — Extended cache poisoning into cache key transformations, internal cache layers, and parser differentials between the cache and origin.
- **[HTTP/2: The Sequel is Always Worse](https://portswigger.net/research/http2)** (2021) — Introduced H2.TE and H2.CL desync variants, request tunneling, and header / URL-prefix injection via HTTP/2 downgrade; demonstrated on Netflix, AWS ALB, Atlassian, and major CDNs.
- **[Browser-Powered Desync Attacks](https://portswigger.net/research/browser-powered-desync-attacks)** (2022) — Coined "client-side desync" — desync between the browser and the front-end — making single-server sites and internal networks exploitable purely via a victim's browser. Cross-link target for any future `../techniques/server-side/client-side-desync.md`.
- **[Smashing the State Machine](https://portswigger.net/research/smashing-the-state-machine)** (2023) — Introduced the **single-packet attack**: withhold final frames of 20-30 requests then release simultaneously, collapsing network jitter to sub-1ms and making race-condition exploitation 4-10x more reliable. See `../techniques/race-conditions/single-packet-attack.md` and `../techniques/race-conditions/substate-races.md`.
- **[Listen to the Whispers: Web Timing Attacks That Actually Work](https://portswigger.net/research/listen-to-the-whispers-web-timing-attacks-that-actually-work)** (2024) — Made timing attacks practical at internet scale by exploiting modern measurement precision; surfaces hidden parameters, blind injection, and misconfigured proxies.
- **[Backslash Powered Scanning: Hunting Unknown Vulnerability Classes](https://portswigger.net/research/backslash-powered-scanning-hunting-unknown-vulnerability-classes)** (2016) — Foundational paper on differential / "augmented" scanning: a scanner that searches for *anomalies* rather than known signatures, finding novel injection classes. Powers the Backslash Powered Scanner extension.
- **[Cracking the Lens: Targeting HTTP's Hidden Attack Surface](https://portswigger.net/research/cracking-the-lens-targeting-https-hidden-attack-surface)** (2017) — Used Collaborator Everywhere to map the invisible HTTP infrastructure behind public sites (internal proxies, log parsers, SSRF surfaces).
- **[Top 10 Web Hacking Techniques of 2024](https://portswigger.net/research/top-10-web-hacking-techniques-of-2024)** (2025) — Latest edition of the annual community vote he has run since 2018 (originally started by Jeremiah Grossman in 2006); the canonical "what mattered this year" list for web AppSec.

## CT podcast appearances

- [2025-09-11 Ep 139 — James Kettle - Pwning in Prod How to do Web Security Research](../sources/podcasts/ct/) *(transcript filename TBD on next ingest)*

## Notes

- **Publication cadence:** One major piece per year, almost always landing at BlackHat USA / DEF CON in August. Each paper ships with a corresponding Burp Scanner check and a Burp extension upgrade — research and tooling are released together.
- **Signature method:** Differential probing. Find two parsers, two cache layers, two protocol implementations that disagree on the same input; turn the disagreement into a primitive. This pattern recurs across desync, cache poisoning, HTTP/2, and timing.
- **Community role:** Curates the annual *Top 10 Web Hacking Techniques* vote (took over from Jeremiah Grossman / WhiteHat in 2018). Three-stage process: open nominations → community shortlist vote → expert-panel final ranking, with PortSwigger's own research excluded from the panel to avoid bias.
- **Tooling philosophy:** Ships research as Burp extensions first (Param Miner, Turbo Intruder, HTTP Request Smuggler), then folds proven techniques into core Burp Scanner. Reading his extension source code is often a faster path to understanding the underlying attack than the paper.
- **Style:** Writes long-form, dense, example-heavy posts with concrete bounty payouts disclosed. Posts age extremely well — the 2018 cache poisoning paper still applies in 2026.
- **Most overlooked vuln class (2025 AMA):** Race conditions beyond the well-understood limit-overuse pattern. All other race condition types mostly discovered by accident or never found.
- **Research topic selection strategy (AMA):** Short-term projects → pick an *active* area (e.g., SAML in 2025) and build on recently published research; fast to validate and publish. Long-term projects → pick a topic *dead for 2+ years* to avoid research collision with others who submitted to Black Hat.
- **AI in research:** Uses OpenAI Deep Research to get up to state-of-the-art fast on a topic, particularly when asked to look at RFCs, academic papers, source code, and Stack Overflow. Notes that AI can occasionally surface a novel hacking technique (happened to him once). Does not use AI as a replacement for domain expertise.
- **Black Hat 2025 research:** Encoding-based attacks (10 classes; long-form documents exist). Collaborated with an external researcher. Made $100K in 2 weeks at some phase of the research (disclosed in AMA; specifics at Black Hat).
- **"Kettled" requests:** His term (coined by Burp engineers in his honour) for an H2 request that cannot be accurately represented in H1 syntax — e.g., a header value containing a newline. Burp shows "this request has been kettled" and hides the H1 message editor view.

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/portswigger-research/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

<!-- sources:auto:start -->
## Ingested blog posts

- [2010 12 chronofeit phishing](../sources/blogs/personal/skeletonscribe-kettle/2010-12-chronofeit-phishing.md)
- [2011 02 hackxor hacking game beta](../sources/blogs/personal/skeletonscribe-kettle/2011-02-hackxor-hacking-game-beta.md)
- [2011 05 js less xss](../sources/blogs/personal/skeletonscribe-kettle/2011-05-js-less-xss.md)
- [2011 05 simulating targets for xsscsrf attacks](../sources/blogs/personal/skeletonscribe-kettle/2011-05-simulating-targets-for-xsscsrf-attacks.md)
- [2011 07 sparse bruteforce addon scanner](../sources/blogs/personal/skeletonscribe-kettle/2011-07-sparse-bruteforce-addon-scanner.md)
- [2011 12 phrack ebook](../sources/blogs/personal/skeletonscribe-kettle/2011-12-phrack-ebook.md)
- [2012 06 x frame options sameorigin warning](../sources/blogs/personal/skeletonscribe-kettle/2012-06-x-frame-options-sameorigin-warning.md)
- [2013 05 practical http host header attacks](../sources/blogs/personal/skeletonscribe-kettle/2013-05-practical-http-host-header-attacks.md)
- [2014 08 comma separated vulnerabilities](../sources/blogs/personal/skeletonscribe-kettle/2014-08-comma-separated-vulnerabilities.md)
- [2015 02 exploiting path relative style sheet](../sources/blogs/personal/skeletonscribe-kettle/2015-02-exploiting-path-relative-style-sheet.md)
- [2015 08 server side template injection](../sources/blogs/personal/skeletonscribe-kettle/2015-08-server-side-template-injection.md)
- [2016 04 exploiting uber and piwik with adapted](../sources/blogs/personal/skeletonscribe-kettle/2016-04-exploiting-uber-and-piwik-with-adapted.md)
- [2016 08 reviewing bug bounties hackers](../sources/blogs/personal/skeletonscribe-kettle/2016-08-reviewing-bug-bounties-hackers.md)
- [2017 04 abusing owasp](../sources/blogs/personal/skeletonscribe-kettle/2017-04-abusing-owasp.md)
- [2017 11 h1 212 ctf writeup](../sources/blogs/personal/skeletonscribe-kettle/2017-11-h1-212-ctf-writeup.md)

<!-- sources:auto:end -->
