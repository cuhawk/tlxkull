---
title: SaaS pre-auth tenant config enumeration
slug: saas-preauth-config-enum
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/recon, technique/saas, technique/info-disclosure]
inbound: []
---

# SaaS pre-auth tenant config enumeration

## Pattern
Multi-tenant SaaS apps frequently expose a **pre-auth config endpoint**
keyed by tenant name / org ID / org key. Its job is usually legitimate
(SSO redirect URL, branding logo, OAuth client ID) but in practice it
leaks far more — internal hostnames, route lists, PAC URLs, sometimes
keys.

DEFCON-33 example (David Cash, Rich Warren): zScaler and Netskope both
expose org-key-keyed config endpoints (e.g.
`/mobile/user/pac?org_key=<key>`) that, given a guessable org-key,
return internal/external proxy hosts, PAC routes, in some cases
sensitive material. Older finding pattern: Workday and AppOmni-targeted
SaaS used the same architecture.

## Preconditions
- Target is a multi-tenant SaaS.
- An identifier (org key, tenant ID, customer slug) is guessable, leak­
  able from public marketing material, or enumerable via a separate
  endpoint.

## Detection
1. Inventory all unauth endpoints (`/api/config`, `/v1/tenant/...`,
   `/setup`, `/mobile/user/pac`, `/.well-known/...`).
2. Try with no auth + a probable tenant identifier (their own marketing
   org name, their stock ticker, common customer slugs).
3. Diff response between tenants — keep the diffs that reveal internal
   data.

## Why it pays
- Even when the bug isn't a CVE-grade vuln, the leaked data feeds every
  downstream attack — internal hostnames → SSRF candidates, routes →
  ATO chain entrypoints, sometimes keys → direct RCE/data access.

## Bypasses / hardening
- Require auth (or signed session) before tenant-keyed config.
- Strict allowlist of fields returned pre-auth; treat anything else as
  internal.

## Seen in the wild
- {date: 2025-08, source: CT Ep 149} — David Cash & Rich Warren DEFCON 33
  talk on zScaler/Netskope.
- Joseph notes the same pattern on Workday during AppOmni days.

## References
- DEFCON 33 — "Breaking into thousands of cloud-based VPNs with one bug"
- Critical Thinking Podcast Ep 149
- Related: [[blind-ssrf-redirect-count-status-leak]]
