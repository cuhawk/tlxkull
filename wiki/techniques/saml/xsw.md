---
title: SAML XML signature wrapping (XSW)
slug: saml-xsw
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/saml, technique/auth-bypass]
inbound: []
---

# SAML XML signature wrapping (XSW)

## Pattern
8 variants placing signature in enveloped / enveloping / detached
positions vs the assertion/response. Exploits the disconnect between
which element the SP validates vs which it consumes.

SAMLRaider Burp extension automates all 8 variants.

## Variants (high-level)
1. Sign envelope, but consumer reads child assertion.
2. Sign decoy assertion, embed real attacker assertion.
3. Detached signature placement in `<Object>`.
4. Wrap assertion in extension element.
5. ... (see SAMLRaider docs for full taxonomy)

## Preconditions
- Target SP validates signature on one element but reads claims from
  another.
- Common with libraries that get-by-ID on `Assertion` IDs without scoping.

## Detection
- Run all 8 SAMLRaider variants.

## Related
- [[saml-signature-exclusion]]
- XSLT pre-signature execution (Transform-based, Turing-complete).

## Seen in the wild
- Recurring across SaaS SAML implementations.
- Critical Thinking Podcast Ep 46.

## References
- SAMLRaider Burp extension
- epi052 — SAML methodology
- GreenDog `weird_proxies` GitHub
- Critical Thinking Podcast Ep 46
