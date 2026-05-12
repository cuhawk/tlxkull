# U.S. Department of State

> Platform: HackerOne — https://hackerone.com/us-department-of-state
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 98% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-01-03

## Scope

- in:  *.AMERICA.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.DEVTESTFAN1.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.FAN.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.FSGB.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.IAWG.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.IBWC.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.OSAC.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.PEPFAR.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.PREPRODFAN.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.SECURITYTESTFAN.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.STATE.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.SUPPORTFAN.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.USCONSULATE.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.USDOSCLOUD.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.USEMBASSY.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.USMISSION.GOV    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ELGUARDIA.NET    # type: wildcard # max: critical # not eligible for bounty
- in:  *.REWARDSFORJUSTICE.NET    # type: wildcard # max: critical # not eligible for bounty
- in:  *.usvisascheduling.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ustraveldocs.com    # type: wildcard # max: critical # not eligible for bounty
- in:  https://*.usvisaappt.com    # type: wildcard # max: critical # not eligible for bounty
- in:  https://ais.usvisa-info.com    # type: url # max: critical # not eligible for bounty
- in:  https://casadmin.peckham.org    # type: url # max: critical # not eligible for bounty
- in:  https://github.com/USStateDept    # type: repo # max: critical # not eligible for bounty
- in:  *.usvisaappt.com    # type: wildcard # max: critical # not eligible for bounty
- in:  usvisaappt.com    # type: url # max: critical # not eligible for bounty
- out:  *.USASEANCONNECT.GOV    # type: wildcard # max: none
- out:  *.FOREIGNASSISTANCE.GOV    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
