---
title: Karpathy llmwiki — canonical reference
slug: karpathy-llmwiki
created_utc: 2026-05-11T00:00:00Z
updated_utc: 2026-05-11T00:00:00Z
tags: [tool/karpathy, pattern/wiki, meta]
inbound: []
---

# Karpathy llmwiki — canonical reference

**Source:** https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
(created 2026-04-04)

## Idea in one sentence
A personal knowledge base where the LLM incrementally maintains a
persistent wiki rather than repeatedly rediscovering information from
raw documents.

## Three layers
1. **Raw sources** — immutable documents that are the single source
   of truth. (For us: confirmed findings, opus transcripts, target
   captures.)
2. **The wiki** — LLM-generated markdown of summaries, entity pages,
   cross-references. (For us: `wiki/`.)
3. **Schema document** — config defining wiki structure + conventions.
   (For us: `wiki/SCHEMA.md`.)

## Three operations
- **Ingest** — new source arrives; LLM reads it, writes summaries,
  updates relevant pages in a single pass (often 10–15 files touched).
  (For us: `wiki-ingest` skill.)
- **Query** — user asks questions against the compiled wiki; answers
  can become new wiki pages. (For us: `wiki-query` skill.)
- **Lint** — periodic health checks: contradictions, orphan pages,
  knowledge gaps. (For us: `wiki-lint` skill.)

## Why this works
The approach offloads tedious bookkeeping — updating cross-references,
maintaining consistency — to the LLM, which handles it at near-zero
cost. The human curates sources and asks questions; the LLM manages
everything else.

## Implementations seen in the wild
Synthadoc, Link, ΩmegaWiki, Kompl. None directly adapted; ours is the
first I'm aware of tailored to bug-bounty workflow.

## What we changed for our use case
- Pages organized by `targets/` (bounty program intel) +
  `techniques/` (bug-class patterns) + `tools/` + `findings/`.
- Cross-link discipline enforced by `wiki-lint`.
- RAG layer (`docs_query` collection named `wiki`) for fast retrieval
  during opus-deep-audit chain analysis.
- Findings get *distilled* into the wiki; full per-engagement state
  stays in `targets/<name>/`.
