---
title: HTTP/2 downgrade smuggling (H2.CL, H2.TE)
slug: http2-downgrade
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/request-smuggling, technique/desync, protocol/http2]
inbound: []
---

# HTTP/2 downgrade smuggling

## Pattern

HTTP/2 carries no `Content-Length` or `Transfer-Encoding` headers semantically — body length is framed at the protocol level (`DATA` frames + `END_STREAM` flag). When a front-end terminates HTTP/2 and proxies HTTP/1.1 to the back-end, it must *synthesize* `Content-Length` (or `Transfer-Encoding: chunked`) from the HTTP/2 frames. If the front-end blindly forwards user-supplied `content-length` / `transfer-encoding` pseudo-headers without sanitization, the back-end sees an HTTP/1.1 request whose framing disagrees with the actual body length.

- **H2.CL**: attacker sets `content-length` in HTTP/2 to a smaller value than the real DATA payload. Front-end forwards `Content-Length: N` plus full body; back-end reads `N` bytes and treats the rest as a new request.
- **H2.TE**: attacker sets `transfer-encoding: chunked` in HTTP/2. Front-end forwards `Transfer-Encoding: chunked` plus the body; back-end interprets the body as chunked and stops at the first `0\r\n\r\n` it can synthesize from the payload.

## Preconditions

- Front-end speaks HTTP/2 to clients, HTTP/1.1 to origin (very common: AWS ALB → EC2, Cloudflare → origin without H2-to-H2, Akamai → origin).
- Front-end does not strip `content-length` / `transfer-encoding` from incoming HTTP/2 headers.
- Back-end is a permissive HTTP/1.1 parser.

## Detection

- Burp's HTTP Request Smuggler extension has H2 downgrade probes.
- Send raw HTTP/2 via `curl --http2` or `nghttp` with explicit header injection.
- CRLF injection inside HTTP/2 header values: HTTP/2 doesn't reject `\r\n` the way HTTP/1.1 does. Bytes like `\r\nHost: evil.com\r\n` inside a pseudo-header are forwarded into the HTTP/1.1 stream as literal CRLF, splitting the request.

## Triggering

H2.CL — minimal example sent over HTTP/2:

```
:method   POST
:path     /
:authority target.example
content-length 0

GET /admin HTTP/1.1
Host: target.example


```

Front-end downgrades to HTTP/1.1 with `Content-Length: 0`. Back-end reads zero bytes of body, then sees `GET /admin HTTP/1.1` on the wire as the next request — bypassing whatever auth or path-blocking the front-end applies to `/admin`.

H2.TE — request with smuggled chunked body:

```
:method   POST
:path     /
:authority target.example
transfer-encoding chunked

0

GET /admin HTTP/1.1
Host: target.example


```

CRLF injection variant — splits via header value:

```
:method   GET
:path     /
:authority target.example
foo       bar\r\n\r\nGET /admin HTTP/1.1\r\nHost: target.example\r\n\r\n
```

## Bypasses

- HTTP/2 implementations that strip *some* hop-by-hop headers but not `transfer-encoding` — RFC 7540 §8.1.2.2 forbids it, but enforcement is uneven.
- Pseudo-header smuggling: inject CRLF into `:path`, `:authority`, or `:scheme` values on stacks that re-serialize them naively.
- Trailer-frame smuggling on back-ends that read HTTP/2 trailers as a continuation of headers.

## Impact ladder

Same as [`cl-te-desync.md`](cl-te-desync.md). H2-downgrade often yields cleaner exploitation because HTTP/2 clients (browsers, curl) cooperate with the attacker on framing — no need to fight a strict HTTP/1.1 client serialization.

## Seen-in-the-wild

- Netflix HTTP/2 downgrade smuggling — Cloudflare presentation, 2021.
- AWS ALB → origin H2.TE for several years before being patched.
- See [research-http-desync-attacks-request-smuggling-reborn](../../sources/blogs/personal/portswigger-research/research-http-desync-attacks-request-smuggling-reborn.md) follow-ups.

## References

- [HTTP Request Smuggling SUMMARY](SUMMARY.md)
- [hacktricks: request-smuggling-in-http-2-downgrades](../../_external/hacktricks/src/pentesting-web/http-request-smuggling/request-smuggling-in-http-2-downgrades.md)
