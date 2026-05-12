# Weblate

> Platform: HackerOne — https://hackerone.com/weblate
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 82% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2019-09-04

## Scope

- in:  hosted.weblate.org    # type: url # max: critical # not eligible for bounty
- in:  https://github.com/WeblateOrg/weblate    # type: repo # max: critical # not eligible for bounty
- in:  https://github.com/WeblateOrg/wlc    # type: repo # max: critical # not eligible for bounty
- in:  https://github.com/WeblateOrg/docker    # type: repo # max: critical # not eligible for bounty
- in:  https://github.com/WeblateOrg/website    # type: repo # max: critical # not eligible for bounty
- in:  https://github.com/WeblateOrg/translation-finder    # type: repo # max: critical # not eligible for bounty
- out:  hg.weblate.org    # type: url # max: none
- out:  github.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
