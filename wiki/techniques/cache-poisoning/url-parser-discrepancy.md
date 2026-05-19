---
title: URL-parser discrepancy cache poisoning
slug: url-parser-discrepancy
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/cache-poisoning, technique/url-parser, technique/static-path-deception]
inbound: []
---

# URL-parser discrepancy cache poisoning

## Pattern

The cache and the origin parse the URL differently. The cache decides "this is a static `.js` asset, cache aggressively under key K". The origin decides "this is the dynamic endpoint X" and returns sensitive or attacker-controllable content. The mismatch lets an attacker either:

- **Static Path Deception** — request a URL that the cache classifies as static (caches it publicly under a permissive TTL) but the origin treats as a dynamic request, leaking the dynamic response to anyone who hits the static-looking key.
- **Cache key collision** — request URLs that *look* different but normalize to the same cache key, so an attacker's response gets stored against a benign-looking URL.

## Preconditions

- A cache that applies static-asset rules based on path heuristics (extension, prefix, content-type guesses).
- Cache and origin use different URL parser libraries or different normalization passes (semicolons, dot-segments, percent-encoding, parameter pollution, trailing slash).
- The origin returns useful content for the parser-confused URL — dynamic page, authenticated content, user data.

## Common discrepancies (from PortSwigger "Gotta Cache 'Em All" and "Hat Trick")

| Trick | Example URL | Cache sees | Origin sees |
|---|---|---|---|
| Semicolon path parameter | `/api/profile;.js` | `/api/profile;.js` → static `.js` | `/api/profile` (Tomcat / Spring strips `;jsessionid=`-style params) |
| Trailing dot | `/admin/dashboard.css` | static | `/admin/dashboard` |
| Encoded slash | `/static/%2Fadmin` | `/static/...` (cacheable prefix) | `/admin` (decoded) |
| Dot-segment | `/static/..%2fadmin` | `/static/..%2fadmin` (cacheable) | resolves to `/admin` |
| Newline in path | `/static/foo%0d%0a/admin` | `/static/foo...` | varies |
| Param injection | `/api/profile?file=.js` | `.js` extension → static | dynamic |
| Double encoding | `/static/%252e%252e/admin` | static | varies |
| Fragment leak (some misconfigured caches) | `/admin#.js` | `.js` static | `/admin` |
| Case sensitivity | `/Admin` vs `/admin` | one key | one resource |
| Trailing whitespace | `/admin ` | distinct key | normalized to `/admin` |

## Detection

1. List the path-based cache rules of the target CDN if known (Cloudflare's default static extension list, Akamai's "Content Refresh", etc.). Pick an authenticated dynamic endpoint.
2. Append each parser-discrepancy suffix above. After each request, look at:
   - `X-Cache:` / `CF-Cache-Status:` — `HIT` means the cache accepted the suffix.
   - Response body — did the origin still return the dynamic content?
3. If both are true, the URL is poisoning-ready.

For Cloudflare specifically: `/path;cf.js`, `/path/cf.js`, `?ext=.js` and the documented file-extension matchers.

## Triggering

Static Path Deception against an authenticated profile endpoint:

```
GET /api/profile;.js HTTP/1.1
Host: target.example
Cookie: session=ATTACKER-SESSION
```

- Cache: `Content-Type: application/javascript`-ish heuristic → cache for 1 hour.
- Origin: strips `;.js`, returns attacker's profile JSON with attacker's session data.
- Cache stores attacker's profile JSON under `/api/profile;.js`.

Now the attacker — or anyone — fetching `/api/profile;.js` gets the attacker's profile back. By itself this is just a self-leak. The attack becomes useful when:

- The origin returns *the requester's* profile (the cache stores whichever response landed first; depending on cache, this can be a victim-on-victim leak).
- The dynamic endpoint contains attacker-controlled reflected content that, served as JS, becomes XSS at the origin scope.

## Bypasses

- Some caches strip `;params` before keying — invert: send `;` to confuse origin instead.
- WAFs that block known suffixes — use double-encoding, mixed encoding, or HTTP/2 pseudo-header injection.
- Path canonicalization differs between OS layers — Windows IIS vs Linux nginx vs Tomcat behind Apache all parse `..\\` and `..%5c` differently.

## Impact ladder

1. Cached XSS at the legitimate origin.
2. Cached authenticated content leak (one user's data served to others).
3. CSP / SOP bypass via JS-context confusion (HTML cached under `.js` key becomes loaded as JS by `<script src>`).
4. DoS of critical authenticated assets via 4xx caching.

## Seen-in-the-wild

- Multiple bounties referenced in PortSwigger "Gotta Cache 'Em All" (Black Hat USA 2024).
- "A Hacking Hat Trick" preview (DEF CON + Black Hat USA) introduced Static Path Deception with Nginx-behind-Cloudflare and Apache case studies.

## References

- [Cache poisoning SUMMARY](SUMMARY.md)
- [research-gotta-cache-em-all](../../sources/blogs/personal/portswigger-research/research-gotta-cache-em-all.md)
- [research-a-hacking-hat-trick](../../sources/blogs/personal/portswigger-research/research-a-hacking-hat-trick-previewing-three-portswigger-research-publications-coming-to-def-con-amp-black-hat-usa.md)
- [hacktricks: cache-poisoning-via-url-discrepancies](../../_external/hacktricks/src/pentesting-web/cache-deception/cache-poisoning-via-url-discrepancies.md)
