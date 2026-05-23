---
name: target-invite-sweep
description: Sweep Gmail for new bug-bounty program invitations across HackerOne / Intigriti / Bugcrowd / Synack. Idempotent — de-dupes against inbox/invites/. Trigger: /target-invite-sweep (manual) or routines/target-discover/routine.sh (daily).
---

# target-invite-sweep

Gmail-driven discovery of new bug-bounty program invitations. Emits
NDJSON to stdout for the deterministic parser
`routines/target-discover/parse_invites.py` to consume.

## When to invoke

- Automatic: `routines/target-discover/routine.sh` fires this daily via
  launchd at 07:00 local.
- Manual: `/target-invite-sweep` or
  `/target-invite-sweep --backfill-days 730 --emit ndjson`.

## Arguments

| flag | default | meaning |
|---|---|---|
| `--backfill-days <N>` | 7 | Window for Gmail `newer_than:Nd`. Use 365 or 730 for first-run backfill. |
| `--emit ndjson` | required by routine.sh | strict stdout protocol; no prose |

## Per-platform queries (DO NOT paraphrase)

```
hackerone:  from:no-reply@hackerone.com subject:"invited you to their HackerOne program" newer_than:${days}d
intigriti:  from:noreply@intigriti.com (subject:"Application accepted" OR subject:"was accepted by" OR subject:"You have been invited to join") newer_than:${days}d
bugcrowd:   from:support@bugcrowd.com subject:"New Engagement Invite" newer_than:${days}d
synack:     from:support@synack.com subject:"onboarded on target" newer_than:${days}d
```

## Execution

1. For each of the four queries:
   - Call `mcp__claude_ai_Gmail__search_threads(query, pageSize=50)`.
   - Paginate via `pageToken` until response has no `nextPageToken`.
2. For Bugcrowd threads only: subjects are opaque ("A New Engagement
   Invite"); engagement name is in the HTML body. Per thread call
   `mcp__claude_ai_Gmail__get_thread(threadId, messageFormat=FULL_CONTENT)`
   and inline the resulting `plaintext_body` field into the thread JSON
   at `messages[0].plaintext_body`. Parser uses this to extract the
   engagement name.
3. Emit one JSON object per line to stdout — exactly the thread dict
   as returned by the MCP, optionally with `plaintext_body` added.
4. Nothing else on stdout. No prose, no markdown, no progress logs.
   Errors go to stderr.

## Error handling

- Gmail MCP returns 401 / not-authenticated → exit non-zero, stderr
  `gmail_auth_failed`.
- Empty result for all four queries → exit 0, no stdout (legitimate
  quiet-day no-op).
- Any partial failure (one query 500s, others succeed) → emit what was
  collected, stderr-log the failed platform, exit 1.

## Result block (when invoked manually)

If invoked manually with no `--emit ndjson`, emit a human-readable
summary instead:

```
target-invite-sweep — backfill 7d
  hackerone: 1 new
  intigriti: 0
  bugcrowd:  0
  synack:    3 new
  → inbox/invites/ written (4 seeds, 0 duplicates, 0 reinvites)
```

## Hard rules

- **Never write directly to `targets/`**. Only the parser writes inbox
  seeds; only `target-promote` (separate skill) creates target dirs.
- **Never delete an existing seed** under `inbox/invites/`.
- **Synack tracking-only**. Synack invites flow through the same pipe,
  but downstream `target-promote` flags them as
  `lifecycle: synack-tracked-only` per
  memory `feedback_synack_no_live_visits`.
