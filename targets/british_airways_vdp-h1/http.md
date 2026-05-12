# British Airways VDP

> Platform: HackerOne — https://hackerone.com/british_airways_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 98% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  *.britishairways.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ba.com    # type: wildcard # max: critical # not eligible for bounty
- in:  www.britishairways.com    # type: url # max: critical # not eligible for bounty
- in:  http://www.britishairways.com/nx    # type: url # max: critical # not eligible for bounty
- in:  Security vulnerabilities that are identified in digital properties owned, operated, or controlled by British Airways are considered in scope.    # type: other # max: critical # not eligible for bounty
- in:  https://api.pgt.shopping.ba.com/    # type: url # max: critical # not eligible for bounty
- in:  https://www.britishairways.com/travel/btt/execclub/_gf/en_gb    # type: url # max: critical # not eligible for bounty
- in:  https://pgt.shopping.ba.com/    # type: url # max: critical # not eligible for bounty
- in:  onbusiness.britishairways.com    # type: url # max: critical # not eligible for bounty
- in:  checkin.ba.com    # type: url # max: critical # not eligible for bounty
- in:  www.ba.com    # type: url # max: critical # not eligible for bounty
- in:  https://www.britishairways.com/nx/*    # type: wildcard # max: critical # not eligible for bounty
- out:  accounts.britishairways.com    # type: url # max: none
- out:  holiday.britishairways.com    # type: url # max: none
- out:  Testing is not permitted on internal systems, employee portals, onboard aircraft systems, third-party services, or any assets using external networks or domains not directly owned or controlled by British Airways    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
