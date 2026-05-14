---
title: CloudFlare cache-key header-overflow WAF/cache bypass
slug: cloudflare-cache-key-header-overflow
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/cache, technique/waf-bypass, technique/cloudflare]
inbound: []
---

# CloudFlare cache-key header-overflow WAF/cache bypass

## Pattern

CloudFlare's edge computes its cache key over a *limited* number of
request headers — the default cap is around 100 headers, including the
internal headers CloudFlare adds before the cache-key calculation. If
an attacker sends `94+` request headers, sensitive headers (e.g.
`X-HTTP-Method-Override`, `X-Forwarded-Host`) fall *outside* the
cache-key window. The origin still sees those headers and acts on them;
the cache stores the resulting response under a key that ignored them.

Concrete impact: poison a cached asset with `X-HTTP-Method-Override:
DELETE` (or `PURGE`, or any method the origin honors); subsequent
unauthenticated visitors get the poisoned response — DoS or stored XSS
depending on origin behaviour.

## Preconditions

- Site behind CloudFlare with caching enabled on the target route.
- Origin honors at least one header that mutates response (e.g.
  `X-HTTP-Method-Override`, `X-Original-Host`).
- The attacker can reach the same edge POP as future victims.

## Detection

- Send a baseline request and a request with the suspect header — see
  if cache key changes (cache MISS vs HIT under same path).
- Pad request with 94+ junk headers; re-send; observe whether the
  cache stores the poisoned variant under the same key as the baseline.

## Triggering

```
GET /static/asset.js HTTP/1.1
Host: target.com
X-Junk-1: a
X-Junk-2: a
...
X-Junk-94: a
X-HTTP-Method-Override: DELETE
```
Cache stores the DELETE-handled response under the asset URL; future
unauth GETs return the poisoned response.

## Bypasses

- If 100 isn't the exact limit on the target's tier, sweep with
  binary search (10, 50, 100, 200) — different CloudFlare plans have
  different limits.
- For poisoning via body-mutation: chain with HTTP/2 header injection
  (some HTTP/2 stacks count pseudo-headers in the cap differently).

## Seen in the wild

- {date: 2025-circa-pre-disclosure, source: CT Ep 150} — disclosed HackerOne
  report on CloudFlare ("Bypass of CloudFlare's cache keys in WAF via
  header overflow"); reporter triggered stored XSS / DoS against
  customer assets.

## References

- HackerOne disclosed report — CloudFlare cache-key header overflow
- Critical Thinking Podcast Ep 150
- Related: [[web-cache-deception]]
