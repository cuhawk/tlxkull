---
title: Smuggling-to-cache (chain)
slug: smuggling-to-cache
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/cache-poisoning, technique/request-smuggling, chain]
inbound: []
---

# Smuggling-to-cache (chain)

## Pattern

HTTP Request Smuggling alone provides per-connection impact: the smuggled bytes attach to whichever request is multiplexed next on the same pooled back-end connection. If the front-end uses per-client connection isolation (connection-locked smuggling, see [../request-smuggling/connection-locked.md](../request-smuggling/connection-locked.md)), there is no cross-user delivery on its own.

Smuggling-to-cache solves this by using the cache as the persistence layer. The attacker smuggles a request whose **response** the front-end then stores in cache. From that moment, *every* subsequent visitor to that cache key gets the attacker's response, regardless of which back-end connection serves them.

This is the highest-impact known cache-poisoning vector: it lets you choose any cacheable URL on the target — including the most heavily trafficked static assets — and serve attacker-controlled content from the target's own origin.

## Preconditions

- A confirmed smuggling primitive on the target (CL.TE, TE.CL, H2.CL, H2.TE, etc.).
- A cache layer in front of (or co-located with) the back-end that caches the relevant URL on `GET`.
- The cache stores responses keyed only on method + path (+ Host), not on the smuggled framing.
- Targeted URL is cacheable. Often it's enough to find any static asset under the same origin — `/static/*.js`, `/favicon.ico`, font files, framework bundles.

## Detection

1. Confirm the smuggling vector independently first (see [request smuggling SUMMARY](../request-smuggling/SUMMARY.md)).
2. Confirm the cache stores `.js` / static responses with `Age:` and `X-Cache:` HIT on repeat requests.
3. Send the smuggle vehicle (host request) + smuggled inner request targeting the static asset path. Observe whether the inner request's response gets cached under the static asset key.

## Triggering

The PayPal exploit from the PortSwigger desync paper is the reference:

```
POST /webstatic/r/fb/fb-all-prod.pp2.min.js HTTP/1.1
Host: c.paypal.com
Content-Length: 61
Transfer-Encoding: chunked

0

GET /webstatic HTTP/1.1
X-Ignore: X
```

Step-by-step:

1. Front-end honors `Content-Length: 61` → forwards the whole blob as one request to `/webstatic/r/fb/fb-all-prod.pp2.min.js`.
2. Back-end honors `Transfer-Encoding: chunked` → reads `0\r\n\r\n` as end-of-body, parses `GET /webstatic HTTP/1.1` as the start of a new request.
3. Back-end responds to `GET /webstatic` (the HTML index page).
4. Front-end receives that HTML response on the same connection it expected the response to `/webstatic/r/fb/fb-all-prod.pp2.min.js`.
5. Front-end caches the HTML response under cache key `/webstatic/r/fb/fb-all-prod.pp2.min.js`.
6. Every visitor to the PayPal login page loads `fb-all-prod.pp2.min.js` → cache HIT → receives HTML, parsed as JS by the browser.

Convert the HTML response to attacker-controlled JS by chaining to a reflected-XSS gadget on the smuggled inner request, or by hijacking a JSONP-style endpoint whose response is valid JS.

## Bypasses

- Cache may require a specific `Cache-Control` header on the response. If the smuggled inner endpoint returns no-cache headers, look for an endpoint that *does* return cacheable headers, or one whose Cache-Control can be overridden via unkeyed input (see [unkeyed-header.md](unkeyed-header.md)).
- Some caches strip `Set-Cookie` responses from cache. Pick smuggled endpoints that don't set cookies, or strip them via header truncation.
- CDN-side cache lock (Cloudflare's `Cache-Lock`) prevents re-fetching while a response is stored — useful to make poisoning persistent.

## Impact

This is the canonical PayPal-class finding. Severity is Critical in nearly every bounty program because:

- Persistent across users (cache lifetime).
- Persistent across user sessions (not bound to attacker session).
- Lands inside the target origin (browser SOP and CSP treat it as first-party).
- Can hijack a script reference loaded by the target's auth page → password capture, token theft, full ATO.

## Seen-in-the-wild

- PortSwigger desync paper — PayPal `c.paypal.com/webstatic/r/fb/fb-all-prod.pp2.min.js`. Critical bounty.
- Multiple Black Hat / DEF CON follow-ups: Slack, New Relic, Atlassian (each via different smuggling variants).
- See [research-http-desync-attacks-request-smuggling-reborn](../../sources/blogs/personal/portswigger-research/research-http-desync-attacks-request-smuggling-reborn.md).

## References

- [Cache poisoning SUMMARY](SUMMARY.md)
- [Request smuggling SUMMARY](../request-smuggling/SUMMARY.md)
- [Connection-locked smuggling](../request-smuggling/connection-locked.md)
- [research-http-desync-attacks-request-smuggling-reborn](../../sources/blogs/personal/portswigger-research/research-http-desync-attacks-request-smuggling-reborn.md)
