# City of Los Angeles

> Platform: HackerOne — https://hackerone.com/city_of_los_angeles_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 71% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-12-06

## Scope

- in:  *.lacity.org    # type: wildcard # max: critical # not eligible for bounty
- in:  *.lacity.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  searchla.lacity.org    # type: url # max: critical # not eligible for bounty
- in:  disclaimer.lacity.org    # type: url # max: critical # not eligible for bounty
- in:  i3-iot.lacity.org    # type: url # max: critical # not eligible for bounty
- in:  myla311.lacity.org    # type: url # max: critical # not eligible for bounty
- in:  dart.lacity.org    # type: url # max: critical # not eligible for bounty
- in:  dpwpay.lacity.org    # type: url # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
