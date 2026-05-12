---
title: Race Conditions — summary
slug: race-conditions-summary
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/race-conditions, summary, index]
inbound: []
---

# Race Conditions — summary

## What this class is

Race condition vulnerabilities arise when a sequence of operations that should be atomic (read-check-then-act) can be interleaved by concurrent requests from an attacker before the state is committed. The classic impact is "limit overuse" — spending a gift card twice, redeeming a coupon multiple times, bypassing a one-time check — but races also enable TOCTOU file system bugs, duplicate account creation, and bypassing rate limits. Modern exploitation favors HTTP/2 single-packet attacks (all requests arrive within one TCP segment) to reduce timing jitter.

## When to suspect

- Endpoints that enforce per-user limits: `check balance → deduct → confirm` patterns
- "One-time use" flows: password reset tokens, email verification links, invite codes, promo codes
- File operations: upload + process + rename in sequence (TOCTOU)
- Wallet / credit / points balances that are read then updated in separate DB calls (no `SELECT FOR UPDATE`)
- Two-step flows: `POST /reserve` then `POST /confirm` — race the confirm against a second reserve
- Low-latency API endpoints with idempotency keys — test without the key
- Response time anomalies: same endpoint returns different status codes on simultaneous requests
- `js_analyzer` relevance: minimal (server-side logic) but JS-initiated concurrent fetch() calls may be the exploit vehicle

## External references

| Topic | PayloadsAllTheThings path | HackTricks path | PortSwigger |
|---|---|---|---|
| Race condition techniques | `../../_external/payloads-all-the-things/Race Condition/` | `../../_external/hacktricks/src/pentesting-web/race-condition.md` | [portswigger-race-conditions](../../sources/portswigger-race-conditions.md) |
| Business logic errors (race targets) | `../../_external/payloads-all-the-things/Business Logic Errors/` | — | — |
| Insecure randomness (token predictability) | `../../_external/payloads-all-the-things/Insecure Randomness/` | — | — |

## Related local pages

- [IDOR SUMMARY](../idor/SUMMARY.md) — race + IDOR chains: race to grab another user's object before ownership check
- (none yet)

## Sub-patterns to expand

- [x] `single-packet-attack.md` — HTTP/2 single-packet race (Burp Turbo Intruder / Caido)
- [x] `limit-overuse.md` — coupon/gift card/credit double-spend
- [ ] `toctou-upload.md` — file upload TOCTOU (check then process race)
- [ ] `one-time-token-race.md` — password reset or invite token used twice
- [ ] `db-no-lock-race.md` — missing SELECT FOR UPDATE allows balance manipulation
- [ ] `rate-limit-bypass-race.md` — racing past per-IP/per-user rate limit counters
