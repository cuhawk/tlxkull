# cookies/

Per-platform session cookies for the dashboard-walk phase.
**Gitignored** — never commit cookie payloads.

## Bootstrap (one-time, ~5 min per platform)

1. Install the Chrome extension
   [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm).
2. For each platform below: log in via real Chrome, click the
   Cookie-Editor icon → Export → JSON. Save the JSON payload to the
   target file below.

| Platform | File | Cookie domain(s) |
|---|---|---|
| HackerOne | `hackerone.json` | `.hackerone.com` |
| Intigriti | `intigriti.json` | `.intigriti.com`, `.app.intigriti.com` |
| Bugcrowd | `bugcrowd.json` | `.bugcrowd.com` |
| Synack | `synack.json` | `.synack.com`, `.platform.synack.com` |

## Validate

```
python3 ../validate_cookies.py            # all platforms
python3 ../validate_cookies.py hackerone  # one
```

Validator checks:
- File parses as JSON array.
- Required session cookie present per platform (`__Host-session` on H1,
  `_intigriti_session_v2` on Intigriti, etc).
- Cookie not expired.

## Refresh cadence

- Synack: short-lived (hours-days) — refresh frequently or accept that
  dashboard walk for Synack falls back to Gmail-only.
- H1/Intigriti/BC: usually weeks. Refresh when `routine.sh` logs
  `cookie_expired` in `_log.jsonl`.

## Security

- `chmod 600 cookies/*.json` recommended.
- These are session cookies, not passwords. Compromise = attacker can
  impersonate your session until the cookie expires.
- Rotate by logging out + back in on the platform, then re-export.
