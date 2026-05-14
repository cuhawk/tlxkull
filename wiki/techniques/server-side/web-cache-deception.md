---
title: Web Cache Deception via extension/path keying
slug: web-cache-deception
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/cache, sink/cdn]
inbound: []
---

# Web Cache Deception via extension/path keying

## Pattern

A reverse proxy or CDN (CloudFlare, Akamai, Varnish, ASP.NET output cache,
Loom-style edge cache) decides "this response is cacheable" based on the
URL path/extension instead of the response `Content-Type` or `Cache-Control`
headers. The origin renders a user-specific response (session token,
PII, credit card) at a dynamic path; the attacker tricks the cache into
storing that response under a key the attacker can later fetch
unauthenticated from anywhere in the same edge POP.

Three concrete variants observed in the wild:

1. **Cache-prevention query parameter (TechCrunch Andre/Joel bug).** The
   origin treats `?cb=<random>` as a cache-buster, but the edge ignores
   it. Attacker crafts a one-off URL with `?cb=<random>`, lures the
   victim to it, the response is rendered with their cookies and cached
   under `path?cb=<random>`. Attacker re-fetches the same URL with no
   auth from the same data-center region.
2. **`.aspx%3F<rand>.js` smuggled question mark.** Edge sees the path as
   ending in `.js`/`.png` and caches; origin URL-decodes and routes the
   request to `index.aspx?...`. Common on .NET stacks.
3. **Path-append `index.aspx/poc-<rand>.png`.** Cache key uses suffix
   only; origin strips the `.png` (route ignores extra path) and renders
   the dynamic page; cache stores it under the static-looking URL.

## Preconditions

- Reverse proxy / CDN that keys on URL path or extension, not
  `Content-Type` / `Vary`.
- An authenticated route that returns user-specific data in the body.
- Attacker can force a victim browser to fetch the malicious URL while
  authenticated.

## Detection

- Response carries `Age:`, `CF-Cache-Status: HIT/MISS`, or any
  cache-hit/miss header on a URL that contains user data.
- `Cache-Control: no-store/private` on the origin but cache hit on the
  edge = the edge is overriding origin directives.
- Burp Cache-Deception scanner; manual: fetch a sensitive page with
  `?cb=<rand>` then re-fetch unauthenticated.

## Triggering

Cache-prevention parameter:
```
GET /api/user/me?cb=8923 HTTP/1.1
Cookie: session=victim-session
```
Re-fetch unauth:
```
GET /api/user/me?cb=8923 HTTP/1.1
```

Smuggled `.js` extension on ASP.NET:
```
GET /account/profile.aspx%3Frnd=8923.js HTTP/1.1
```

Path-append `.png`:
```
GET /account/profile.aspx/poc-8923.png HTTP/1.1
```

## Bypasses

- If cache normalizes case, try mixed case in path.
- Edge caches sometimes drop a leading `/`; combine with `//path`.
- Cache key may include `Host` header — set `Host: <internal>` if reverse
  proxy trusts it.
- If `Vary: Cookie` is set, cache is normally not hit cross-session; look
  for endpoints that respond with `Cache-Control: public` and no `Vary`.

## Seen in the wild

- {date: 2023-03-16, source: CT Ep 11} — TechCrunch session-token leak via
  cache-prevention parameter; ASPX `%3F` trick on a government target;
  path-append `.png` on an airline (Justin Gardner finds).

## References

- Critical Thinking Podcast Ep 11
- OmerGil / Acunetix Web Cache Deception writeups
- Related: [[../csrf/content-type-swap]]
