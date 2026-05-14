---
title: MathML element makes any descendant clickable (Firefox)
slug: math-element-clickable-firefox
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/event-handler, browser/firefox]
inbound: []
---

# MathML element makes any descendant clickable (Firefox)

## Pattern

Firefox treats elements inside `<math>` (MathML namespace) as clickable
hyperlinks when they carry an `href` attribute, even on tag names that
don't otherwise support `href`. So `<math><xss href="javascript:alert(1)">x</xss></math>`
fires `javascript:` on click in Firefox. Why: MathML inherits XLink-style
`href` semantics on arbitrary child elements; the layout engine wires the
click handler to navigate.

Quirk noted by `@theRCEguy` and revisited on Ep 26.

## Preconditions

- Firefox (~2.5% market share, but matters for high-profile multi-browser
  bug bounty programs).
- HTML injection that allows the `<math>` element and at least one
  unknown-tag child with attributes.

## Detection

- Drop `<math><xss href="javascript:alert(1)">x</xss></math>` into the
  injection; click in Firefox -- alert.

## Triggering

```html
<math>
  <xss href="javascript:alert(1)">click</xss>
</math>
```

User must click; pair with click-jacking or cookie-consent dialog overlay
for a credible PoC.

## Bypasses

- Sanitizers that allow `<math>` plus arbitrary child tags but strip
  on-events still miss this -- the sink is `href`, not an on-handler.
- Not Chrome -- verify the program scope includes Firefox impact.

## Related

- [[event-handler-matrix]]
- [[popover-target-xss]]
- [[consuming-tags-and-hoisting]]

## Seen in the wild

- {date: 2023-07-06, source: CT Ep 26} -- "Don't forget about the magical
  math element which can make any HTML element clickable within the
  Firefox browser."

## References

- Critical Thinking Podcast Ep 26
- `@theRCEguy` tweet -- original disclosure
