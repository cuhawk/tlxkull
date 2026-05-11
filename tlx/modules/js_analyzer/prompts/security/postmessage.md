---
id: postmessage
kind: security
title: postMessage origin / data validation
tags: [postmessage, cross-origin, listener]
always_include: false
priority: 50
---

postMessage / cross-frame messaging analysis.

Look for:
  window.addEventListener('message', handler) — flag any handler that does NOT
  validate `event.origin` against an allow-list before reading `event.data`.

Common bugs:
  - No origin check at all → any frame may inject.
  - Wildcard postMessage targetOrigin '*' on the sender side leaks data.
  - Origin compared with `indexOf` / `includes` instead of strict equality
    (e.g., 'evil.com.attacker.tld'.includes('evil.com') is true).
  - Trusting `event.source` without origin check.
  - JSON.parse on event.data without try/catch crashes; with eval is RCE.

Trace pattern:
  1. semantic_search "addEventListener message" / "onmessage".
  2. For each handler, walk to the first read of event.data.
  3. Confirm an `event.origin === 'https://known.tld'` (or strict allow-list)
     occurs *before* that read.
