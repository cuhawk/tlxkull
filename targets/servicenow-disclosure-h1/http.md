# ServiceNow Disclosure

> Platform: HackerOne — https://hackerone.com/servicenow-disclosure
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 91% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2021-09-27

## Scope

- in:  *.lightstep.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.servicenow.com    # type: url # max: critical # not eligible for bounty
- in:  *.service-now.com    # type: url # max: critical # not eligible for bounty
- in:  lightstep.com    # type: url # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
