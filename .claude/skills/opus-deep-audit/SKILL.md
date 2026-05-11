---
name: opus-deep-audit
description: Deep-audit each chain in chains/dom_reachable.jsonl (fallback chains/hot.jsonl) using TLX's Sonnet→Opus advisor pipeline (js_run_audit + js_audit_status). Writes opus/<chain_id>.md with verdict + reasoning + proposed PoC. Respects opus_budget_per_target_usd from memory.md. Run after dom-xss-hunt. Verdict ∈ {true_positive, false_positive, undetermined}.
---

# opus-deep-audit

## Purpose
Use Opus (via TLX's bounded advisor) to apply real reasoning to chains
that survived static + reachability filtering. This is where TP rate
gets earned.

## Inputs
- `targets/<name>/chains/dom_reachable.jsonl` (preferred) or
  `chains/hot.jsonl` (fallback if dom hunt was skipped).
- budget: `memory.md > opus_budget_per_target_usd`.

## Steps
1. Read budget. If `status.json.opus_cost_usd` already at limit,
   halt and require user to raise.
2. For each chain in input file:
   a. `js_examine_chain(chain_id=...)` → full source/sink/path.
   b. `js_get_snippet(qname=...)` for each function in the path
      adjacent ±1 hop.
   c. Compose the audit context (chain detail + snippets + framework
      hints + relevant `wiki/techniques/<sink_kind>/` page if exists —
      retrieve via `docs_query` against the wiki collection).
   d. Trigger `js_run_audit(target_folder=...)` if not already running
      for this target (it's a fire-and-forget audit loop that uses the
      Sonnet→Opus advisor internally).
   e. Poll `js_audit_status(run_id=...)` until `status == "done"`.
   f. Pull verdict + reasoning + PoC from audit output.
3. Write `targets/<name>/opus/<chain_id>.md` with sections:
   - Chain summary
   - Source / sink / path
   - Audit verdict
   - Reasoning trace (summarized — full transcript is in TLX SQLite)
   - Proposed PoC (HTML / curl / browser steps)
4. Submit verdict via `js_submit_finding(chain_id, verdict, proof)`.
5. Track cost: read `js_audit_status` cost fields, add to
   `status.json.opus_cost_usd`.

## Outputs
- `targets/<name>/opus/<chain_id>.md` per chain.
- updated `status.json.phases.opus`.

## Failure modes
- Budget exceeded mid-batch → halt, write partial result block,
  notify user.
- `js_run_audit` errors out → log to `status.json.errors`, mark chain
  `verdict: undetermined` so `autoresearch-loop` can retry later.
- Opus verdict says TP but proposed PoC obviously wrong → write
  verdict but flag `requires_user_review: true` in result block.

## Result block
```json
"phases": { "opus": { "status": "done", "ts": "<iso>",
  "chains_audited": N, "tp": X, "fp": Y, "undetermined": Z,
  "opus_cost_usd": Decimal, "user_review_flagged": [...] } }
```
