# Blue Apron (Wonder Group) VDP

> Platform: HackerOne — https://hackerone.com/wonder-vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 75% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2026-03-31

## Scope

- in:  https://*.wonder.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.grubhub.com    # type: wildcard # max: high # not eligible for bounty
- in:  *.seamless.com    # type: wildcard # max: high # not eligible for bounty
- in:  *.tapingo.com    # type: wildcard # max: high # not eligible for bounty
- in:  *.jo30.com    # type: wildcard # max: high # not eligible for bounty
- in:  *.tastemade.com    # type: wildcard # max: high # not eligible for bounty
- in:  https://blog.blueapron.com/    # type: url # max: critical # not eligible for bounty
- in:  www.blueapron.com    # type: url # max: critical # not eligible for bounty
- in:  http://www.blueapron.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  https://order.wonder.com    # type: url # max: critical # not eligible for bounty
- in:  http://www.blueapron.com/api    # type: url # max: critical # not eligible for bounty
- in:  auth.grubhub.com    # type: url # max: critical # not eligible for bounty
- in:  tastemade.com    # type: url # max: critical # not eligible for bounty
- in:  https://core-api.production.claim.co    # type: url # max: critical # not eligible for bounty
- in:  https://cs-dashboard.production.claim.co/graphql    # type: url # max: critical # not eligible for bounty
- in:  https://cs-dashboard.staging.claim.co/graphql    # type: url # max: critical # not eligible for bounty
- in:  https://core-api.staging.claim.co    # type: url # max: critical # not eligible for bounty
- in:  www.grubhub.com    # type: url # max: high # not eligible for bounty
- in:  www.menupages.com    # type: url # max: high # not eligible for bounty
- in:  www.seamless.com    # type: url # max: high # not eligible for bounty
- in:  www.tapingo.com    # type: url # max: high # not eligible for bounty
- in:  www.jo30.com    # type: url # max: high # not eligible for bounty
- in:  restaurant.grubhub.com    # type: url # max: high # not eligible for bounty
- in:  sensor.grubhub.com    # type: url # max: high # not eligible for bounty
- in:  com.blueapron.blueapron.release    # type: android_app # max: critical # not eligible for bounty
- in:  com.grubhub.android    # type: android_app # max: critical # not eligible for bounty
- in:  com.tastemade.app    # type: android_app # max: critical # not eligible for bounty
- in:  976642810    # type: ios_app # max: critical # not eligible for bounty
- in:  302920553    # type: ios_app # max: critical # not eligible for bounty
- in:  971197898    # type: ios_app # max: critical # not eligible for bounty
- in:  api-merchant-gtm.grubhub.com     # type: api # max: high # not eligible for bounty
- in:  wonder.com    # type: url # max: critical # not eligible for bounty
- out:  http://support.wonder.com    # type: url # max: none
- out:  support.blueapron.com    # type: url # max: none
- out:  support.grubhub.com    # type: url # max: none
- out:  support.seamless.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
