# Myndr

> Platform: HackerOne — https://hackerone.com/myndr
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2020-03-21

## Scope

- in:  *.myndr.net    # type: wildcard # max: critical # not eligible for bounty
- in:  *.myndr.nl    # type: wildcard # max: none # not eligible for bounty
- in:  www.myndr.nl    # type: url # max: medium # not eligible for bounty
- in:  osd.myndr.nl    # type: url # max: critical # not eligible for bounty
- in:  bibliotheek.myndr.nl    # type: url # max: medium # not eligible for bounty
- out:  mqtt.myndr.net    # type: url # max: none
- out:  forum.myndr.nl    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
