---
title: Cache parameter cloaking
slug: cache-parameter-cloaking
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/server-side, technique/cache-poisoning]
inbound: []
---

# Cache parameter cloaking

## Pattern
The cache and the backend parse query strings differently. An attacker
crafts a URL where the cache computes a "safe" cache key while the backend
sees an extra parameter (e.g., `callback`) that changes the response body.
The poisoned response is stored under the safe key and served to all
subsequent users whose request hashes to that key.

Concrete mechanisms:

1. **Fat GET**: Cache treats GET as body-less; backend (Rails, Rack) reads
   the request body as URL-encoded parameters. Attacker injects `callback=
   evil` in the body; cache keys on URL only.

2. **Semicolon separator skew**: `?utm_source=x;callback=evil` — Ruby on
   Rails treats `;` as an `&` separator, so it sees `utm_source=x` AND
   `callback=evil`. CDNs (Akamai, Fastly) key only on the query string
   parsed by their own parser, which may treat `;` as part of the value
   and not split it — or may exclude `utm_*` params and key on
   `callback=evil` after splitting, producing a different key than the
   back-end hash.

3. **CDN-level parameter exclusion**: Akamai and others allow operators to
   exclude "harmless" params (`utm_*`, `fbclid`, etc.) from the cache key.
   Attacker appends excluded params around a reflected parameter to cloak
   the poisoned key from the cache's perspective.

4. **Regex-based exclusion**: some cache configs use a regex like
   `[?&]utm_[^&]*` to strip marketing params from the key. If the
   stripping is order-sensitive, appending `&utm_foo=bar` after a
   reflected param changes what the regex strips.

**Web cache oracle methodology** (Kettle): find an endpoint that reflects
any arbitrary query parameter value in the response (a "cache oracle").
Then systematically test parameter parsing differences between the CDN and
the backend by injecting `;`, `%23`, `%3f`, chunked body, etc., and
comparing cache keys vs. backend behavior.

## Preconditions
- Target uses a CDN or reverse proxy that caches GET/HEAD responses.
- Backend and cache use different query string parsers (language, config,
  or RFC interpretation).
- At least one reflected parameter exists (for RXSS delivery) OR a
  behavior-changing parameter exists (for cache poisoning to affect
  functionality without reflection).

## Detection
- Send two requests: one with `?param=canary1`, one with `?param=canary2`.
  If second response is cached (same body as first), cache keys do not
  include `param`.
- Try `?utm_source=x&param=poison` vs `?param=poison` — if same cache hit,
  `utm_source` is excluded from cache key.
- Try semicolons: `?legit=1;injected=2` vs `?legit=1&injected=2` — if
  backend reflects `injected`, both forms poison the same cache entry.
- Burp Suite "Param Miner" extension automates cache key discovery.

## Triggering
1. Identify a reflected parameter (e.g., `callback`) on a cached endpoint.
2. Identify a parameter excluded from cache key (e.g., `utm_source`).
3. Craft: `GET /endpoint?callback=evil&utm_source=x HTTP/1.1`
   - Backend sees `callback=evil`, reflects it in response.
   - Cache keys on `?callback=evil` after stripping `utm_source=x`…
     OR cache keys on URL without body params (fat GET variant).
4. Poison: send the crafted request. Cache stores the poisoned response.
5. Victim requests `/endpoint` (no params) → served the poisoned XSS
   response.

## Bypasses
- **Vary header**: if the response includes `Vary: X-Forwarded-For`, the
  cache key expands. Check whether Vary headers are actually respected.
- **Per-user caching**: session-keyed caches are not poisonable globally;
  pivot to self-poisoning to exfil session data.
- **Parameter not reflected but behavior-changing**: use to smuggle
  functionality without XSS (e.g., `debug=1` shows stack traces cached
  for everyone).

## Seen in the wild
- **GitHub**: $7,500 — cache poisoning via parameter cloaking to inject
  XSS into cached pages (Kettle, Web Cache Entanglement research).
- **Zendesk**: account hijack via poisoned cache response that set an
  attacker-controlled OAuth redirect (Kettle).
- **Firefox update endpoint**: DoS via cache poisoning that served a
  malformed update manifest — $5,000 (Kettle).
- PortSwigger Top 10 Web Hacking Techniques 2020.

## References
- PortSwigger TV: "Web Cache Entanglement: Novel Pathways to Poisoning"
  — James Kettle (2020) — `wiki/sources/portswigger-tv/whisper/transcripts/bDxYWGxuVqE_*.txt`
- PortSwigger Research: https://portswigger.net/research/web-cache-entanglement
- Related: [[cloudflare-cache-key-header-overflow]], [[cookie-clear-path-confusion]]
