---
title: X-Content-Type-Options nosniff duplicate-header bypass
slug: x-content-type-options-double-header
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/header-confusion, technique/mime-sniff]
inbound: []
---

# `X-Content-Type-Options: nosniff` duplicate-header bypass

## Pattern
The header `X-Content-Type-Options: nosniff` disables browser MIME-sniffing.
Empirical Chromium behaviour discovered by JG: if the response contains
**two** `X-Content-Type-Options` headers (e.g. one legitimate `nosniff`
plus one attacker-injected garbage value), Chrome appears to discard both
and resume sniffing. Most other headers' duplicate behaviour is "take the
first" or "concatenate with comma" — this one is anomalously permissive.

Useful when CRLF injection lands you below the original header (you can't
overwrite it) but you can append a second one.

## Preconditions
- CRLF / response-header injection below an existing `X-Content-Type-Options`
  header.
- Body content the browser would gladly sniff as something dangerous
  (HTML, script).

## Detection
- Send a probe with `X-Content-Type-Options: nosniff` followed by your
  injected `X-Content-Type-Options: foo` (or duplicate `nosniff`). Verify
  the browser sniffs the body type.
- Cross-browser test — JG's note targets Chromium; Firefox/Safari may
  behave differently.

## Triggering
Pseudo response:
```http
HTTP/1.1 200 OK
Content-Type: image/png
X-Content-Type-Options: nosniff
X-Content-Type-Options: foo

<html><script>alert(1)</script></html>
```
Browser ignores `Content-Type: image/png` because both nosniff headers are
discarded; sniffs the body as HTML; XSS fires.

## Bypasses / hardening
- Edge / WAF: collapse duplicate `X-Content-Type-Options` headers before
  forwarding.
- Don't allow header injection in the first place (CRLF hardening).

## Open research
JG: "I wonder if there's other headers that behave this way." Easy
research project — Dockerize a server that responds with duplicate
headers across the security set and diff browser behaviour.

## Seen in the wild
- {date: 2025-01-23, source: CT Ep 107} — JG personal find, queued for
  CT Research Lab follow-up.

## References
- Critical Thinking Podcast Ep 107
- WHATWG fetch spec — header parsing
