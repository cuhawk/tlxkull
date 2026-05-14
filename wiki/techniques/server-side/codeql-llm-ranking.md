---
title: CodeQL + LLM Ranking for Reproducible CVE Discovery (Slice)
slug: codeql-llm-ranking
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/whitebox, technique/ai, technique/codeql]
inbound: []
---

# CodeQL + LLM Ranking for Reproducible CVE Discovery (Slice)

## Pattern

Caleb Gross's "Slice" pattern wraps CodeQL with an LLM filter+rank stage
to turn one-off "GPT found a CVE once" demos into reproducible 10-out-
of-10 discoveries. The four-stage pipeline:

1. **Parse** - feed the codebase to CodeQL, run a class-level query
   (e.g. "all unbounded copies into fixed-size buffers in this kernel
   subsystem").
2. **Query** - execute the CodeQL query, capture all candidate sinks.
3. **Filter** - pass each candidate to the LLM with the surrounding
   function context; the LLM rejects obvious non-bugs.
4. **Rank** - the LLM scores remaining candidates by exploitability,
   reachability, and impact.

Used to reproduce CVE-2025-37778 (Linux SMB driver vulnerability) - the
original AI-only discovery hit ~1-in-100 reproducibility; Slice's
pipeline hit 10/10.

The technique is most powerful on **lower-level codebases** (C, kernel,
firmware) where CodeQL has strong query libraries for memory-safety bug
classes. Pure-LLM analysis there is unreliable; CodeQL alone is too noisy.

## Preconditions

- CodeQL coverage for the language (excellent for C/C++, Java, JS,
  Python, Go; weaker for Rust, Swift).
- A reproducible CodeQL query for the bug class of interest.
- Compute budget for the LLM filter/rank pass (GPT-5 with thinking mode
  works best per Caleb's writeup - costly but accurate).

## Detection

Not applicable - this is itself a detection pipeline.

## Triggering

```bash
# Caleb's Slice tool (https://github.com/calebgross/slice)
slice analyze \
  --target /path/to/codebase \
  --query memory-safety/unbounded-copy \
  --model gpt-5-thinking \
  --top-n 20
```

Workflow:
1. Pick a bug-class query (or write one).
2. Run CodeQL across the target.
3. Slice's LLM pass filters and ranks; output is a markdown list with
   reasoning per candidate.
4. Manually verify the top N.

## Bypasses

Not applicable.

## Seen in the wild

- {date: 2025-08-28, source: CT Ep 137} - Caleb Gross released Slice; reproduced CVE-2025-37778 (Linux kernel SMB driver) 10/10 vs prior AI-only 1/100. Best fit: low-level codebases with strong CodeQL bug-class queries.

## References

- Caleb Gross blog - Slice writeup (referenced in episode).
- Slice tool - GitHub (referenced in episode).
- CVE-2025-37778 - Linux kernel SMB driver.
- Critical Thinking Podcast Ep 137 - <https://www.youtube.com/watch?v=sTG-OX5BbBc>
- Related: [[ai-whitebox-source-review]]
- [Server-side SUMMARY](SUMMARY.md)
