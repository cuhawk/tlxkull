# Palo Alto Software

> Platform: HackerOne — https://hackerone.com/palo_alto_software
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 86% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-09-29

## Scope

- in:  app.liveplan.com    # type: url # max: critical # not eligible for bounty
- in:  www.paloalto.com    # type: url # max: medium # not eligible for bounty
- in:  www.liveplan.com    # type: url # max: medium # not eligible for bounty
- in:  www.bplans.com    # type: url # max: low # not eligible for bounty
- out:  app.outpost.co    # type: url # max: none
- out:  api.outpost.co    # type: url # max: none
- out:  www.outpost.co    # type: url # max: none
- out:  www.teamoutpost.com    # type: url # max: none
- out:  www.mplans.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
