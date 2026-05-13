---
title: input type=image onerror XSS (WAF bypass)
slug: input-type-image-onerror
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/dom-xss, technique/waf-bypass]
inbound: []
---

# input type=image onerror

## Pattern
`<input type="image" src="X">` is treated as a replaced image element
and fires `onerror` when src fails to load. WAF bypass: most WAFs only
flag `<img>` for image-related XSS, not `<input type=image>`.

MDN does not document the onerror handler firing — but it does.

## Preconditions
- HTML injection sink that allows `<input>`.
- WAF with `<img>`-specific rule (very common).

## Triggering
```html
<input type=image src=/ onerror=alert(1)>
```

## Related primitives (Ep 26 etc.)
- `<image>` outside SVG rewrites to `<img>` (HTML5 spec) — separate
  filter bypass for `img`/`IMG`-only blocks.
- Popover-target attribute `<button popovertarget="hiddenForm">` makes
  any element clickable.
- `<math>` wrapper makes `href="javascript:..."` clickable in Firefox.
- `<?xx>` numeric-tag becomes HTML comment in Chromium.

## Seen in the wild
- Critical Thinking Podcast Ep 62.

## References
- Critical Thinking Podcast Eps 26, 62
- HTML5 spec — input type=image
