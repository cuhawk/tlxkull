---
title: Blind SSRF Oracle via Uptime-Check Response Validation
slug: uptime-check-blind-ssrf-oracle
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/ssrf, technique/blind-ssrf, technique/data-exfiltration]
inbound: []
---

# Blind SSRF Oracle via Uptime-Check Response Validation

## Pattern

When an application's SSRF-capable functionality also offers a
"response validation" feature (e.g., assert that the response contains
a given string or matches a regex), a blind SSRF becomes an oracle for
data exfiltration. The attacker configures the validator to match
successive prefixes of the secret, inferring one character at a time
analogously to Blind SQL Injection.

Using binary search with regex character-class ranges reduces the
requests needed from O(|alphabet| × |secret|) to O(log₂(|alphabet|) × |secret|).
Sending paired positive/negative regexes disambiguates instance misses on
load-balanced endpoints.

## Preconditions

- Server has a blind SSRF to an internal metadata endpoint.
- Functionality exposes a "response assertion" or "health-check string"
  input that the server evaluates against the fetched body.
- The boolean pass/fail result is observable by the attacker (different
  HTTP status, timing difference, alert email).

## Detection

- Look for "Uptime Checks", webhook verifiers, canary-token services, or
  health monitors that let you specify expected response strings.
- Confirm SSRF: set hostname to 169.254.169.254 and observe the 2 ms
  response vs. external timing.
- Confirm oracle: set expected string to a known prefix of the response.

## Triggering

```
# Positive filter — matches if token starts with "ya29.A"
expected_string: ya29.A[a-z]

# Negative filter — matches if token does NOT start with a lowercase letter
expected_string: [^a-z]
```

Repeat, narrowing the character class until each byte is identified.

## Bypasses

- Load-balanced backends: use paired positive+negative filters; discard
  rounds where neither matches (indicates wrong instance hit).
- Rate limits: space requests or use async check scheduling.

## Seen in the wild

- 2021-04-06 — Google Cloud Monitoring (Uptime Checks), $31,337.
  Attacker set custom headers to bypass GCP metadata protection header
  requirement. Response validation used as exfiltration oracle. Google
  PoC showed binary-search regex extraction of unique access tokens.
  [BBRE](https://www.youtube.com/watch?v=ashSoc59z1Y)

## References

- See also: [blind-ssrf-redirect-count-status-leak](blind-ssrf-redirect-count-status-leak.md)
- Blind SQLi analogy: successive prefix matching
