# Brightspeed

> Platform: HackerOne — https://hackerone.com/brightspeed
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  *.brightspeed.com    # type: wildcard # max: critical # not eligible for bounty
- in:  brightspeed.com    # type: url # max: critical # not eligible for bounty
- in:  brightspeed.service-now.com    # type: url # max: critical # not eligible for bounty
- in:  brightspeedtsm.service-now.com    # type: url # max: critical # not eligible for bounty
- in:  gobrightspeed.net    # type: url # max: critical # not eligible for bounty
- out:  *dhcp*.gobrightspeed.net    # type: wildcard # max: none
- out:  dhcp.embarqhsd.net    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
