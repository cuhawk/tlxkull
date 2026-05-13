---
title: JWT unknown-algorithm fail-open
slug: jwt-unknown-alg-fail-open
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/jwt]
inbound: []
---

# JWT unknown-algorithm fail-open

## Pattern
JWT library accepts not just `none` but ANY unknown alg string (`bandana`,
`ZZZ`, `XYZ`) and bypasses signature verification. Test with non-standard
alg values, not just `none`.

CVE-2026-23993 (Pentester Labs / Harbor lang).

## Preconditions
- Target uses a JWT lib with unknown-alg fail-open.
- Token-validation code path doesn't enforce alg-allowlist before
  signature verification.

## Detection
- Send tokens with `{"alg":"BANDANA"}`, `{"alg":"XYZ"}`, `{"alg":"hs256"}`
  (lowercase variant) — check whether server still trusts unsigned claims.

## Triggering
```
header:  {"alg":"BANDANA","typ":"JWT"}
payload: {"sub":"victim", ...}
sig:     <empty | random>
```

## Bypasses
- Alg-allowlist `if alg not in {RS256,...}: reject` defeats.

## Related
- [[jwt-zero-ecdsa-bypass]]
- [[jwt-none-algorithm]]
- [[jwt-cross-env-secret-reuse]]

## Seen in the wild
- {date: 2026, CVE: CVE-2026-23993} — Harbor/Pentester Labs.
- Discussed Critical Thinking Podcast Ep 169.

## References
- CVE-2026-23993
- Critical Thinking Podcast Ep 169
- Zeropath — Django-Allauth 7-vuln writeup (related class)
