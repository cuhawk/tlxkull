---
title: TURN Server SSRF via WebRTC Credential Leak
slug: turn-server-ssrf
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/ssrf, technique/webrtc, technique/turn]
inbound: []
---

# TURN Server SSRF via WebRTC Credential Leak

## Pattern

Applications that offer voice/video calling via WebRTC must provision
TURN relay servers for clients behind symmetric NAT. The server-side
call-setup API often returns TURN credentials (username, password, host)
in plaintext JSON so the browser can connect. Because TURN servers proxy
arbitrary UDP/TCP traffic to any address the client requests, a client
that knows the TURN credentials can direct the server to relay traffic
into the application's internal network — effectively an SSRF via a
legitimate but unprotected proxy.

## Preconditions

- Application exposes a voice/video calling feature backed by a TURN server.
- TURN server has no IP allowlist; RFC 5766 Section 8 blacklist of private
  ranges is absent or incomplete.
- TCP channel support is enabled (greatly increases exploitability beyond UDP-only audio).

## Detection

- Look for API responses containing fields like `turnauth`, `turn_server`,
  `iceServers`, `credentials`, or `username`+`password`+`hostname` tuples.
- Check whether the TURN hostname resolves to an IP in the same network
  segment as other internal services.
- Send an ALLOCATE + CHANNEL-BIND request pointing to 169.254.169.254 or
  10.0.0.0/8; a successful bind confirms exploitability.

## Triggering

1. Call the voice-setup API to obtain TURN credentials.
2. Open a raw TCP channel via `CHANNEL-BIND` request, setting the
   `XOR-PEER-ADDRESS` to the target internal IP + port.
3. Send `SEND` indications to proxy HTTP traffic to internal services
   (e.g., cloud metadata endpoints).

## Bypasses

- If UDP-only is allowed, DNS-based protocols (e.g., JNDI, DNS rebinding)
  may still be reachable.
- Even without credential recovery, a timing side-channel on ALLOCATE
  responses can confirm reachable vs. unreachable internal hosts.

## Seen in the wild

- 2020-04-14 — Slack, $3,500. TURN server on `slack-core` subdomain exposed
  without allowlist; TCP allowed. Reported by Sandro Gauci (Enable Security).
  [BBRE](https://www.youtube.com/watch?v=iBOhI-X6lCI)

## References

- RFC 5766 — TURN Protocol
- Enable Security blog: "Real-World TURN Server Exploitation"
- See also: [headless-browser-html-ssrf](headless-browser-html-ssrf.md),
  [blind-ssrf-redirect-count-status-leak](blind-ssrf-redirect-count-status-leak.md)
