# Newegg

> Platform: HackerOne — https://hackerone.com/newegg
> Type: BBP
> Bounty: Low $150 | Medium $350 | High $1,000–$2,000 | Critical $3,000–$3,500
> Avg bounty: $350–$500
> Response efficiency: 96% | Avg first response: N/A | Total paid: $104,100
> Last scope update: 2025-08-09

## Scope

- in:  http://*.newegg.com    # type: wildcard # max: critical
- in:  http://*.newegg.ca    # type: wildcard # max: critical
- in:  https://secure.newegg.com    # type: url # max: critical
- in:  secure.newegg.ca    # type: url # max: critical
- in:  pmtcards.newegg.com    # type: url # max: critical
- in:  com.newegg.app    # type: android_app # max: critical
- in:  com.newegg.app    # type: ios_app # max: critical
- in:  sellerportal.newegg.com    # type: url # max: critical # not eligible for bounty
- in:  sellingpilot.com    # type: url # max: critical
- in:  https://apps.apple.com/us/app/newegg-tech-shopping-online/id345188269    # type: ios_app # max: critical
- in:  *.abs.com    # type: wildcard # max: critical
- in:  *.nutrend.com    # type: wildcard # max: critical
- in:  *.rosewill.com    # type: wildcard # max: critical
- in:  *.rosewillhome.com    # type: wildcard # max: critical
- in:  *.purefsi.com    # type: wildcard # max: critical
- out:  http://*.neweggbusiness.com    # type: wildcard # max: none
- out:  jobs.newegg.com    # type: url # max: none
- out:  sellingpilot.newegg.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $104,100
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
