---
title: Rails HEAD-method CSRF bypass (GitHub OAuth $25K)
slug: csrf-rails-head
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/csrf]
inbound: []
---

# Rails HEAD-method CSRF bypass

## Pattern
Rails `match via: [:get, :post]` routes HEAD through the `:get` handler.
Controller logic `if request.get? ... else <post path> end` makes HEAD
trigger the post path. Result: CSRF via HEAD bypasses CSRF tokens (which
many Rails apps only enforce on POST/PUT/DELETE).

Teddy Katz — GitHub OAuth $25K.

## Preconditions
- Target framework: Rails with `match via:` route definition that pairs
  GET+POST.
- CSRF middleware checks `request.post?` (false for HEAD).

## Detection
- Scan routes file for `match via:`.
- Test HEAD request against any post-only endpoint that has the same
  path as a public GET.

## Triggering
```js
fetch('/oauth/authorize?client_id=...', {
  method: 'HEAD',
  credentials: 'include',
});
```
Server-side `request.get?` returns false → falls through to post-path
logic → mutation happens without CSRF token check.

## Related
- [[csrf-content-type-swap]] — JSON → text/plain Content-Type bypass.
- [[csrf-referrer-unsafe-url]] — `<meta name=referrer content=unsafe-url>`
  on attacker page.
- Rails `?_method=POST` overrides verb.

## Seen in the wild
- GitHub OAuth — Teddy Katz, $25K (2019).
- Critical Thinking Podcast Ep 28.

## References
- blog.teddykatz.com — GitHub OAuth HEAD CSRF
- Critical Thinking Podcast Ep 28
