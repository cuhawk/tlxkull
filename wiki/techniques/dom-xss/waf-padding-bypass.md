---
title: WAF Padding Bypass (no-WAF-pls)
slug: waf-padding-bypass
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/waf-bypass, technique/padding]
inbound: []
---

# WAF Padding Bypass (no-WAF-pls)

## Pattern

Most cloud WAFs (Cloudflare, AWS WAF, Akamai, Imperva) impose a hard
inspection size limit on request bodies - between **8 KB and ~1 MB**
depending on the product and tier. Requests larger than the limit are
**not inspected** but are forwarded to the origin unchanged. By padding
a request body with junk (e.g. `A=AAA...A&` repeated) to push the
sensitive portion of the body past the inspection threshold, an attacker
defeats signature matching.

Assetnote / Shubs released "no-waf-pls" at H1-2024 - the tool that
automates this. Available as Burp and Caido extensions (Justin authored
the Caido version) and as a hosted web tool at
`tools.slcyber.io/no-waf-pls`.

## Preconditions

- Target origin accepts large request bodies (no separate origin-side
  size limit below the WAF threshold).
- WAF in front uses size-based inspection truncation (most do).

## Detection

- Probe: send a known-blocked payload (e.g. `' OR 1=1--`) -> 403. Pad
  with 16 KB of junk before the payload, retry -> 200. If origin
  processes the payload, confirmed.
- Per-WAF thresholds vary; binary search the padding size starting at
  8 KB.

## Triggering

URL-encoded body padding:

```
POST /endpoint HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 16500

junk=AAAAAAAA...[16 KB of A's]...&realparam=' OR 1=1--
```

JSON body padding:

```json
{
  "junk": "AAAAAAAAAA...[16 KB]...",
  "realparam": "' OR 1=1--"
}
```

Multipart with large junk field, similar approach.

## Bypasses

This IS the bypass - for WAF-side mitigation, see no-waf-pls README for
per-WAF inspection limits and config recommendations.

## Seen in the wild

- {date: 2024-05-30, source: CT Ep 73} - Assetnote release of no-waf-pls; documented bypasses against Cloudflare, AWS WAF, Akamai, Imperva.

## References

- Assetnote no-waf-pls writeup - H1-2024 talk.
- tools.slcyber.io/no-waf-pls - hosted web tool.
- Critical Thinking Podcast Ep 73 - <https://www.youtube.com/watch?v=uHOxsmdsXUA>
- Related: [[waf-bypass]], [[optional-chaining-waf-bypass]]
