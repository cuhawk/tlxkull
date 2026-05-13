---
title: CSRF via Content-Type swap
slug: csrf-content-type-swap
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/csrf]
inbound: []
---

# JSON CSRF via Content-Type swap

## Pattern
Flip `Content-Type: application/json` to `text/plain` or
`application/x-www-form-urlencoded`. If server still parses JSON, you've
got CSRF on a "JSON-only" endpoint. Test one or two endpoints — usually
applied at middleware level, so result is uniform per host.

## Preconditions
- Endpoint accepts JSON body.
- CSRF protection assumes `application/json` Content-Type triggers
  preflight (so cookie-cross-site CSRF is "blocked").

## Detection
- Send the same request with `Content-Type: text/plain`. Watch for same
  response shape.

## Triggering
HTML form for CSRF:
```html
<form action="https://target/api/endpoint" method="POST"
      enctype="text/plain">
  <input name='{"action":"transfer","amount":1000,"to":"attacker","x":"' value='"}'>
</form>
```
(JSON smuggled as form-field name+value, no preflight triggered.)

## Related
- [[csrf-rails-head]]
- [[csrf-referrer-unsafe-url]]
- enctype text/plain JSON trick (form `enctype="text/plain"` + crafted
  name/value pair).

## Seen in the wild
- LHE-class wins across multiple targets.
- Critical Thinking Podcast Ep 28.

## References
- jub0bs — "the great same-site confusion"
- Critical Thinking Podcast Ep 28
