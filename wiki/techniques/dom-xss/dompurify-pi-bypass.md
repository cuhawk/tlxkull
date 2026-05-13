---
title: DOMPurify processing-instruction bypass
slug: dompurify-pi-bypass
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/dom-xss, technique/sanitizer-bypass]
inbound: []
---

# DOMPurify processing-instruction bypass

## Pattern
DOMPurify `sanitize()` accepts both string and `Element` input. When the
Element contains XML processing-instruction nodes (`<?xml ?>` style),
DOMPurify replaces them with HTML comment tags. Nested inside `<svg>` or
custom-tag-name configs, an unclosed PI (`<? ... >` with no `?>`) escapes
the SVG into HTML context and allows `<img onerror>` etc.

A separate bypass-of-the-bypass also exists via DOMPurify's
`CUSTOM_ELEMENT_HANDLING` config. Researcher: slonser_ ; Riotuck found
additional bypasses post-fix.

## Preconditions
- Target sanitizes user input via DOMPurify with default or custom-element
  config.
- Sanitized output is parsed as HTML in the browser.

## Detection
- Check DOMPurify version + config.
- Submit `<svg><?xml ?><img src=x onerror=alert(1)></svg>` and inspect
  sanitized output for surviving PI / nested image.

## Triggering
```html
<svg>
  <?xml something
  <img src=x onerror=alert(1)>
</svg>
```

Plus combination with permissive `data-*` (DOMPurify default):
```html
<x data-x=foo>
```

## Bypasses
- Cure53 ships same-day fixes; payload variants come and go.
- Variants chained with HTMX `data-hx-on:click=` survive sanitizer + fire
  on HTMX-rendered pages — see [[htmx-csp-bypass]].

## Seen in the wild
- {date: 2024-03-28, target: undisclosed} — Ep 64.
- {date: 2024-04-25, target: HTMX combo} — Ep 68.

## References
- Critical Thinking Podcast Eps 64, 68
- blog.slonser.info — DOMPurify PI bypass writeup
- Related: [[htmx-csp-bypass]]
