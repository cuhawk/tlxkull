# <target-program-name>

> Rename `_TEMPLATE_http.md` to `<target-name>/http.md` and fill in.
> `target-init` skill reads this file and writes `status.json` next to
> it. Everything downstream depends on this seed being correct.

## Scope

> Domains / patterns the program declares in-scope. One per line.
> Globs (`*.example.com`) get converted to regex automatically.

- in:  example.com
- in:  *.example.com
- in:  api.example.com
- out: blog.example.com
- out: status.example.com

## Auth

> `type` is one of: `session | bearer | none | mtls`.
> `creds` lines reference Caido workflows or env vars — NEVER paste
> raw credentials here.

- type: session
- creds: caido_workflow:login-user-a
- creds: caido_workflow:login-user-b   # second account for IDOR/BAC

## Notes

> Free text. Use for prior intel — rate limits, payout speed, known
> auth quirks, paths you already explored, anything that helps future
> sessions resume context.

- payout speed: ~7 days
- triagers prefer SARIF + html PoC bundle
- session cookie TTL: 4 hours; re-login needed often
- watch out for: cloudflare rate limit on /api/* paths

## Optional: known peer IDs (for caido-idor)

> If you have known peer-owned identifiers (numeric ids, UUIDs,
> emails), drop them here. `caido-idor` reads this list when fuzzing
> IDs. NEVER include personal data of strangers — only test-account
> peers you control.

- peer_ids:
  - 42
  - 51e8a3c2-b7a1-4d6f-9e0f-4bc1234abcde
  - peer-test@example.com
