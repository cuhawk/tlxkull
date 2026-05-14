---
title: javascript:name URI - Payload-less XSS Trigger
slug: javascript-uri-name-payload
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/waf-bypass, technique/smuggling]
inbound: []
---

# `javascript:name` URI - Payload-less XSS Trigger

## Pattern

When a browser navigates to `javascript:<expr>`, the expression's return
value (if a string) is set as the new document's content under the
**previous page's origin**. Because `window.name` persists across
navigations and is an arbitrary attacker-set string, the URL
`javascript:name` is a **complete XSS payload that does not contain the
XSS payload** - the actual exploit bytes live in `window.name`, set by
the attacker page before navigation, and never appear in any HTTP request
or URL.

Variants that don't require `name` to be set first:
- `javascript:1` - renders `1` on the page.
- `javascript:persistent` - global that holds `1`.
- Any global string reference accessible at that moment.

The technique is genuinely WAF-invisible: the only bytes the WAF sees are
`javascript:name`, which most WAFs allow because they're not signature-
matching on globals.

## Preconditions

- Sink accepts a `javascript:` URI (e.g. `<a href>`, `window.open`,
  `location.assign`, form action when nav-allowed).
- Attacker controls the surrounding window's `window.name` (i.e.
  same browsing-context group via `window.open` with `name=` argument).

## Detection

- `js_analyzer`: any `location.href = userInput` or
  `anchor.href = userInput` where the input could equal
  `javascript:name` after WAF filtering.
- Test: open a popup with `window.open(url, 'X<svg/onload=alert(1)>')`,
  then navigate the popup to `javascript:name`.

## Triggering

```html
<!-- attacker.com -->
<a href="https://victim.com/redirect?u=javascript:name"
   target="<svg/onload=alert(1)>">click</a>
```

The link's `target` attribute sets the new window's name to the SVG
string. Navigating that new window to `javascript:name` renders the SVG
on victim.com's origin.

## Bypasses

- WAFs that block `javascript:` literally - case toggle (`JaVaScript:`),
  tab/newline inside scheme (`java\tscript:`), or `\x01\x02\x03javascript:`
  whitespace prefix.
- Sinks that pass URLs through a parser - `name` as a single token survives
  most URL validators because the URI has no fragment / query / path.

## Seen in the wild

- {date: 2024-11-14, source: CT Ep 97} - discussed by Gardner / Margolis as a classic, well-documented WAF-invisible payload pattern.

## References

- Critical Thinking Podcast Ep 97 - <https://www.youtube.com/watch?v=m5mR6dvhtpg>
- Related: [[window-name-exfil]], [[waf-bypass]]
