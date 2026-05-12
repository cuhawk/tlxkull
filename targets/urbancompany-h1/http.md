# Urban Company

> Platform: HackerOne — https://hackerone.com/urbancompany
> Type: BBP
> Bounty: Low $250 | Medium $500 | High $1,500 | Critical $3,000
> Avg bounty: $250–$250
> Response efficiency: 32% | Avg first response: N/A | Total paid: $87,900
> Last scope update: 2023-08-01

## Scope

- in:  www.urbancompany.com    # type: url # max: critical
- in:  www.urbanclap.com    # type: url # max: critical
- in:  com.urbanclap.provider    # type: android_app # max: critical
- in:  com.urbanclap.urbanclap    # type: android_app # max: critical
- in:  1032480595    # type: ios_app # max: critical
- in:  982922982    # type: ios_app # max: critical
- out:  Other urbancompany.com subdomains except for the ones in-scope    # type: other # max: none
- out:  Other .urbanclap.com subdomains except for the ones in-scope    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $87,900

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
