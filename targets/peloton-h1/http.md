# Peloton

> Platform: HackerOne — https://hackerone.com/peloton
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2024-08-06

## Scope

- in:  cms.onepeloton.com    # type: url # max: critical # not eligible for bounty
- in:  cosmos.onepeloton.com    # type: url # max: critical # not eligible for bounty
- in:  www.onepeloton.com    # type: url # max: critical # not eligible for bounty
- in:  cosmos-stage.onepeloton.com    # type: url # max: high # not eligible for bounty
- in:  qa1-cms.onepeloton.com    # type: url # max: high # not eligible for bounty
- in:  auth-test.onepeloton.com    # type: url # max: high # not eligible for bounty
- in:  auth.onepeloton.com    # type: api # max: critical # not eligible for bounty
- in:  auth-stage.onepeloton.com     # type: api # max: high # not eligible for bounty
- in:  auth-orca.onepeloton.com     # type: api # max: critical # not eligible for bounty
- in:  auth2.onepeloton.com    # type: api # max: critical # not eligible for bounty
- in:  auth2-stage.onepeloton.com    # type: api # max: high # not eligible for bounty
- out:  Security vulnerabilities that are identified in Peloton products or in website domains owned, operated, or controlled by Peloton that are not listed above are OOS    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
