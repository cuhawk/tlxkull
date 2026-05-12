# eero

> Platform: HackerOne — https://hackerone.com/eero
> Type: BBP
> Bounty: Low $200–$500 | Medium $600–$4,000 | High $6,000–$8,000 | Critical $25,000–$30,000
> Avg bounty: $200–$200
> Response efficiency: 97% | Avg first response: N/A | Total paid: $26,300
> Last scope update: 2025-11-11

## Scope

- in:  *.eero.com    # type: wildcard # max: critical
- in:  *.e2ro.com    # type: wildcard # max: critical
- in:  eero Devices    # type: firmware # max: critical
- in:  com.eero.android    # type: android_app # max: critical
- in:  1023499075    # type: ios_app # max: critical
- in:  https://node.e2ro.com/*    # type: other # max: critical
- in:  https://api-user.e2ro.com/*    # type: other # max: critical
- in:  eero Pro (2nd Generation)    # type: firmware # max: critical
- in:  eero Beacon (2nd Generation)    # type: firmware # max: critical
- in:  eero (2nd Generation)    # type: firmware # max: critical
- in:  eero 6 (3rd Generation)    # type: firmware # max: critical
- in:  eero 6 Extender (3rd Generation)    # type: firmware # max: critical
- in:  eero 6 Pro    # type: firmware # max: critical
- in:  eero 6+ (4th Gen)    # type: firmware # max: critical
- in:  eero 6E Pro (4th Gen)    # type: firmware # max: critical
- out:  Anything not in scope    # type: other # max: none
- out:  Services, Apps, Mobile    # type: other # max: none
- out:  Devices    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $26,300
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
