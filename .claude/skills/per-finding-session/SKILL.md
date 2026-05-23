---
name: per-finding-session
description: Fan-out browser-confirm queue — one CC subagent per finding (browser-confirm → confirmed.json → report-finding). Trigger: /per-finding-session <target>, "drain the confirm queue in parallel", "one session per finding".
---

# per-finding-session

## Purpose

Replace the serial `browser-confirm` queue-drain with a fan-out
pattern: one read-write subagent per queued chain. Mirrors the
Anthropic Cloud Security UX where each scanner finding gets its
own dedicated Claude session, observable independently in the
agents-view dashboard. Local equivalent here: one
`general-purpose` subagent per finding, each with isolated
context + its own per-finding scratch dir.

Why this matters:

- **Context isolation.** Main session no longer accumulates all
  chains' DOM dumps + screenshots + console messages. Each
  finding's noise stays in its own subagent.
- **Parallel progress.** Three findings can advance simultaneously
  instead of waiting for the first one's CSP analysis.
- **Failure isolation.** A misbehaving subagent on one finding
  (e.g. live target blocks IP) doesn't poison the queue.
- **Better evidence.** A subagent dedicated to one chain reasons
  more carefully than a tired main session on chain #12.

## Hard rules

1. **Cap concurrency at 3.** More than 3 parallel browser
   sessions through Caido overloads the queue and times out.
2. **Subagents are NOT read-only** — they may `Write` /
   `Edit` inside `targets/<name>/findings/<chain_id>/`. They MAY
   NOT write anywhere else (no global wiki edits, no
   status.json mutations outside the per-finding payload).
3. **No live HTTP without consent.** If `memory.md` flags the
   target as live-sensitive (e.g. Synack), refuse dispatch and
   recommend manual review.
4. **No Anthropic API direct call.** No `ANTHROPIC_API_KEY`,
   no Gemini chat models. Subagents are Claude Code
   `general-purpose` only.
5. **Idempotent.** Re-running skips chains that already have
   `findings/<id>/confirmed.json` OR `findings/<id>/failed.json`.

## Inputs

| Path | Required | Producer |
| --- | --- | --- |
| `targets/<name>/findings/_queue_browser_confirm.jsonl` | required | `cc-taint-route` |
| `targets/<name>/status.json` | required | `target-init` |
| `memory.md` for live/mock + sensitivity preference | required | n/a |
| `chrome-devtools` MCP | required (live mode) | system |
| Caido running on `:8443` (live mode) | required | `caido-capture` |

## Steps

### Step 1 — plan (BLOCKING)

```bash
python3 bin/per_finding_dispatch.py plan --target <name>
```

Writes `targets/<name>/findings/_dispatch_plan.json`:

```json
{
  "ts": "<utc>",
  "target": "<name>",
  "mode": "live | mock",
  "queue_size": N,
  "pending": [
    {"chain_id": "...", "triage": "runtime", "confidence": "high",
     "scratch_dir": "findings/<id>/",
     "already_confirmed": false, "already_failed": false}
  ],
  "max_parallel": 3,
  "estimated_minutes_per_finding": 8
}
```

Skips chains that already have `confirmed.json` or `failed.json`.
Default `mode` derives from `memory.md` Caveat: live-sensitive
targets force `mode=mock`.

### Step 2 — dispatch (per batch of up to 3)

Read the plan. Pick the next 1-3 pending chains. For each, dispatch:

```
Agent(
  subagent_type="general-purpose",
  description="per-finding session: <chain_id>",
  prompt=<rendered from .claude/skills/per-finding-session/prompts/finding.md>,
)
```

The prompt body embeds:

- chain_id, target name, target dir
- chain payload (from the queue entry)
- opus record (`opus/<chain_id>.json`)
- mode (live / mock)
- scratch dir
- the inline-prose body of the browser-confirm SKILL.md Step 2/3
  flow PLUS the `bin/poc_verify_contract.js` DOM-contract reader
  (cite location, don't inline the entire JS file)
- the success criteria (writes `confirmed.json` OR `failed.json`)
- forbidden actions (no wiki writes, no global status.json edits,
  no Anthropic API calls)

Wait for all subagents in the batch to return before dispatching
the next batch. Subagent returns either:

- Success: `{"chain_id": "...", "outcome": "confirmed | failed |
  csp_blocked", "files_written": [...]}`
- Failure: raises with a short reason; the orchestrator logs to
  `findings/_dispatch_errors.jsonl` and moves on.

### Step 3 — collect

```bash
python3 bin/per_finding_dispatch.py collect --target <name>
```

Scans `findings/*/{confirmed,failed}.json`, updates
`status.json.phases.browser_confirm.confirmed_ids` /
`failed_ids` accordingly, prunes drained entries from
`_queue_browser_confirm.jsonl`.

### Step 4 — followups

For each `findings/<id>/confirmed.json` that has no
corresponding `<id>.md` writeup, queue `report-finding`. This
remains serial — writeups don't parallelise well.

## Failure modes

| Symptom | Action |
| --- | --- |
| Caido times out (queue blocked) | Per `memory.md feedback_caido_queueing_blocks_browser` — pause Caido intercept, flush queue, retry. |
| Live target rate-limits | Drop mode to mock; re-queue affected chains. |
| Subagent emits prose instead of JSON | Mark chain as `dispatch_failure`, leave on queue, surface to user. |
| Multiple subagents collide on the same `findings/<id>/` | Shouldn't happen (one chain per subagent); if it does, error to `_dispatch_errors.jsonl` and skip. |
| CSP blocks PoC | Subagent writes `findings/<id>/csp_notes.md` and exits with `outcome=csp_blocked`. Don't auto-retry — needs human bypass design. |

## Result block

`status.json.phases.per_finding_session`:

```json
{
  "status": "draining | done",
  "ts": "<utc>",
  "batches_run": N,
  "subagents_dispatched": K,
  "confirmed": [...],
  "failed": [...],
  "csp_blocked": [...],
  "errors": [...]
}
```

## Why this exists

Per Anthropic Cloud Security (2026-05): "Each finding gets its own
session so the analyst can drop into any single investigation
without context bleed from the others." TLX adopts the same UX
locally — fan-out subagents replace the dashboard-managed
sessions. Tradeoff: no dashboard yet, but full Linux + git history
beats a hosted UI for our scale.

If `agents-view` dashboard becomes a thing locally (already in
the CC desktop preview), this skill's UX gets a free upgrade.
