# PortSwigger Web Security

> Platform: HackerOne — https://hackerone.com/portswigger
> Type: BBP
> Bounty: Low N/A | Medium $1,000 | High $5,000 | Critical $15,000
> Avg bounty: $350–$400
> Response efficiency: 98% | Avg first response: N/A | Total paid: $72,500
> Last scope update: 2026-05-06

## Scope

- in:  portswigger.net    # type: url # max: critical
- in:  ai.portswigger.net    # type: url # max: critical
- in:  collections.portswigger.net    # type: url # max: critical
- in:  share.portswigger.net    # type: url # max: critical
- in:  links.portswigger.net    # type: url # max: critical
- in:  http1mustdie.com    # type: url # max: high
- in:  Burp Suite DAST    # type: other # max: critical
- in:  Burp Collaborator    # type: downloadable_executables # max: critical
- in:  Burp Suite Pro/Community    # type: downloadable_executables # max: high
- in:  Burp Suite Extension (BApps)    # type: downloadable_executables # max: none # not eligible for bounty
- in:  https://enterprise-demo.portswigger.net/    # type: url # max: critical
- in:  forum.portswigger.net    # type: url # max: critical
- in:  Burp Suite Enterprise Edition    # type: downloadable_executables # max: critical
- out:  *.portswigger.net    # type: wildcard # max: none
- out:  *.web-security-academy.net    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $72,500

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
