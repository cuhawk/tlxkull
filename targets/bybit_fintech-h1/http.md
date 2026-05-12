# Bybit Fintech Ltd

> Platform: HackerOne — https://hackerone.com/bybit_fintech
> Type: BBP
> Bounty: Low $600 | Medium $1,500 | High $5,000 | Critical $10,000
> Avg bounty: $505–$576
> Response efficiency: 95% | Avg first response: N/A | Total paid: $80,514
> Last scope update: 2026-01-26

## Scope

- in:  *.bybit.com    # type: wildcard # max: critical
- in:  *.bybit.eu    # type: wildcard # max: critical
- in:  *.bybit.tr    # type: wildcard # max: critical
- in:  http://testnet.bybit.eu    # type: url # max: critical
- in:  http://www.bybit.com/trade/tradfi/    # type: url # max: critical
- in:  http://www.bybit.com/en/alpha/overview/    # type: url # max: critical
- in:  http://www.byreal.io    # type: url # max: critical
- in:  https://play.google.com/store/apps/details?id=com.bybit.app&hl=en    # type: android_app # max: critical
- in:  https://apps.apple.com/us/app/bybit-app/id1488296980    # type: ios_app # max: critical
- in:  *.bybit-tr.com    # type: wildcard # max: critical
- in:  Web3 Smart Contract    # type: other # max: critical
- in:  bybit.com    # type: url # max: critical

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $80,514
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
