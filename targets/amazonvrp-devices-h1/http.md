# Amazon Vulnerability Research Program - Devices

> Platform: HackerOne — https://hackerone.com/amazonvrp-devices
> Type: BBP
> Bounty: Low $200–$500 | Medium $600–$4,000 | High $6,000–$8,000 | Critical $25,000–$30,000
> Avg bounty: $500–$600
> Response efficiency: 85% | Avg first response: N/A | Total paid: $577,550
> Last scope update: 2025-11-11

## Scope

- in:  read.amazon.com    # type: url # max: critical
- in:  alexaanswers.amazon.com    # type: url # max: critical
- in:  blueprints.amazon.com    # type: url # max: critical
- in:  creator.amazon.com    # type: url # max: critical
- in:  amazon.com/hz/mycd/*    # type: url # max: critical
- in:  a4k.amazon.com    # type: url # max: critical
- in:  developer.amazon.com/apps-and-games/*    # type: url # max: critical
- in:  developer.amazon.com/alexa/*    # type: url # max: critical
- in:  alexa.amazon.com    # type: url # max: critical
- in:  skills-store.amazon.com    # type: url # max: critical
- in:  www.amazon.com/photos/*    # type: url # max: critical
- in:  api.amazonalexa.com/*    # type: url # max: critical
- in:  https://www.amazon.com/luna/*    # type: url # max: critical
- in:  https://luna.amazon.com/*    # type: url # max: critical
- in:  Tablets    # type: firmware # max: critical
- in:  Echo Family Devices    # type: firmware # max: critical
- in:  FireTV    # type: firmware # max: critical
- in:  Kindle E-Reader    # type: firmware # max: critical
- in:  Luna    # type: firmware # max: critical
- in:  com.amazon.kindle    # type: android_app # max: critical
- in:  com.amazon.storm.lightning.client.aosp    # type: android_app # max: critical
- in:  com.amazon.tahoe.freetime    # type: android_app # max: critical
- in:  com.amazon.dee.app    # type: android_app # max: critical
- in:  com.amazon.clouddrive.photos    # type: android_app # max: critical
- in:  com.amazon.tails    # type: android_app # max: critical
- in:  com.amazon.dee.alexaonwearos    # type: android_app # max: critical
- in:  944011620    # type: ios_app # max: critical
- in:  302584613    # type: ios_app # max: critical
- in:  947984433    # type: ios_app # max: critical
- in:  1324809509    # type: ios_app # max: critical
- in:  621574163    # type: ios_app # max: critical
- in:  1528364633    # type: ios_app # max: critical
- in:  Other    # type: other # max: critical # not eligible for bounty
- in:  com.amazon.cosmos    # type: android_app # max: critical
- in:  1291586307    # type: ios_app # max: critical
- in:  com.amazon.dee.app    # type: ios_app # max: critical
- in:  com.amazon.tahoe.freetime    # type: url # max: critical
- in:  com.amazon.dee.app    # type: url # max: critical
- in:  com.amazon.healthtech.malibu    # type: url # max: critical
- out:  Devices    # type: other # max: none
- out:  Services and Apps    # type: other # max: none
- out:  "Contact Us" Functionality    # type: other # max: none
- out:  com.amazon.healthtech.malibu    # type: android_app # max: none
- out:  Halo    # type: firmware # max: none
- out:  1496435377    # type: ios_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $577,550
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
