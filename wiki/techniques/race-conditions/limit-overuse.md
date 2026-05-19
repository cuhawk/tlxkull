---
title: Limit overrun — coupon / credit / token double-spend
slug: limit-overuse
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/race-conditions, sink/business-logic]
inbound: []
---

# Limit overrun — coupon / credit / token double-spend

## Pattern

An endpoint enforces a per-user limit (one promo redemption, non-negative balance, single-use token) via a read-check-then-update sequence without an atomic lock. Sending multiple concurrent requests within the race window causes the check to pass multiple times before any update commits, allowing the limit to be exceeded — effectively spending the resource N times.

## Preconditions

- An endpoint performs a read-check-act sequence: `SELECT balance WHERE user=X` → check ≥ deduction → `UPDATE balance -= deduction`.
- No `SELECT FOR UPDATE`, database transaction, or application-level mutex surrounds the sequence.
- The attacker can issue concurrent HTTP requests (single-packet or last-byte sync).

## Detection

- Endpoints with "one-time" semantics: promo codes, gift cards, invite links, email verification tokens, password reset tokens.
- Wallet / credits / points: any endpoint that reads then debits a balance.
- Response anomaly: send 2 simultaneous requests — if both return `200 OK` (vs expected `200` + `409/400`), the race window is exploitable.
- Check DB query structure via error messages or timing: slow `SELECT` before fast `UPDATE` suggests no atomic locking.

## Triggering

Burp Suite — parallel group send (single-packet, HTTP/2):
1. Send the promo redemption request to Repeater.
2. Duplicate it 10–20 times into a group.
3. "Send group in parallel (single-packet attack)".
4. Observe: N × `200 OK` responses instead of 1 × `200 OK` + N-1 × `400 Already used`.

Last-byte synchronization (HTTP/1.1):
- Prepare 20 requests, send all headers + all but last byte of body.
- Release last bytes simultaneously.

Partial construction race (uninitialized field):
```
GET /api/user/info?user=victim&api-key[]=
```
(Injecting `api-key[]=` null/empty array matches an uninitialized `api_key` field during object creation window.)

## Bypasses

- Idempotency keys: if the API supports `Idempotency-Key` header, omit it — some apps only enforce limits when the key is present.
- Per-session locking: use a fresh session token for each concurrent request to circumvent session-scoped locks.
- Retry on `429`: some rate limiters allow bursts; probe with exponential backoff to find the window.

## Seen-in-the-wild

- **2024-10-18 — Mozilla Monitor email limit bypass** (Mozilla / sushantd19, H1 #1913309, Low): Concurrent POSTs to the "add monitored email" endpoint allowed users to exceed the 5-address limit. Classic read-check-then-insert without transaction. See [H1 #1913309](../../sources/hacktivity/1913309.md).
- **2024-04-04 — WorldID max verifications bypass** (Tools for Humanity / toormund, H1 #2110030, High, $3 000): Parallel requests to the cloud backend verification endpoint bypassed the per-user verification count limit. Fix: enforce the cap atomically in the database. See [H1 #2110030](../../sources/hacktivity/2110030.md).
- **2025-07-03 — MozillaVPN local privilege escalation via install race** (Mozilla / northsea, H1 #2261577, Medium): TOCTOU during VPN installer: attacker replaces the binary between the signature check and execution, resulting in root execution on macOS. See [H1 #2261577](../../sources/hacktivity/2261577.md).

## References

- [PortSwigger Race conditions](../../sources/portswigger-race-conditions.md) — limit overrun, methodology sections
- [Race Conditions SUMMARY](SUMMARY.md)
