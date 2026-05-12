# Flipkart

> Platform: HackerOne — https://hackerone.com/flipkart
> Type: BBP
> Bounty: Low $350 | Medium $800 | High $2,500 | Critical $4,000
> Avg bounty: $300–$350
> Response efficiency: 96% | Avg first response: N/A | Total paid: $41,480
> Last scope update: 2025-04-03

## Scope

- in:  https://api.myntra.com    # type: url # max: critical
- in:  https://payments.myntra.com    # type: url # max: critical
- in:  https://www.myntra.com    # type: url # max: critical
- in:  https://www.flipkart.com    # type: url # max: critical
- in:  https://pay.payzippy.com    # type: url # max: critical
- in:  https://uiscoop.payzippy.com    # type: url # max: critical
- in:  https://apps.apple.com/in/app/flipkart-online-shopping-app/id742044692    # type: url # max: critical
- in:  https://play.google.com/store/apps/details?id=com.flipkart.android    # type: url # max: critical
- in:  https://play.google.com/store/apps/details?id=com.myntra.android    # type: android_app # max: critical
- in:  https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059    # type: ios_app # max: critical
- in:  https://*.payzippy.com    # type: wildcard # max: critical
- in:  www.flipkart.com    # type: url # max: critical
- in:  www.myntra.com    # type: url # max: critical
- in:  *.ekartlogistics.com    # type: wildcard # max: critical
- in:  *.payzippy.com    # type: wildcard # max: critical
- in:  *.flipkart.com    # type: wildcard # max: critical
- in:  accounts.myntra.com    # type: url # max: critical
- in:  payments.myntra.com    # type: url # max: critical
- in:  pps.myntra.com    # type: url # max: critical
- in:  api.myntra.com    # type: url # max: critical
- in:  seller.flipkart.com    # type: url # max: critical
- in:  https://www.cleartrip.com/    # type: url # max: critical
- in:  https://play.google.com/store/apps/details?id=com.myntra.android    # type: other # max: critical
- in:  https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059    # type: other # max: critical
- in:  com.flipkart.android    # type: android_app # max: critical
- in:  com.flipkart.seller    # type: android_app # max: critical
- in:  742044692    # type: ios_app # max: critical
- in:  com.toogud.android    # type: android_app # max: critical
- in:  *.2gud.com    # type: wildcard # max: critical
- in:  www.flipkart.com    # type: url # max: critical
- in:  affiliate.flipkart.com    # type: url # max: critical
- in:  seller.flipkart.com    # type: url # max: critical
- in:  affiliate.flipkart.com    # type: url # max: none # not eligible for bounty
- in:  seller.flipkart.com    # type: url # max: none # not eligible for bounty
- in:  ads.flipkart.com    # type: url # max: none # not eligible for bounty
- in:  adp.flipkart.com    # type: url # max: none # not eligible for bounty
- in:  brands.flipkart.com    # type: url # max: none # not eligible for bounty
- in:  adp.flipkart.com    # type: url # max: none # not eligible for bounty
- out:  blog.flipkart.com    # type: url # max: none
- out:  tech.flipkart.com    # type: url # max: none
- out:  ads.flipkart.com    # type: url # max: none
- out:  brands.flipkart.com    # type: url # max: none
- out:  stories.flipkart.com    # type: url # max: none
- out:  healthplus.flipkart.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $41,480
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
