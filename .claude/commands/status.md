---
description: Print the pipeline status of the current (or named) bug-bounty target. Usage: /status or /status <target-name>.
argument-hint: "[target-name]"
---

# /status

Show `targets/<name>/status.json` formatted for the human eye:

1. If `$ARGUMENTS` is empty, read `memory.md > Current target` and use
   that. If no current target, print the list of all targets and ask.
2. Read `targets/<name>/status.json`.
3. Print:
   - target name + created date
   - scope summary (N in / N out)
   - per-phase status (init, harvest, explode, rag, index, triage,
     dom_hunt, opus, browser_confirm, caido_capture, replay, idor,
     autoresearch, report) with timestamps and key counts
   - findings count (TP / FP / undetermined)
   - opus cost so far vs budget
   - last error if any
4. End with a one-line suggestion of the next skill to run.
