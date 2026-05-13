---
title: HTMX — quirks and bypass-relevant config
slug: htmx-notes
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [tool/htmx]
inbound: []
---

# HTMX notes

HTMX is HTML-over-the-wire. Server returns rendered HTML for fetch
responses. ~10-yr-old underlying framework; recent (2023–2024) trend
adoption surge.

## Bypass-relevant config

### `allowEval` (default: true)
HTMX `hx-trigger`, `hx-on:*`, `hx-vals` use `eval()` internally. Apps
must allow `unsafe-eval` in CSP if they use these features. With
`allowEval: false`, HTMX disables the eval-based attribute primitives.

### Response headers HTMX honors (security-relevant)
- `HX-Redirect` → `window.location.href = headerValue` no scheme check.
- `HX-Location` → `htmx.ajax(...)` to URL.
- `HX-Retarget` → overrides `hx-target` per response.
- `HX-Reswap` → overrides swap mode.
- `HX-Refresh` → triggers `window.location.reload()`.
- `HX-Trigger` → fires custom JS event (with attacker-supplied event
  name → can collide with handler names).

### Attribute syntax forms
- Legacy: `hx-on="event:body"`
- New (post v1.9): `hx-on:event="body"` — colon syntax.

`hx-disable` only checks legacy form → new colon syntax bypass.

## Equivalents in other frameworks
- Rails Hotwire (Turbo Frames + Turbo Streams) — Ruby equivalent. GitHub
  uses it. Per-form CSRF tokens path-bound.
- Laravel Livewire — PHP.
- Phoenix LiveView — Elixir.

## Related techniques
- [[htmx-csp-bypass]] — full bypass suite.
- [[dompurify-pi-bypass]] — DOMPurify + HTMX `data-hx-*` chain.
- [[csp-form-action-gap]] — adjacent CSP gap class (Hotwire affected).

## References
- htmx.org/docs/
- Critical Thinking Podcast Ep 68
