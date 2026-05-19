---
title: Connection-state request smuggling
slug: connection-state-smuggling
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/server-side, technique/request-smuggling, technique/ssrf]
inbound: []
---

# Connection-state request smuggling

## Pattern
Some servers perform security checks (host header validation, auth checks,
rate-limit gates) only on the **first request** received over a given TCP
connection, not on subsequent requests on the same keep-alive connection.
An attacker sends a legitimate "precursor" request that passes validation,
then immediately sends a malformed request on the same connection before
the server closes it. The malformed request skips the per-first-request
check.

Demonstrated by James Kettle in a Burp Suite short: an SSRF vulnerability
on a target was blocked by host header validation on every direct attempt.
But by sending a valid request first (using the same connection), the
smuggled second request with an internal `Host` bypassed the check and
reached the admin panel.

The technique is general: any server-side check applied only to the first
request per connection can be bypassed — not just host header validation.

Burp Suite "Custom Actions" feature implements this as a one-click button:
it takes the current Repeater request, sends a simplified precursor with a
legitimate host header on the same connection, then sends the actual
malicious request on that connection and returns the response.

## Preconditions
- Server validates some header or property **per connection** rather than
  per request.
- Server supports HTTP/1.1 keep-alive (persistent connections); shares
  a connection pool across requests.
- Attacker can reuse the same TCP connection across requests (Burp Suite
  or raw socket required — most HTTP clients open new connections).

## Detection
- Send a malicious request directly (e.g., `Host: internal-service`);
  observe a rejection or redirect.
- Send the same malicious request preceded by a clean precursor on the
  same connection; if accepted, the server validates per-connection.
- In Burp Suite, use the Logger to compare connection IDs — a reused
  connection ID for the second request confirms keep-alive reuse.

## Triggering
In Burp Repeater with a "Custom Action" configured for connection-state
attacks:
1. Craft the malicious request (e.g., `Host: 169.254.169.254`).
2. Click the custom action button; Burp sends:
   - Request 1 on new connection: `GET / HTTP/1.1\r\nHost: target.com\r\n…`
   - Request 2 on **same connection**: the malicious request from Repeater.
3. Response to request 2 is returned in Repeater.

Manual via raw socket or `curl --next`:
```
curl --next https://target.com/legit --next https://target.com/admin \
  -H "Host: internal-service"
```

## Bypasses
- **Connection: close on first response**: server closes after response 1,
  preventing connection reuse. Try pipeline mode (`Expect: 100-continue`
  to keep connection open) or use HTTP/2 with multiplexing.
- **Load balancer round-robins**: each request may hit a different backend,
  breaking the per-connection state assumption. Test from a single
  source IP on a predictable affinity configuration.

## Seen in the wild
- James Kettle demo: SSRF blocked by host-header validation — bypassed via
  connection-state attack (PortSwigger TV short, 2023).
- Applicable to any server that gates on first-request: auth headers,
  origin validation, rate-limit state.

## References
- PortSwigger TV: "HTTP is supposed to be stateless…" — James Kettle
  (short) — `wiki/sources/portswigger-tv/whisper/transcripts/BAZ-z2fA8E4_*.txt`
- Related: [[h2-downgrade-request-smuggling]], [[hop-by-hop-smuggling]]
