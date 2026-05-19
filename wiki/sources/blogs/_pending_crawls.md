---
title: Personal Blog Ingest — Status
slug: personal-blogs-status
created_utc: 2026-05-19T14:35:00Z
updated_utc: 2026-05-19T17:30:00Z
tags: [meta, ingest-queue]
inbound: []
---

# Personal-blog ingest status (final, 2026-05-19)

Two passes done same day:

1. **Pass 1 (firecrawl direct, 10 sites, 617 posts)** — Detectify+P0+
   BugHunters+MSRC vendor blogs + first 10 personal blogs.
2. **Pass 2 (fallback trafilatura crawler + firecrawl HTTP API resume)** —
   filled in 14 more personal sites and Kettle/Heyes legacy blogs.

Cumulative wiki Chroma additions: **1026 source files / ~13.7K chunks**.

## Ingested (24 personal blogs)

| Slug | Files | Source |
|---|---:|---|
| portswigger-research | 176 | portswigger.net/research (Kettle, Heyes, et al.) |
| embracethered | 109 | embracethered.com (Johann Rehberger) |
| daniel-miessler | 79 | danielmiessler.com |
| orange-tsai | 73 | blog.orange.tw |
| assetnote | 59 | blog.assetnote.io |
| kevin-mizu | 50 | mizu.re |
| spaceraccoon | 47 | spaceraccoon.dev |
| zlz-buerhaus | 45 | buer.haus |
| securitum-research | 26 | research.securitum.com + securitum.com/pentest-chronicles |
| skeletonscribe-kettle | 25 | skeletonscribe.net (James Kettle legacy) |
| oversecured | 25 | blog.oversecured.com + oversecured.com/blog |
| matt-brown | 17 | brownfinesecurity.com |
| corben-leo | 17 | corben.io |
| slonser | 10 | blog.slonser.info |
| sam-curry | 10 | samcurry.net |
| rez0-thacker | 10 | josephthacker.com |
| jack-cable | 10 | cablej.io |
| inti | 8 | inti.io |
| daniel-thatcher | 5 | blog.long.lat |
| alex-chapman | 4 | blog.ajxchapman.com |
| sam-erb | 3 | blog.erbbysam.com |
| naglinagli-gh | 3 | naglinagli.github.io (Gal Nagli) |
| matanber | 3 | matanber.com |
| thespanner-heyes | 1 | thespanner.co.uk (Gareth Heyes legacy index) |
| spaceraccoon-book | 1 | fromdayzerotozeroday.com (index) |
| douglas-day | 1 | dday.us |

Plus vendor blogs from pass 1:

| Slug | Files | Source |
|---|---:|---|
| detectify | 32 | labs.detectify.com (full author archive incl. Frans Rosén) |
| p0 | 93 | projectzero.google (Google Project Zero) |
| bughunters | 70 | bughunters.google.com/blog (Google Bug Hunters Security Engineering) |
| msrc | 9 | microsoft.com/msrc/blog (filtered to research/technical) |

## Permanently skipped (single-page portfolios / no blog content)

These hosts returned <2 substantive posts; their writing lives elsewhere
(usually on PortSwigger Research, Twitter/X, or as embedded readmes in
GitHub gists). Do not retry without a per-host adapter.

| Host | Owner | Why skipped |
|---|---|---|
| garethheyes.co.uk | Gareth Heyes | CSS/HTML game showcase + portfolio; research is on portswigger-research |
| jameskettle.com | James Kettle | Talks index + portfolio; research is on portswigger-research + skeletonscribe |
| galnagli.com | Gal Nagli | Static landing; writeups are on naglinagli.github.io |
| joaxcar.com | Johan Carlsson | Single-page bio; content on X/HackerOne |
| nickcopi.site | Nick Copi | Single-page bio; writeups are gists |
| avlidienbrunn.se | Mathias Karlsson | Static landing; posts under detectify labs |
| cspbypass.com | Renniepak | Single payload-listing page (not posts) |
| blog.jr0ch17.com | Jasmin Landry | Empty/landing |
| fromdayzerotozeroday.com | Eugene Lim | Book landing; posts are on spaceraccoon.dev |

## Re-run recipe

```sh
# Add new firecrawl crawl job to bin/_firecrawl_resume.py JOBS list, then:
set -a && source .env && set +a
tlx/.venv/bin/python bin/_firecrawl_resume.py        # crawl + write markdown
tlx/.venv/bin/python bin/ingest-wiki.py              # embed into wiki Chroma
python3 bin/_crosslink_blog_ingest.py                # cross-link people pages
```
