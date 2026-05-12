# Hotmart (VDP)

> Platform: HackerOne — https://hackerone.com/hotmartvdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 86% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  *.buildstaging.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.kpages.com.br    # type: wildcard # max: high # not eligible for bounty
- in:  https://hotmart.com    # type: url # max: critical # not eligible for bounty
- in:  https://teachable.com    # type: url # max: critical # not eligible for bounty
- out:  *.hotmart.com    # type: wildcard # max: none
- out:  *.teachable.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
