# UPS VDP

> Platform: HackerOne — https://hackerone.com/ups
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 80% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2021-04-28

## Scope

- in:  *.ups.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ups-tms.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ups-mi.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.freightex.com    # type: wildcard # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
