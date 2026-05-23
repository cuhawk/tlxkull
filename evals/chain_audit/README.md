# Chain audit eval set

Pinned regression set for `cc-taint-adversarial`. Promoted from
`notes/pipeline_calibration_2026-05-18.md` per the 2026-05-23
implementation plan.

## Purpose

Without an eval set, every change to taint logic
(`tlx/modules/js_analyzer/`, `implicit-tags`, `sanitizer-on-path`,
`cc-taint-adversarial`) is a coin-flip. You change something, hope
the TP rate didn't regress, and learn the truth weeks later when
the next confirmed bug fails.

This set is small (target 30 entries: 10 control + 10 edge + 10
boundary), but every entry is a real chain from a real engagement
with a hand-verified expected outcome. Re-run after every
non-trivial change to taint logic.

## Bucket semantics

| Bucket | Expected | Sourced from |
| --- | --- | --- |
| `control.jsonl` | `triage="runtime"` + confidence high|medium. **Known true positives** — chains that produced confirmed findings. | `findings/<id>/confirmed.json` + `opus/<id>.json` |
| `edge.jsonl` | `triage="drop"` + any confidence. **Known false positives** — chains the auditor correctly dropped. Catches over-firing. | `chains/_fp_archive.jsonl` and per-target `opus/*.json` with `triage="drop"` that turned out correct |
| `boundary.jsonl` | `triage="evidence_gap"`. **Should refuse to commit either way** — chains where the right answer is "I can't tell from static evidence alone". | Hand-curated from `opus/*.json` audited records with `_verifier_history` showing initial high-confidence verdict that got downgraded by the two-judge verifier |

The asymmetry matters: a regression in control = missed bug; a
regression in edge = FP storm and wasted browser-confirm budget;
a regression in boundary = audit pretends to know more than it does.

## Entry schema

Each line in the JSONL files is one entry:

```json
{
  "name": "<short id, kebab-case, unique within the file>",
  "source_target": "<target name this chain came from>",
  "chain": { ...full chain row as it appeared in chains/dom_reachable.jsonl... },
  "expanded": { ...the matching expanded snippet bundle... },
  "expected_triage": "runtime | evidence_gap | drop",
  "expected_confidence": "high | medium | low",
  "notes": "<2-4 sentences explaining why this is the expected outcome>"
}
```

`chain` and `expanded` are the same shape as in target dirs. Copy
them verbatim from a real run; do not handcraft. Hand-crafted
entries are worth nothing because they don't reflect the data the
auditor actually sees.

## How to populate

1. For each engagement where `cc-taint-adversarial` produced
   confirmed TPs, copy 1-2 chain+expanded pairs into
   `control.jsonl`. Anonymize target name if needed but keep the
   chain shape intact.
2. For each engagement where `cc-taint-route` archived a chain
   to `_fp_archive.jsonl` and the user manually verified it was
   correctly dropped, copy into `edge.jsonl`.
3. For chains where the two-judge verifier downgraded a
   high-confidence verdict (see `opus/<id>.json._verifier_history`),
   copy into `boundary.jsonl`.

Target: 10 entries per bucket. Quality > quantity — one curated
entry beats five hand-wavy ones. The set should grow ~1 entry per
real engagement, never bulk.

## How to run

```bash
# Phase 1 — render prompts for every entry
python3 bin/run_chain_eval.py prepare --bucket all

# Phase 2 — Claude Code dispatches one read-only subagent per prompt
#          (same pattern as cc-taint-adversarial), captures JSON
#          response to evals/chain_audit/_runs/<utc>/_responses/<name>.json

# Phase 3 — score each response against the expected outcome
python3 bin/run_chain_eval.py score --run <utc>
```

Score output: `evals/chain_audit/_runs/<utc>/score.json` plus a
markdown summary. Compares this run's per-bucket pass rate against
the previous run; flags regressions per bucket.

## Don't

- Don't auto-regenerate the eval set from current chains — that
  defeats the point. Eval entries are pinned snapshots.
- Don't grow `boundary.jsonl` past 15 entries; small and curated.
- Don't run the eval against a freshly-changed target; eval runs
  against frozen snapshots, not live data.
- Don't use the eval to grade other skills (browser-confirm,
  caido-replay). They get their own eval sets, separately, when
  they earn one.
