---
title: PortSwigger — Race conditions
slug: portswigger-race-conditions
url: https://portswigger.net/web-security/race-conditions
fetched_utc: 2026-05-12T00:00:00Z
kind: article
extracted: true
extract_model: sonnet
tags: [source, technique/race-conditions, ref/portswigger]
inbound: []
---

# PortSwigger — Race conditions

## TL;DR

- Race conditions arise when websites process concurrent requests without adequate safeguards, allowing multiple threads to interact with the same data in the "race window."
- The single-packet attack (HTTP/2) delivers 20–30 requests in one TCP segment, eliminating network jitter for reliable exploitation.
- Limit overrun (TOCTOU) is the most common pattern: redeeming single-use coupons/tokens/credits multiple times within the race window.
- Hidden multi-step sequences create invisible sub-states (e.g., MFA temporarily not enforced) that can be hit with concurrent requests.
- Partial construction races exploit object creation windows where required fields are uninitialized, matchable with `param[]=` or null values.

## Sub-sections

- Limit overrun race conditions
  - Detecting and exploiting with Burp Repeater
  - Detecting and exploiting with Turbo Intruder
- Hidden multi-step sequences
- Methodology
  - 1 - Predict potential collisions
  - 2 - Probe for clues
  - 3 - Prove the concept
- Multi-endpoint race conditions
  - Aligning multi-endpoint race windows
  - Connection warming
  - Abusing rate or resource limits
- Single-endpoint race conditions
- Session-based locking mechanisms
- Partial construction race conditions
- Time-sensitive attacks
- How to prevent race condition vulnerabilities
