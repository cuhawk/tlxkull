# Chain DSL — spec (DEFERRED implementation)

Status: **spec only**. No code yet. Implement after the 2026-05-23
implementation batch (`plans/IMPLEMENTATION_2026-05-23.md`) proves
out the two-judge verifier and eval set are paying off.

Inspired by Elicit's AshPL DSL pattern shown at Code with Claude
London 2026 ("Making agentic workflows trustworthy and verifiable
with a custom DSL"). Same idea: stop having Opus reason against
opaque JSON; give it a Python-subset DSL that it can READ and
REWRITE, with content-addressable memoization on the AST.

## Motivation

Today a chain audit looks like:

1. `chains/dom_reachable.jsonl` holds rows of `{"id":"c123","source":{...},"path":[...],"sink":{...}}`.
2. `cc-taint-adversarial` renders a giant prompt with the chain JSON
   embedded, the auditor re-quotes the JSON in its reasoning, and
   emits a free-form `exploit_argument` / `counterargument`.
3. The two-judge verifier reads the auditor's prose + the same JSON.

Problems:
- **Opaque reasoning**: the audit transcript shows Claude quoting
  JSON keys back at itself. Hard to spot where it went wrong.
- **No memoization**: same chain, same prompt, same audit — every time.
- **No legible diff**: when the verifier downgrades, we can't easily
  see WHICH part of the auditor's claim changed.

DSL fix:
- Chain is represented as a small Python-subset declarative form.
- Auditor's job is to REWRITE the form with annotations + verdict
  fields filled in.
- Content-hash the form before and after; cache responses keyed by
  pre-rewrite hash.
- Verifier reads the rewritten form, not the prose.

## DSL shape (proposed)

```python
chain c042:
  source:
    kind = "url_fragment"
    qname = "Window.onhashchange.handler"
    file_line = "app.js:128"
    confidence = 1.0
  flows_through:
    - "parseHash @ app.js:135" via "implicit_closure(0.7)"
    - "decoded @ utils.js:42" via "direct"
    - "render @ render.js:88" via "direct"
  sanitizers_on_path:
    # auditor fills this after analysis:
    # - "DOMPurify.sanitize @ utils.js:55"  (dominates render call)
    []
  sink:
    kind = "dom_xss"
    qname = "Element.innerHTML.setter"
    file_line = "render.js:88"
    confidence = 1.0
  framework_context:
    family = "vanilla"
    csp = "default-src 'self'; script-src 'self'"
    trusted_types = false
  evidence:
    # auditor cites concrete lines used in their reasoning:
    - file = "render.js:85-92"
      excerpt = "el.innerHTML = decoded;"
      role = "sink_unguarded"
  verdict:
    # filled in last, after evidence + reasoning above:
    confidence = "high"
    triage = "runtime"
    rationale_ref = "exploit_argument"  # auditor's prose still lives separately
```

Key choices:

- **Python subset**: `chain c042:`, indented blocks, `key = value`,
  list literals. Easy for Claude to read AND write because it
  matches existing static-analysis idioms.
- **Comments are first-class** for "auditor's TODO" placeholders.
- **`verdict` block lives at the bottom** — reasons-first key order
  on the DSL too, mirroring the prompt-schema decision in
  cc-taint-adversarial.
- **Free-form prose** (`exploit_argument`, `counterargument`,
  `blocking_unknowns`) stays in the JSON record alongside the DSL.
  DSL = structured evidence; JSON = narrative.

## Memoization scheme

1. Compute `chain_hash = sha256(canonical_form_pre_audit)` where
   "canonical form" is the DSL serialized with stable key order,
   `verdict` block removed, comments stripped.
2. Lookup `chain_hash` in `targets/<name>/dsl_cache/<hash[:2]>/<hash>.json`.
3. If hit: skip the auditor subagent dispatch, reuse the cached
   verdict + evidence rewrite.
4. If miss: dispatch, write the post-audit DSL + verdict back to
   the cache, AND emit `opus/<chain_id>.json` as today.

Cache invalidation:
- Re-index of `js_analyzer.db` → chain payload changes → new hash.
- New `framework_context` (e.g. CSP changed) → new hash.
- Manual: `python3 bin/chain_dsl.py invalidate --chain-id c042`.

## Migration

Phase 1 (write):
- `bin/chain_dsl.py emit --target <name>` reads
  `chains/dom_reachable.jsonl` + `chains/expanded/<id>.json` and
  writes `chains/dsl/<id>.dsl` per chain.
- DSL emitter is pure Python (no LLM).

Phase 2 (read in audit):
- `cc-taint-adversarial` prompt body changes: instead of embedding
  raw JSON in `{{EVIDENCE_PAYLOAD}}`, embed the `.dsl` file's content.
- Subagent's task: output JSON (today's schema) PLUS the rewritten
  DSL with `evidence`, `sanitizers_on_path`, and `verdict` filled.
- Ingest validates both: JSON schema (today) + DSL re-parse (new).

Phase 3 (read in verifier):
- Verifier sees the rewritten DSL. Easier to spot
  `sanitizers_on_path: []` when there's an obvious DOMPurify call
  in the expanded snippet.

Phase 4 (cache):
- `bin/chain_dsl.py cache-status --target <name>` reports hit rate.
- Re-runs of `cc-taint-adversarial` after taint-logic changes show
  measurable speedups (most chains haven't changed; cache hits).

## What this does NOT change

- The eval set (`evals/chain_audit/`) still uses
  `chains/dom_reachable.jsonl` shape — the DSL is an additional
  rendering, not a replacement. Eval entries don't need DSL form.
- The two-judge verifier still uses JSON-only output. The DSL is
  evidence; the verifier's verdict structure stays.
- `chains/_fp_archive.jsonl` and `_re_expand_queue.jsonl` shapes
  stay JSON-only; only the auditor + verifier prompts get the DSL.

## When to actually build this

Don't start until ALL of these are true:

1. Two-judge verifier is in steady use AND has surfaced ≥5
   false-positive verdicts that the verifier caught.
2. Eval set has at least 15 entries across the three buckets.
3. `cc-taint-adversarial` has run on ≥4 fresh targets and per-target
   audit cost is measurably the bottleneck of the engagement.

Before that, the DSL is yak-shaving. Audit quality > audit speed.

## Open questions

- DSL parser: hand-rolled (small subset, ~200 LoC) or use a
  pip-installable PEG / `lark`? Hand-rolled is fewer deps; `lark`
  is more maintainable. Decision deferred.
- Should `evidence[].excerpt` be inlined into the DSL or referenced
  by `file_line`? Inlining helps cache stability but inflates
  prompt size. Reference-only saves tokens but loses portability.
  Probably reference + materialize at prompt-render time.
- Versioning: DSL format will evolve. Embed `dsl_version: 1` at
  top of every file from day one.

## References

- Code with Claude London 2026 — "Making agentic workflows
  trustworthy and verifiable with a custom DSL" (Elicit talk).
- `plans/IMPLEMENTATION_2026-05-23.md` — defers this in favour of
  six smaller wins first.
- `plans/CC_TAINT_ADVERSARIAL.md` — existing chain audit pipeline
  this DSL plugs into.
