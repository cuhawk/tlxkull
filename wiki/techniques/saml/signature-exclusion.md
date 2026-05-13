---
title: SAML signature exclusion
slug: saml-signature-exclusion
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/saml, technique/auth-bypass]
inbound: []
---

# SAML signature exclusion

## Pattern
Strip the `<Signature>` element from `SAMLResponse` and submit. Many SPs
accept it; oracle the missing attributes the SP complains about and fill
them in. Jolko Uber/OneLogin WP plugin H1 #136169.

## Preconditions
- Target SP processes SAML response.
- Signature handling library accepts missing signature OR conditionally
  validates.

## Detection
- Submit assertion sans `<Signature>` and check response.
- Use SAMLRaider Burp extension.

## Triggering
Base64-decode SAMLResponse, remove `<ds:Signature>` block, re-encode,
submit.

## Related (full SAML attack family)
- [[saml-xsw]] — XML signature wrapping (8 variants).
- Certificate faking — inject attacker X.509 in `<KeyInfo>`.
- X.509 AIA URL → SSRF via cert chain validation. Michael Stepankin
  (GitHub blog 2023).
- XSLT pre-signature execution via `<Transform>` — XSLT Turing-complete.
  Project Zero 2022.
- Recipient confusion — SP doesn't validate
  `<SubjectConfirmationData Recipient="...">`.
- XSS in attributes: `Destination="x&lt;script&gt;..."` reflected decoded
  in HTML error.
- XXE via SAMLResponse: base64-decode + inflate, inject DOCTYPE+ENTITY,
  re-encode.

## Seen in the wild
- Uber OneLogin WordPress plugin SAML auth bypass — Jolko, 2016, H1 #136169.
- Critical Thinking Podcast Ep 46.

## References
- epi052 — "How to hunt bugs in SAML — a methodology" (3-part, 2019)
- "How to break SAML if I have a paws" — GreenDog
- Michael Stepankin (GitHub) 2023 — X.509-extension SSRF
- Project Zero 2022 — XSLT-transform XXE bypass
- HackerOne report 136169
- SAMLRaider Burp extension
- Critical Thinking Podcast Ep 46
