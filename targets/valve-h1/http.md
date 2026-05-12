# Valve

> Platform: HackerOne — https://hackerone.com/valve
> Type: BBP
> Bounty: Low $200 | Medium $750 | High $2,500 | Critical $7,500
> Avg bounty: $750–$750
> Response efficiency: 76% | Avg first response: N/A | Total paid: $2,753,750
> Last scope update: 2026-05-05

## Scope

- in:  *.steamstatic.com    # type: wildcard # max: critical
- in:  www.dota2.com    # type: url # max: critical
- in:  support.steampowered.com    # type: url # max: critical
- in:  partner.steampowered.com    # type: url # max: critical
- in:  store.steampowered.com    # type: url # max: critical
- in:  www.valvesoftware.com    # type: url # max: critical
- in:  api.steampowered.com    # type: url # max: critical
- in:  partner.steamgames.com    # type: url # max: critical
- in:  steamcommunity.com    # type: url # max: critical
- in:  www.teamfortress.com    # type: url # max: critical
- in:  www.counter-strike.net    # type: url # max: critical
- in:  playartifact.com    # type: url # max: critical
- in:  help.steampowered.com    # type: url # max: critical
- in:  developer.valvesoftware.com    # type: url # max: low
- in:  Steam Servers    # type: other # max: critical
- in:  Steam Client    # type: other # max: critical
- in:  com.valvesoftware.Steam    # type: android_app # max: critical
- in:  com.valvesoftware.Steam    # type: ios_app # max: critical
- in:  storefront.steampowered.com    # type: url # max: critical # not eligible for bounty
- in:  wiki.teamfortress.com    # type: url # max: critical # not eligible for bounty
- in:  https://github.com/valvesoftware    # type: repo # max: critical # not eligible for bounty
- in:  steam.exe    # type: downloadable_executables # max: critical
- in:  csgo.exe    # type: downloadable_executables # max: critical
- in:  dota2.exe    # type: downloadable_executables # max: critical
- in:  tf2.exe    # type: downloadable_executables # max: critical
- in:  hl.exe    # type: downloadable_executables # max: critical
- in:  *.exe    # type: downloadable_executables # max: critical
- out:  valvestore.forfansbyfans.com,store.valvesoftware.com    # type: url # max: none
- out:  www.steampowered.com    # type: url # max: none
- out:  translation.steampowered.com    # type: url # max: none
- out:  www.steamgames.com    # type: url # max: none
- out:  list.valvesoftware.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $2,753,750
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
