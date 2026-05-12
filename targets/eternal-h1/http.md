# Eternal

> Platform: HackerOne — https://hackerone.com/eternal
> Type: BBP
> Bounty: Low $100–$300 | Medium $250–$1,000 | High $500–$2,000 | Critical $1,000–$4,000
> Avg bounty: $200–$250
> Response efficiency: 100% | Avg first response: N/A | Total paid: $469,668
> Last scope update: 2026-03-23

## Scope

- in:  *.zomato.com    # type: wildcard # max: critical
- in:  *.zdev.net    # type: wildcard # max: critical
- in:  *.zomans.com    # type: wildcard # max: critical
- in:  *.hyperpure.com    # type: wildcard # max: critical
- in:  *.runnr.in    # type: wildcard # max: critical
- in:  http://*.grofer.io    # type: wildcard # max: critical
- in:  http://*.grofers.com    # type: wildcard # max: critical
- in:  *.district.in    # type: wildcard # max: critical
- in:  *.edition.in    # type: wildcard # max: critical
- in:  *.ticketnew.com    # type: wildcard # max: critical
- in:  *.insider.in    # type: wildcard # max: critical
- in:  *.tktnew.com    # type: wildcard # max: critical
- in:  *.eternal.com    # type: wildcard # max: critical
- in:  winecellar.zomato.com    # type: url # max: critical
- in:  api.grofers.com    # type: url # max: critical
- in:  api2.grofers.com    # type: url # max: critical
- in:  blinkit.com    # type: url # max: critical
- in:  bistro-api.blinkit.com    # type: url # max: critical
- in:  https://mcp-server.zomato.com/mcp    # type: url # max: critical
- in:  All Assets (other than Blinkit)    # type: other # max: critical
- in:  Tier 2    # type: other # max: critical
- in:  Tier 1    # type: other # max: critical
- in:  Tier 3    # type: other # max: critical
- in:  Data Protection Program    # type: other # max: critical
- in:  com.application.zomato    # type: android_app # max: critical
- in:  com.grofers.customerapp    # type: android_app # max: critical
- in:  com.blinkit.bistro    # type: android_app # max: critical
- in:  com.application.zomato.district    # type: android_app # max: critical
- in:  434613896    # type: ios_app # max: critical
- in:  960335206    # type: ios_app # max: critical
- in:  6670203019    # type: ios_app # max: critical
- in:  6670536058    # type: ios_app # max: critical
- in:  Scope Questions: Items not explicitly listed here    # type: other # max: critical # not eligible for bounty
- in:  com.application.zomatomerchant    # type: android_app # max: critical # not eligible for bounty
- in:  All Blinkit assets (in scope)    # type: other # max: critical
- in:  991745732    # type: ios_app # max: critical # not eligible for bounty
- in:  912349367    # type: ios_app # max: critical # not eligible for bounty
- in:  www.zomato.com    # type: url # max: critical
- out:  staging*.runnr.in    # type: wildcard # max: none
- out:  http://*.blinkit.support    # type: wildcard # max: none
- out:  *.zomatoportugal.com    # type: wildcard # max: none
- out:  *.bstro.io    # type: wildcard # max: none
- out:  *.ali.zomans.com    # type: wildcard # max: none
- out:  business-blog.zomato.com    # type: url # max: none
- out:  blog.zomato.com    # type: url # max: none
- out:  community.zomato.com    # type: url # max: none
- out:  success.zomato.com    # type: url # max: none
- out:  dev.hyperpure.com    # type: url # max: none
- out:  devapi.hyperpure.com    # type: url # max: none
- out:  devpod.hyperpure.com    # type: url # max: none
- out:  send.zomato.com    # type: url # max: none
- out:  www.zomatobook.com    # type: url # max: none
- out:  com.application.zomato.ordering    # type: android_app # max: none
- out:  edition.in    # type: url # max: none
- out:  http://*.blinkit.in    # type: wildcard # max: none
- out:  http://*.blinkit.com    # type: wildcard # max: none
- out:  All merchant & partners endpoints     # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $469,668

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
