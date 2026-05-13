---
title: JWT cross-environment signing-secret reuse
slug: jwt-cross-env-secret-reuse
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/jwt, technique/auth-bypass]
inbound: []
---

# JWT cross-environment signing-secret reuse

## Pattern
Same JWT signing secret used across staging/prod, or across multiple apps
that share a central auth middleware. Sign up on the easier env (no MFA,
weaker validation), mint JWT, replay against the harder env. Watch
Facebook/Meta-style centralised auth where the verifier checks signature
only, not `aud`/app-id.

## Preconditions
- Two environments / apps trust JWTs signed by the same key.
- No `aud` enforcement.

## Detection
- Mint JWT on staging, replay against prod with same claim structure.
- Decode JWTs from each env and look for identical `iss`/`kid` headers.
- Probe for `aud` validation by tampering value.

## Triggering
1. Sign up on staging / a low-trust env.
2. Capture JWT.
3. Replay against prod endpoint with same path/host.

## Related
- [[jwt-none-algorithm]]
- [[jwt-zero-ecdsa-bypass]]
- [[jwt-unknown-alg-fail-open]]

## Seen in the wild
- LHE-class wins, multiple targets.
- Critical Thinking Podcast Eps 44, 52.

## References
- Critical Thinking Podcast Eps 44, 52
- Sam Curry — points.com $secret$ literal secret writeup
- iangcarroll/cookiemonster
