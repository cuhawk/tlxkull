---
title: H2 downgrade request smuggling
slug: h2-downgrade-request-smuggling
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/server-side, technique/request-smuggling, technique/h2]
inbound: []
---

# H2 downgrade request smuggling

## Pattern
Frontend speaks HTTP/2 with client; backend speaks HTTP/1.1. Translation
layer (reverse proxy, CDN) must map H2 frames → H1 wire format. Attacker
exploits ambiguity in the translation to insert a hidden H1 prefix that
the backend interprets as a second request, while the frontend sees only
one stream.

Key H2.TE attack: inject `Transfer-Encoding: chunked` into an H2 request.
RFC forbids TE in H2, but many proxies forward it anyway. Backend switches
to chunked parsing; attacker can truncate the body, leaving a dangling
prefix that forms the beginning of a smuggled request.

H2.CL attack: inject `Content-Length` with a value larger than the H2
body. Backend reads that many bytes, overshooting into the next request.

Header injection via pseudo-headers: newline characters in `:path`,
`:method`, or `:authority` survive H2→H1 translation on some servers,
injecting extra headers or an entire second request-line into the
translated H1 stream.

Auto-retry amplification: when a connection appears to fail (H2 GOAWAY),
some clients auto-retry. If the front proxy poisoned the connection with a
dangling prefix, the retry's request gets prepended with attacker content.

## Preconditions
- Frontend accepts H2; backend receives H1 (H2-to-H1 downgrade path).
- Translation layer does not sanitize connection-specific headers
  (`Transfer-Encoding`, `Content-Length`) or pseudo-header values before
  emitting H1.
- At least one other user shares the back-end connection pool (classic
  "socket poison" model), OR attacker can trigger server-side retries.

## Detection
- Use Burp Suite HTTP/2 tab to inject `Transfer-Encoding: chunked` into
  an H2 request; observe timing difference (backend waits for chunk
  terminator).
- Inject `\r\n` (`%0d%0a`) in the `:path` pseudo-header; if the probe
  response echoes an unexpected header you injected, downgrade is
  vulnerable.
- Send H2 request with `Content-Length` larger than body; if 400 or
  timeout, backend parsed it as H1.
- Turbo Intruder / Burp Repeater "H2 CLTE/TECL" tabs for timing-based
  detection.

## Triggering
```
:method  POST
:path    /vulnerable-endpoint
:authority target.com
transfer-encoding: chunked

0

GET /admin HTTP/1.1
Host: target.com
X-Ignore: X
```
Backend receives the H1 translation and sees the chunked body terminate
at `0\r\n\r\n`, then reads `GET /admin HTTP/1.1…` as a new request on
the same socket.

For pseudo-header injection (CRLF in `:authority`):
```
:authority target.com\r\nTransfer-Encoding: chunked
```
Some proxies emit this verbatim into the H1 `Host:` line.

## Bypasses
- **H2 mandatory headers check**: some proxies reject H2 requests with
  `Content-Length` or `TE`; work around by encoding the header name
  (`transfer-encoding` vs `Transfer-Encoding` casing — H2 is
  case-insensitive, H1 parsers vary).
- **SSRF via Host injection**: inject `\r\nHost: internal-service.local`
  in the `:authority` pseudo-header to reach internal backends.
- **Akamai / Cloudflare stripping**: some CDNs strip TE before forwarding.
  Use CL mismatch instead.

## Seen in the wild
- Netflix: $20,000 (account takeover via socket poisoning — James Kettle).
- Bitbucket (Atlassian): $15,000 triple bounty (Kettle), H2.TE + response
  queue poisoning.
- Oath (Yahoo/AOL): $7,000 + $10,000 (Kettle).
- Apache mod_proxy zero-day: CRLF in `:path` injected second request;
  assigned CVE, coordinated disclosure by Kettle.
- Netlify, Jira: additional examples from "HTTP/2: The Sequel is Always
  Worse" (Black Hat USA 2021 / PortSwigger TV).

## References
- PortSwigger TV: "HTTP/2: The Sequel is Always Worse" — James Kettle
  (2021) — `wiki/sources/portswigger-tv/whisper/transcripts/gAnDUoq1NzQ_*.txt`
- PortSwigger Research: https://portswigger.net/research/http2
- Related: [[hop-by-hop-smuggling]], [[h2-request-tunneling]]
