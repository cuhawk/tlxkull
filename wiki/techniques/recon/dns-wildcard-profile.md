---
title: DNS wildcard profiling for subdomain enumeration
slug: dns-wildcard-profile
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/recon, technique/subdomain-enum, technique/dns]
inbound: []
---

# DNS wildcard profiling

## Pattern
Most subdomain wordlists fall apart against wildcard DNS — every probe
resolves so naive enum returns nothing useful. Naive defense is "if it
matches the wildcard, drop it." That throws away **the diamonds in the
rough**: subdomains that legitimately exist within the wildcard zone but
return a *different* response (different IP-set, different ports, different
TLS cert) than the wildcard's canonical answer.

Build a wildcard **profile**:

1. Resolve a random/unlikely label (e.g. `nonexistent-$RANDOM.target.com`)
   multiple times across multiple resolvers (1.1.1.1, 8.8.8.8, internal,
   etc.) to capture round-robin IP variance.
2. Repeat with several random labels at the suspected wildcard depth.
3. Walk parent zones progressively (`*.target.com`, `*.app.target.com`)
   to identify the wildcard's actual scope.
4. Record canonical IP-set, TTL, CNAME chain, and any port-443
   certificate SAN list.

Then when enumerating, **keep** any subdomain that resolves *outside* the
profile.

Side-trick: `dig STAR.target.com` (literal `*` label) often returns the
wildcard's own A record directly — quick wildcard confirmation.

## Preconditions
- Target zone uses wildcard DNS (signaled by NXDOMAIN-vs-A pattern across
  random labels).

## Detection signals
- Random-label probes all resolve to the same IP-set → wildcard active.
- A real subdomain in the same zone resolves to a *different* IP-set —
  surface it.
- TLS cert SAN list of a returned IP may also enumerate hidden hostnames.

## Triggering / tooling
- `dnsx`, `puredns`, custom Python with `dnspython` + multiple resolvers.
- AssetNote's `surf` style tooling for surfacing internal-host candidates.

## Seen in the wild
- {date: 2023-11-30, source: CT Ep 47} — JG + Joel discord-collaboration
  notes; AssetNote's Sean (S-Y) chimes in on Discord.

## References
- Critical Thinking Podcast Ep 47
- Related: [[threat-intel-creds-residential]]
