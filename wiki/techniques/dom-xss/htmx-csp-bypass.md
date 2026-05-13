---
title: HTMX CSP / sanitizer bypasses (suite)
slug: htmx-csp-bypass
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/dom-xss, technique/csp-bypass, technique/sanitizer-bypass]
inbound: []
---

# HTMX CSP / sanitizer bypasses

Suite of bypasses targeting apps using [HTMX](https://htmx.org). Source:
Mathias Karlsson + Justin Gardner research, Ep 68.

## Pattern
HTMX is HTML-over-the-wire. Several of its attributes invoke `eval()` or
`new Function()` internally, which forces hosts to allow `unsafe-eval` in
CSP and creates universal sanitizer bypasses.

## Specific bypasses

### 1. `eval`-based attribute primitives
HTMX `hx-trigger`, `hx-on:*`, `hx-vals` use `eval()` internally → apps must
allow `unsafe-eval`. Even with `unsafe-inline` blocked, attribute-based
trigger fires.

```html
<img hx-on:htmx:load="alert(1)" src=x>
```

**Mitigation:** HTMX config flag `allowEval: false` (defaults true).

### 2. `HX-Redirect` response-header XSS
HTMX assigns `window.location.href = responseHeader` with no scheme check.

```http
HX-Redirect: javascript:alert(1)
```

Useful when you control a URL that HTMX fetches cross-region.

### 3. `hx-disable` bypass via colon-syntax
`hx-disable` parser only checks legacy `hx-on="evt:..."` syntax, not new
`hx-on:event=...` colon-prefixed form.

```html
<div hx-disable>
  <img hx-on:click="alert(1)">  <!-- still fires -->
</div>
```

### 4. DOMPurify allows `data-*` → HTMX trigger
DOMPurify permits all `data-*` attrs by default. HTMX honors `data-hx-*`.

```html
<x data-hx-on:click="alert(1)">
```

Survives DOMPurify; HTMX picks it up post-sanitize.

### 5. `hx-trigger` template-injection into `eval`
`hx-trigger` value is concatenated into an anonymous-function wrapper and
`eval`'d. Inject template-breakout payload.

```html
<button hx-trigger="x[name],...alert(1)//]">
```

Triggers from opaque elements (`<input type=hidden>`, `<meta>`) where HTML
normally cannot fire handlers.

### 6. `HX-Retarget` / `HX-Location` overrides
Response headers `HX-Retarget` and `HX-Location` override `hx-target`,
defeating any `hx-disable` placed on the intended target element.

## Preconditions
- Target uses HTMX (look for `htmx.org/dist/htmx.min.js`, `hx-*` attrs in
  DOM, or `hx-vals`/`hx-trigger` in HTML responses).
- Sanitizer that allows `data-*` (most do, including DOMPurify default
  config).
- For redirect variant: attacker-controlled fetched response.

## Seen in the wild
- {date: 2024-04-25, target: undisclosed (Mathias prior bounty)} — Ep 68
  Critical Thinking Podcast HTMX 0-day suite.

## References
- Critical Thinking Podcast Ep 68 — "HTMX-SS with Mathias"
- Riotuck — DOMPurify + HTMX `data-hx-on` bypass
- HTMX docs: `hx-on`, `hx-trigger`, `HX-Redirect`, `hx-disable`
- See related: [[dompurify-pi-bypass]] for DOMPurify processing-instruction
  bypass class
