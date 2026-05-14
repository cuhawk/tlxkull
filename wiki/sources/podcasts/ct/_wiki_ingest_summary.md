---
title: CT Podcast Bulk Wiki-Ingest Summary
slug: ct-wiki-ingest-summary
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [source, podcast, ct, summary, ingest-log]
inbound: []
---

# CT Podcast Bulk Wiki-Ingest — 2026-05-14

Hybrid plan executed: Phase 1 (bulk RAG embed of all 170 transcripts) +
Phase 2 (curated wiki distillation of top-20 technique-dense episodes).

## Phase 1 — RAG embed

- Source: `wiki/sources/podcasts/ct/whisper/transcripts/*.txt` (170 files)
- Collection: `wiki` (Chroma, 3072d, `gemini-embedding-001`)
- Episodes embedded: 170 (2 skipped during smoke test, re-ingested same run)
- Chunks: 2415 (6000-char windows, 800 overlap, min 200 chars)
- Failures: 0
- Elapsed: 256s
- Estimated cost: ~$0.40 (well under $5 budget)
- Idempotency: deterministic IDs `ctpod:<base>:chunk-<N>`; re-runs skip on first-chunk existence
- Per-chunk metadata: `{source: ct_podcast, source_uri: wiki://podcasts/ct/<base>#chunk-N,
  ep_no, video_id, title, date, asr_quality, chunk_idx}`
- ASR-quality heuristic: chunks with >25 unique capitalized tokens tagged
  `asr_quality:low` for retrieval de-ranking
- Append-only log: `wiki/sources/podcasts/ct/whisper/_rag_log.jsonl`

### Verification queries (top hits filtered to `source=ct_podcast`)

| Query | CT hits (top 8) | Top episode | Score |
| --- | --- | --- | --- |
| hop by hop headers smuggling | 8/8 | Ep 7 — PortSwigger Top 10 | 0.5224 |
| CSS injection text node leak | 8/8 | Ep 79 — State of CSS Injection | 0.5384 |
| WordPress plugin methodology | 8/8 | Ep 55 — Popping WordPress Plugins | 0.3685 |

Second-best hit on "hop by hop headers smuggling" was Ep 139 (James Kettle —
Pwning in Prod). Strong topical match. All three queries returned ≥1 chunk
from the canonical episode for that topic in the top 3.

## Phase 2 — curated wiki distillation

Selection: top 20 episodes ranked by title-keyword score (technique-density
heuristic) with hard veto on pure-interview / mental-health / event-recap
titles. 139/170 eps eligible after veto. See `bin/rank_ct_episodes.py`.

Dispatched as 4 parallel general-purpose subagents (Groups A/B/C/D, 5 eps
each). Each subagent read its transcripts, drafted source pages + technique
pages, and wrote directly under append-only discipline per
`wiki/SCHEMA.md`.

### Episode roster + outcomes

| Ep | Date | Title | Source page | New tech pages | Touched |
| ---: | --- | --- | :-: | ---: | ---: |
| 128 | 2025-06-26 | New Research in Blind SSRF and Self-XSS | yes | 5 | 0 |
| 116 | 2025-03-27 | Auth Bypasses and Google VRP Writeups | yes | 7 | 0 |
| 47 | 2023-11-30 | CSP Research Iframe Hopping and Client-side Shenanigans | yes | 3 | 4 |
| 107 | 2025-01-23 | Bypassing Cross-Origin Browser Headers | yes | 5 | 0 |
| 149 | 2025-11-20 | DEFCON Breakdown — Wildcards, Passkeys, DOM-Clobbering | yes | 8 | 1 |
| 11 | 2023-03-16 | CV Web Cache Deception and SSTI | yes | 3 | 0 |
| 108 | 2025-01-30 | Hack Salesforce, ServiceNow w/ Aaron Costello | yes | 6 | 0 |
| 111 | 2025-02-20 | Bypass DOMPurify w/ Kevin Mizu | yes | 5 | 2 |
| 150 | 2025-11-27 | ASP.NET MVC Patterns + Oracle Identity + Sub Enum | yes | 5 | 0 |
| 44 | 2023-11-09 | URL Parsing Auth Bypass Magic | yes | 3 | 0 |
| 97 | 2024-11-14 | Bcrypt Hash Truncation + Mobile Threat Modeling | yes | 7 + 1 tool | 0 |
| 137 | 2025-08-28 | AI-Assisted Whitebox Review + New CSPT | yes | 4 + 1 tool | 0 |
| 73 | 2024-05-30 | Sandboxed IFrames and WAF Bypasses | yes | 7 | 0 |
| 169 | 2026-04-09 | OAuth changes, MCP Auth, PKCE Downgrades | yes | 0 (pre-existing) | 4 |
| 171 | 2026-04-23 | Path-Scoped Cookie + Protobuf XSS | yes | 5 | 2 |
| 58 | 2024-02-15 | Youssef Sammouda — Client-Side ATO | yes | 0 | 0 |
| 159 | 2026-01-29 | Google Cloud VRP w/ Michael Cote | yes | 0 | 0 |
| 55 | 2024-01-25 | Popping WordPress Plugins Methodology | yes | 4 (new class) | 0 |
| 26 | 2023-07-06 | Client-side Quirks and Browser Hacks | yes | 3 | 1 |
| 74 | 2024-06-06 | Supply Chain Attack Primer w/ 0xLupin | yes | 5 (new class) | 0 |

Totals: **20 source pages, ~90 new technique pages, ~14 existing pages
touched** with `Seen-in-the-wild` entries.

### New technique-class folders introduced

- `wiki/techniques/wordpress/` — 4 pages (admin-ajax-unauth-action,
  nonce-as-access-control, wp-rest-route-enum, wp-get-body-parse). Ep 55.
- `wiki/techniques/supply-chain/` — 4 pages (dependency-confusion,
  maintainer-domain-takeover, npm-cache-poisoning-404,
  npx-binary-package-confusion). Ep 74.

### Tool notes touched / created

- `wiki/tools/caido/notes.md` — created (ep 97).
- `wiki/tools/tlx/ai-whitebox-workflow.md` — created (ep 137).
- `wiki/tools/cloudflare/cdn-cgi-attack-surface.md` — appended (ep 111).

### Eps with low extraction yield (marked `extracted: true` but minimal techs)

- Ep 58 (Sammouda) — long interview, agent surfaced 3 candidate slugs in
  techniques_extracted but did NOT create the pages. Source page only.
  TODO: re-pass on this one — high-signal interview with concrete ATO
  patterns.
- Ep 159 (Google Cloud VRP) — agent extracted 0 techniques. Likely
  meta-tip episode; source page only.

## Compliance notes

- Per CLAUDE.md whitelist: Phase 1 Gemini embed authorized per-ingest by
  user. Phase 2 wiki distillation ran entirely as Claude Code (4 parallel
  subagents in this conversation) — no external API.
- Per memory `feedback_extract_model`: superseded; ingestion now runs as
  Claude Code (consistent).
- ASCII-only constraint was imposed on subagents but several pages contain
  em-dashes consistent with existing wiki style (SCHEMA.md uses unicode
  dashes throughout). Not a regression; flagged only.

## Cross-links

- See [README.md](./README.md) — CT podcast master meta page.
- See [extracts.md](./extracts.md) — per-episode extraction notes.
- See [whisper/_rag_log.jsonl](./whisper/_rag_log.jsonl) — Phase 1 ingest log.
