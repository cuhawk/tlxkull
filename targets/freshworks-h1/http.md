# Freshworks 

> Platform: HackerOne — https://hackerone.com/freshworks
> Type: BBP
> Bounty: Low $100 | Medium $250–$300 | High $500–$1,000 | Critical $1,000–$2,500
> Avg bounty: $100–$100
> Response efficiency: 88% | Avg first response: N/A | Total paid: $236,399
> Last scope update: 2026-05-01

## Scope

- in:  yourdomain.freshdesk.com    # type: url # max: critical
- in:  yourdomain.freshservice.com    # type: url # max: critical
- in:  yourdomain.freshchat.com    # type: url # max: critical
- in:  yourdomain.freshcaller.com    # type: url # max: critical
- in:  yourdomain.myfreshworks.com    # type: url # max: critical
- in:  yourdomain.freshrelease.com    # type: url # max: critical
- in:  Freshservice Discovery Agent and Probe    # type: other # max: critical
- in:  com.freshservice.helpdesk    # type: android_app # max: critical
- in:  com.freshdesk.helpdesk    # type: android_app # max: critical
- in:  com.freshchat.agent.android    # type: android_app # max: critical
- in:  com.freshworks.freshcaller    # type: android_app # max: critical
- in:  com.freshservice.helpdesk.intune    # type: android_app # max: critical
- in:  Freshdesk-iOS-App    # type: ios_app # max: critical
- in:  Freshservice-iOS-App    # type: ios_app # max: critical
- in:  Freshchat-iOS-App    # type: ios_app # max: critical
- in:  Freshcaller-iOS-App    # type: ios_app # max: critical
- in:  Freshservice-Intune-iOS-App    # type: ios_app # max: critical
- in:  Freshserive-Intune-iOS-App    # type: ios_app # max: critical
- in:  http://yourdomain.myfreshworks.com/crm    # type: url # max: critical
- out:  wchat.freshchat.com    # type: url # max: none
- out:  www.freshworks.com    # type: url # max: none
- out:  freshworks.atlassian.net    # type: url # max: none
- out:  yourdomain.freshsurvey.io    # type: url # max: none
- out:  yourdomain.freshstatus.io    # type: url # max: none
- out:  yourdomain.freshping.io    # type: url # max: none
- out:  http://yourdomain.myfreshworks.com/crm/sales    # type: url # max: none
- out:  http://yourdomain.myfreshworks.com/crm/marketer    # type: url # max: none
- out:  com.freshdesk.freshsales.mobile    # type: android_app # max: none
- out:  Freshsales-iOS-App    # type: ios_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $236,399

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
