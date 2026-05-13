---
title: JWT alg none — still landing in 2023+
slug: jwt-none-algorithm
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/jwt]
inbound: []
---

# JWT alg=none

## Pattern
Strip signature, set header `alg: none` (case variants `None`, `NONE`,
`nOnE`). Verifier returns true without checking signature.

## Preconditions
- JWT library with unpatched none-alg handling, or alg-allowlist missing.

## Detection
- Tools: Joseph (Burp), JWT-Editor.
- Auto-generate variants with cookie-monster.

## Triggering
```
{"alg":"none","typ":"JWT"}.<claims>.
```
(empty signature segment; case variants for filter bypass.)

## Related
- [[jwt-zero-ecdsa-bypass]]
- [[jwt-unknown-alg-fail-open]]
- [[jwt-cross-env-secret-reuse]]

## Seen in the wild
- Recurring through 2023 per Critical Thinking Podcast Ep 39.

## References
- Critical Thinking Podcast Ep 39
- jwt.io
- portswigger/burp-extension-jwt-editor
