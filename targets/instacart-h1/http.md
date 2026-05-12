# Instacart

> Platform: HackerOne — https://hackerone.com/instacart
> Type: BBP
> Bounty: Low $250 | Medium $1,500 | High $5,000 | Critical $15,000
> Avg bounty: $200–$250
> Response efficiency: 86% | Avg first response: N/A | Total paid: $515,795
> Last scope update: 2024-04-24

## Scope

- in:  *.instacart.com    # type: wildcard # max: critical
- in:  *.instacart.tools    # type: wildcard # max: critical
- in:  api.instacart.com    # type: url # max: critical
- in:  www.instacart.com    # type: url # max: critical
- in:  admin.instacart.com    # type: url # max: critical
- in:  shoppers.instacart.com    # type: url # max: critical
- in:  template.uat.foodstorm.com    # type: url # max: critical
- in:  Android & iOS App for Instacart Shoppers    # type: other # max: critical
- in:  com.instacart.client    # type: android_app # max: critical
- in:  545599256    # type: ios_app # max: critical
- in:  570231180    # type: ios_app # max: critical
- in:  392633134    # type: ios_app # max: critical
- in:  638455030    # type: ios_app # max: critical
- in:  shop.raleys.com    # type: url # max: medium
- in:  shop.hebtoyou.com    # type: url # max: medium
- in:  shop.sprouts.com    # type: url # max: medium
- in:  harmonsgrocery.com    # type: url # max: medium
- in:  shop.lowesfoods.com    # type: url # max: medium
- in:  shopthefastlane.com    # type: url # max: medium
- in:  freshthyme.com    # type: url # max: medium
- in:  app.longos.com    # type: url # max: medium
- in:  shop.lundsandbyerlys.com    # type: url # max: medium
- in:  shopping.rochebros.com    # type: url # max: medium
- in:  sprouts.com    # type: url # max: medium
- in:  shop.pricechopper.com    # type: url # max: medium
- in:  pricechopper.com    # type: url # max: medium
- in:  com.rochebros.app.android    # type: android_app # max: medium
- in:  com.gpshopper.lunds    # type: android_app # max: medium
- in:  com.longos    # type: android_app # max: medium
- in:  discover.freshthyme.com    # type: url # max: medium
- out:  *.email.instacart.com    # type: wildcard # max: none
- out:  brand.instacart.com    # type: url # max: none
- out:  careers.instacart.com    # type: url # max: none
- out:  carrotstore.instacart.com    # type: url # max: none
- out:  corporate.instacart.com    # type: url # max: none
- out:  covidresponse.instacart.com    # type: url # max: none
- out:  design.instacart.com    # type: url # max: none
- out:  life.instacart.com    # type: url # max: none
- out:  news.instacart.com    # type: url # max: none
- out:  tech.instacart.com    # type: url # max: none
- out:  enterprise-status.instacart.com    # type: url # max: none
- out:  instacart.careers    # type: url # max: none
- out:  shop.foodlion.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $515,795
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
