---
title: H2 request tunneling
slug: h2-request-tunneling
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/server-side, technique/request-smuggling, technique/h2, technique/ssrf]
inbound: []
---

# H2 request tunneling

## Pattern
A variant of H2 downgrade smuggling that does not require a shared
connection pool. Instead, the attacker wraps a complete HTTP/1.1 request
inside an H2 request body (or via header injection) such that the frontend
and backend disagree on where the outer request ends and the inner request
begins.

Unlike classic smuggling, tunneling targets per-stream isolation: the
hidden inner request is processed *only* by the backend, not by the proxy.
This makes it ideal for:
- **WAF/auth bypass**: headers added by the proxy (auth tokens, IP
  allowlisting headers) are absent in the tunneled inner request.
- **Internal SSRF**: inner request can target a different `Host` than the
  outer request without the proxy blocking it.
- **Header smuggling to internal services**: proxy may enforce HTTPS or
  authentication on the outer layer; tunneled inner request bypasses both.

Mechanism: inject a complete H1 request (including its own headers +
body) into the H2 body, exploiting a Content-Length mismatch or chunked
boundary that the proxy ignores but the backend parses. The backend may
route the inner request to a different handler than the outer one.

## Preconditions
- H2→H1 downgrade path exists (same as [[h2-downgrade-request-smuggling]]).
- No shared connection required (attacker's own H2 stream is sufficient).
- Backend parses the inner request headers separately from what the proxy
  forwarded.
- Target benefit: proxy adds security headers (auth, IP check) that the
  attacker wants to bypass.

## Detection
- Send a HEAD request with a smuggled GET body; if you receive two
  responses (one for HEAD, one for the tunneled GET), tunneling works.
- Inject `Host: internal-host` inside the tunneled body; observe whether
  the backend responds with internal-host content.
- `Content-Length` mismatch probing: set CL to a value that causes the
  proxy to consider the request complete while the backend reads further.

## Triggering
```
:method  POST
:path    /public-endpoint
:authority target.com
content-length: <outer-length>

GET /internal-admin HTTP/1.1
Host: 127.0.0.1
X-Forwarded-For: 127.0.0.1
Content-Length: 0

<padding to reach outer-length>
```
The proxy forwards the outer POST (adding its auth headers). The backend
reads the outer POST body and encounters the embedded GET, processes it
against the internal routing table.

## Bypasses
- **Proxy strips body from GET**: tunnel via POST with specially crafted CL.
- **Backend connection: close**: if backend closes after each response,
  tunnel is one-shot; still useful for single auth-bypass request.
- **Proxy validates Host header**: use `127.0.0.1` or CIDR-internal
  addresses that the proxy does not block in bodies (only in outer Host).

## Seen in the wild
- Demonstrated by James Kettle in "HTTP/2: The Sequel is Always Worse";
  exploited in several unnamed program bounties.
- Useful for bypassing Nginx/HAProxy auth_request directives that gate
  access based on proxy-added headers.

## References
- PortSwigger TV: "HTTP/2: The Sequel is Always Worse" — James Kettle
  (2021) — `wiki/sources/portswigger-tv/whisper/transcripts/gAnDUoq1NzQ_*.txt`
- PortSwigger Research: https://portswigger.net/research/browser-powered-desync-attacks
- Related: [[h2-downgrade-request-smuggling]], [[hop-by-hop-smuggling]]
