# GoodRx

> Platform: HackerOne — https://hackerone.com/goodrx
> Type: BBP
> Bounty: Low $750 | Medium $2,500 | High $5,000 | Critical $7,500
> Avg bounty: $250–$300
> Response efficiency: 84% | Avg first response: N/A | Total paid: $70,000
> Last scope update: 2025-02-03

## Scope

- in:  www.goodrx.com    # type: url # max: critical
- in:  com.goodrx    # type: android_app # max: critical
- in:  com.goodrx.iphone    # type: ios_app # max: critical
- in:  10.0.0.0/8    # type: cidr # max: critical
- in:  graph.goodrx.com    # type: url # max: critical # not eligible for bounty
- in:  http://securetest.scriptcycle.com    # type: url # max: critical # not eligible for bounty
- in:  GoodRx #1 2023 - iOS transfer scope    # type: other # max: none
- in:  www.hellogoodrx.com    # type: url # max: critical
- in:  co.heydoctor.android    # type: android_app # max: critical
- in:  com.heydoctor.iphone    # type: ios_app # max: critical
- in:  gold.goodrx.com    # type: url # max: critical
- in:  heydoctor.goodrx.com    # type: url # max: critical
- in:  m.goodrx.com    # type: url # max: critical
- in:  api.goodrx.com    # type: url # max: high
- out:  support.goodrx.com    # type: url # max: none
- out:  sso.identity.goodrx.com    # type: url # max: none
- out:  investors.goodrx.com    # type: url # max: none
- out:  com.goodrx.doctors    # type: android_app # max: none
- out:  com.goodrx.gold    # type: android_app # max: none
- out:  com.goodrx.doctors    # type: ios_app # max: none
- out:  com.goodrx.gold    # type: ios_app # max: none
- out:  api.heydoctor.com    # type: url # max: none
- out:  remote.goodrx.com    # type: other # max: none
- out:  remote2.goodrx.com    # type: url # max: none
- out:  www.iodine.com    # type: url # max: none
- out:  bugbounty-stage.goodrxbenefits.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $70,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
