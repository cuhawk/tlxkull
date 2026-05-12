---
title: HTTP/2 single-packet attack for race conditions
slug: single-packet-attack
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/race-conditions, technique/http2, sink/limit-overuse]
inbound: []
---

# HTTP/2 single-packet attack for race conditions

## Pattern

HTTP/2 multiplexes multiple requests over a single TCP connection. By buffering 20–30 complete requests and sending them in a single TCP segment (zero timing delta at the network level), an attacker eliminates network jitter and delivers all requests to the server within a single scheduling slice. This dramatically shrinks the race window needed for exploitation and makes previously "too narrow to hit" races reliable.

## Preconditions

- The target endpoint is reachable over HTTP/2 (check `Alt-Svc`, `Upgrade` headers, or ALPN in TLS handshake).
- The vulnerable operation has a check-then-act window (TOCTOU): e.g. read balance → check limit → deduct.
- The attacker can issue concurrent requests (no per-session serialization / mutex enforced server-side).

## Detection

- Confirm HTTP/2 support: `curl -I --http2 https://target.com/endpoint` — response shows `HTTP/2`
- Identify TOCTOU endpoints: endpoints that enforce per-user limits, one-time use tokens, or balance checks
- Burp Suite: send request to Repeater, switch to HTTP/2, use "Send group in parallel (single-packet attack)" option
- Timing probe: send 2 simultaneous requests and compare responses — different outcomes (200+200 vs 200+409) indicate a race window

## Triggering

Turbo Intruder (Burp extension) single-packet template:
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                          concurrentConnections=1,
                          engine=Engine.BURP2)
    for i in range(20):
        engine.queue(target.req, gate='1')
    engine.openGate('1')
```

Caido equivalent: group the requests, set parallel send mode with gate synchronization before firing.

HTTP/1.1 fallback (last-byte sync technique):
- Send all requests with `Content-Length` set but hold back the final byte of each request body.
- Release all final bytes simultaneously — achieves approximate synchronization without HTTP/2.

## Bypasses

- Session-based locking: some frameworks lock at the session level — use separate session tokens per concurrent request.
- Rate limiting: if rate limiter fires before the race window, use "connection warming" (pre-warm the connection with a dummy request) to reduce setup latency.
- CDN/load balancer jitter: single-packet attack may not work if requests land on different backend instances — test against a specific backend instance if possible, or use sticky session cookies.
- Server queues requests: if the server processes serially within a thread pool, HTTP/2 parallelism may still serialize at the app layer — confirm by observing response timing spread.

## Seen-in-the-wild

(none yet)

## References

- [PortSwigger Race conditions](../../sources/portswigger-race-conditions.md) — single-packet attack, Turbo Intruder template
- [Race Conditions SUMMARY](SUMMARY.md)
