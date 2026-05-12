# 3CX

> Platform: HackerOne — https://hackerone.com/3cx
> Type: BBP
> Bounty: Low $350 | Medium $1,150 | High $2,300 | Critical $3,500
> Avg bounty: $200–$350
> Response efficiency: 94% | Avg first response: N/A | Total paid: $34,799
> Last scope update: 2025-05-28

## Scope

- in:  https://apps.microsoft.com/detail/3cx/9NW77489NGJ0    # type: windows_app_store_app_id # max: critical
- in:  https://portal.3cx.com    # type: url # max: critical
- in:  3CX Phone System    # type: other # max: critical
- in:  3CX Live chat WordPress plugin    # type: other # max: medium
- in:  https://play.google.com/store/apps/details?id=com.tcx.sipphone14    # type: android_app # max: critical
- in:  3CX SBC    # type: downloadable_executables # max: critical
- in:  https://apps.apple.com/us/app/3cx/id992045982    # type: ios_app # max: critical
- in:  Other    # type: other # max: none # not eligible for bounty
- in:  com.tcx.sipphone14    # type: android_app # max: medium
- in:  id992045982    # type: ios_app # max: high
- out:  *.3cx.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $34,799
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
