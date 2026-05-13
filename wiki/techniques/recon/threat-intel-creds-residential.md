---
title: Threat-intel cred hunting + residential proxy recon
slug: threat-intel-creds-residential
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/recon]
inbound: []
---

# Threat-intel cred hunting + residential-proxy recon

Jason Haddix — Critical Thinking Podcast Ep 63.

## Pattern

### Threat-intel cred hunting
Buy stealer-log creds (RedLine etc.) on Telegram / dark-web forums.
Sellers post free preview samples — grep previews for `@target.com` to
find fresh corp creds. Stealer malware also dumps browser cookies →
bypasses 2FA by injecting cookie. Some BB programs accept (esp. ones
who've been breached this way before). 5 of 6 recent red-team engagements
landed via this. Cost: ~$10/cred to thousands for full packs.

### Residential proxy recon
When target blacklists VPS ranges (DigitalOcean, AWS, API-Gateway/FireProx),
use Bright Data residential proxies (rotates per request through users
running their agent on home machines) for recon (httpx, screenshots,
etc). Keep threads low (~15) to avoid burning residential IPs.

## Preconditions
- Program's policy permits use of leaked creds (NOT all do — confirm).
- Bright Data approval requires interview.

## Detection
- Flare / SensePost Frack — paid commercial threat-intel platform indexing
  dark-web/Telegram cred data; pen-test/red-team pricing tier (cheaper
  than enterprise CTI).

## Related
- HackRevDNS — fast PTR lookup tool for ASN ranges.
- CSPRecon CLI — reverse-CSP lookup.
- DMARC.live — reverse-DMARC lookup.
- whoisxmlapi (paid) — reverse nameserver query (12 unknown FIS apex
  domains found this way).
- FireProx — AWS API Gateway IP rotation.
- Geo-locked targets (regional KYC) = drastically less competition.

## Seen in the wild
- 5/6 red-team wins via stealer creds (Haddix ~2024).
- Critical Thinking Podcast Ep 63.

## References
- Critical Thinking Podcast Ep 63
- bughuntersmethodology JS-analysis section (Q1 2024 cohort)
