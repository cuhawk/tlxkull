---
title: DOMPurify ALLOWED_URI_REGEXP missing-anchor bypass
slug: dompurify-allowed-uri-regex-anchor
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/sanitizer-bypass, technique/regex]
inbound: []
---

# DOMPurify ALLOWED_URI_REGEXP missing-anchor bypass

## Pattern

DOMPurify lets the integrator override the URI-validation regex via the
`ALLOWED_URI_REGEXP` config option. The default regex is anchored with
`^...$` and tested against the *whole* URI value of `href` / `src` /
`action` / `xlink:href` / `<use href=>` attributes.

Developers who want to "lock down to our own domain" often write something
like:
```js
DOMPurify.sanitize(input, { ALLOWED_URI_REGEXP: /^https:\/\/mizu\.re/ })
```
or even:
```js
ALLOWED_URI_REGEXP: /https:\/\/mizu\.re/
```

Two common mistakes:
1. **Missing trailing `$`** — the regex matches anywhere in the URI;
   attacker prepends `javascript:alert(1)//` and appends the allowed
   domain.
2. **Unescaped `.`** — `mizu.re` matches `mizuXre`; attacker registers
   `mizuxre.com` or stuffs the value with characters that the URL
   parser later normalizes.

Attack payload (no trailing anchor):
```
javascript:alert(1)//https://mizu.re
```
DOMPurify sees the regex match (substring `https://mizu.re` is present);
the browser's URL parser treats the value as `javascript:alert(1)//...`
because `//` after the scheme is a comment for `javascript:` URIs.

## Preconditions

- Application uses DOMPurify with a custom `ALLOWED_URI_REGEXP`.
- Custom regex omits `^...$` anchors, or omits backslash-escapes on
  `.` / `?` / other meta-chars.
- A sink consumes the sanitized output and assigns to an attribute that
  produces a URL navigation (`href`, `xlink:href`, `<use href>`).

## Detection

- Set a Chrome DevTools log-point at the first line of DOMPurify's
  `sanitize()` function; dump the `cfg` argument.
- Inspect `cfg.ALLOWED_URI_REGEXP` source text — eyeball for missing
  `^` / `$` / unescaped `.`.
- Probe with `javascript:alert(1)//<the-domain-from-the-regex>`.

## Triggering

```html
<a href="javascript:alert(1)//https://mizu.re">click</a>
```
through DOMPurify with the missing-anchor regex passes; the `href`
fires `javascript:alert(1)` on click.

For `<use href>` (SVG): same payload, no click needed if the SVG is
animated/auto-loaded.

## Bypasses

- If only `^` is missing: append the allowed domain.
- If only `$` is missing: prepend `javascript:` and use `//` as comment.
- Unescaped `.`: register a domain that visually matches but routes
  elsewhere.

## Seen in the wild

- {date: 2025-02-20, source: CT Ep 111} — Kevin Mizu cites this as the
  most-frequently-found DOMPurify misconfig in bounty programs:
  "developers don't understand they are overwriting the default; they
  forget the dollar at the end."

## References

- DOMPurify config docs — `ALLOWED_URI_REGEXP`
- Kevin Mizu — mizu.re DOMPurify-in-bug-bounty article
- Critical Thinking Podcast Ep 111
- Related: [[dompurify-pi-bypass]]
