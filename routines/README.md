# routines/

Self-contained recurring jobs that run on a schedule (launchd / cron /
schedule-skill remote agent). Each routine lives in its own subfolder
with everything needed to bootstrap, run, and audit it.

## Layout

```
routines/
├── _TEMPLATE/             # scaffold for new routines
└── <routine-name>/
    ├── README.md          # what + why + when + how to install
    ├── routine.sh         # entry point (launchd-callable)
    ├── prompts/           # CC slash-command prompts the routine invokes
    ├── cookies/           # gitignored — session cookies per platform
    ├── inbox/             # routine-local outputs (separate from /inbox/)
    ├── launchd/           # *.plist templates for `launchctl bootload`
    └── _log.jsonl         # append-only run log
```

## Conventions

- **Idempotent**: re-run must be a no-op if nothing changed.
- **Locked**: each `routine.sh` uses a flock at `/tmp/tlx-<routine>.lock`.
- **Non-destructive**: routines never delete `targets/<name>/` even if a
  program goes off-platform — only update `status.json.lifecycle`.
- **Secrets stay out of git**: `cookies/`, `.env`, `auth_cache.json`
  globbed by root `.gitignore`.
- **Observable**: append `{ts, routine, action, ok, errors}` to
  `_log.jsonl` per run.

## Adding a routine

1. `cp -r _TEMPLATE <new-name>`
2. Fill `README.md` (purpose, schedule, deps).
3. Implement `routine.sh` + any `prompts/*.md`.
4. Test by hand: `bash routine.sh --dry-run`.
5. Generate launchd plist: `bash launchd/install.sh`.
6. Verify with `launchctl print gui/$UID/com.tlx.<name>`.

## Current routines

- `target-discover/` — Gmail-driven invite tracker for H1/Intigriti/BC/Synack
  + cookie-based dashboard sweep for new programs and scope updates.
