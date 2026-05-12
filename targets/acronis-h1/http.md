# Acronis

> Platform: HackerOne — https://hackerone.com/acronis
> Type: BBP
> Bounty: Low $1,000 | Medium $2,000 | High $3,500 | Critical $10,000
> Avg bounty: $200–$250
> Response efficiency: 64% | Avg first response: N/A | Total paid: $520,324
> Last scope update: 2026-05-01

## Scope

- in:  *-api-*.acronis.com    # type: wildcard # max: critical
- in:  *.acronis.com    # type: wildcard # max: critical
- in:  *.5nine.com    # type: wildcard # max: critical
- in:  *.devicelock.com    # type: wildcard # max: critical
- in:  *.acronis.work    # type: wildcard # max: critical
- in:  beta-cloud.acronis.com    # type: url # max: critical
- in:  account.acronis.com    # type: url # max: critical
- in:  Acronis Cyber Infrastructure    # type: other # max: critical
- in:  Other Acronis Domains    # type: other # max: medium
- in:  com.acronis.acronistrueimage    # type: android_app # max: critical
- in:  com.acronis.abc    # type: android_app # max: critical
- in:  Acronis Agent    # type: downloadable_executables # max: critical
- in:  Acronis Cyber Protect    # type: downloadable_executables # max: critical
- in:  Acronis DeviceLock DLP    # type: downloadable_executables # max: critical
- in:  Acronis Snap Deploy    # type: downloadable_executables # max: critical
- in:  Other Acronis executables    # type: downloadable_executables # max: critical
- in:  Acronis Cloud Manager    # type: downloadable_executables # max: critical
- in:  Acronis True Image (formerly Acronis Cyber Protect Home Office)    # type: downloadable_executables # max: critical
- in:  1118448159    # type: ios_app # max: critical
- in:  978342143    # type: ios_app # max: critical
- in:  1192506963    # type: ios_app # max: critical
- in:  Acronis Cyber Files    # type: downloadable_executables # max: critical
- in:  429704844    # type: ios_app # max: critical
- in:  Acronis Cyber Protect Home Office (formerly Acronis True Image)    # type: downloadable_executables # max: critical
- in:  Mobile applications    # type: other # max: medium
- in:  *.acronis.com    # type: url # max: high
- out:  learn.acronis.com    # type: url # max: none
- out:  training.acronis.com    # type: url # max: none
- out:  199.193.158.0/23, 199.193.156.0/24    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $520,324

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
