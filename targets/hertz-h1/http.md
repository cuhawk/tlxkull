# Hertz VDP

> Platform: HackerOne — https://hackerone.com/hertz
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 89% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  *.hertz.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *hertz.io    # type: wildcard # max: critical # not eligible for bounty
- in:  http://auth.hertz.com    # type: url # max: critical # not eligible for bounty
- in:  hertz.com    # type: url # max: critical # not eligible for bounty
- in:  http://www.c2c-prod.hertz.com    # type: url # max: critical # not eligible for bounty
- in:  http://www.hertz.com/rentacar/member/authentication    # type: url # max: critical # not eligible for bounty
- in:  https://auth.hertz.com    # type: url # max: critical # not eligible for bounty
- in:  https://www.c2c-prod.hertz.com/    # type: url # max: critical # not eligible for bounty
- in:  https://www.hertz.com/rentacar/member/authentication    # type: url # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
