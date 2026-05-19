---
title: Personal Blog Ingest — Pending Crawls
slug: personal-blogs-pending
created_utc: 2026-05-19T14:35:00Z
updated_utc: 2026-05-19T14:35:00Z
tags: [meta, ingest-queue]
inbound: []
---

# Pending personal-blog crawls

Firecrawl plan credits exhausted partway through the 2026-05-19 ingest.
The 22 blogs below remain ungrabbed and should be picked up on the next
ingest pass once credits replenish (or by switching to direct
`requests` + a Python crawler bypassing Firecrawl).

Each entry: `host  —  owner-slug  —  source-of-truth file in wiki/people/`.

| Host | Owner | People page |
|---|---|---|
| garethheyes.co.uk | Gareth Heyes | [gareth-heyes.md](../../people/gareth-heyes.md) |
| jameskettle.com | James Kettle | [james-kettle.md](../../people/james-kettle.md) |
| danielmiessler.com | Daniel Miessler | [daniel-miessler.md](../../people/daniel-miessler.md) |
| josephthacker.com | Joseph Thacker / rez0 | [rez0.md](../../people/rez0.md) |
| corben.io | Corben Leo | [corben-leo.md](../../people/corben-leo.md) |
| galnagli.com | Gal Nagli | [gal-nagli.md](../../people/gal-nagli.md) |
| joaxcar.com | Johan Carlsson | [johan-carlsson.md](../../people/johan-carlsson.md) |
| matanber.com | Matan Berson | [matanber.md](../../people/matanber.md) |
| nickcopi.site | Nick Copi / 7urb0 | [nick-copi.md](../../people/nick-copi.md) |
| inti.io | Inti De Ceukelaire | [inti-de-ceukelaire.md](../../people/inti-de-ceukelaire.md) |
| avlidienbrunn.se | Mathias Karlsson | [mathias-karlsson.md](../../people/mathias-karlsson.md) |
| fromdayzerotozeroday.com | Eugene Lim / Spaceraccoon (book) | [spaceraccoon.md](../../people/spaceraccoon.md) |
| blog.slonser.info | Vsevolod Kokorin | [slonser.md](../../people/slonser.md) |
| blog.ajxchapman.com | Alex Chapman | [alex-chapman.md](../../people/alex-chapman.md) |
| cspbypass.com | René de Sain / Renniepak | [renniepak.md](../../people/renniepak.md) |
| blog.long.lat | Daniel Thatcher | [daniel-thatcher.md](../../people/daniel-thatcher.md) |
| brownfinesecurity.com | Matt Brown | [matt-brown.md](../../people/matt-brown.md) |
| blog.jr0ch17.com | Jasmin Landry | [jr0ch17.md](../../people/jr0ch17.md) |
| blog.erbbysam.com | Sam Erb | [sam-erb.md](../../people/sam-erb.md) |
| dday.us | Douglas Day | [douglas-day.md](../../people/douglas-day.md) |
| naglinagli.github.io | Gal Nagli (GH writeups) | [gal-nagli.md](../../people/gal-nagli.md) |
| cablej.io | Jack Cable | [jack-cable.md](../../people/jack-cable.md) |

## Already ingested in this batch

Under `wiki/sources/blogs/personal/<slug>/`:

- portswigger-research (Kettle, Heyes, et al.) — 175 posts
- embracethered (Rehberger) — 109 posts
- assetnote (Shubham Shah, Sean Yeoh) — 58 posts
- orange-tsai — 73 posts
- zlz-buerhaus (Brett Buerhaus) — 45 posts
- sam-curry — 10 posts
- kevin-mizu — 50 posts
- securitum-research (Bentkowski + team) — 25 posts
- spaceraccoon (Eugene Lim) — 47 posts
- oversecured (Sergey Toshin) — 25 posts

Total: 617 personal-blog posts. Earlier same-day batch ingested 204
posts from Detectify Labs (32), Project Zero (93), Google Bug Hunters
(70), MSRC SRD (9).

## Resume recipe

```sh
# After firecrawl credits replenish:
python3 bin/_personal_blog_queue.py   # confirm queue
# For each pending host, fire firecrawl_crawl with onlyMainContent=true,
# limit ~80, maxDiscoveryDepth=4. Then run:
python3 bin/_split_personal_blogs.py  # extend JOBS list with new payloads
set -a && source .env && set +a
tlx/.venv/bin/python bin/ingest-wiki.py
```
