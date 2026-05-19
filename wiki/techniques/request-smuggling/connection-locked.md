---
title: Connection-locked smuggling
slug: connection-locked
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/request-smuggling, technique/desync, scope/connection-locked]
inbound: []
---

# Connection-locked smuggling

## Pattern

The front-end opens a fresh back-end connection per client, so the smuggled prefix only attaches to *the attacker's own* next request — not to a different user. Direct cross-user request theft fails. The desync is real, but it cannot reach a victim through pooled connections.

This is the common case behind Cloudflare, Akamai, and any front-end that does per-client connection isolation or has very low keep-alive pooling.

## When to suspect

- Smuggling probes succeed locally (the second request on your own connection shows the smuggled effect) but fail to harvest other users' requests during longer Turbo Intruder runs.
- CDN documentation explicitly mentions per-client connection isolation.
- Reports historically downgraded ("won't fix — connection-locked").

## Why it's still a bug

The connection lock only blocks one of the exploitation primitives. Three others survive:

1. **Cache poisoning** — the smuggled response gets stored against a cache key. Once cached, every visitor sees the attacker payload, regardless of which back-end connection served the original. See [../cache-poisoning/smuggling-to-cache.md](../cache-poisoning/smuggling-to-cache.md).
2. **Internal header disclosure** — smuggle a request that reflects what the front-end injects (`X-Forwarded-For`, `X-Forwarded-Host`, internal trust tokens). The reflection lands in the attacker's response, not a victim's, but the leaked headers often enable authentication bypass (`X-User-Id`, `X-Internal-Auth`).
3. **Front-end security bypass** — reach paths or methods the front-end blocks. The attacker is the only one affected, but if `/admin` is gated only at the front-end, that is a clean privilege escalation.

## Detection

Turbo Intruder with `requestsPerConnection=2`:

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=1,
        requestsPerConnection=2,
        pipeline=False,
    )
    engine.queue(target.req)              # smuggle vehicle
    engine.queue(target.req.replace(...)) # second request on same connection
```

Repeater alternative: tab group → "Send group in sequence (single connection)".

If the smuggled effect requires you to be on the same connection as your own follow-up request, you have a connection-locked smuggle.

## Triggering — cache poisoning chain

Find a cacheable static asset (`/static/site.js`, fonts, images). Smuggle a request whose response will land in cache against the static asset's key:

```
POST /static/site.js HTTP/1.1
Host: target.example
Content-Length: 156
Transfer-Encoding: chunked

0

GET /attacker-controlled-page HTTP/1.1
Host: target.example
X-Ignore: X
```

Front-end caches the response (HTML / attacker payload) under `/static/site.js`. Subsequent users requesting `site.js` get the cached payload — script-type confusion or CSP bypass converts it to XSS. PayPal `fb-all-prod.pp2.min.js` is the canonical example.

## Impact

H1 and Synack triagers historically rejected connection-locked smuggling as low-impact. The accepted reframing post-2020 PortSwigger paper: if you can demonstrate cache poisoning or front-end-bypass, severity is still high (often Critical). Pair the connection-locked finding with one of those primitives before reporting.

## References

- [HTTP Request Smuggling SUMMARY](SUMMARY.md)
- [research-how-to-distinguish-http-pipelining-from-request-smuggling](../../sources/blogs/personal/portswigger-research/research-how-to-distinguish-http-pipelining-from-request-smuggling.md) — the canonical "is this actually smuggling or just pipelining?" decision tree.
- [Cache poisoning: smuggling-to-cache](../cache-poisoning/smuggling-to-cache.md)
