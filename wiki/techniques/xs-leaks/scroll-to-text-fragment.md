---
title: Scroll-to-text-fragment xs-leak
slug: scroll-to-text-fragment
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/xs-leaks]
inbound: []
---

# Scroll-to-text-fragment xs-leak

## Pattern
Chrome `#:~:text=word` fragment causes auto-scroll IF the navigation came
from same-origin. Iframe a target page with `#:~:text=secret`; if the
word is present, the iframe scrolls. Chrome bug: the parent window also
scrolls (treated as accepted risk pre-Yusuf's report) → 1-bit oracle of
"word present in cross-origin page".

Combined with a "redirect-via-attacker-controlled-fragment" gadget on the
target (e.g. `facebook.com/some-endpoint` doing
`window.opener.location.href = <URL with hash>`), refresh repeatedly to
walk the search space without losing browsing session.

For character-level granularity:
- Force page served as `text/plain` (all searchable text, incl. CSRF
  tokens).
- Abuse charset confusion (re-encode as UTF-16) to make Chinese-style word
  boundaries on every character pair.

## Preconditions
- Chrome (technique browser-specific).
- Cross-origin gadget that triggers a same-origin nav with attacker
  fragment.
- Target page has searchable text content.

## Detection
- Test iframe with `#:~:text=knownword` → check whether parent scrolls.
- Find `window.opener.location.href = ...` style sinks on target.

## Triggering
```js
// Attacker page
const w = window.open('https://target.com/gadget-redirect#:~:text=' + encodeURIComponent(guess));
// Detect parent scroll via window.scrollY polling or visibilitychange events.
```

## Bypasses
- Chrome no longer fires `hashchange` on cross-origin
  `window.opener.location.href = '...with-hash'` without user gesture
  (post-Yusuf patch).

## Related
- [[postmessage-async-origin-swap]]
- [[math-random-prediction]]
- frame-count xs-leak (`attackerWin.frames.length`)
- history-length xs-leak

## Seen in the wild
- Facebook / Meta — Yusuf Sammouda chains, Ep 58.

## References
- Critical Thinking Podcast Ep 58
- xsleaks.dev
