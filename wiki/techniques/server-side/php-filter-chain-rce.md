---
title: PHP filter-chain LFI → RCE
slug: php-filter-chain-rce
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/server-side, technique/rce, technique/lfi]
inbound: []
---

# PHP filter-chain LFI → RCE

PortSwigger Top 10 2023.

## Pattern
Chain PHP wrappers (`php://filter/convert.iconv...|...|.../resource=...`)
to fabricate arbitrary PHP source from an arbitrary readable file, then
execute via `include`. Eliminates the LFI → RCE precondition (no log
poisoning, no file-upload, no temp-file race).

## Preconditions
- LFI sink where attacker controls `include`/`require`/`include_once`
  argument.
- PHP 8.x (iconv filter chain available).

## Detection
- Test `php://filter/convert.base64-encode/resource=/etc/passwd` →
  base64-encoded passwd in response confirms filter wrapper support.

## Triggering
Use `php-filter-chain-generator` (synacktiv) to produce a payload that,
when included, emits attacker PHP source:
```
php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-decode|...
... very long chain ...
.../resource=<any-readable-file>
```

Payload chains UTF-8 → CSISO2022KR conversions plus base64-decode to
build arbitrary PHP bytes byte-by-byte.

## Related
- LFI → log-poisoning RCE (legacy fallback).
- LFI → temp-file race (more reliable on Windows).

## Seen in the wild
- PortSwigger Top 10 2023.
- Critical Thinking Podcast Ep 60.

## References
- synacktiv/php_filter_chain_generator (GitHub)
- portswigger.net/research/top-10-web-hacking-techniques-of-2023
- Critical Thinking Podcast Ep 60
