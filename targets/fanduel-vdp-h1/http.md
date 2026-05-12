# FanDuel Response

> Platform: HackerOne — https://hackerone.com/fanduel-vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 67% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  *.fdbox.net    # type: wildcard # max: critical # not eligible for bounty
- in:  support.fanduel.com    # type: url # max: critical # not eligible for bounty
- in:  *.racing-staging.fanduel.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.dev.us.fdbox.net    # type: wildcard # max: critical # not eligible for bounty
- in:  *.perftest.fdbox.net    # type: wildcard # max: critical # not eligible for bounty
- in:  *.perftest.aw.fdbox.net    # type: wildcard # max: critical # not eligible for bounty
- in:  *.pdx.tvg.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.canada.fanduel.com    # type: wildcard # max: critical # not eligible for bounty
- in:  live.fanduel.com    # type: url # max: critical # not eligible for bounty
- in:  connect.fanduel.com    # type: url # max: critical # not eligible for bounty
- in:  fanduel.design    # type: url # max: medium # not eligible for bounty
- out:  affiliates.fanduel.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
