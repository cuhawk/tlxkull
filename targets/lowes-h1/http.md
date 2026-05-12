# Lowe's Companies VDP

> Platform: HackerOne — https://hackerone.com/lowes
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 85% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  lowes.com    # type: url # max: critical # not eligible for bounty
- in:  https://uat.lpsdxp.com/    # type: url # max: critical # not eligible for bounty
- in:  https://talent.lowes.com/    # type: url # max: critical # not eligible for bounty
- in:  https://www.lowes.co.in/    # type: url # max: critical # not eligible for bounty
- in:  https://corporate.lowes.com/    # type: url # max: critical # not eligible for bounty
- in:  com.lowes.LowesStoreTestFlight    # type: testflight # max: critical # not eligible for bounty
- in:  com.LowesAndroid    # type: android_app # max: critical # not eligible for bounty
- in:  com.lowes.LowesStore    # type: ios_app # max: critical # not eligible for bounty
- out:  www.lowesprosupply.com/    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
