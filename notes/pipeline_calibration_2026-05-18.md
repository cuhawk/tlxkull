# Pipeline calibration audit — 2026-05-18

Gate diagnostic for `project_implicit_tags_plan`. Method per memory note.

## Stage counts (last 3 engagements with non-empty `chains/`)

| Target | all | hot | audited | confirmed_tp | submitted |
|---|---:|---:|---:|---:|---:|
| netlify-h1 | 500 | 20 | 0 | 0 | 0 |
| coolblue-intigriti | 859 | 20 | 0 | 0 | 0 |
| coralbug3-syn | 4 | 4 | 4 | 0 | 0 |

## Drop analysis

- **all → hot**: 25x (netlify), 43x (coolblue), 1x (coralbug3).
  Big targets hit the `hot.jsonl` 20-row cap. Triage scoring is the
  bottleneck for any project with >20 viable chains. Implicit tags
  alone won't lower the ratio — it'll widen the `all` set further —
  but the *quality* of the top-20 selection is what matters, and that
  depends on `source_conf × sink_conf` multiplier (Phase 1 + triage
  patch in the plan).

- **hot → audited**: 0/20 on both big targets. The audit phase never
  fired. Separate workflow issue (likely user abandoned the engagement
  before running `cc-taint-adversarial` / `opus-deep-audit`). Not a
  static-analysis lever problem. **Flag and out-of-scope for this
  build.**

- **audited → confirmed**: 0/4 on coralbug3. 4 Opus runs, all
  `false_positive`. n=4 is noisy but consistent with the FP-rate
  hypothesis Phase 2 (sanitizer-on-path CFG-dominance) targets.

- **confirmed → submitted**: no data (zero confirmed).

## Verdict

**Proceed with implicit-tags plan.** Justification:

1. The dominant signal where data exists is `all → hot` scoring
   pressure. Plan's Phase 1 + chain-triage patch addresses it
   directly via per-tag confidence multipliers, allowing widened
   source/sink sets without diluting the top-20 hot subset.
2. Coralbug3 4/4 FP, while small-n, aligns with the Phase 2
   sanitizer-on-path goal. Even one prevented FP per audit run
   improves Opus budget efficiency.
3. The `hot → audited` zero is a workflow gap (audits not run), not
   addressable by static analysis improvements. Track separately.

## Out-of-scope flags for this build

- **Audit-trigger workflow gap**: `hot.jsonl` exists but `opus/` is
  empty. The user's session-completion habit, not implicit tags, is
  the bottleneck on netlify + coolblue. Fix separately.
- **Sample size**: only 4 fully-audited chains across 3 engagements.
  Validation phase of the plan needs at least 2 fresh targets run
  end-to-end to measure the ≥30% surface / ≥1 new TP acceptance
  criteria honestly.

## Audit data sources

- `targets/netlify-h1/chains/{all,hot}.jsonl`
- `targets/coolblue-intigriti/chains/{all,hot}.jsonl`
- `targets/coralbug3-syn/chains/{all,hot,dom_reachable,dom_unreachable}.jsonl`
- `targets/coralbug3-syn/opus/*.md` (verdicts: `grep -iE verdict opus/*.md`)
