---
title: Match-and-replace admin-flag endpoint discovery
slug: match-replace-admin-flag
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/idor, technique/recon]
inbound: []
---

# Match-and-replace admin-flag endpoint discovery

Douglas Day (Archangel) methodology — Critical Thinking Podcast Ep 35.

## Pattern
Set Burp/Caido match-and-replace rules turning `"is_admin": false` →
`true` (and every boolean flag like `is_*: false→true`) in responses.
The UI loads admin-only modules from those flags, exposing endpoints
without ever reading minified JS.

Top hunter Douglas does NOT analyze JS — match-and-replace alone yields
top-of-board placements.

## Preconditions
- SPA-style app where front-end gates UI on response flags.
- Burp/Caido (or any intercepting proxy with response rewrite).

## Detection
N/A — this IS the detection technique.

## Triggering
Burp → Proxy → Match and Replace, add rules:
```
Match: "is_admin": false
Replace: "is_admin": true
Type: Body
```
Plus variants for `is_owner`, `is_staff`, `is_superuser`, `can_*`,
`feature_*`, `tier`, `role`. Optionally include capability arrays.

Now browse normally. Hidden / disabled UI controls become active. Each
new endpoint surfaced = potential IDOR / missing-server-side-check report.

## Related
- [[intercom-widget-bypass]]
- Bookmarklet to remove `disabled`/`hidden` attrs from every element
  (Ep 41).
- xnl-reveal Chrome extension (XNL Hacker).

## Seen in the wild
- Douglas Day's bread-and-butter for ~$60K over ~100 reports at $500
  mediums on one custom-roles SaaS.
- Critical Thinking Podcast Eps 35, 41.

## References
- Critical Thinking Podcast Eps 35, 41
- Douglas Day NahamCon 2023 talk — "nose in the application"
