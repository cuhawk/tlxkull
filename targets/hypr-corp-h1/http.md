# HYPR

> Platform: HackerOne — https://hackerone.com/hypr-corp
> Type: BBP
> Bounty: Low $300–$500 | Medium $750 | High $2,000–$2,500 | Critical $4,000–$5,000
> Avg bounty: $250–$250
> Response efficiency: 100% | Avg first response: N/A | Total paid: $72,475
> Last scope update: 2022-12-12

## Scope

- in:  *.hypr.com    # type: wildcard # max: critical
- in:  *.gethypr.com    # type: wildcard # max: critical
- in:  com.hypr.one    # type: android_app # max: critical
- in:  HyprUnlock.exe    # type: downloadable_executables # max: critical
- in:  HYPR Workforce Access.app    # type: downloadable_executables # max: critical
- in:  com.hypr.one    # type: ios_app # max: critical
- in:  pentesting.gethypr.com    # type: url # max: critical
- in:  pentesting3.gethypr.com    # type: url # max: critical
- in:  pentesting2.gethypr.com    # type: url # max: critical
- in:  hypr74352.gethypr.com    # type: url # max: critical
- in:  hypr37448.gethypr.com    # type: url # max: critical
- in:  hypr97507.gethypr.com,    # type: url # max: critical
- in:  https://hypr.app.box.com/file/743095899517?s=bpd445lnbfhyxmkelo4lb5iqj5a0v0re    # type: repo # max: critical
- out:  support.hypr.com    # type: url # max: none
- out:  help.hypr.com    # type: url # max: none
- out:  partners.hypr.com    # type: url # max: none
- out:   All Other Assets    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $72,475

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
