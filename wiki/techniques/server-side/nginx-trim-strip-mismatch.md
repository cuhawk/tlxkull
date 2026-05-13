---
title: Nginx trim-strip mismatch — route bypass via non-printable chars
slug: nginx-trim-strip-mismatch
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/server-side, technique/proxy-bypass]
inbound: []
---

# Nginx trim-strip mismatch

PortSwigger Top 10 2023.

## Pattern
Backend frameworks `trim()` various non-printable chars that nginx
`location` matcher doesn't strip. Send `GET /admin\xa0 HTTP/1.1`:
- nginx routes by `/admin\xa0` → no `/admin` rule → falls through to a
  permissive default location.
- Backend (Node, Spring, Flask, PHP) trims `\xa0` and reads `/admin` →
  serves admin endpoint.

Per-framework strip sets:
- **Node.js**: `\xa0` (v1.16–v1.22), `\x09` (tab), `\x0c` (form-feed).
- **Spring / Flask / PHP**: each with own set.

## Preconditions
- Nginx in front (or any front proxy with strict location matching).
- Backend framework that trims one of the bypass chars.

## Detection
- Test each non-printable byte appended to a protected path.
- Compare nginx routing decision vs backend response.

## Triggering
```
GET /admin\xa0 HTTP/1.1
Host: target.com
```
(byte 0xa0 appended after `/admin`.)

## Related
- Nginx header line-folding (Ep 60): `X-Foo: a\r\n\tb` = one header
  `X-Foo: a b`. AWS WAF doesn't fold, backend does → smuggle disallowed
  values past WAF.
- Nginx regex `location ~ "[^/]+"` MORE PERMISSIVE than `.*` for newline
  injection — `[^/]` includes `\n`, `.` doesn't (without `s` flag).
- Sergey Bobrov 505-detection probe for request-splitting: append `
  HTTP/13.37\r\n` → 505 status = proxy is splitting.
- Backend non-slash path prefix: `GET @host/path`, `GET ;param`,
  `GET *path`, `GET http://x/path HTTP/0.9`.
- [[nginx-dotslash-bypass]] — VMware vRNI `/./SAS/...` (Summoning Team).
- [[nginx-alias-traversal]] — off-by-slash alias.

## Seen in the wild
- Many in-the-wild via PortSwigger top 10 2023 winners.

## References
- portswigger.net/research/top-10-web-hacking-techniques-of-2023
- Critical Thinking Podcast Ep 60
