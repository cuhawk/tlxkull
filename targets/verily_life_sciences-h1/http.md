# Verily Life Sciences

> Platform: HackerOne — https://hackerone.com/verily_life_sciences
> Type: BBP
> Bounty: Low $500 | Medium $1,500 | High $5,000 | Critical $10,000
> Avg bounty: $100–$150
> Response efficiency: 88% | Avg first response: N/A | Total paid: $58,149
> Last scope update: 2026-01-02

## Scope

- in:  https://*.verily.com/    # type: wildcard # max: critical
- in:  https://*.signalpath.com/    # type: wildcard # max: critical
- in:  https://*.verilyme.com/    # type: wildcard # max: critical
- in:  https://*.projectbaseline.com/    # type: wildcard # max: low
- in:  https://play.google.com/store/apps/details?id=com.verily.me    # type: android_app # max: critical
- in:  https://apps.apple.com/us/app/verily-me/id6448808133    # type: ios_app # max: critical
- in:  granularinsurance.com    # type: url # max: high
- in:  com.verily.me    # type: android_app # max: critical
- out:  https://*.onduo.com/    # type: wildcard # max: none
- out:  onduo.com    # type: url # max: none
- out:  com.google.android.apps.diabetes    # type: android_app # max: none
- out:  https://play.google.com/store/apps/details?id=com.google.android.apps.diabetes    # type: android_app # max: none
- out:  https://apps.apple.com/us/app/onduo/id1138490045    # type: ios_app # max: none
- out:  https://*.granularinsurance.com/    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $58,149
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
