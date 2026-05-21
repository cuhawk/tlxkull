---
title: CL.TE HTTP Smuggling — Whitespace / Encoding Bypass Variants
slug: cl-te-whitespace-bypass
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/request-smuggling, technique/desync, technique/waf-bypass]
inbound: []
---

# CL.TE HTTP Smuggling — Whitespace / Encoding Bypass Variants

## Pattern

Standard CL.TE / TE.CL desync (see [cl-te-desync](cl-te-desync.md)) requires
the front-end and back-end to disagree on which framing header wins. When the
front-end enforces `Content-Length` and the back-end accepts chunked encoding,
smuggling succeeds. However, many CDNs and load balancers strip or canonicalize
`Transfer-Encoding` headers before passing them to the origin. Attackers
bypass this by:

1. **Tab delimiter**: `Transfer-Encoding:\tchunked` — some parsers split on
   colon only without stripping tabs, causing the CDN to miss the header while
   the origin recognizes it.
2. **Space in chunk size**: inserting a space or comment before the chunk size
   causes the CDN to reject chunked parsing while the origin accepts it.
3. **`x` prefix**: `Transfer-Encoding: xchunked` — some origins accept this
   extension but CDNs reject it.
4. **Dual TE headers**: `Transfer-Encoding: chunked\r\nTransfer-Encoding: identity`
   — origin uses first, CDN uses last (or vice versa).

The key insight from Slack and Zomato-class bugs: even hardened modern stacks
can disagree on whitespace handling or comment interpretation in TE headers.

## Preconditions

- Same as [cl-te-desync](cl-te-desync.md): two parsers in the path.
- Front-end applies some TE canonicalization but not all bypass variants.
- Back-end is more permissive in its TE parsing.

## Detection

- Use Burp's HTTP Request Smuggler extension to try all TE obfuscation variants
  automatically.
- Manually: send the tab variant and compare timing with a normal chunked
  request; if the tab variant causes the back-end to hang (waiting for a
  terminator that the front-end already stripped), you have a candidate.

## Triggering

Tab bypass example:
```
POST / HTTP/1.1
Host: target.example
Content-Length: 6
Transfer-Encoding:\tchunked

0

X
```

The front-end sees `Transfer-Encoding:\tchunked` as an unrecognized header
name (not `Transfer-Encoding`) and honors `Content-Length: 6`. The back-end
parses it as chunked; reads the `0\r\n\r\n` and treats `X` as a new request.

## Bypasses

If the back-end normalizes TE headers: try H2 downgrade (see
[h2-downgrade-request-smuggling](h2-downgrade-request-smuggling.md)) where the
front-end converts HTTP/2 to HTTP/1.1 and re-adds TE headers.

## Seen in the wild

- 2019–2020 — Slack, $11,500. CL.TE smuggling via whitespace variant at
  Slack's CDN edge → origin desync. Attacker could capture other users'
  session cookies.
  [BBRE](https://www.youtube.com/watch?v=gzM4wWA7RFo)
- 2019–2020 — Zomato, same technique, separate program. Reported together
  in same BBRE episode.
  [BBRE](https://www.youtube.com/watch?v=gzM4wWA7RFo)

## References

- See also: [cl-te-desync](cl-te-desync.md), [h2-downgrade-request-smuggling](h2-downgrade-request-smuggling.md)
- James Kettle: "HTTP Desync Attacks: Request Smuggling Reborn" (PortSwigger)
