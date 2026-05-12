# Starling Bank VDP

> Platform: HackerOne — https://hackerone.com/starling_bank
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2019-09-30

## Scope

- in:  app.starlingbank.com    # type: url # max: critical # not eligible for bounty
- in:  oauth.starlingbank.com    # type: url # max: critical # not eligible for bounty
- in:  help.starlingbank.com    # type: url # max: critical # not eligible for bounty
- in:  developer.starlingbank.com    # type: url # max: critical # not eligible for bounty
- in:  api.starlingbank.com    # type: url # max: critical # not eligible for bounty
- in:  token-api.starlingbank.com    # type: url # max: critical # not eligible for bounty
- in:  openbanking.starlingbank.com    # type: url # max: critical # not eligible for bounty
- in:  api-openbanking.starlingbank.com    # type: url # max: critical # not eligible for bounty
- in:  payment-api.starlingbank.com    # type: url # max: critical # not eligible for bounty
- in:  www.starlingbank.com    # type: url # max: medium # not eligible for bounty
- in:  com.starlingbank.android    # type: android_app # max: critical # not eligible for bounty
- in:  uk.co.starlingbank.Starling    # type: ios_app # max: critical # not eligible for bounty
- in:  developer.starlingbank.com    # type: url # max: medium # not eligible for bounty
- in:  developer-sandbox.starlingbank.com    # type: url # max: medium # not eligible for bounty
- in:  demo.starlingbank.com    # type: url # max: medium # not eligible for bounty
- in:  redash.starlingbank.com    # type: url # max: medium # not eligible for bounty
- in:  foo.starlingbank.com    # type: url # max: medium # not eligible for bounty
- in:  demo-api.possiblefs.com    # type: url # max: high # not eligible for bounty
- in:  falcon.starlingbank.com    # type: url # max: high # not eligible for bounty
- out:  prod-alertmanager.jn3cx6xo36.net    # type: url # max: none
- out:  oauth.starlingbank.com    # type: url # max: none
- out:  demo-oauth.possiblefs.com    # type: url # max: none
- out:  dw0341p8zbsxi.cloudfront.net    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
