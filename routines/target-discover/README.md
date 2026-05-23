# target-discover

Daily discovery of new bug-bounty program invitations and scope updates
across HackerOne / Intigriti / Bugcrowd / Synack.

## Two channels

1. **Gmail sweep** (zero auth deps, runs anywhere). Searches for
   invitation emails by per-platform from + subject patterns.
2. **Dashboard walk** (needs saved session cookies). Visits each
   platform's program listing for *new programs* (platforms don't email
   when their catalogue grows) and detects *scope-table changes* on
   programs already tracked.

## Schedule

- Default: daily 07:00 local (`launchd/com.tlx.target-discover.plist`).
- Gmail sweep can also run more often (hourly cheap), independent of
  dashboard walk.

## Email signatures (sender → subject pattern → slug rule)

| Platform | Sender | Subject pattern | Slug derivation |
|---|---|---|---|
| HackerOne | `no-reply@hackerone.com` | `<Program> has invited you to their HackerOne program` | `<program-slug>-h1` |
| Intigriti #1 | `noreply@intigriti.com` | `[ intigriti ] Application accepted!` | body: `application for <prog> was accepted by <company>` → `<company>_<prog>-intigriti` |
| Intigriti #2 | `noreply@intigriti.com` | `[ intigriti ] You have been invited to join <Prog>` | body: `<company> has invited you` → `<company>_<prog>-intigriti` |
| Bugcrowd | `support@bugcrowd.com` | `A New Engagement Invite` | body required — engagement name is in the HTML body, not the subject |
| Synack | `support@synack.com` | `You have been onboarded on target <CODE>` | `<code-lower>-syn` |

Synack-aware: `*-syn` dirs are *tracking-only*. No browser MCP, no
requests. Per memory rule `feedback_synack_no_live_visits`.

## Cookie bootstrap

Dashboard-walk requires session cookies. Two options:

### Option A — Cookie-Editor Chrome extension (recommended)

1. Install the
   [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
   extension once.
2. For each platform:
   - Log in via your real Chrome.
   - Click the Cookie-Editor icon → Export → JSON → copy.
   - Paste into `cookies/<platform>.json`.
3. `cookies/` is gitignored. Refresh every ~30d or when sweep reports
   401/redirect-to-login.

### Option B — Chrome remote-debug port (advanced)

Launch Chrome with `--remote-debugging-port=9222` once, then
`routine.sh --bootstrap-cookies` connects via CDP and dumps cookies
from your authenticated origins. Restart of Chrome may be required.

## Lifecycle preservation

This routine NEVER deletes a `targets/<name>/` directory. When a program
goes paused/retired, `status.json.lifecycle` flips to the new state and
`lifecycle_history[]` appends `{ts, state, reason}`. Old state preserved
forever.

States:

| state | meaning |
|---|---|
| `invited-pending` | Invite seen, not yet promoted to active target |
| `active` | Currently hunting |
| `paused` | Program paused — dir kept, do not send traffic |
| `retired` | Program closed permanently — dir kept for reference |
| `synack-tracked-only` | Synack target — tracked from email, no live visits |

## Outputs

Per platform, per slug:

```
inbox/invites/<platform>/<slug>/
├── email.json           # raw Gmail thread snapshot
├── meta.json            # parsed: {platform, slug, program, company, invited_at, expires_at, invite_url}
└── READY                # marker for target-promote skill
```

If slug already exists under `targets/`:
- `lifecycle=active|invited-pending` → mark `DUPLICATE` (skip).
- `lifecycle=paused|retired` → mark `REINVITE` (user reviews).

## Manual runs

```
bash routine.sh --gmail-only         # skip dashboard walk
bash routine.sh --dashboard-only     # skip Gmail
bash routine.sh --backfill 365       # one-time full backfill
bash routine.sh --dry-run            # print diff, write nothing
```

## Failure recovery

- Gmail 401 → re-auth Claude.ai Gmail MCP (`/connect gmail`).
- Cookie 401 → re-bootstrap cookies (Option A above).
- Dashboard parse fail → schema drift on platform side; check
  `_log.jsonl` and update selectors in `prompts/02_dashboard_walk.md`.
