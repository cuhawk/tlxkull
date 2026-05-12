---
title: Shadow DOM onslotchange (no interaction)
slug: shadow-dom-slot-change
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# Shadow DOM onslotchange (no interaction)

## Payload

```html
x<template shadowrootmode=open><slot onslotchange=alert(1)>
```

## Context

Fires without user interaction when the declarative shadow root's slot is assigned content. The `shadowrootmode=open` attribute creates a shadow root declaratively; the `x` text node before the template immediately gets slotted, triggering `onslotchange` on parse. Chrome 90+/Edge; not supported in Firefox/Safari as of 2026 without polyfill. Useful when standard event handlers are blocked and only newer Chromium-specific APIs are available. Sink: `innerHTML` in Chromium.

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
