---
title: HTTP/3 connection contamination
slug: h3-connection-contamination
created_utc: 2026-05-19T00:00:00Z
updated_utc: 2026-05-19T00:00:00Z
tags: [technique/server-side, technique/h2, technique/h3, technique/request-smuggling]
inbound: []
---

# HTTP/3 connection contamination

## Pattern
HTTP/2 introduced connection reuse across *multiple websites* provided they
are "closely related" (share an IP address / TLS certificate). Servers
that have assumed since HTTP/1.1 (1997) that all requests on a single
connection belong to the same website are caught off-guard: a browser
sends a request intended for site-A down a connection already established
with site-B, and site-B's server handles it as if it were its own.

HTTP/3 makes this dramatically worse: its spec removes the shared-IP
requirement. Any two sites hosted by the **same company** (CDN, hosting
provider) can share a connection — regardless of IP. What was rare in H2
becomes systemic in H3.

**Attack primitive:** Compromise a low-security website at company X.
Victim browsers with an H3 connection to that insecure site may also use
it for requests to secure sites at the same company. The compromised site
can read, modify, or respond to those cross-site requests.

**Discovery:** Kettle found the H2 variant after a developer accidentally
triggered it and posted a confused complaint on a forum. The angry post
read as a security bug to an offensive researcher.

## Protocol timeline

| Version | Connection reuse scope | Smuggling introduced |
|---------|----------------------|----------------------|
| HTTP/1.0 (1996) | One request per connection | None |
| HTTP/1.1 (1996) | Multiple requests, one site | Yes — CL.TE/TE.CL |
| HTTP/2 (2015) | Multiple sites sharing same IP | H2 desync (mostly fixed) + **connection contamination** |
| HTTP/3 (spec) | Multiple sites, any IP (same org) | **Contamination goes wide** |

## Preconditions
- Target uses HTTP/2 or HTTP/3.
- Two sites share a connection under H2's same-IP/cert rule (or H3's
  relaxed rule).
- At least one of the sites does not validate that the `Host` / `:authority`
  pseudo-header matches its own identity before processing the request.
- For exploitation: attacker controls one of the sites sharing the
  connection (via compromise or ownership of a co-hosted domain).

## Detection
- Enumerate CDN/hosting co-tenants of the target (Shodan, cert
  transparency, IP reverse DNS).
- Test whether the server accepts H2/H3 requests with `:authority` set
  to a different co-hosted domain and returns that domain's content.
- Observe whether an H2 session established to domain A will serve
  responses for domain B without issuing a redirect.

## Triggering
In Burp Suite (H2 Inspector tab), send to a server that hosts multiple
domains:
```
:method  GET
:path    /admin
:authority  target-secure.example.com
:scheme  https
```
via a connection established to `insecure.example.com` (same IP, same
CDN PoP). If the server returns `target-secure`'s content, contamination
is live.

## Impact
- **Cross-site request hijacking**: victim's authenticated H3 request to
  `secure.company.com` is served by attacker-controlled `pwned.company.com`.
- **Session stealing**: cookies scoped to `.company.com` sent to
  the wrong origin.
- **Response injection**: attacker's site injects crafted responses into
  the victim's connection for the secure site.

## Bypasses / mitigations
- **Server-side**: validate `:authority` matches the current server's
  identity on every request, not just the first.
- **Client-side**: browsers should issue ORIGIN frames (H2) or equivalent
  H3 mechanism to explicitly declare which origins a connection serves;
  servers must enforce this.
- **Short-term**: disable H2/H3 connection coalescing at CDN level for
  multi-tenant setups.

## Seen in the wild
- James Kettle (PortSwigger): discovered via forum post where a developer
  accidentally triggered cross-site routing on a CDN; formalized as
  research and published 2023.
- H3 risk is **forward-looking** (2025+): widespread H3 adoption by CDNs
  will expand the affected population from "same-IP tenants" to
  "same-CDN tenants".

## References
- PortSwigger TV: "HTTP/3 Connection Contamination Made Simple" — James Kettle
  — `wiki/sources/portswigger-tv/whisper/transcripts/-mHjTEp5SAc_*.txt`
- PortSwigger Research blog: HTTP/3 Connection Contamination (2023)
- Related: [[h2-downgrade-request-smuggling]], [[h2-request-tunneling]], [[hop-by-hop-smuggling]]
