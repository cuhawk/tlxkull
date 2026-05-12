# Vueling

> Platform: HackerOne — https://hackerone.com/vueling_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 88% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2025-10-06

## Scope

- in:  *.vueling.com    # type: wildcard # max: critical # not eligible for bounty
- in:  apimobile.vueling.com    # type: api # max: critical # not eligible for bounty
- in:  http://m.vueling.com    # type: url # max: critical # not eligible for bounty
- in:  http://tickets.vueling.com    # type: url # max: critical # not eligible for bounty
- in:  ams.vueling.com    # type: api # max: critical # not eligible for bounty
- in:  http://apimobile.vueling.com    # type: url # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
