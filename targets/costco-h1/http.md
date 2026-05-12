# Costco

> Platform: HackerOne — https://hackerone.com/costco
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-06-28

## Scope

- in:  *.costco.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.costco.ca    # type: wildcard # max: critical # not eligible for bounty
- in:  *.costcobusinessdelivery.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.costcobusinesscentre.ca    # type: wildcard # max: critical # not eligible for bounty
- in:  *.costcotravel.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.costcotravel.ca    # type: wildcard # max: critical # not eligible for bounty
- in:  www.costco.ca    # type: url # max: critical # not eligible for bounty
- in:  www.costco.com    # type: url # max: critical # not eligible for bounty
- in:  www.costcobusinesscentre.ca    # type: url # max: critical # not eligible for bounty
- in:  www.costcobusinessdelivery.com    # type: url # max: critical # not eligible for bounty
- in:  www.costcotravel.com    # type: url # max: critical # not eligible for bounty
- in:  www.costcotravel.ca    # type: url # max: critical # not eligible for bounty
- in:  com.costco.app.android    # type: android_app # max: critical # not eligible for bounty
- in:  com.costco.costco    # type: ios_app # max: critical # not eligible for bounty
- in:  535509415    # type: ios_app # max: critical # not eligible for bounty
- out:  signin.costco.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
