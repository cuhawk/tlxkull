---
title: Hop-by-hop header smuggling
slug: hop-by-hop-smuggling
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/server-side, technique/request-smuggling]
inbound: []
---

# Hop-by-hop header smuggling

## Pattern
Per RFC, headers named in `Connection: <header>` are stripped by the
front proxy before the back-end sees them. Send `Connection: <hopHeader>`
to instruct the proxy to strip an arbitrary header.

Jacopo Tediosi's Akamai attack: define `Content-Length` as hop-by-hop in
the connection header, smuggle a second request inside body, response
gets queued for the next requester.

## Preconditions
- Front proxy obeys RFC `Connection: <name>` semantics (most do).
- Back-end behaves differently when the header is missing (auth bypass,
  smuggling, cache poisoning).

## Detection
- Test `Connection: X-Forwarded-For` and observe whether back-end echoes
  XFF differently with/without it.
- Same for `Authorization`, `Cookie`, `Content-Length`, `Host`.

## Triggering
```
GET / HTTP/1.1
Host: target.com
Connection: Content-Length
Content-Length: 0

GET /admin HTTP/1.1
Host: target.com
...
```

## Related
- Nathan Davidson original hop-by-hop research (~2019).
- James Kettle CRLF in request-line: URL-encode `\r\n` (`%0D%0A`) in path
  (Ep 7).
- [[akamai-edge-smuggling]]
- [[smtp-smuggling]]

## Seen in the wild
- Akamai (Tediosi).
- PortSwigger Top 10 2022.
- Critical Thinking Podcast Ep 7.

## References
- Critical Thinking Podcast Ep 7
- Nathan Davidson hop-by-hop research
