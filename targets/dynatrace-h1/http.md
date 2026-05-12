# Dynatrace

> Platform: HackerOne — https://hackerone.com/dynatrace
> Type: BBP
> Bounty: Low $100–$250 | Medium $250–$750 | High $500–$2,500 | Critical $1,500–$5,000
> Avg bounty: $250–$250
> Response efficiency: 96% | Avg first response: N/A | Total paid: $176,900
> Last scope update: 2026-04-24

## Scope

- in:  *.sprint.dynatracelabs.com    # type: wildcard # max: critical
- in:  *.sprint.apps.dynatracelabs.com    # type: wildcard # max: critical
- in:  account-sprint.dynatracelabs.com    # type: url # max: critical
- in:  sso-sprint.dynatracelabs.com    # type: url # max: critical
- in:  myaccount-hardening.dynatracelabs.com    # type: url # max: critical
- in:  https://github.com/Dynatrace    # type: repo # max: critical
- in:  All other Assets    # type: other # max: critical
- in:  Core Assets    # type: other # max: critical
- in:  Dynatrace OneAgent    # type: downloadable_executables # max: critical
- in:  Dynatrace ActiveGate    # type: downloadable_executables # max: critical
- in:  Dynatrace MobileAgent    # type: downloadable_executables # max: critical
- in:  https://github.com/keptn    # type: repo # max: critical
- in:  Tier 2    # type: other # max: critical
- in:  Dynatrace Synthetic    # type: other # max: critical
- in:  https://github.com/keptn    # type: url # max: critical
- out:  *.dynatrace.com    # type: wildcard # max: none
- out:  *.dev.dynatracelabs.com    # type: wildcard # max: none
- out:  university-staging.dynatracelabs.com    # type: url # max: none
- out:  easyTravel demo application    # type: downloadable_executables # max: none
- out:  EasyTrade demo application    # type: downloadable_executables # max: none
- out:  https://github.com/Dynatrace-oss-contrib    # type: repo # max: none
- out:  https://github.com/Dynatrace-innovationlab    # type: repo # max: none
- out:  *.live.dynatrace.com    # type: wildcard # max: none
- out:  help.dynatrace.com    # type: url # max: none
- out:  answers.dynatrace.com    # type: url # max: none
- out:  login.dynatrace.com    # type: url # max: none
- out:  www.dynatrace.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $176,900
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
