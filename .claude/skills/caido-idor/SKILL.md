---
name: caido-idor
description: Sweep every authenticated request captured by caido-capture against a role matrix (no-auth, user-A, user-B) plus ID-mutation to surface IDOR and broken-access-control candidates. Run when the user says "idor sweep" or when memory.md > auto_idor_on_capture is true. Requires two sets of auth creds referenced from http.md.
---

# caido-idor

## Purpose
Industrialize the manual "what if I send this request as user B?"
check. Across hundreds of captured requests, the patterns that emerge
are almost always real bugs.

## Inputs
- `targets/<name>/status.json.auth.creds` with at least two distinct
  identities (referenced via `caido_workflow:<id>`).
- Caido project from `caido-capture` containing recent requests.

## Steps
1. Acquire cookie/header for each identity via
   `caido_workflow_run(workflow_id)`. Cache in
   `targets/<name>/caido/auth_cache.json` (NEVER commit; gitignore
   already covers `auth_cache.json`).
2. List candidate requests:
   `caido_requests_list(project, filter={status: [200,201,204,206,302]})`.
3. For each request:
   - **no-auth** variant: drop cookie/Authorization header.
   - **swap-auth** variant: replace with user-B's cookie.
   - **swap-id** variants: if URL or body has numeric/UUID/email
     fields, replace with peer-owned known values from
     `targets/<name>/caido/peer_ids.json` (user-curated).
4. For each variant, replay via `caido-replay` (call the skill
   programmatically — meaning: invoke the same MCP tools the skill
   wraps). Capture diffs.
5. Classify:
   - **idor_candidate** = swap-auth returned ≥80% body parity with
     baseline (peer data leaks across accounts).
   - **bac_candidate**  = no-auth returned ≥80% body parity with
     baseline (no auth required).
   - **noisy**          = neither.
6. Write summary to `targets/<name>/findings/idor-candidates.md`
   sorted by severity (auth-leak > id-leak > nuisance).

## Outputs
- `targets/<name>/caido/idor/<request_id>.json` per request.
- `targets/<name>/findings/idor-candidates.md` (consolidated).

## Failure modes
- Auth workflow returns 401/forbidden → workflow stale; user must
  re-record in Caido GUI. Halt and surface.
- Body parity is misleading due to per-user content (e.g. timestamps,
  avatars) → user can extend `ignore_body_regex` in
  `targets/<name>/caido/replay_overrides.json`.
- Volume too large → respect `caido_replay_budget_per_target` from
  memory.md; halt mid-sweep, persist state, resume on next run.

## Result block
```json
"phases": { "idor": { "status": "done", "ts": "<iso>",
  "requests_swept": N, "idor_candidates": M, "bac_candidates": K } }
```
