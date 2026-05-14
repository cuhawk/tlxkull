---
title: SVG-Enhanced Clickjacking (Visual Click Feedback Under Invisible Iframe)
slug: svg-enhanced-clickjacking
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/clickjacking, technique/svg]
inbound: []
---

# SVG-Enhanced Clickjacking

## Pattern

Classic clickjacking puts a near-invisible iframe over a visible-looking
button on the attacker page. Modern users notice the lack of visual
feedback on the visible button - buttons don't depress, hover states
don't activate, focus doesn't move. Lyra (2026) published an SVG-based
technique that gives the **decoy** button realistic click feedback while
the **real** click lands inside the iframe.

The trick uses SVG filters and `:active` styling on overlay SVG paths to
produce a click animation that fires on `pointerdown` / `pointerup` -
visually convincing the victim their click "worked" even though the
actual mouse event was consumed by the iframe overlay.

Additionally enables "modal" interactions that adjust to victim cursor
position via SVG `mouseover` filters - the lure looks responsive without
JavaScript on the visible elements.

## Preconditions

- Target supports framing (no `X-Frame-Options`/`frame-ancestors`).
- The attack requires a visible decoy element that mimics interactive
  UI (button, form, etc.).

## Detection

- Watch for SVG elements with `filter:` references and `:active`
  pseudo-class styling overlaid on iframe content - pattern of
  click-feedback SVG.

## Triggering

```html
<style>
  .decoy {
    filter: url(#shadow);
    transition: filter 100ms;
  }
  .decoy:active { filter: url(#shadow-pressed); }
</style>

<svg height="0" width="0">
  <filter id="shadow"><feDropShadow dx="2" dy="2"/></filter>
  <filter id="shadow-pressed"><feDropShadow dx="0" dy="0"/></filter>
</svg>

<div class="decoy">Click here for free coupon</div>
<iframe src="https://victim.com/action-trigger"
        style="position:absolute;top:0;left:0;opacity:0.01;
               width:100%;height:100%"></iframe>
```

Combine with [[ctrl-click-iframe-top-level-nav]] and CSS that hides the
decoy unless the Ctrl key is held - only the well-instructed victim
sees the lure, so the attack is harder for casual users to stumble
across (less likely to be reported as suspicious by an aware victim
visiting attacker.com directly).

## Bypasses

- `frame-ancestors 'none'` - defeats.
- Cross-origin isolation policies - defeat under stricter modes.

## Seen in the wild

- {date: 2026-04-23, source: CT Ep 171} - Justin Gardner cited Lyra's SVG-enhanced clickjacking research; planning to build a reusable library.

## References

- Lyra - SVG-enhanced clickjacking research (referenced in episode).
- Critical Thinking Podcast Ep 171 - <https://www.youtube.com/watch?v=l5fs7Okdj3o>
- Related: [[ctrl-click-iframe-top-level-nav]], [[keydown-user-gesture-popup]]
