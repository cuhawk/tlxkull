---
title: SAML cross-tenant signature reuse
slug: cross-tenant-signature-reuse
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/saml, technique/auth-bypass, technique/multi-tenant]
inbound: []
---

# SAML cross-tenant signature reuse

## Pattern
A SaaS SP that supports SAML SSO across many tenants validates the
**signature is from a recognized IdP** but fails to bind the signed
assertion to the **specific consumer tenant**. The attacker creates
their own tenant on the same SaaS, gets the IdP to sign an assertion
for their tenant, then replays the same signed assertion against a
*victim* tenant's SAML endpoint — fields inside the assertion
(`NameID`, `Recipient`, `AudienceRestriction`) are not checked.

Joseph and Monkey-Kiron (AppOmni) found this recurring across SaaS
products. David Cash & Rich Warren's DEFCON 33 talk hit it on both
zScaler and Netskope.

## Preconditions
- Target SP supports multi-tenant SAML and you can sign up as a tenant
  yourself.
- SP's signature check trusts a global IdP cert (or shared IdP) rather
  than per-tenant IdP-cert binding.
- SP doesn't strictly validate `Recipient` / `AudienceRestriction` /
  `Destination` per consumer tenant.

## Detection
- Sign up two tenants (yours-A, yours-B). Sign an assertion for A,
  POST to B's ACS URL. Did B accept it as a user in A?
- Inspect each claim — modify Subject email to a victim user;
  replay.
- Modify `AudienceRestriction` to mismatch the SP — does it still
  accept?

## Triggering
Standard SAMLRaider / `python3 -c "..."` script-signing flow. The IdP
itself does nothing wrong; the SP is the vulnerable party.

## Bypasses / hardening
- Bind signature validation to a *per-tenant* IdP cert.
- Strict equality on Destination, AudienceRestriction, Recipient,
  and InResponseTo per consumer.

## Related primitives
- [[xsw]] — signature-wrapping variants.
- [[signature-exclusion]] — drop signature entirely.
- [[saml-roundtrip-attribute-mutation]] — REXML / Nokogiri double-parse.

## Seen in the wild
- {date: 2025-08, source: CT Ep 149} — DEFCON 33 zScaler & Netskope.
- Joseph: pattern recurring across SaaS during AppOmni research.

## References
- DEFCON 33 — "Breaking into thousands of cloud-based VPNs with one bug"
- Critical Thinking Podcast Ep 149
- Related: [[saml-roundtrip-attribute-mutation]], [[xsw]], [[signature-exclusion]]
