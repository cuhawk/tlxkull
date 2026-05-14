---
title: keydown-Triggered window.open (User-Gesture Source Other Than Click)
slug: keydown-user-gesture-popup
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/clickjacking, technique/user-gesture]
inbound: []
---

# keydown-Triggered window.open

## Pattern

Modern browsers gate `window.open(url)` behind a **user gesture** to
prevent pop-up spam. Conventional wisdom says "user gesture = click",
but the gesture-source set is broader. `keydown` events (any key press)
satisfy the requirement, as do `pointerdown`, `pointerup`, and
`touchend`. This widens PoC delivery for click-jacking-adjacent attacks:
- A page can capture any key press anywhere on the document and use it
  to spawn a new window without pop-up block.
- Combined with an "accept cookies" or "press any key to continue"
  social-engineering element, the gesture is trivially elicited.

## Preconditions

- A keydown handler (or other allowed gesture event) is reachable on
  the attacker page.
- `window.open` is called synchronously in the handler, with the URL or
  target the attacker wants opened.

## Detection

- Whitebox: scan for `window.open` calls inside `keydown` /
  `pointerdown` / `touchend` handlers - gesture-validity audit.

## Triggering

```html
<body>
  <p>Press any key to continue.</p>
  <script>
    addEventListener('keydown', () => {
      window.open('https://attacker.com/oauth-grab', '_blank');
    });
  </script>
</body>
```

Pairs naturally with [[ctrl-click-iframe-top-level-nav]] for chained
clickjacking flows.

## Bypasses

- Browsers with stricter gesture policy (Safari) may exclude `keydown`
  for popups - test cross-browser before relying.

## Seen in the wild

- {date: 2026-04-23, source: CT Ep 171} - Justin Gardner: highlighted as overlooked gesture source; useful for crafting cleaner PoCs that don't require a click target.

## References

- Critical Thinking Podcast Ep 171 - <https://www.youtube.com/watch?v=l5fs7Okdj3o>
- HTML spec - "Activation triggering input events".
- Related: [[ctrl-click-iframe-top-level-nav]], [[svg-enhanced-clickjacking]]
