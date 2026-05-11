---
description: Start autoresearch-loop for the current target. Usage: /loop <minutes>.
argument-hint: "<minutes>"
---

# /loop

Invoke the `autoresearch-loop` skill with:
- `target` = current target (from memory.md)
- `total_budget_minutes` = `$ARGUMENTS` (integer minutes)

Iters write append-only to `targets/<current>/autoresearch.jsonl`.
A summary file is written when the budget is exhausted or all open
chains are processed.

Warn user if `$ARGUMENTS > 240` (4 hours) and ask to confirm.
