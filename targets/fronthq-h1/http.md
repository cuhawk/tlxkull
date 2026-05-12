# Front

> Platform: HackerOne — https://hackerone.com/fronthq
> Type: BBP
> Bounty: Low $200 | Medium $500 | High $5,000 | Critical $10,000
> Avg bounty: $150–$200
> Response efficiency: 77% | Avg first response: N/A | Total paid: $117,508
> Last scope update: 2024-03-13

## Scope

- in:  app.frontapp.com    # type: url # max: critical
- in:  api2.frontapp.com    # type: url # max: critical
- in:  com.frontapp.mobile    # type: android_app # max: high
- in:  Front for Mac    # type: downloadable_executables # max: high
- in:  Front for Windows    # type: downloadable_executables # max: high
- in:  com.frontapp.mobile    # type: ios_app # max: high
- in:  http://help.front.com    # type: url # max: critical
- in:  *.front.com    # type: wildcard # max: high
- out:  community.front.com    # type: url # max: none
- out:  http://onboarding.front.com    # type: url # max: none
- out:  frontapp.com    # type: url # max: none
- out:  chat-identity.frontapp.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $117,508
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
