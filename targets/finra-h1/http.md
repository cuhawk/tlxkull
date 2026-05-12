# FINRA Response

> Platform: HackerOne — https://hackerone.com/finra
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2020-07-15

## Scope

- in:  *.finra.org    # type: wildcard # max: critical # not eligible for bounty
- in:  https://ews.qa.finra.org/*    # type: wildcard # max: critical # not eligible for bounty
- out:  https://ews.finra.org/*    # type: wildcard # max: none
- out:  *.fip.finra.org    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
