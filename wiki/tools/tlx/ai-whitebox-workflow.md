---
title: TLX - AI Whitebox Workflow Prompts (Gemini.md / CLAUDE.md)
slug: tlx-ai-whitebox-workflow
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [tool/tlx, tool/ai, tool/whitebox]
inbound: []
---

# AI Whitebox Workflow Prompts

Captured patterns for agentic-CLI source review (Gemini CLI, Claude Code,
Cursor). See [[../../techniques/recon/ai-whitebox-source-review]] for the
detailed technique writeup; this page logs prompt skeletons and observed
gotchas.

## Gemini CLI quick notes (Ep 137)

- Gemini CLI's launch release was unstable; current state (Aug 2025) is
  usable when forced onto Pro (`--model gemini-2.5-pro`). Flash drops
  context fidelity on long code reviews.
- The massive context window is the only reason to pick Gemini over
  Claude Code for repo-wide indexing - but if a Claude Code subscription
  is available, prefer it for tool-calling reliability.
- `GEMINI.md` (project root) is the auto-loaded memory file.

## Claude Code

- `CLAUDE.md` auto-loaded.
- Build slash commands for the four-pass workflow (`/index-files`,
  `/architecture-summary`, `/test-mining`, `/adjacent-gap`).

## Highest-yield prompt (Justin's Ep 137 quote)

> "Look at where security controls are implemented and then look at
> similar or adjacent functions that might be missing that same control."

## Highest-signal context prompt

> "What tests are validating a security control? That points you directly
> to what the team cares about."

## Related

- [[../../techniques/recon/adjacent-function-gap]] — the killer
  prompt above, formalized with a TLX skill spec.
- [[../karpathy/js-review-cascade]] — Sonnet→Opus cascade to keep
  the four-pass workflow inside the per-target Opus budget.
- [[sourcemap-recon]] — hidden-map + Sentry recon before the
  workflow can run (no source → no whitebox).

## Source

- CT Ep 137 - <https://www.youtube.com/watch?v=sTG-OX5BbBc>
- See [[../../sources/podcasts/ct/20250828_sTG-OX5BbBc_How_We_Do_AI-Assisted_Whitebox_Review_New_CSPT_Ep._137]]
