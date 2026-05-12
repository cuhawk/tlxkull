# Plaid

> Platform: HackerOne — https://hackerone.com/plaid
> Type: BBP
> Bounty: Low $1,000 | Medium $2,500 | High $5,000 | Critical $10,000
> Avg bounty: $250–$500
> Response efficiency: 93% | Avg first response: N/A | Total paid: $80,000
> Last scope update: 2023-03-15

## Scope

- in:  production.plaid.com    # type: url # max: critical
- in:  dashboard.plaid.com    # type: url # max: critical
- in:  cdn.plaid.com    # type: url # max: critical
- in:  my.plaid.com    # type: url # max: critical
- in:  secure.plaid.com    # type: url # max: critical
- in:  demo.plaid.com    # type: url # max: medium
- in:  plaid.com    # type: url # max: medium
- in:  https://github.com/plaid/plaid-link-ios    # type: repo # max: critical
- in:  https://github.com/plaid/plaid-link-android    # type: repo # max: critical
- in:  https://github.com/plaid/plaid-ruby    # type: repo # max: critical
- in:  https://github.com/plaid/react-native-plaid-link-sdk    # type: repo # max: critical
- in:  https://github.com/plaid/react-plaid-link    # type: repo # max: critical
- in:  https://github.com/plaid/plaid-link-examples    # type: repo # max: critical
- in:  secure.quovo.com    # type: url # max: critical
- in:  app.quovo.com    # type: url # max: critical
- in:  manage.blockscore.com    # type: url # max: critical
- in:  api.blockscore.com    # type: url # max: critical
- in:  link.plaid.com    # type: url # max: critical
- in:  https://github.com/plaid/plaid-link-examples    # type: url # max: critical
- in:  api.plaid.com    # type: url # max: critical

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $80,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
