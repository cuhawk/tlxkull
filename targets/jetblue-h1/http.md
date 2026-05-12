# JetBlue

> Platform: HackerOne — https://hackerone.com/jetblue
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 86% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-01-21

## Scope

- in:  *.jetblue.com    # type: wildcard # max: critical # not eligible for bounty
- in:  www.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  book.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  checkin.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  mobile.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  movil.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  api.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  accounts.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  help.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  azrest.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  magnolia.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  experience.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  paisly.jetblue.com    # type: url # max: critical # not eligible for bounty
- in:  api.paisly.jetblue.com    # type: url # max: critical # not eligible for bounty
- out:  bluesky.cl    # type: url # max: none
- out:  www.bluesky.cl    # type: url # max: none
- out:  interstitials.travelproducts.jetblue.com    # type: url # max: none
- out:  irisimagegenprd.travelproducts.jetblue.com    # type: url # max: none
- out:  oe.travelproducts.jetblue.com    # type: url # max: none
- out:  prod.travelproducts.jetblue.com    # type: url # max: none
- out:  travelproducts.jetblue.com    # type: url # max: none
- out:  jbdealsfeed-stgnew.jetblue.com    # type: url # max: none
- out:  Vendor/Partner    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
