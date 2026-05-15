---
title: Padre — Padding Oracle / CBC Attack Framework
slug: tools-padre-notes
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [tool/crypto, tool/padre]
inbound: []
---

# Padre

## What

`padre` is a CLI framework for **padding-oracle** and other
**CBC-mode** attacks. Originally Go-based. Handles the bookkeeping for
byte-by-byte ciphertext recovery against a target that leaks plaintext
validity (padding errors, response-shape differences, status-code
differences, decryption-error pages, response-time deltas).

## Strengths

- **Extensible.** Custom HTTP oracle definitions: define what counts
  as a "padding valid" vs "padding invalid" response (regex on body,
  status code, response length, response time).
- **Concurrent.** Decrypts blocks in parallel; useful for slow targets.
- **Side primitives.** Useful for IV-recovery (see
  [[../../techniques/server-side/cbc-iv-recovery-null-block]]) — the
  brute-force loop and ciphertext-bookkeeping is the same skeleton.

## When to reach for it

- App returns CBC ciphertext anywhere user-visible (cookie, URL
  parameter, token, viewstate-style blob).
- Bit-flipping any byte produces:
  - a different error page, **or**
  - a different status code, **or**
  - a "junk character" substitution at a predictable offset (= raw
    CBC, often unauthenticated).
- You have a partial known plaintext format (Stack Overflow / docs /
  another endpoint that returns the same shape unencrypted).

## Operational notes

- Get familiar with the oracle definition syntax once; subsequent
  targets become 15-minute tasks.
- Pair with a short Python harness when the oracle is more subtle
  than padre's built-in patterns can express — padre handles the
  bit-flipping, your harness handles the "did this look right?"
  judgement.

## Seen used

- **2026-05 — SFDC Marketing Cloud chain** (Searchlight Cyber). Used
  with the [[../../techniques/server-side/cbc-iv-recovery-null-block]]
  technique against an unauthenticated CBC QS parameter.
  Source: [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174).

## Related

- [[../../techniques/server-side/cbc-iv-recovery-null-block]]
- [[../../techniques/server-side/ampscript-template-injection]] (chained)
