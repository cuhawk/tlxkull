---
title: SSRF Bypass via Trailing Dot in Hostname (DNS Denylist Evasion)
slug: ssrf-trailing-dot-bypass
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/ssrf, technique/waf-bypass, technique/dns]
inbound: []
---

# SSRF Bypass via Trailing Dot in Hostname (DNS Denylist Evasion)

## Pattern

DNS hostnames are absolute when they include a trailing dot (e.g.,
`localhost.` vs `localhost`). The trailing dot refers to the DNS root zone;
most clients strip it before making requests, but HTTP clients (curl, Python
requests, browsers) preserve it and still resolve the hostname correctly.

SSRF protection libraries that implement domain denylists often check whether
the provided hostname matches a blocked entry using simple string comparison.
If the comparison is `host == "blocked.internal"` (without normalizing the
trailing dot), then `blocked.internal.` (with trailing dot) bypasses the denylist
while still resolving to the same IP address.

Stripe's Smokescreen (open-source SSRF protection proxy) was vulnerable:
`hostMatchesGlob()` performed a direct string comparison. The hostname
`localhost.` was not equal to `localhost` in the comparison, so it was
allowed to pass the denylist, but the OS DNS resolver stripped the trailing
dot and resolved it normally. Stripe awarded $1,500 for finding this bypass
in their production SSRF protection library.

## Preconditions

- SSRF filter uses string comparison (not IP resolution) for denylist checks.
- HTTP client used by the application accepts trailing dots in hostnames and
  resolves them correctly (curl, Python requests, most HTTP clients do).
- The denylist is not applied post-resolution (i.e., the IP is not also checked).

## Detection

- Test `http://localhost./` and `http://169.254.169.254./` — if the application
  processes these differently than without the trailing dot, the bypass is active.
- Check open-source SSRF proxy code for string comparison vs hostname normalization.
- Verify the HTTP client: `curl http://localhost.` — most curl versions work.

## Triggering

Replace blocked hostnames with trailing-dot variants:
```
http://localhost./  → bypasses "localhost" denylist
http://169.254.169.254./  → bypasses AWS metadata IP denylist
http://metadata.google.internal./  → bypasses GCP metadata denylist
```

## Bypasses

The technique is itself a bypass technique. If it fails:
- Try URL encoding: `http://localhost%2E/`
- Try IDN encoding: `http://localhost。/` (Unicode fullstop as IDN separator)

## Seen in the wild

- 2021 — Stripe, $1,500 ($500 base + $1,000 bonus). Smokescreen SSRF proxy
  denylist bypass using trailing dot. The attack was limited to configurations
  where specific domains (not IPs) were blocklisted. Found by Greg (BBRE host)
  during a 100-hour challenge on Stripe.
  [BBRE](https://www.youtube.com/watch?v=Ga9o--v-grA)

## References

- Smokescreen GitHub (Stripe's SSRF proxy)
- RFC 1035 — DNS trailing dot semantics
- See also: [dns-rebinding-toctou-ssrf](dns-rebinding-toctou-ssrf.md)
- See also: [octal-ip-ssrf](octal-ip-ssrf.md)
