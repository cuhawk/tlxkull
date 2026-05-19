---
description: Report targets stuck at hot->audited workflow gap (per notes/pipeline_calibration_2026-05-18.md). Usage: /audit-gap [target-name].
argument-hint: "[target-name]"
---

# /audit-gap

Surface the static-vs-audit gate diagnosed in
`notes/pipeline_calibration_2026-05-18.md`. Static analysis hands
`chains/hot.jsonl` to the pipeline; on big targets the audit phase
never fires because the session ends first.

Steps:
1. If `$ARGUMENTS` is empty, run
   `python3 bin/audit_gap_check.py` (every target).
   Otherwise: `python3 bin/audit_gap_check.py --target $ARGUMENTS`.
2. For each gap, print the `next_step` command verbatim — the user
   can dispatch directly.
3. If `/audit-gap` returns empty, say "no audit gaps" and stop.

Install as a SessionStart hook (one-time, user-approved):
```
python3 bin/install_audit_gap_hook.py
```
That edits `.claude/settings.json` to run the same check at every
session boot.
