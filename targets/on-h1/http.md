# On 

> Platform: HackerOne — https://hackerone.com/on
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2021-03-30

## Scope

- in:  *.on-running.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.on.com    # type: wildcard # max: critical # not eligible for bounty
- in:  on.com    # type: url # max: critical # not eligible for bounty
- in:  on-app-backend.on-running.com    # type: url # max: high # not eligible for bounty
- in:  on-app-backend.on.com    # type: url # max: high # not eligible for bounty
- out:  https://shz64n.on-running.com/    # type: url # max: none
- out:  onward.on-running.com    # type: url # max: none
- out:  onward.on.com    # type: url # max: none
- out:  partners.on-running.com    # type: url # max: none
- out:  partners.on.com    # type: url # max: none
- out:  shz64n.on.com/    # type: url # max: none
- out:  events.on-running.com    # type: url # max: none
- out:  events.on.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
