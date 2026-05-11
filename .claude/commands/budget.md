---
description: Print Opus + Caido replay spend so far for the current target, vs the budgets in memory.md. Usage: /budget or /budget <target-name>.
argument-hint: "[target-name]"
---

# /budget

Show per-target spend against the budgets defined in `memory.md`:

1. Resolve target (arg or current).
2. Read `targets/<name>/status.json`:
   - `opus_cost_usd` (sum across all opus-deep-audit + autoresearch
     iters)
   - `caido_replay_count` (sum of variants sent across all
     caido-replay + caido-idor runs)
3. Read `memory.md` budgets:
   - `opus_budget_per_target_usd`
   - `caido_replay_budget_per_target`
4. Print a 4-line table:
   ```
                spent     budget    %used
   opus_usd     X.XX      Y.YY      ZZ%
   caido_reqs   N         M         ZZ%
   ```
5. If either is >80%, print a warning. If >100%, print an explicit
   "stop and confirm before more spend" line.
