---
title: onerror on Failed Resource Load (no interaction)
slug: onerror-resource-load
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# onerror on Failed Resource Load (no interaction)

## Payload

```html
<audio src/onerror=alert(1)>
```

## Variants

```html
<img src onerror=alert(1)>
<img/src/onerror=alert(1)>
<video src=x onerror=alert(1)>
<iframe src=x onerror=alert(1)>
```

## Context

Fires without user interaction when the browser attempts to load a resource and fails. `src` with an empty or invalid value causes an immediate load error, firing `onerror`. The `/` delimiter in `<audio src/onerror=...>` is a quirk-mode parser trick — the slash separates `src` attribute from `onerror` attribute without whitespace. `<img src onerror=...>` is the classic form; `<img/src/onerror=...>` removes spaces. Works in all browsers via `innerHTML`, `outerHTML`, `document.write`. Also used as the execution payload in prototype-pollution gadgets and consuming-tag mXSS payloads.

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
- [Consuming Tags and Hoisting](../../techniques/dom-xss/consuming-tags-and-hoisting.md)
- [Prototype Pollution to XSS](../../techniques/dom-xss/prototype-pollution-xss.md)
