---
name: caido-idor
description: Generic IDOR + broken-access-control sweep. Wraps bin/idor_sweep.py (plan + consume) plus the Caido MCP. Pattern-driven — auto-detects ID-shaped params (int, uuid, objectid, email, hashid, ...) in URL path / query / headers / body across every captured request, generates shape-respecting mutations + auth-swap variants, replays through Caido, classifies responses via body-parity diff. Trigger when the user says "idor sweep", "access control check", or memory.md > auto_idor_on_capture is true.
---

# caido-idor

## Purpose

Industrialize the manual "what if I send this request as user B?" +
"what if I bump the id by one?" + "what if I drop the cookie?" checks.

Pattern-based and target-agnostic — works on every program without
per-target tuning. Per-target inputs (peer ids, alt identities) are
optional and only sharpen results.

## Inputs

1. **A Caido project** with captured authenticated traffic
   (`caido-capture` skill provides this).
2. **`targets/<name>/caido/identities.json`** (optional, REQUIRED for
   IDOR signal — BAC still works without it):
   ```json
   {
     "userB":     {"Cookie": "session=...", "Authorization": "Bearer ..."},
     "lowPriv":   {"Cookie": "session=..."},
     "otherTenant": {"Cookie": "session=..."}
   }
   ```
   Cookies/tokens belong in this file only — `.gitignore` covers
   `caido/identities.json`. NEVER commit.
3. **`targets/<name>/caido/peer_ids.json`** (optional — list of
   identifier *values* known to belong to other users; the cleanest
   mutation type):
   ```json
   ["00000000-0000-0000-0000-000000000001", 12345, "alice-2"]
   ```

## Steps

### 1. Capture is in place

```
caido_select_project(<project-id-from-status.json>)
caido_list_requests(project=..., filter={status:[200,201,204,206,302]}, limit=N)
```
Stream rows to `targets/<name>/caido/idor/requests.jsonl` — one line per
request, fields `{id, method, url, headers, body}`.

If the capture has < 10 authenticated requests, halt and ask the user
to browse the target for 10+ minutes via `caido-capture`.

### 2. Build the variant plan

```
python3 bin/idor_sweep.py plan <target> \
    --requests targets/<target>/caido/idor/requests.jsonl \
    [--max-mutations 6]
```

Outputs `targets/<target>/caido/idor/plan.jsonl`. Each line is one
variant to send: baseline (re-send as-captured), `no_auth` (cookies
stripped), `swap_auth:<env>` (per identity from `identities.json`),
and `mutate:<location>:<name>:<mutation>` per shape-respecting mutation
the detector produced.

For an integer `user_id`: `+1`, `-1`, `+2`, `-2`, `0`, `-1`,
INT32_MAX, type-confusion (stringify), empty, null, `[...]` wrap,
`*` wildcard, plus any `peer_ids.json` values. For UUIDs: nil-UUID,
last-char-flip, random-deterministic. For ObjectIds: increment hex.
For emails: `admin@<domain>`, `+idor` tag aliasing.

### 3. Execute the plan through Caido

For each row in `plan.jsonl`, send the variant via Caido MCP and
append the response to `targets/<target>/caido/idor/results.jsonl`:

```
caido_send_request(
    method=row.request.method,
    url=row.request.url,
    headers=row.request.headers,
    body=row.request.body,
)
```

Batch in chunks of 50 with `caido_batch_send` when available. Respect
`memory.md > caido_replay_budget_per_target` (5000 by default) — halt
when the budget is hit; the consume phase can run on a partial
results file.

Each result row:
```json
{"request_id": "...", "variant": "...", "status": 200, "body": "..."}
```

Rate-limit handling: if any response has `Retry-After`, sleep that
many seconds. If three consecutive responses are 429, halve the
concurrency and continue.

### 4. Consume + classify

```
python3 bin/idor_sweep.py consume <target>
```

Reads `plan.jsonl` + `results.jsonl`, joins on `(request_id, variant)`,
diffs each variant against its `baseline`, applies the taxonomy from
`bin/response_diff.py`:

- `bac_candidate`    — `no_auth` variant returned ≥ 0.8 body parity
                       with baseline.
- `idor_candidate`   — `swap_auth:<env>` or `mutate:*:peer_value:*`
                       returned ≥ 0.8 parity.
- `leak_partial`     — 0.4 ≤ parity < 0.8 AND variant body contains
                       PII regexes (email/phone/Luhn-valid card/SSN).
- `access_denied`    — variant 4xx/5xx while baseline 2xx (defense in
                       place; not a finding).
- `noisy`            — neither.

Writes:
- `targets/<target>/caido/idor/candidates.jsonl`
- `targets/<target>/findings/idor-candidates.md`

### 5. Triage the markdown

Sort by category rank (BAC > IDOR > leak_partial), then by confidence.
For each top-N candidate:

- Open the matching `request_id` + variant in Caido Replay (the
  driver records `request_url` + `mutation` + `candidate` info).
- Re-send manually to confirm not flaky.
- If confirmed, run `report-finding` skill — it will pull the diff
  from `candidates.jsonl` and produce the writeup.

## Outputs

- `targets/<target>/caido/idor/requests.jsonl` — captured-request input.
- `targets/<target>/caido/idor/plan.jsonl`     — variant plan.
- `targets/<target>/caido/idor/results.jsonl`  — Caido responses.
- `targets/<target>/caido/idor/candidates.jsonl` — classified findings.
- `targets/<target>/findings/idor-candidates.md` — human-readable triage.

## Failure modes

- `identities.json` missing → BAC sweep still runs; IDOR mutations
  fall back to `peer_ids.json` only. Surface as "BAC-only mode".
- Auth cookie/token in `identities.json` is expired → swap_auth
  variants all 401. Detector classifies as `access_denied`; surface
  to user "userB credentials look expired".
- Caido project not selected → `caido_list_requests` returns 0 rows.
  Halt and ask user to run `caido_select_project`.
- Volume too large → respect `caido_replay_budget_per_target`. Halt
  mid-execution, persist `results.jsonl`, resume on next run by
  skipping rows already present.

## Result block

```json
"phases": {
  "idor_sweep_plan":    { "status": "done", "ts": "<iso>",
                          "requests": N, "variants": M },
  "idor_sweep_consume": { "status": "done", "ts": "<iso>",
                          "candidates": K,
                          "by_category": { "bac_candidate": ...,
                                           "idor_candidate": ...,
                                           "leak_partial": ... } }
}
```

## Architecture note — why plan/consume split

`bin/idor_sweep.py` is pure Python and never calls MCP. The Caido
execution layer (step 3 above) is the only piece that touches the
network, and it lives in the *skill* (this file's instructions, run
by Claude Code) — that's the only environment where the
`mcp__caido__*` tools are reachable. The split keeps mutation logic
testable + lets the same plan be replayed by hand if the user wants
to verify a specific variant.

## Tests

- `bin/tests/test_id_patterns.py` (28 tests) — name scoring, value
  classification, candidate extraction across all 4 locations,
  per-shape mutation generation.
- `bin/tests/test_response_diff.py` (23 tests) — normalization, body
  parity, PII detection (incl. Luhn), variant classification taxonomy.
- `bin/tests/test_idor_sweep.py` (11 tests) — mutation-application
  per location, variant-plan building, full plan→consume integration
  on a tmp target.
