# Varonis

> Platform: HackerOne — https://hackerone.com/varonis
> Type: BBP
> Bounty: Low $150 | Medium $500 | High $1,500 | Critical $4,000
> Avg bounty: $310–$400
> Response efficiency: 94% | Avg first response: N/A | Total paid: $10,000
> Last scope update: 2025-02-20

## Scope

- in:  *.varonis.com    # type: wildcard # max: critical
- in:  *.varonis.io    # type: wildcard # max: critical
- in:  *.varonis.net    # type: wildcard # max: high
- in:  messaging.api.varonis.io    # type: url # max: none
- in:  chd.varonis.io    # type: url # max: none
- in:  varonis.net    # type: url # max: high
- in:  blog.varonis.ru    # type: url # max: high
- in:  blog.varonis.fr    # type: url # max: high
- in:  blog.varonis.es    # type: url # max: high
- in:  blog.varonis.de    # type: url # max: high
- out:  *.varonis-preprod.com    # type: wildcard # max: none
- out:  *.cyral.com    # type: wildcard # max: none
- out:  All other assets    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $10,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
