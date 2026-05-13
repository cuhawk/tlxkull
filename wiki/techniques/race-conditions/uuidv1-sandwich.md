---
title: UUIDv1 sandwich attack — predict victim token
slug: uuidv1-sandwich
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/race-condition, technique/predictable-token]
inbound: []
---

# UUIDv1 sandwich attack

Lupin (0xLupin) + Holmes — recap Ep 32 + 37.

## Pattern
UUIDv1 = nanosecond timestamp + clock_id + MAC of generating host.
Detect: third octet's first char == `1`. Reconstruct timestamp from
`time_low/mid/hi` concatenated → Julian-calendar nano-timestamp → epoch.

To predict a victim's password-reset token:
1. Reset YOUR password → token A (bookend).
2. Wait for victim to reset → token V (filling).
3. Reset YOUR password again → token C (bookend).

Tokens A and C bound the millisecond range; brute-force the V value
within range. Tighten window with single-packet/race tricks.

## Preconditions
- Target generates password-reset tokens (or other secrets) as UUIDv1.
- Attacker can trigger token generation on own account (most reset flows).
- Attacker can race-trigger near victim's reset.

## Detection
- Reset own password 2x; decode UUIDs:
  - Bytes 0-3 = time_low, bytes 4-5 = time_mid, bytes 6-7 = time_hi.
  - Concatenate (skipping version nibble), interpret as 100ns intervals
    since 1582-10-15 UTC.
- If consecutive tokens differ by predictable nanosecond steps → UUIDv1.

## Triggering
1. `POST /reset-password` for own account → capture UUIDv1 A.
2. Trigger victim reset (often via account-enumeration flow).
3. Immediately `POST /reset-password` for own account → capture UUIDv1 C.
4. Bruteforce values of `time_low/mid/hi` between A and C; reconstruct
   clock_id and MAC from A (these don't change per token); verify candidate
   matches by submitting reset confirmation URL.

## Bypasses
- Tighten window: combine with H2 single-packet attack to compress
  bookend-to-victim-token interval.

## Related
- [[substate-races]] — INSERT-default + UPDATE-correct admin window.
- [[single-packet-attack]] (existing) — Kettle H2 race.

## Seen in the wild
- Lupin/Holmes — public PoC video.
- Critical Thinking Podcast Eps 32, 37.

## References
- VerSprite blog post on UUIDv1 timestamps
- youtube — Lupin "sandwich attack" video
- Critical Thinking Podcast Eps 32, 37
