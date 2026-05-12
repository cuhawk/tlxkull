# eufy Security

> Platform: HackerOne — https://hackerone.com/eufy_security
> Type: BBP
> Bounty: Low $100–$150 | Medium $300–$500 | High $800–$1,200 | Critical $2,000–$8,000
> Avg bounty: $200–$300
> Response efficiency: 94% | Avg first response: N/A | Total paid: $62,940
> Last scope update: 2025-05-09

## Scope

- in:  https://us.eufy.com/products/e8213181    # type: firmware # max: critical
- in:  eufyMake E1    # type: firmware # max: critical
- in:  Solarbank 2 E1600 Pro    # type: firmware # max: critical
- in:  https://us.eufy.com/products/t88711w1    # type: firmware # max: high
- in:  https://us.eufy.com/products/t88511d1    # type: firmware # max: high
- in:  https://us.eufy.com/products/t8410121    # type: firmware # max: high
- in:  com.oceanwing.care.cam    # type: android_app # max: critical
- in:  com.oceanwing.battery.cam    # type: android_app # max: high
- in:  com.oceanwing.FDMPrint    # type: android_app # max: high
- in:  com.anker.charging    # type: android_app # max: high
- in:  eufyMake Studio software    # type: downloadable_executables # max: high
- in:  com.security.care    # type: ios_app # max: critical
- in:  com.security.BatteryCam    # type: ios_app # max: high
- in:  com.anker.AnkerMake    # type: ios_app # max: high
- in:  Anker    # type: ios_app # max: high
- in:  com.eufylife.EufyHome    # type: ios_app # max: low
- in:  id1635029057    # type: ios_app # max: high
- in:  https://makeitreal-beta.eufymake.com/    # type: url # max: critical
- in:  eufyMake Studio    # type: downloadable_executables # max: critical
- in:  com.anker.charging    # type: ios_app # max: high
- in:  https://www.ankermake.com/products/m5?variant=42744298373269    # type: firmware # max: medium
- in:  https://passport.eufy.com/?app=eufy-us    # type: url # max: critical
- in:  eufy Security and Privacy Whitepaper    # type: other # max: high
- in:  eufy security and privacy whitepaper    # type: other # max: critical
- in:  https://us.eufy.com/products/e8213181    # type: url # max: critical

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $62,940
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
