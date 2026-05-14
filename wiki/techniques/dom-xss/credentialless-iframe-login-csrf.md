---
title: Credentialless iframe login-CSRF (cookie-jar swap)
slug: credentialless-iframe-login-csrf
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/iframe-hopping, technique/login-csrf]
inbound: []
---

# Credentialless iframe login-CSRF

## Pattern
A `<iframe credentialless>` is **same-origin** with a normal `<iframe>` of the
same URL (the RFC explicitly notes opaque-origin was wanted but not implemented
"due to implementation difficulties"). The credentialless iframe has its own
empty cookie jar; from the parent you can reach into it via the standard SOP
DOM access. Drop a login-CSRF inside the credentialless iframe to mint a fresh
session in the attacker's account without first having to log the victim out
(the persistent attack pattern formerly required a logout-CSRF or cookie-jar
overflow). Combined with self-XSS this gives one-step ATO of arbitrary users.

## Preconditions
- Browser support for `credentialless` attribute on iframes (Chrome 110+).
- Target accepts login-CSRF (no CSRF token on the login endpoint, or token is
  predictable / fetchable cross-origin).
- A same-origin self-XSS or stored content gadget that fires once the attacker's
  cookies are loaded inside the iframe.

## Detection
- Audit login endpoint for CSRF protection — most apps still leave login
  unprotected.
- Confirm `iframe credentialless` is permitted by parent CSP `frame-src` and
  is not blocked by `Permissions-Policy: credentialless=()`.

## Triggering
```html
<iframe credentialless src="https://target.com/login-via-get?u=ATTACKER&p=...">
</iframe>
<script>
  // Same-origin → reach in, trigger self-XSS in attacker session
  // After self-XSS lands, register fetchLater handlers (see related), then
  // attacker logs out / victim logs back in → fetchLater fires under victim
  // credentials.
</script>
```

## Bypasses / hardening
- `Permissions-Policy: credentialless=()` blocks the feature outright.
- Forcing the login endpoint to be POST with a fetched CSRF token kills the
  login-CSRF half.

## Seen in the wild
- {date: 2025-06-26, source: CT Ep 128} — Slonser "Make Self-XSS Great Again" research.

## References
- Slonser blog — Make Self-XSS Great Again
- Critical Thinking Podcast Ep 128
- Related: [[fetchlater-redirect-persistence]], [[captcha-passthrough-websocket]]
