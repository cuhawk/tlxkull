# Flexport VDP

> Platform: HackerOne — https://hackerone.com/flexport_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 93% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-06-09

## Scope

- in:  *.flexport.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.transmissionapp.com    # type: wildcard # max: critical # not eligible for bounty
- out:  http://www.flexport.com/blog    # type: url # max: none
- out:  http://www.flexport.com/careers    # type: url # max: none
- out:  apidocs.flexport.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
