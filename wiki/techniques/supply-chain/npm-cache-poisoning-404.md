---
title: npm registry cache poisoning via 404 caching
slug: npm-cache-poisoning-404
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/supply-chain, technique/cache-poisoning, technique/dos, registry/npm]
inbound: []
---

# npm registry cache poisoning (404 DoS)

## Pattern

The public `registry.npmjs.org` CDN caches negative responses. A specific
request header on a `GET /<package>` request triggers a 404 at the
registry; the 404 then gets cached on a CDN edge node. Any subsequent
request from any client routed to that edge node receives the cached
404 -- `npm install <package>` fails until the cache TTL expires.

Discovered by 0xLupin (Ronnie) while building a depi availability-impact
module. Impact: DoS of arbitrary public npm packages -- `express` at
30M weekly installs, `react`, anything. ~1 in 4 edge nodes hit the
poisoned cache per his testing.

GitHub initially rated it informational / DDoS (out of scope), $500
bounty after a year of back-and-forth. Public disclosure 2024-06-04.

## Preconditions

- npm registry edge cache layer that does not vary on the specific
  request header (the actual header name was withheld in the public
  blog).
- Public attack -- no auth required.

## Detection

- Send `GET https://registry.npmjs.org/<small-test-pkg>` with the
  trigger header -> response 404.
- Wait 30s, retry without the header -> still 404 (poisoned).
- Try same package from a second IP / second region -> ~25% of requests
  hit poisoned edge nodes per Ronnie's measurements.

## Triggering

Held back from public blog for ethical reasons; the header is a
specific malformed request header that the application layer treats
as "package not found" while the CDN treats as a valid cacheable
response.

## Impact

- DoS at the supply-chain layer -- every `npm install <pkg>` against a
  poisoned edge fails.
- Incident response often misattributes the outage internally ("our DNS
  is broken") before realizing npm is serving 404s.
- DDoS of Express on a deploy-Thursday at 5pm = global incident.

## Bypasses

(Defender-side; once registry forces `Cache-Control: no-store` on errors
the attack dies.)

## Seen in the wild

- {date: 2024-06-04, source: CT Ep 74} -- Ronnie's coordinated disclosure;
  GitHub fix landed only after disclosure timeline expired.

## References

- Critical Thinking Podcast Ep 74
- 0xLupin / Ronnie -- npm cache-poisoning writeup (lnh.tech blog)
- Related: [[dependency-confusion]], [[npx-binary-package-confusion]]
