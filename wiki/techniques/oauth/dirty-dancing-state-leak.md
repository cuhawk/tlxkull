---
title: OAuth dirty dancing — state mismatch leaks code
slug: oauth-dirty-dancing-state
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/oauth]
inbound: []
---

# OAuth dirty dancing — state break leaks code

Frans Rosén's Detectify 2022 research.

## Pattern
Attacker generates the OAuth URL with a state value only the attacker
knows, then hands the victim a *different* state value. Victim completes
the flow → code lands at the correct (validated) `redirect_uri`, but
state-validation fails. The application redirects to an error page that
may leak the code via:

- `Referer` header to a third party.
- postMessage listener on the error page.
- URL fragment retained across the error redirect.
- Google Analytics / GTM script (if user-pickable, attacker chose attacker
  GA ID).

Attacker exchanges the leaked code with the matching state.

## Key insight
State validation runs **before** code exchange. So attacker can replay
the code with their own state.

## Related primitives (Frans, Ep 45)
- `response_mode=form_post` to subdomain that reflects POST data (e.g.
  `script.google.com`) → exfil access token.
- `response_mode=web_message` postMessage normalised to origin → relay
  listener → child iframe XSS / `window.name` sink.
- 307 open-redirect chained with `form_post` forwards POST'd OAuth tokens
  cross-origin (rare, load-balancer misconfig).

## Preconditions
- Target uses OAuth implicit/authorization-code flow.
- State validation produces an error page that leaks the code in any
  side channel.

## Detection
- Test every error-redirect path that follows a bad-state OAuth callback
  for `code=...` retention.
- Check if Referer policy strips path on the error page.

## Triggering
1. Attacker generates valid OAuth URL with `state=A`.
2. Attacker hands victim a tampered URL with `state=B`.
3. Victim completes IdP login; code arrives at `redirect_uri`.
4. App fails state check, redirects to error page; code leaks via Referer
   / postMessage / GTM.
5. Attacker exchanges `code` + `state=A` for token.

## Seen in the wild
- {date: 2022, target: multiple, Frans Rosén Detectify writeup}.
- Recapped Ep 45 Critical Thinking Podcast (2023-11-16).

## References
- Frans Rosén — "Account hijacking using dirty dancing in sign-in OAuth
  flows" (Detectify, 2022)
- Critical Thinking Podcast Ep 45
