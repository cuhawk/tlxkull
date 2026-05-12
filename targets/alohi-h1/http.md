# Alohi

> Platform: HackerOne — https://hackerone.com/alohi
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-06-03

## Scope

- in:  *.sign.plus    # type: wildcard # max: critical # not eligible for bounty
- in:  *.fax.plus    # type: wildcard # max: critical # not eligible for bounty
- in:  www.alohi.com    # type: url # max: critical # not eligible for bounty
- in:  FAX Programmable API    # type: other # max: critical # not eligible for bounty
- in:  plus.fax.android    # type: android_app # max: critical # not eligible for bounty
- in:  plus.sign.android    # type: android_app # max: critical # not eligible for bounty
- in:  plus.scan.android    # type: android_app # max: critical # not eligible for bounty
- in:  plus.scan.ScanPlus    # type: ios_app # max: critical # not eligible for bounty
- in:  plus.sign.SignPlus    # type: ios_app # max: critical # not eligible for bounty
- in:  plus.fax.FaxPlus    # type: ios_app # max: critical # not eligible for bounty
- in:  1170782544    # type: ios_app # max: critical # not eligible for bounty
- in:  1478723637    # type: ios_app # max: critical # not eligible for bounty
- in:  www.sign.plus    # type: url # max: critical # not eligible for bounty
- in:  www.fax.plus    # type: url # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
