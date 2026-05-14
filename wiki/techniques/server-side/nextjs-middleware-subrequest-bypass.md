---
title: Next.js x-middleware-subrequest header bypass (CVE-2025-29927)
slug: nextjs-middleware-subrequest-bypass
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/auth-bypass, technique/framework-bug]
inbound: []
---

# Next.js `x-middleware-subrequest` header bypass

## Pattern
Next.js middleware (`middleware.ts` at root or under `pages/_middleware`)
runs on every request and is the typical home of auth checks, CSP
injection, geo redirects, locale rewrites. To prevent middleware → fetch
→ middleware infinite loops, Next.js trusts an internal header:

```
x-middleware-subrequest: <middleware-path>
```

If present and the value matches the path of the middleware about to run,
Next.js short-circuits the middleware and proceeds straight to the route
handler. The header is parsed from **client input**, so a remote attacker
can just send it.

Path values by Next.js version:
- ≤ 12.1: `pages/_middleware`
- ≥ 12.2: `middleware` (root) or `src/middleware`
- Repeat with `:` separator for nested middleware in newer versions
  (`middleware:middleware:middleware`).

## Impact
- Auth bypass on any route the middleware was guarding.
- CSP / X-Frame-Options injection bypass when middleware adds them.
- Cache-poisoning DoS when middleware rewrites locale/region — bypass the
  rewrite, get the cached default served regardless of the client's
  region.

## Preconditions
- Target uses Next.js middleware for security-relevant work.
- Vulnerable Next.js version not yet patched (CVE-2025-29927).

## Detection
- Recon: identify Next.js targets (e.g. via `__NEXT_DATA__` or build
  manifest paths) and fingerprint the version.
- Send candidate headers and look for `403 → 200` transitions on protected
  routes.

## Triggering
```http
GET /admin HTTP/1.1
Host: target
x-middleware-subrequest: middleware

```
Try variants:
```
x-middleware-subrequest: pages/_middleware
x-middleware-subrequest: src/middleware
x-middleware-subrequest: middleware:middleware
```

## Bypasses / hardening
- Patched in Next.js 15.2.3 / 14.2.25 / 13.5.9. WAF rules dropping the
  header at the edge are a stopgap.

## Seen in the wild
- {date: 2025, source: CT Ep 116} — zhero-web-sec landed against multiple
  bug bounty programs.

## References
- zhero-web-sec.github.io — Next.js corrupt middleware writeup
- CVE-2025-29927
- Critical Thinking Podcast Ep 116
- Related: [[secondary-context-path-traversal]]
