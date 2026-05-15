---
title: Two-tier triage→analysis cascade for JS / source review
slug: js-review-cascade
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [tool/karpathy, tool/llm, pattern/cascade, whitebox]
inbound: []
---

# JS-review LLM cascade (Slice-style)

## Pattern

Never feed raw SAST output (CodeQL, semgrep, jsluice, taint-chain
list) straight into the flagship model. Always enrich with tree-sitter
call-chain bodies first, then run a *cheap* model to reject obvious
non-bugs, then run a *flagship* model on the survivors.

Caleb Gross's "Slice" demonstrated this pipeline on Linux SMB driver
CVE-2025-37778 — original AI-only discovery hit ~1-in-100
reproducibility; the cascade hit 10/10 at ~$3.35 per run.

Pipeline:

```
candidates --> tree-sitter enrich (bodies + call-chain depth=3)
            --> cheap triage (GPT-5-mini / Sonnet)  : reject obvious FPs
            --> flagship analyze (GPT-5 / Opus)     : verdict + PoC
```

## Why it works

1. Tree-sitter context kills "reachability" false negatives in the
   cheap stage — the model sees the call chain, not just the sink line.
2. Cheap triage cuts flagship spend 5-10x. Slice numbers: 217 CodeQL
   candidates → 9 survivors after GPT-5-mini high-reasoning → 1-2
   confirmed by GPT-5 flagship.
3. Cost-bounded. Budget = Σ(cheap_calls × cheap_$) +
   Σ(flagship_calls × flagship_$). Predictable per chain count.

## How TLX integrates

Current `opus-deep-audit` runs Sonnet primary + Opus consult, but
Opus consult is gated by `consults_used`, not by cheap-filter survival.

Proposed change:

1. `js_run_audit(chain)` runs Sonnet pass with a strict
   "obvious-FP-reject" rubric (5 bullet-point disqualifiers). If
   Sonnet rejects, persist verdict=`false_positive` and stop.
2. Only survivors go to `js_consult_opus`. Opus output drives the
   PoC.
3. Cap Opus survivor count via `opus_budget_per_target` in memory.md.

Implementation note: this is a prompt + control-flow change, not a
new model. `js_analyzer/claude_agent.py` already has both Sonnet
and Opus calls — wire the gate.

## Cheap-stage rubric (draft)

Sonnet rejects a chain if any of:

- Source is a literal constant not user-controlled at any callsite.
- Sink is wrapped in a known-safe sanitizer call within the function
  body (DOMPurify.sanitize, encodeURIComponent for URL component
  context, JSON.stringify before innerHTML).
- All intermediate nodes are pure-function (no taint propagation).
- Source→sink path passes through a length check < 8 chars.
- Function is dead code (no inbound edges in callgraph).

If none fire, escalate to Opus.

## Cost math example

- Hot-chains in a target: 80
- Sonnet cost: $0.003/chain
- Opus cost: $0.30/chain (8 min thinking budget)
- Survival rate (Slice benchmark): ~5%
- Cost without cascade: 80 × $0.30 = $24
- Cost with cascade: 80 × $0.003 + 4 × $0.30 = $0.24 + $1.20 = **$1.44**
- ~16x cheaper, same TPs found.

## Related

- [[../../techniques/server-side/codeql-llm-ranking]] — Slice's
  reference description.
- [[source-code-review]] — three-root-causes model that informs the
  rubric.
- [[../../techniques/recon/ai-whitebox-source-review]] — sibling
  workflow that uses long-context (no RAG) for small bundles.
- [[../tlx/ai-whitebox-workflow]].

## Sources

- Caleb Gross, "Slice" — <https://noperator.dev/posts/slice/>
- CT Ep 128 "Source-code Review AI Bots" —
  <https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-128-new-research-in-blind-ssrf-and-self-xss-and-how-to-architect-source-code-review>
- CT Ep 137 — adjacent-function gap workflow pairs with this cascade.
