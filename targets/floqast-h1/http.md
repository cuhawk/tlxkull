# FloQast

> Platform: HackerOne — https://hackerone.com/floqast
> Type: BBP
> Bounty: Low $5 | Medium $10 | High $25 | Critical $50
> Avg bounty: $1,000–$1,000
> Response efficiency: 88% | Avg first response: N/A | Total paid: $151,975
> Last scope update: 2025-10-24

## Scope

- in:  *.eu.floqast.app    # type: wildcard # max: critical
- in:  *.floqast.app    # type: wildcard # max: critical
- in:  https://*.floqast.engineering    # type: wildcard # max: critical
- in:  api-eu.floqast.app    # type: url # max: critical
- in:  eu.floqast.app    # type: url # max: critical
- out:  *.floqast.com    # type: wildcard # max: none
- out:  *.floqast.studio    # type: wildcard # max: none
- out:  Any Asset Not Specifically Listed as In-Scope    # type: other # max: none
- out:  s3://floqast    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $151,975
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
