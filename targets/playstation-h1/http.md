# PlayStation

> Platform: HackerOne — https://hackerone.com/playstation
> Type: BBP
> Bounty: Low $100–$500 | Medium $400–$2,500 | High $1,000–$10,000 | Critical $3,000–$50,000
> Avg bounty: $400–$400
> Response efficiency: 86% | Avg first response: N/A | Total paid: $885,350
> Last scope update: 2025-03-25

## Scope

- in:  *.playstation.net    # type: url # max: critical
- in:  *.sonyentertainmentnetwork.com    # type: url # max: critical
- in:  *.api.playstation.com    # type: url # max: critical
- in:  my.playstation.com    # type: url # max: critical
- in:  store.playstation.com    # type: url # max: critical
- in:  social.playstation.com    # type: url # max: critical
- in:  transact.playstation.com    # type: url # max: critical
- in:  wallets.api.playstation.com    # type: url # max: critical
- in:  direct.playstation.com    # type: url # max: critical
- in:  api.direct.playstation.com    # type: url # max: critical
- in:  ca.account.sony.com    # type: url # max: critical
- in:  my.account.sony.com    # type: url # max: critical
- in:  ps5.np.playstation.net    # type: url # max: critical
- in:  checkout.playstation.com    # type: url # max: critical
- in:  PlayStation 4    # type: firmware # max: critical
- in:  PlayStation 5    # type: firmware # max: critical
- in:  Android Playstation App    # type: android_app # max: critical
- in:  iOS Playstation App    # type: ios_app # max: critical
- in:  410896080    # type: ios_app # max: critical
- in:  com.scee.psxandroid    # type: android_app # max: critical
- in:  PlayStation Network    # type: other # max: critical

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $885,350
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
