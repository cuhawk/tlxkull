---
title: HTTP Request Smuggling — summary
slug: request-smuggling-summary
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/request-smuggling, technique/desync, summary, index]
inbound: []
---

# HTTP Request Smuggling — summary

## What this class is

HTTP Request Smuggling — also called HTTP Desync — exploits disagreement between a front-end proxy (CDN, load balancer, WAF, reverse proxy) and the back-end origin server about where one HTTP request ends and the next begins on a reused TCP/TLS connection. By crafting a request whose body boundary is interpreted differently by the two hops, an attacker prepends arbitrary bytes onto the *next* request the back-end sees on that pooled connection. The victim is whichever client's request is multiplexed onto the same connection next.

Smuggling is an attack on the **HTTP parser frontier**, not on application code. The application layer behaves correctly given the bytes it receives; the bytes are simply not the bytes the next user actually sent.

## When to suspect

- Any deployment with a CDN or reverse proxy in front of an origin (Cloudflare, Akamai, Fastly, AWS ALB/ELB, nginx, HAProxy, Varnish, Envoy) — that is, almost any modern web target.
- HTTP/2 front-end downgrading to HTTP/1.1 back-end — H2.CL and H2.TE class.
- Behavior changes between requests sent with `Connection: keep-alive` versus `Connection: close`.
- Reflective endpoints that occasionally return another user's data, headers, or auth context.
- 4xx / 5xx responses arriving out of order with the request stream.
- Hop-by-hop header handling differences (`Transfer-Encoding`, `Content-Length`, `Connection`, `Upgrade`).

## Failure modes (class taxonomy)

| Variant | Front-end uses | Back-end uses | Smuggled bytes hide in |
|---|---|---|---|
| CL.TE | `Content-Length` | `Transfer-Encoding: chunked` | Body after CL bytes |
| TE.CL | `Transfer-Encoding: chunked` | `Content-Length` | Chunked extension or trailing chunks |
| TE.TE | Both, with obfuscated `Transfer-Encoding` header (one side ignores it) | The other | Same as TE side |
| H2.CL | HTTP/2 :method + cl header | HTTP/1.1 `Content-Length` | HTTP/2 body |
| H2.TE | HTTP/2 :method | HTTP/1.1 `Transfer-Encoding` | HTTP/2 body |
| CL.0 | `Content-Length` (positive) | Ignores body entirely (CL 0) | Body |
| Browser-powered (client-side desync) | Browser sends, victim's own browser pool desyncs | — | Pipelined fetch on shared connection |

## What you can do with a smuggle

1. **Steal next user's request prefix** — the back-end appends their bytes onto your smuggled request, returns the result in your response, leaking their cookies / auth headers.
2. **Bypass front-end security controls** — front-end blocks `/admin`, but smuggled inner request goes straight to back-end with that path.
3. **Cache poison via smuggle** — smuggle a request whose response gets stored under a benign cache key. See [../cache-poisoning/smuggling-to-cache.md](../cache-poisoning/smuggling-to-cache.md). This is the highest-impact chain because it converts a per-connection bug into an everyone-affected bug.
4. **Reveal internal headers** — smuggle a request that reflects what the front-end injected (`X-Forwarded-*`, internal trust headers), often gives auth-bypass primitives.
5. **Connection-locked smuggling** — attacker and victim land on different connections so direct request-prefix theft fails, but cache poisoning and input-reflection disclosure still work.

## Detection workflow

1. Time-based probe: send a malformed CL/TE request; if the back-end stalls waiting for "the rest of the body" the front-end already forwarded, the connection hangs until timeout — confirms desync.
2. Differential probe: send the same payload twice in a single connection (`requestsPerConnection=2` in Turbo Intruder, or Repeater "Send group in sequence (single connection)") and observe whether the second response shows the smuggled effect.
3. HTTP/2 ↔ HTTP/1 boundary probe: send raw HTTP/2 with header injection in `:path` or pseudo-headers; downstream HTTP/1.1 may reparse and split.
4. CDN identification first — Cloudflare, Akamai, Fastly each have known smuggling research; pin the vector to the CDN family before fuzzing blindly.

## External references

| Topic | PayloadsAllTheThings | HackTricks | PortSwigger |
|---|---|---|---|
| Request smuggling | [`Request Smuggling/`](../../_external/payloads-all-the-things/Request%20Smuggling/README.md) | [`http-request-smuggling/`](../../_external/hacktricks/src/pentesting-web/http-request-smuggling/README.md) | [research-http-desync-attacks-request-smuggling-reborn](../../sources/blogs/personal/portswigger-research/research-http-desync-attacks-request-smuggling-reborn.md) |
| HTTP/2 downgrade | — | [`request-smuggling-in-http-2-downgrades.md`](../../_external/hacktricks/src/pentesting-web/http-request-smuggling/request-smuggling-in-http-2-downgrades.md) | — |
| Pipelining vs smuggling | — | — | [research-how-to-distinguish-http-pipelining-from-request-smuggling](../../sources/blogs/personal/portswigger-research/research-how-to-distinguish-http-pipelining-from-request-smuggling.md) |
| Response smuggling / desync | — | [`http-response-smuggling-desync.md`](../../_external/hacktricks/src/pentesting-web/http-response-smuggling-desync.md) | — |
| Connection smuggling | — | [`http-connection-request-smuggling.md`](../../_external/hacktricks/src/pentesting-web/http-connection-request-smuggling.md) | — |
| Hop-by-hop header abuse | — | [`abusing-hop-by-hop-headers.md`](../../_external/hacktricks/src/pentesting-web/abusing-hop-by-hop-headers.md) | — |
| CRLF injection (cousin class) | [`CRLF Injection/`](../../_external/payloads-all-the-things/CRLF%20Injection/README.md) | [`crlf-0d-0a.md`](../../_external/hacktricks/src/pentesting-web/crlf-0d-0a.md) | — |

## Related local pages

- [Cache poisoning SUMMARY](../cache-poisoning/SUMMARY.md) — smuggling is one of the strongest cache-poisoning delivery mechanisms.
- [CSRF SUMMARY](../csrf/_index.md) — smuggled requests can carry the victim's cookies if pooled on the same connection.
- [server-side / h2-downgrade-request-smuggling](../server-side/h2-downgrade-request-smuggling.md) — Kettle's HTTP/2 downgrade deep dive
- [server-side / h2-request-tunneling](../server-side/h2-request-tunneling.md) — HTTP/2 tunneling primitive (related desync class)
- [server-side / h3-connection-contamination](../server-side/h3-connection-contamination.md) — HTTP/3 same-org connection sharing
- [server-side / connection-state-smuggling](../server-side/connection-state-smuggling.md) — pooled-connection state confusion
- [server-side / akamai-edge-smuggling](../server-side/akamai-edge-smuggling.md) — Akamai-specific edge desync
- [server-side / hop-by-hop-smuggling](../server-side/hop-by-hop-smuggling.md) — hop-by-hop header abuse
- [server-side / cloudflare-cache-key-header-overflow](../server-side/cloudflare-cache-key-header-overflow.md) — Cloudflare cache-key boundary
- [server-side / smtp-smuggling](../server-side/smtp-smuggling.md) — same parser-disagreement pattern, different protocol

## Sub-patterns to expand

- [x] [`cl-te-desync.md`](cl-te-desync.md) — classic CL.TE / TE.CL variants
- [x] [`http2-downgrade.md`](http2-downgrade.md) — H2.CL / H2.TE on downgrading proxies
- [x] [`connection-locked.md`](connection-locked.md) — pooled-connection-only smuggling and how to extract value
- [ ] `cl-0-desync.md` — CL.0 / 0.CL variants
- [ ] `te-obfuscation-cheatsheet.md` — every `Transfer-Encoding:` obfuscation that has worked on at least one stack
- [ ] `client-side-desync.md` — browser-powered desync (PortSwigger 2022)
- [ ] `cdn-fingerprints.md` — per-CDN known vectors (Cloudflare, Akamai, Fastly, AWS ALB)
