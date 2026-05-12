# BlackRock

> Platform: HackerOne — https://hackerone.com/blackrock
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 86% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2025-12-08

## Scope

- in:  *.blackrock.com    # type: url # max: critical # not eligible for bounty
- in:  *.ishares.com    # type: url # max: high # not eligible for bounty
- in:  *.isharesonline.com    # type: other # max: critical # not eligible for bounty
- in:  69.52.0.0/16    # type: cidr # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
