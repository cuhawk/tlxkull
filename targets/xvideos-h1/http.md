# XVIDEOS

> Platform: HackerOne — https://hackerone.com/xvideos
> Type: BBP
> Bounty: Low $200 | Medium $600 | High $3,000 | Critical $20,000
> Avg bounty: $200–$200
> Response efficiency: 94% | Avg first response: N/A | Total paid: $134,092
> Last scope update: 2025-09-09

## Scope

- in:  www.xvideos.com    # type: url # max: critical
- in:  www.xvideos.red    # type: url # max: critical
- in:  www.xnxx.com    # type: url # max: critical
- in:  https://www.xvideos.net/app/    # type: url # max: critical
- in:  www.xnxx.gold    # type: url # max: critical
- in:  gold.xnxx.com    # type: url # max: critical
- in:  *.xnxx.com    # type: wildcard # max: critical
- in:  *.xvideos.com    # type: wildcard # max: critical
- out:  www.xvcams.com    # type: url # max: none
- out:  www.xvlivecams.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $134,092
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
