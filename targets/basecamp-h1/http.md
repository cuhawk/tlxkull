# Basecamp

> Platform: HackerOne — https://hackerone.com/basecamp
> Type: BBP
> Bounty: Low $249 | Medium $999 | High $4,999 | Critical $10,000
> Avg bounty: $210–$250
> Response efficiency: 100% | Avg first response: N/A | Total paid: $397,191
> Last scope update: 2026-03-17

## Scope

- in:  HEY.exe    # type: windows_app_store_app_id # max: critical
- in:  *.hey.com    # type: wildcard # max: critical
- in:  3.basecamp.com    # type: url # max: critical
- in:  launchpad.37signals.com    # type: url # max: critical
- in:  world.hey.com    # type: url # max: critical
- in:  com.basecamp.bc3    # type: android_app # max: critical
- in:  com.basecamp.hey    # type: android_app # max: critical
- in:  basecamp3.exe    # type: downloadable_executables # max: critical
- in:  Basecamp.app    # type: downloadable_executables # max: critical
- in:  HEY.app    # type: downloadable_executables # max: critical
- in:  hey-mail    # type: downloadable_executables # max: critical
- in:  com.basecamp.bc3-ios    # type: ios_app # max: critical
- in:  com.hey.app.ios    # type: ios_app # max: critical
- in:  fizzy.do    # type: url # max: critical # not eligible for bounty
- in:  https://github.com/basecamp/writebook    # type: repo # max: high # not eligible for bounty
- in:  https://github.com/basecamp/once-campfire    # type: repo # max: high # not eligible for bounty
- in:  ONCE: Campfire    # type: repo # max: high # not eligible for bounty
- in:  https://github.com/basecamp/fizzy    # type: repo # max: high # not eligible for bounty
- in:  hey.com    # type: url # max: critical
- out:  *.basecamphq.com    # type: wildcard # max: none
- out:  *.highrisehq.com    # type: wildcard # max: none
- out:  basecamp.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $397,191

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
