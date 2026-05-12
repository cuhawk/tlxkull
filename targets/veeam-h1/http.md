# Veeam

> Platform: HackerOne — https://hackerone.com/veeam
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 94% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-01-31

## Scope

- in:  *.veeam.com    # type: url # max: critical # not eligible for bounty
- in:  *.kasten.io    # type: url # max: critical # not eligible for bounty
- in:  *.veeamgov.com    # type: url # max: critical # not eligible for bounty
- in:  Product Vulnerabilities    # type: other # max: critical # not eligible for bounty
- in:  Corporate Infrastructure    # type: other # max: critical # not eligible for bounty
- out:  Virtual Chat Assistants    # type: other # max: none
- out:  Customer Support Request Forms    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
