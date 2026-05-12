# WellHive

> Platform: HackerOne — https://hackerone.com/wellhive
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 83% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2024-05-15

## Scope

- in:  analytics.wellhive.com    # type: url # max: critical # not eligible for bounty
- in:  app.wellhive.com    # type: url # max: critical # not eligible for bounty
- in:  login.wellhive.com    # type: url # max: critical # not eligible for bounty
- in:  corporate-okta.wellhive.com    # type: url # max: critical # not eligible for bounty
- in:  wellhivecorporate.okta.com    # type: url # max: critical # not eligible for bounty
- out:  www.wellhive.com    # type: url # max: none
- out:  wellhive.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
