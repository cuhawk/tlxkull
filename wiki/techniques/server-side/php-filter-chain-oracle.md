---
title: PHP Filter-Chain Oracle Exfil with Lightyear
slug: php-filter-chain-oracle
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/php, technique/file-read]
inbound: []
---

# PHP Filter-Chain Oracle Exfil with Lightyear

## Pattern

PHP supports stream wrappers like `php://filter/convert.iconv.UTF-8.UTF-16/
resource=...` that chain encoding transforms. A long chain of `iconv`
filters can act as an oracle, producing per-byte read primitives even from
sinks that don't directly return file contents (e.g., a single byte of the
file leaks through error/length differentials).

**Lightyear** (2024) is a tool that improves on the older
`php-filter-chains-oracle-exploit`:

- Reads files of tens of thousands of bytes with payloads only a few
  thousand characters long - usable even when injection is via a GET
  parameter limited to ~8 KB.
- Faster and more efficient: smaller per-byte payloads.
- Produces no PHP warnings/errors - silent to defenders.

Used to exfiltrate `.env` files, source code, and other secrets when an
attacker has injection into any PHP function that accepts a stream wrapper
(`file_get_contents`, `include`, `fopen`, `readfile`, `simplexml_load_file`,
many more).

## Preconditions

- Target is PHP.
- Injection lands in a function that supports stream wrappers
  (`php://filter/...`).
- File of interest is readable by the PHP process.

## Detection

- Sink inventory: grep `file_get_contents`, `include`, `require`, `fopen`,
  `XMLReader::open`, `imagecreatefromstring` (via wrapper), etc., for
  user-controlled paths.
- Probe: inject `php://filter/convert.base64-encode/resource=/etc/passwd`
  and inspect output / error differential.

## Triggering

```bash
# Lightyear (replaces older filter-chains tool)
python lightyear.py \
  --target 'https://victim.com/page.php?file=PAYLOAD' \
  --file /var/www/.env \
  --method GET
```

Manual oracle (small probe):
```
php://filter/convert.iconv.UTF-8.UTF-16LE|convert.base64-encode/resource=/etc/passwd
```

## Bypasses

- GET parameter size limits (URI too long): switch to Lightyear's
  compact-payload mode (~2 KB payloads dump 10s of KB).
- WAF blocking `php://filter` literal: try `pHp://`, URL-encode the
  scheme, or chain through another wrapper that resolves to `php://`.
- A PHP PR to limit filter chain depth was opened in 2024 and may merge as
  a configurable option (`max_filter_count`). Currently unlikely to land
  enabled-by-default.

## Seen in the wild

- {date: 2024-11-14, source: CT Ep 97} - Lightyear announced; replaces `php-filter-chains-oracle-exploit` as the go-to tool.

## References

- Lightyear tool - referenced in episode show notes.
- Original `php-filter-chains-oracle-exploit` (2023).
- Critical Thinking Podcast Ep 97 - <https://www.youtube.com/watch?v=m5mR6dvhtpg>
- Related: [[php-filter-chain-rce]]
- [Server-side SUMMARY](SUMMARY.md)
