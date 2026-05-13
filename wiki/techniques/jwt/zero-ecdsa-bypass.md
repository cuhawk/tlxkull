---
title: ECDSA all-zero signature bypass (CVE-2022-21449)
slug: jwt-zero-ecdsa-bypass
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/jwt, technique/crypto]
inbound: []
---

# ECDSA all-zero signature bypass

## Pattern
Java 15–18 ECDSA verifier accepts a signature with R=S=0 due to math-side
oversight in the Java rewrite. Any JWT/JOSE/SAML signature target running
on vulnerable JDK accepts an all-zero R/S signature.

## Preconditions
- Verifier runs on Java 15–18 (pre-patch).
- Signature algorithm is ECDSA (ES256/ES384/ES512).

## Detection
- Probe target JDK version via banner / error / behavioural fingerprint.
- Submit JWT with all-zero R/S; check accepted.

## Triggering
Forge JWT with header `{"alg":"ES256"}` and signature segment = base64url
of zero bytes:
```
eyJhbGciOiJFUzI1NiJ9.<claims>.AAAAAAAA...AAAA
```
(64 zero bytes for ES256 = `AAAA...` base64.)

Tool: jwt.io with same public key → "zero R/S accepted".

## Bypasses
- Patched JDK rejects. Use other algs (`none`, alg confusion, weak keys).

## Related
- [[jwt-none-algorithm]] — recap.
- [[jwt-unknown-alg-fail-open]] (CVE-2026-23993) — any unknown alg
  fail-open.
- [[jwt-cross-env-secret-reuse]] — shared secret stage/prod.

## Seen in the wild
- {date: 2022, CVE: CVE-2022-21449}.
- Recapped Critical Thinking Podcast Ep 7.

## References
- CVE-2022-21449
- Wycheproof (Google) crypto test suite
- Critical Thinking Podcast Ep 7
