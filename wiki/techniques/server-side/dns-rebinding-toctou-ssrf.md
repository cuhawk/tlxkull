---
title: DNS Rebinding TOCTOU SSRF (Time-of-Check / Time-of-Use)
slug: dns-rebinding-toctou-ssrf
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/ssrf, technique/dns-rebinding, technique/toctou]
inbound: []
---

# DNS Rebinding TOCTOU SSRF

## Pattern

When a server makes two separate DNS resolutions for the same hostname
(one during URL validation, one during the actual HTTP request), an attacker
can make the DNS server return a safe public IP for the first query and a
private/localhost IP for the second. This is a Time-of-Check / Time-of-Use
(TOCTOU) race condition: validation passes on the first resolution, but
exploitation succeeds on the second.

## Preconditions

- Server performs DNS resolution during input validation, then a *second*
  DNS resolution during the actual fetch (or uses the validated hostname,
  not the resolved IP, for the final connection).
- Attacker controls a DNS server that can serve different responses per query.

## Detection

- Look for SSRF-protected functionality that validates URLs server-side.
- Check whether the fix resolves the hostname once and reuses the IP
  (`getaddrinfo` result cached → immune) vs. resolving again at request time.
- Bypass signal: `getaddrinfo` throwing a socket error causes the validator
  to return "safe" rather than "unsafe" (see bypass variant below).

## Triggering

Classic setup:
1. Register `evil.attacker.com` with a short TTL (0 or 1 second).
2. First query returns a public IP (passes validation).
3. Immediately update DNS to return `127.0.0.1` (or target internal IP).
4. Second query (at request time) resolves to the internal IP.

Variant — resolver-error bypass (GitLab 2020 bypass):
1. DNS server returns NXDOMAIN for the first query.
2. Validator catches the socket error and returns "valid" instead of "blocked".
3. Second DNS query (at request time) returns `127.0.0.1`.

## Bypasses

- If server pins the resolved IP after first query: use multi-A rebind
  (see [multi-a-dns-rebind](multi-a-dns-rebind.md)).
- If socket errors are correctly handled: pair error-handling bypass with
  zero-TTL DNS setup.

## Seen in the wild

- 2020-04-14 — GitLab, $5,000. Classic TOCTOU: `URLBlocker.validate` resolved
  hostname, checked IP, returned URI. HTTP client then resolved again, got
  internal IP. [BBRE](https://www.youtube.com/watch?v=R5WB8h7hkrU)
- 2020-05-01 — GitLab, $3,500. Bypass of 2020-04-14 fix: `getaddrinfo`
  socket error during validation returned "valid" instead of "blocked", so
  second query at request time hit internal IP.
  [BBRE](https://www.youtube.com/watch?v=hozjuAej1mo)

## References

- See also: [multi-a-dns-rebind](multi-a-dns-rebind.md)
- GitLab `URLBlocker` class
