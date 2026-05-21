---
title: Facebook / Meta
slug: facebook-meta
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [target/facebook, target/meta, platform/meta-bugbounty]
inbound: []
---

# Facebook / Meta

## Snapshot

Meta operates the Facebook, Instagram, WhatsApp, and Oculus bug bounty programs
at https://www.facebook.com/whitehat. Separate from HackerOne. Consistently
one of the highest-paying programs (no cap on critical severity payouts).

## Scope quirks

- Entire `*.facebook.com` ecosystem including Canvas Apps, third-party JS SDK
  integrations, Oversight Board, Workplace.
- Facebook JS SDK (`connect.facebook.net/en_US/sdk.js`) included by many
  third-party websites — bugs in the SDK can affect thousands of external sites.
- FXAuth (unified Meta auth token) is a high-value target.
- Sandbox domains (e.g., `*.fbsbx.com`) are in scope; often have looser security.
- `*.fbcdn.net` CDN edge — cache poisoning surface.

## Auth quirks

- Create test Facebook accounts; Meta is lenient about researcher accounts.
- OAuth token flows: need two accounts (attacker + victim) to test OAuth chains.
- Canvas Apps: requires registering a Facebook App (free developer account).

## Prior findings (from BBRE)

- postMessage ATO via Canvas App `page_proxy` missing origin check — $25,000.
  [BBRE](https://www.youtube.com/watch?v=jPMaZt9ZJes)
- OAuth + CSRF chain: captcha lockout + sandbox iframe code leak → ATO — $44,625.
  [BBRE](https://www.youtube.com/watch?v=pk7oYuz4x0Q)
- Three-bug chain: endpoint ATO + ASPX shared machineKey + path bypass — $54,800.
  [BBRE](https://www.youtube.com/watch?v=JiMzpjgAXv8)
- Video upload IDOR via two-step exchange (video ID → internal ID) — Youssef Sammouda.
  [BBRE](https://www.youtube.com/watch?v=fpW-h9uT6Uo)
- CSRF via GET method triggering JS state change — various.
  [BBRE](https://www.youtube.com/watch?v=o2rj0utFZvg)

## Sub-targets

- facebook.com — main web application
- Instagram (separate auth surface)
- Facebook Canvas Apps / `page_proxy`
- Facebook JavaScript SDK (third-party inclusion)
- FXAuth token endpoints
- fbsbx.com sandbox domain
- Oversight Board (oversightboard.com)

## Top hunters

- Youssef Sammouda — top-ranked for 3 consecutive years; multiple ATO chains.
  [See people/youssef-sammouda.md](../people/youssef-sammouda.md)

## Notes

- Facebook's sandbox domains (`fbsbx.com`) are frequently used as CSRF bypass
  helpers: they are same-origin with each other but cross-origin with
  facebook.com, yet sometimes trust postMessages from facebook.com.
- The `page_proxy` architecture (Canvas App message relay) is historically vulnerable;
  verify if any such proxy endpoints still exist.
- ASP.NET-based third-party services hosted under `*.facebook.com` subdomains
  may share machineKey with other services — check for `.ASPXAUTH` cookies.
