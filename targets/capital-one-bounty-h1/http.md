# Capital One Bug Bounty

> Platform: HackerOne — https://hackerone.com/capital-one-bounty
> Type: BBP
> Bounty: Low $250 | Medium $750 | High $2,500 | Critical $5,000
> Avg bounty: $250–$750
> Response efficiency: 89% | Avg first response: N/A | Total paid: $59,063
> Last scope update: 2024-09-04

## Scope

- in:  Eno® Browser Extension    # type: other # max: critical
- in:  *.capitalone.com    # type: other # max: critical
- in:  *.capitaloneshopping.com    # type: other # max: critical
- in:  Capital One Shopping Browser Extension    # type: other # max: critical
- in:  *.capitalonegslbex.com    # type: other # max: critical
- in:  *.capitalone.ca    # type: other # max: critical
- in:  com.konylabs.capitalone    # type: android_app # max: critical
- in:  com.wikibuy.prod.main    # type: android_app # max: critical
- in:  407558537    # type: ios_app # max: critical
- in:  1089294040    # type: ios_app # max: critical
- in:  verified.capitalone.com*    # type: url # max: critical
- in:  myaccounts.capitalone.com*    # type: url # max: critical
- in:  spring.capitalone.com*    # type: url # max: critical
- out:  http://myaccounts.capitalone.com/Profile    # type: url # max: none
- out:  http://myaccounts.capitalone.com/Security    # type: url # max: none
- out:  http://myaccounts.capitalone.com/Settings    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $59,063
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
