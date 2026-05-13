---
title: Math.random prediction via iframe name cross-origin read
slug: math-random-prediction
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/xs-leaks, technique/predictable-prng]
inbound: []
---

# Math.random prediction via iframe name leak

Donut's predictable-PRNG research, used by Yusuf Sammouda on Facebook
chat plugin.

## Pattern
Facebook chat plugin generated iframe `name` attribute via `Math.random()`.
`iframe.name` is readable cross-origin. Iframe a 2-deep page (X-Frame-Options
`ALLOW-FROM` deprecated, ignored on mobile/desktop → still iframable on
mobile). Refresh the inner plugin via a no-callback API call → new
`Math.random` sample. After ~5 leaked floats (even with gaps), reconstruct
V8 xorshift128+ seed → predict secret callback ID for next instantiation →
exploit DOM XSS sink that required the secret.

## Preconditions
- Target uses `Math.random()` for security-relevant value (callback ID,
  CSRF token, password-reset token).
- Some seeded value leaks cross-origin (iframe name, document title,
  predictable URL, etc.).
- V8 (Chrome/Node) — xorshift128+ has known seed-reconstruction attack
  from 5 outputs.

## Detection
- Audit JS for `Math.random()` in security-relevant contexts (token gen,
  ID gen).
- Test if iframe `name` (or any other cross-origin-readable property) is
  derived from `Math.random()`.

## Triggering
1. Iframe target plugin many times, harvest `iframe.name` after each refresh.
2. Convert names to floats.
3. Run xorshift128+ seed-recovery (public PoC by Donut / others).
4. Predict next callback ID; trigger DOM XSS sink with it.

## Related
- V8 xorshift128+ reverse — pub research circa 2018+.
- For non-V8 engines: SpiderMonkey/JSC use different PRNGs; check
  vulnerability separately.

## Seen in the wild
- Facebook chat plugin — Yusuf Sammouda, Ep 58.

## References
- Critical Thinking Podcast Ep 58
- Donut — predictable-Math.random research
- V8 source — xorshift128+ implementation
