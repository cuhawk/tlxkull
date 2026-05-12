# DoorDash

> Platform: HackerOne — https://hackerone.com/doordash
> Type: BBP
> Bounty: Low $100 | Medium $1,000 | High $5,000 | Critical $12,000
> Avg bounty: $724–$741
> Response efficiency: 94% | Avg first response: N/A | Total paid: $36,456
> Last scope update: 2025-10-07

## Scope

- in:  www.doordash.com    # type: url # max: critical
- in:  com.dd.doordash    # type: android_app # max: critical
- in:  doordash.DoorDashConsumer    # type: ios_app # max: critical
- out:  *.dashapi.com    # type: wildcard # max: none
- out:  *.doorcrawl.com    # type: wildcard # max: none
- out:  *.order.online    # type: wildcard # max: none
- out:  doordash.com/unified-gateway/*    # type: wildcard # max: none
- out:  doordash.com/orders/drive/*    # type: wildcard # max: none
- out:  http://help.doordash.com    # type: url # max: none
- out:  careersatdoordash.com    # type: url # max: none
- out:  ir.doordash.com    # type: url # max: none
- out:  unified-gateway.doordash.com    # type: url # max: none
- out:  consumer-mobile-bff.doordash.com    # type: url # max: none
- out:  merchant-mobile-bff.doordash.com    # type: url # max: none
- out:  merchant-portal.doordash.com    # type: url # max: none
- out:  https://doordash.com/merchant    # type: url # max: none
- out:  track.doordash.com    # type: url # max: none
- out:  internal.doordash.com    # type: url # max: none
- out:  DoorDash Payments    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $36,456
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
