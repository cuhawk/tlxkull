# Gmail sweep — invite tracker prompt

Used by the `target-invite-sweep` CC skill. Per-platform query patterns
are stable strings; do NOT paraphrase.

## Per-platform queries

Replace `${days}` with `--backfill-days` value at run time
(default 7, backfill mode passes 365 or 730).

| Platform | Query |
|---|---|
| HackerOne | `from:no-reply@hackerone.com subject:"invited you to their HackerOne program" newer_than:${days}d` |
| Intigriti | `from:noreply@intigriti.com (subject:"Application accepted" OR subject:"was accepted by" OR subject:"You have been invited to join") newer_than:${days}d` |
| Bugcrowd | `from:support@bugcrowd.com subject:"New Engagement Invite" newer_than:${days}d` |
| Synack | `from:support@synack.com subject:"onboarded on target" newer_than:${days}d` |

## Output protocol

The skill calls `mcp__claude_ai_Gmail__search_threads` with each query
(pageSize=50, paginate via `pageToken` until exhausted), then **emits
NDJSON to stdout**: one line per thread dict from the MCP response.
Nothing else on stdout — no prose, no markdown.

```
{"id":"...","messages":[{"id":"...","sender":"...","subject":"...","snippet":"...","date":"..."}]}
{"id":"...","messages":[...]}
...
```

`routine.sh` pipes this into `parse_invites.py` which de-dupes against
`inbox/invites/` and emits `READY`/`DUPLICATE`/`REINVITE` markers.

## Bugcrowd body fetch

Bugcrowd subjects are opaque (`A New Engagement Invite`). The
engagement name lives in the HTML body. After listing threads,
for each Bugcrowd thread call
`mcp__claude_ai_Gmail__get_thread(threadId=..., messageFormat=FULL_CONTENT)`
and inline the `plaintext_body` field into the emitted thread JSON
under `messages[0].plaintext_body`. `parse_invites.py` uses that field
to extract the engagement name when present.

## Failure modes

- Gmail MCP returns 401 → skill exits non-zero with stderr
  `gmail_auth_failed`. Re-auth Claude.ai Gmail MCP, then re-run.
- Empty result for all 4 platforms → exit 0 with no output (legitimate
  no-op for a quiet day).
