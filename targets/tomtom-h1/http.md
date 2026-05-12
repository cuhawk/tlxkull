# TomTom

> Platform: HackerOne — https://hackerone.com/tomtom
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 91% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  *.tomtom-global.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tomtom.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tomtomgroup.com    # type: wildcard # max: critical # not eligible for bounty
- in:  https://github.com/tomtom-international/*    # type: repo # max: critical # not eligible for bounty
- in:  com.tomtom.gplay.navapp    # type: android_app # max: critical # not eligible for bounty
- in:  com.tomtom.speedcams.android.map    # type: android_app # max: critical # not eligible for bounty
- in:  api.tomtom.com    # type: url # max: critical # not eligible for bounty
- in:  *.business.tomtom.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.teleatlas.com    # type: wildcard # max: critical # not eligible for bounty
- out:  *.telematics.tomtom.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
