---
title: React useParams uppercase %2F CSPT differential
slug: cspt-react-useparams
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/dom-xss, technique/cspt, technique/url-parsing]
inbound: []
---

# React useParams uppercase %2F CSPT differential

## Pattern
React Router's `useParams()` calls a normalize step that does a
**case-sensitive** `replace('%2F', '/')` (see `match-path` line ~118).
After a regression of an earlier double-decode patch, only the uppercase
form decodes to a slash. Lowercase `%2f` survives → server sees encoded,
React resolves to `/`. Attackers testing CSPT with lowercase have been
missing bugs.

## Preconditions
- Target uses React Router (any version with the regression).
- Some upstream consumer of `useParams()` interpolates the value into a
  `fetch()` URL / `<link href>` / `<img src>` etc. (the CSPT sink).

## Detection
- Send `/route/%252F<rest>` (lowercase) vs `/route/%252F<rest>` (uppercase)
  — diff resulting fetch URL the page emits.
- Inspect React Router version + `match-path.js` for the case-sensitive
  replace.

## Triggering
With route `/settings/:id`:
```
/settings/%252Fapi%252Fsecret  (uppercase F — decodes to /)
```
React lands `id = "/api/secret"` after double-decode. Downstream fetch:
```js
fetch(`/api/users/${id}`)  // → /api/users//api/secret
```

## Related variants
- **Triple-URL-encode for React CSPT**: server decodes once before parsing,
  React decodes once → triple-encode `%252525` to land literal `%2F` at the
  backend.
- **Next.js `await params` SCPT**: server-side `await params` in route
  handler ALSO decodes `%2F`. Concat into outbound URL string → server-side
  path traversal triggered via crafted client navigation. Same pattern in
  SvelteKit.
- **Splat-route signal**: route defined `/files/*` (splat) is much more
  CSPT-prone than `/files/:id`. Splat capture passed raw to fetch.

## Blind SCPT detection
```
/settings/<valid_segment>%2F..%2F<valid_segment>  → 200 (canonicalizes)
/settings/<garbage_segment>                       → 500
```
Differential confirms server-side normalization.

## Bypasses
- Lowercase `%2f` only decodes when the version drops the case-sensitive
  replace.
- For WAF blocks on `..`: `fetch()` strips `\t \n \r` from URL silently —
  payload `%2F%2E%09%2E%5C` bypasses WAF.

## Seen in the wild
- {date: 2026-04-02, target: undisclosed (XSSDoctor research)} — Ep 168.

## References
- Critical Thinking Podcast Ep 168 — XSSDoctor
- React Router GitHub `match-path` line ~118
- lab.ctbb.show — XSSDoctor full writeup
- See related: [[cspt-fetch-hijacking]]
