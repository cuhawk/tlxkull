---
name: target-promote
description: Promote READY inbox markers into proper targets/<slug>-<plat>/ engagements. Synack auto-promotes as tracking-only. Trigger: /target-promote (all), /target-promote <slug> (one), or /target-promote --synack-only. Run after target-invite-sweep.
---

# target-promote

Convert `inbox/invites/<plat>/<slug>/READY` seeds into live `targets/`
engagements. Two-step pipeline: discovery (`target-invite-sweep`) →
promotion (this skill) → optional scope fill (browser MCP).

## When to invoke

- Manual: `/target-promote` after `target-invite-sweep` populates inbox.
- Manual one-shot: `/target-promote regions_financial_bounty-h1`
- Synack auto: `/target-promote --synack-only` (creates all tracking-only
  stubs; safe because no requests sent).

## Arguments

| flag | meaning |
|---|---|
| `<slug>` | promote a single slug (matches dir name under `inbox/invites/<plat>/`) |
| `--synack-only` | only process synack seeds (tracking-only, fully auto) |
| `--skip-synack` | process H1/Intigriti/BC only |
| `--fetch-scope` | after promotion, also call browser MCP to fill scope (H1/Intigriti only — needs cookies + logged-in Chrome) |
| `--dry-run` | print actions, write nothing |

## Discovery

Walk `inbox/invites/<plat>/<slug>/` for every dir containing `READY`.
Skip dirs with `DONE` (already promoted) or `DUPLICATE` (already in
`targets/`) or `REINVITE` (already in `targets/` but lifecycle != active
— surface to user, do not auto-promote).

## Per-platform promotion

### Synack (`<slug>-syn/`)

Fully auto. No browser MCP. No scope fill.

1. Read `meta.json`.
2. Compute target dir `targets/<slug>-syn/`. Skip if exists.
3. Write `targets/<slug>-syn/http.md` from this template:

```markdown
# <CODENAME>

> Platform: Synack — Researcher Portal (tracking-only, no live visits per memory rule)
> Type: BBP | Onboarded: <ISO date>
> Asset class: <web | host | mobile> (parsed from email subject)

## Scope

- in: (see Synack Researcher Portal — not duplicated in repo per
       feedback_synack_no_live_visits)

## Auth

- type: session
- creds: synack_researcher_portal

## Notes

- TRACKING ONLY — never send automated requests, never fire active skills.
- Onboarded from Gmail invite: thread_id <GMAIL_THREAD_ID>
```

4. Write `targets/<slug>-syn/status.json`:

```json
{
  "ts_created": "<utc>",
  "platform": "synack",
  "slug": "<slug>-syn",
  "lifecycle": "synack-tracked-only",
  "lifecycle_history": [
    {"ts": "<utc>", "state": "synack-tracked-only", "reason": "auto-promoted from gmail invite"}
  ],
  "source": {"channel": "gmail", "thread_id": "<id>", "received_at": "<iso>"}
}
```

5. Flip `inbox/invites/synack/<slug>/READY` → `DONE`.
6. Append `{ts, slug, action: "promoted", platform: "synack"}` to
   `routines/target-discover/_promote_log.jsonl`.
7. Do NOT call `target-init` (active skills must skip
   synack-tracked-only per memory rule).

### HackerOne / Intigriti / Bugcrowd

Stub-only by default. Real scope fill is user-gated (`--fetch-scope`).

1. Read `meta.json` + `email.json`.
2. Compute dir `targets/<slug>-<plat>/`. Skip if exists.
3. Write `targets/<slug>-<plat>/http.md` from stub template:

```markdown
# <PROGRAM>

> Platform: <HackerOne | Intigriti | Bugcrowd> — <program URL from email>
> Type: <BBP | VDP | Application> (parse from email body if present, else "TBD")
> Bounty: TBD (fill from program page)
> Avg payout: N/A | Total paid: N/A
> Last scope update: TBD

## Scope

- in: TBD — fetch via browser MCP or paste manually from program page
- out: TBD

## Auth

- type: session
- creds: env:<H1_SESSION_TOKEN | INTIGRITI_SESSION_TOKEN | BC_SESSION_TOKEN>

## Notes

- Invited via Gmail thread <id> on <date>.
- Expires (HackerOne only): <expires_at from email body if available>
```

4. Write `targets/<slug>-<plat>/status.json` with:

```json
{
  "ts_created": "<utc>",
  "platform": "<hackerone|intigriti|bugcrowd>",
  "slug": "<slug>-<plat>",
  "lifecycle": "invited-pending",
  "lifecycle_history": [
    {"ts": "<utc>", "state": "invited-pending", "reason": "auto-promoted stub from gmail invite"}
  ],
  "source": {"channel": "gmail", "thread_id": "<id>", "received_at": "<iso>"},
  "scope_filled": false
}
```

5. If `--fetch-scope`:
   - Open browser MCP, navigate to program URL.
   - Capture scope table HTML.
   - Parse into `_TEMPLATE_http.md` shape.
   - Overwrite the `## Scope` block in `http.md`.
   - Set `status.json.scope_filled=true`, lifecycle=`active`,
     append lifecycle_history entry.
6. Else: leave lifecycle=`invited-pending` — user fills scope by hand
   later then manually flips to `active` (or re-runs `/target-promote
   --fetch-scope <slug>` once at desk).
7. Flip `READY` → `DONE`.
8. Run `target-init` to normalize the http.md into `status.json` scope
   structure. `target-init` MUST preserve existing
   `lifecycle` + `lifecycle_history` fields (does not overwrite).

## Lifecycle field reference

| State | Set by | Meaning |
|---|---|---|
| `invited-pending` | target-promote (no --fetch-scope) | Stub exists, scope not yet filled |
| `active` | target-promote --fetch-scope, or manual | Ready to hunt |
| `paused` | dashboard-walk drift detection, or manual | Program paused — keep dir, send no traffic |
| `retired` | dashboard-walk drift, or manual | Program closed permanently — keep dir for reference |
| `synack-tracked-only` | target-promote (synack) | Synack target — no requests |

`lifecycle_history[]` is append-only. Never delete entries.

## Hard rules

- **Never delete** an existing `targets/<dir>/`. If `inbox` slug already
  has a target dir, mark `REINVITE` and surface to user — do not
  re-create.
- **Synack tracking-only**: NEVER call `target-init`, never write
  scope, never fire downstream skills.
- **Scope-fill is user-gated**: stub never auto-fills production scope
  data without `--fetch-scope` flag.
- **status.json.lifecycle is sacred**: every downstream skill (recon,
  js-harvest, opus-deep-audit, etc.) MUST check this field. Skip target
  if `lifecycle in {paused, retired, synack-tracked-only}` unless
  user explicitly forces with `--force-lifecycle`.

## Result block

```json
{
  "ts": "<utc>",
  "skill": "target-promote",
  "promoted": [{"slug": "...", "platform": "...", "lifecycle": "..."}],
  "skipped": [{"slug": "...", "reason": "already_exists"}],
  "reinvites": [{"slug": "...", "existing_lifecycle": "..."}],
  "errors": []
}
```

Appended to `routines/target-discover/_promote_log.jsonl`.
