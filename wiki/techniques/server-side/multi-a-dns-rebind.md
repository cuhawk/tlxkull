---
title: Multi-A DNS rebinding (Rhynorater)
slug: multi-a-dns-rebind
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/ssrf, technique/dns-rebinding]
inbound: []
---

# Multi-A DNS rebinding

Justin Gardner (Rhynorater) — `rebindmultia.com`.

## Pattern
Two A records per hostname. First IP = attacker server (kills connection
on second hit). Second IP = `127.0.0.1`. Browser failover triggers
rebind without TTL games. Works on Chrome/Firefox/Edge on Windows.
`0.0.0.0` fallback works on Linux/Mac (covers loopback in many stacks).

## Preconditions
- SSRF-able client (headless browser, server-side fetch with default DNS
  resolver, IoT device).
- Reachable attacker DNS server able to answer with two A records.

## Detection
- Use `rebindmultia.com` / github.com/Rhynorater/rebindmultia.
- Pattern: `127.0.0.1.target.<vps-ip>.ns.rebindmultia.com`.

## Triggering
```
GET / HTTP/1.1
Host: 127.0.0.1.target.<vps-ip>.ns.rebindmultia.com
```

## Related
- Chrome multi-A instant rebind to `0.0.0.0` (Ep 21 — Corben Leo).
- NCC Singularity (still effective for `0.0.0.0` post-Chrome restrictions).
- WebSocket-timing port scanner against local services still works
  post-mitigation.

## Seen in the wild
- Multiple in-the-wild SSRF chains against headless-browser, IoT.

## References
- github.com/Rhynorater/rebindmultia
- NCC Group — "State of DNS Rebinding in 2023"
- Critical Thinking Podcast Eps 9, 21
