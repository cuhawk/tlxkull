# Fastly VDP

> Platform: HackerOne — https://hackerone.com/fastly-vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 82% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-03-01

## Scope

- in:  https://*.fastly.com/    # type: wildcard # max: critical # not eligible for bounty
- in:  *.signalsciences.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.fanout.io    # type: wildcard # max: critical # not eligible for bounty
- in:  manage.fastly.com    # type: url # max: critical # not eligible for bounty
- in:  api.fastly.com    # type: url # max: critical # not eligible for bounty
- in:  docs.fastly.com    # type: url # max: high # not eligible for bounty
- out:  *.fastly.net    # type: wildcard # max: none
- out:  community.fastly.com    # type: url # max: none
- out:  connect.fastly.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
