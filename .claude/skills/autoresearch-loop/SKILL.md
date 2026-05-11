---
name: autoresearch-loop
description: Karpathy autoresearch pattern applied to bug hunting. Time-budgeted loop over open chains. Each iter generates an exploit hypothesis via Opus, runs minimum-viable test (mock | live | caido), judges via Opus, logs append-only to autoresearch.jsonl. Fixed 5-min wall-clock per iter mirrors Karpathy's spec (≈12 iters/hour). Trigger: "loop <target> <minutes>" or auto after hot chains done if user opted in.
---

# autoresearch-loop

## Purpose
Apply Karpathy's autoresearch pattern (autonomous experiment loop with
reviewable scope + fixed time budget per iter) to bug hunting. Lets
Claude keep working on a target overnight, pursuing chains too cold for
Opus's first pass but worth probing with concrete tests.

## Inputs
- `targets/<name>/chains/all.jsonl` (full chain inventory)
- `targets/<name>/chains/dom_unreachable.jsonl` + `chains/hot.jsonl`
  already-processed (skip set)
- Total budget: `<minutes>` (default `memory.md > autoresearch_default_minutes`).
- Per-iter budget: `autoresearch_iter_max_minutes` (default 5).

## Loop
```
start_t = now()
while now() - start_t < total_budget:
    iter_t = now()
    chain = pick_next_chain()                    # see scoring below
    if chain is None: break

    hyp   = generate_hypothesis(chain)           # opus, single-shot
    test  = minimum_viable_test(hyp)             # one of:
              # - mock_confirm against mock
              # - browser-confirm live
              # - caido-replay variant set
    score = judge(hyp, test)                     # opus, single-shot

    append_jsonl("autoresearch.jsonl", {
        iter, ts, chain_id, hyp, test_kind, test_result,
        score, verdict, cost_usd, duration_s
    })
    update_chain_state(chain, verdict, score)

    if now() - iter_t > per_iter_max: log_timeout
```

## Chain picking — marginal information gain
For each candidate chain not yet probed, compute:

```
score = expected_severity_if_TP * uncertainty_about_TP
      - probed_cost_estimate
```

Highest score wins. Re-rank after every iter (a confirmed
true_positive in one sink kind raises priors on similar sinks).

## Test kind chooser
- DOM sinks with no auth required → mock_confirm (cheapest).
- DOM sinks needing real auth context → browser-confirm live.
- Server-side sinks (auth, IDOR signals via path) → caido-replay set.

## Outputs
- `targets/<name>/autoresearch.jsonl` (append-only).
- `targets/<name>/autoresearch_summary_<run_id>.md` (post-loop).
- updated chain verdicts in `chains/all.jsonl`.

## Failure modes
- Per-iter timeout exceeded → log "iter_timeout", continue. Don't
  count cost against the chain (it's an env problem, not a chain
  problem).
- Opus budget exceeded mid-loop → halt; emit partial summary; note
  budget block prominently to user.
- All chains probed before budget exhausted → halt early; emit
  summary; suggest re-running with a wider chain set or new
  `js-index` after target changes.

## Result block
```json
"phases": { "autoresearch": { "status": "done", "ts": "<iso>",
  "iters": N, "budget_min": B, "elapsed_min": E,
  "new_tp": X, "new_fp": Y, "still_undetermined": Z,
  "opus_cost_usd": Decimal } }
```

## Notes
- Karpathy autoresearch: `https://github.com/karpathy/autoresearch`
- Single-file-scope analog: every iter writes ONE jsonl line. That's
  the analog of "agent edits one `train.py`". Audit by reading the
  jsonl chronologically.
