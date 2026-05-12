# Matomo

> Platform: HackerOne — https://hackerone.com/matomo
> Type: BBP
> Bounty: Low $333 | Medium $777 | High $1,777 | Critical $13,000
> Avg bounty: $333–$333
> Response efficiency: 99% | Avg first response: N/A | Total paid: $118,843
> Last scope update: 2026-01-13

## Scope

- in:  matomo.cloud    # type: url # max: critical
- in:  https://github.com/matomo-org/docker    # type: url # max: critical
- in:  https://github.com/matomo-org/matomo    # type: repo # max: critical
- in:  https://plugins.matomo.org/developer/matomo-org    # type: repo # max: critical
- in:  https://plugins.matomo.org/developer/innocraft    # type: repo # max: critical
- in:  https://github.com/matomo-org    # type: repo # max: high
- in:  https://github.com/innocraft/    # type: repo # max: high
- in:  org.piwik.mobile2    # type: android_app # max: medium # not eligible for bounty
- in:  737216887    # type: ios_app # max: medium # not eligible for bounty
- out:  api.matomo.org    # type: url # max: none
- out:  matomo.org    # type: url # max: none
- out:  forum.matomo.org    # type: url # max: none
- out:  shop.matomo.org    # type: url # max: none
- out:  plugins.matomo.org    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $118,843

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
