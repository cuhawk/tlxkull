# Prudential Financial

> Platform: HackerOne — https://hackerone.com/prudential-financial
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 93% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-07-14

## Scope

- in:  *.prudential.com    # type: url # max: critical # not eligible for bounty
- in:  Prudential Assets    # type: other # max: critical # not eligible for bounty
- out:  *.pramericalife.in    # type: wildcard # max: none
- out:  *.prudentialagf.cl    # type: wildcard # max: none
- out:  *.prudentialplc.com    # type: url # max: none
- out:  *.prudential.co.kr    # type: url # max: none
- out:  pramericalife.in    # type: url # max: none
- out:  prudentialagf.cl    # type: url # max: none
- out:  afphabitat.cl    # type: url # max: none
- out:  Prudential Joint Ventures    # type: other # max: none
- out:  afphabitat.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
