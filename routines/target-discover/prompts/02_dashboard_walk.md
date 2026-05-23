# Dashboard walk — new-program + scope-change detector

**Status: v0.2 — not yet wired into routine.sh.** Requires cookies
bootstrapped first.

## Purpose

Gmail covers *invitations*, but platforms add new public programs
without emailing. And existing in-scope assets change frequently.
This walk:

1. Visits each platform's program-list dashboard (paginated) using a
   headless Chromium with injected session cookies.
2. Diffs against `inbox/known_programs.json` for new program slugs.
3. For each program already tracked under `targets/`, refetches the
   scope table and compares against the canonical scope in
   `targets/<slug>/http.md`. Diffs land in
   `targets/<slug>/_scope_diffs/<utc>.md` for user review.

## Dashboard URLs (post-login)

| Platform | URL | Notes |
|---|---|---|
| HackerOne | `https://hackerone.com/opportunities/all/search?type=team` | All public + invited |
| HackerOne | `https://hackerone.com/invitations` | Pending only |
| Intigriti | `https://app.intigriti.com/researcher/programs` | Tabs: joined, available |
| Bugcrowd  | `https://bugcrowd.com/user/dashboard/engagements` | Active engagements |
| Synack    | `https://platform.synack.com/targets` | All onboarded targets |

## Tooling

- **Headless Chromium**: `playwright sync_api` from Python. Chosen over
  `claude-in-chrome` because routine runs headless on schedule with no
  user-Chrome dependency.
- **Cookies**: loaded from `cookies/<platform>.json` (Cookie-Editor JSON
  format). Skill expects `[{"name": "...", "value": "...", "domain":
  "...", "path": "...", "httpOnly": ..., "secure": ...}, ...]`.
- **Caido**: NOT used — these are platform meta pages, not target
  assets.

## Scope-diff algorithm

For each `targets/<slug>/`:

1. Fetch program detail page → parse scope table (in/out, asset type,
   max severity, bounty eligibility).
2. Normalize to the same shape as `_TEMPLATE_http.md > Scope` section.
3. `diff` vs `targets/<slug>/http.md`.
4. If non-empty:
   - Write `targets/<slug>/_scope_diffs/<utc-iso>.md` with added/removed/changed.
   - Append `{ts, slug, added: N, removed: M, changed: K}` to
     `routines/target-discover/_scope_diff_log.jsonl`.
5. NEVER auto-edit `http.md`. Surface to user for review.

## TODO

- [ ] write `routines/target-discover/dashboard_walk.py`
- [ ] write per-platform parser modules under `dashboard_parsers/`
- [ ] write `bin/scope_diff.py` (shared with `target-init` lib)
- [ ] integrate with `routine.sh` (uncomment the dashboard block)
- [ ] add `_known_programs.json` snapshot mechanism
