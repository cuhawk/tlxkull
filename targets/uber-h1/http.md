# Uber

> Platform: HackerOne — https://hackerone.com/uber
> Type: BBP
> Bounty: Low $300 | Medium $2,500 | High $11,000 | Critical $15,000
> Avg bounty: $500–$700
> Response efficiency: 93% | Avg first response: N/A | Total paid: $4,369,464
> Last scope update: 2025-06-02

## Scope

- in:  uber.com    # type: url # max: critical
- in:  Recon Data    # type: other # max: none
- in:  *.uberinternal.com    # type: other # max: none
- in:  *ubereats.com    # type: other # max: none
- in:  Uber Assets    # type: other # max: critical
- in:  uber.com    # type: url # max: none
- out:  *scaledsolutions.uber.com    # type: wildcard # max: none
- out:  scaledsolutions*.uber.com    # type: wildcard # max: none
- out:  *.uberscoot.us    # type: url # max: none
- out:  *.ubertransit.io    # type: url # max: none
- out:  merchants.ubereats.com    # type: url # max: none
- out:  bizblog.uber.com    # type: url # max: none
- out:  et.uber.com    # type: url # max: none
- out:  newsroom.uber.com    # type: url # max: none
- out:  eng.uber.com    # type: url # max: none
- out:  people.uber.com    # type: url # max: none
- out:  love.uber.com    # type: url # max: none
- out:  drive.uber.com    # type: url # max: none
- out:  uber.onelogin.com    # type: url # max: none
- out:  uber.com.cn    # type: url # max: none
- out:  https://assets.uber.com    # type: url # max: none
- out:  https://brand.uber.com    # type: url # max: none
- out:  Fraud Reports    # type: other # max: none
- out:  *.ubercarshare.com    # type: other # max: none
- out:  Routematch    # type: other # max: none
- out:  *.xchangeleasing.com    # type: url # max: none
- out:  Autocab    # type: other # max: none
- out:  UT    # type: other # max: none
- out:  Postmates    # type: downloadable_executables # max: none
- out:  HKTaxi    # type: other # max: none
- out:  Drizly    # type: other # max: none
- out:  Cornershop    # type: other # max: none
- out:  Careem    # type: other # max: none
- out:  Car Next Door    # type: other # max: none
- out:  *.support-uber.com    # type: url # max: none
- out:  *.sobi.io    # type: url # max: none
- out:  *.ot.to    # type: url # max: none
- out:  *.lioncityrentals.com.sg    # type: url # max: none
- out:  *.carnextdoor.com.au    # type: url # max: none
- out:  uber.onelogin.com    # type: url # max: none
- out:  *.uber.com.cn    # type: url # max: none
- out:  bizblog.uber.com    # type: url # max: none
- out:  newsroom.uber.com    # type: url # max: none
- out:  love.uber.com    # type: url # max: none
- out:  drive.uber.com    # type: url # max: none
- out:  eng.uber.com    # type: url # max: none
- out:  people.uber.com    # type: url # max: none
- out:  et.uber.com    # type: url # max: none
- out:  Transplace    # type: other # max: none
- out:  Divested Companies    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $4,369,464
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
