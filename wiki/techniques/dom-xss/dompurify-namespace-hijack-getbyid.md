---
title: DOMPurify double-call namespace hijack via getElementById clobbering
slug: dompurify-namespace-hijack-getbyid
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/sanitizer-bypass, technique/dom-clobbering]
inbound: []
---

# DOMPurify double-call namespace hijack via getElementById clobbering

## Pattern

When an application calls `DOMPurify.sanitize()` twice in a row with two
*adjacent* user inputs, and the second call's namespace is selected by
reading an element via `document.getElementById('config')` or similar
selector, a DOM-clobbering payload in the *first* input can change the
DOM such that the second call's namespace lookup resolves to an
attacker-controlled `<svg>` or `<math>` element. The second sanitize
then runs in SVG/MathML namespace, where DOMPurify's HTML-namespace
mitigations don't apply.

This is "Dom Clobbering Light": you don't need a global; you just need
to control which element gets returned for an ID-or-name lookup that
the sanitize wrapper uses to detect "in what context am I running."

## Preconditions

- App calls `DOMPurify.sanitize()` at least twice within the same flow.
- Between calls, the sanitized output is inserted into the DOM where
  it can satisfy an ID/name selector.
- The wrapper reads `document.getElementById('config')` /
  `document.querySelector('#x')` / similar to decide context for the
  second call.
- DOMPurify version where the bypass exists in SVG/MathML namespace
  (Mizu's specific version-dependent payload).

## Detection

- Static-search the app's JS bundle for `DOMPurify.sanitize` —
  positive if there are ≥2 calls with overlapping data flows.
- DOMlogger++ hook on `DOMParser.prototype.parseFromString` — count
  invocations during a single user action.

## Triggering

First input — drop a clobbering element with the ID used by the
wrapper:
```html
<svg id="config"><foreignObject>...</foreignObject></svg>
```

Second input — payload that's safe in HTML namespace but lethal in
SVG/MathML:
```html
<math><mi//xlink:href="javascript:alert(1)">click</mi></math>
```
The wrapper's namespace lookup returns the clobbered `<svg>` element;
DOMPurify runs in SVG namespace; payload survives sanitization and
fires.

## Bypasses

- Newer DOMPurify versions catch some cross-namespace bypasses; pair
  with [[dompurify-pi-bypass]] or
  [[dompurify-allowed-uri-regex-anchor]] for full coverage.

## Seen in the wild

- {date: 2025-02-20, source: CT Ep 111} — Kevin Mizu, found in a bug bounty
  program before the fix; the specific version is restricted.

## References

- mizu.re — DOMPurify in Bug Bounty article (post-research follow-up)
- Critical Thinking Podcast Ep 111
- Related: [[dompurify-pi-bypass]], [[dom-clobbering-to-xss]]
