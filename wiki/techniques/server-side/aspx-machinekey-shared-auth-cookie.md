---
title: ASP.NET MachineKey Shared Auth Cookie Forgery
slug: aspx-machinekey-shared-auth-cookie
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/server-side, technique/auth-bypass, technique/cookie-forgery, technique/dotnet]
inbound: []
---

# ASP.NET MachineKey Shared Auth Cookie Forgery

## Pattern

ASP.NET forms authentication cookies are HMAC-signed using the application's
`machineKey` (from `web.config`). If multiple applications on the same server
or farm share a `machineKey` — or if the key can be leaked — an attacker who
has a valid session on one application can forge a cookie accepted by another.
In the Facebook case, a third-party ASP.NET application hosted on `*.facebook.com`
shared a `machineKey` with the main application. The attacker obtained a session
on the third-party app, extracted the signed cookie, then replaced the username
in the cookie payload and re-signed it with the shared key — the resulting
forged cookie was accepted by the main Facebook ASP.NET endpoint.

Additionally, known/default `machineKey` values exist in public documentation
and example configs; scanning for them enables authentication bypass on any
app that uses a default key.

## Preconditions

- Two or more ASP.NET applications share a `machineKey` (or a key is leaked/default).
- An attacker can obtain a valid auth cookie from the weaker application.
- The stronger application uses forms authentication with the same key.

## Detection

- Identify `*.target.com` ASP.NET applications (look for `.ASPXAUTH` cookie name,
  `__VIEWSTATE`, `.aspx` extensions).
- Check if a cookie from app A is accepted by app B (sign in to A, send cookie to B).
- Look for `machineKey` leaks in: open-source repos of related apps, error messages
  that expose stack traces with config, exposed `web.config` via path traversal.
- Known default keys are searchable in GitHub and exploit databases.

## Triggering

1. Sign in to the weaker application; capture the `.ASPXAUTH` cookie.
2. Decode: `base64 → decrypt (AES) → HMAC verify`.
3. Modify the username/identity field in the decrypted payload.
4. Re-encrypt and re-HMAC with the shared key.
5. Submit the forged cookie to the target application.

Tools: `machinekey-forger`, `YSoSerial.NET` (includes `machineKey` module).

## Seen in the wild

- 2020–2021 — Facebook/Meta, part of a $54,800 combined payout for three bugs.
  An ASP.NET app under `*.facebook.com` shared its `machineKey` with the main
  Facebook authentication layer. The attacker forged an auth cookie to access
  the primary Facebook endpoint as any user. Reported in BBRE.
  [BBRE](https://www.youtube.com/watch?v=JiMzpjgAXv8)

## References

- Microsoft ASP.NET `machineKey` documentation
- See also: [aspnet-machinekey-rce](aspnet-machinekey-rce.md) — RCE via ObjectStateFormatter
- YSoSerial.NET — `machineKey` plugin
