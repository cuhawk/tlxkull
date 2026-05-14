---
title: DOMPurify post-output `replace()` re-introduces 2020 jQuery slash bypass
slug: dompurify-post-output-replace
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/sanitizer-bypass, technique/jquery]
inbound: []
---

# DOMPurify post-output `replace()` re-introduces 2020 jQuery slash bypass

## Pattern

Apps that pipe DOMPurify output through *any* post-sanitization string
transform reintroduce mutation surface. The canonical case is jQuery
`<= 3.5`: `jQuery.htmlPrefilter` rewrites self-closing tags like
`<style/>` to `<style></style>`. After Masato Kinugawa's 2020 finding,
Cure53 added a DOMPurify guard that detected this jQuery rewrite and
neutered the bypass. In a 2024 release, the guard was *removed*
("enough downstream protections elsewhere now").

That removal re-enabled the bypass on any application that:
1. Sanitizes input with DOMPurify.
2. Passes the output through `jQuery.html()` or jQuery's
   `htmlPrefilter`.
3. Uses a jQuery version that still does the slash-rewrite.

The payload uses `<style/>` (or any other void-element-like syntax) to
embed mutation-XSS that DOMPurify accepts as harmless markup but jQuery
later rewrites into an active context.

## Preconditions

- DOMPurify ≥ 2024-removed-guard version (or any earlier version
  before the original 2020 patch).
- jQuery `≤ 3.5` (still does the `<X/>` rewrite).
- Sanitized output flows through jQuery's `.html()` /
  `htmlPrefilter`.

## Detection

- Confirm DOMPurify version + jQuery version in browser-side bundles.
- Probe with `<style/>X<img src=x onerror=alert(1)>`; check
  post-jQuery DOM for `<style>X<img>` (slash collapsed).

## Triggering

```html
<style/><img src=x onerror=alert(1)>
```
through DOMPurify (allowed, `<style>` is a regular tag) → jQuery
rewrites the `/` collapse → context shifts so `<img>` is sibling of
`</style>` rather than text content → onerror fires.

## Bypasses

- For jQuery > 3.5: try `<title/>`, `<textarea/>` variants — depends
  on which void-rewrite jQuery retained.

## Seen in the wild

- {date: 2025-02-20, source: CT Ep 111} — Kevin Mizu confirms re-enabled
  bypass in current DOMPurify default config; ties to Masato Kinugawa's
  original 2020 jQuery research.

## References

- Masato Kinugawa — 2020 jQuery / DOMPurify writeup
- Cure53 DOMPurify changelog (2024 guard removal)
- Critical Thinking Podcast Ep 111
- Related: [[dompurify-pi-bypass]]
