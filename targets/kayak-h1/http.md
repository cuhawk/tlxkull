# KAYAK

> Platform: HackerOne — https://hackerone.com/kayak
> Type: BBP
> Bounty: Low $100 | Medium $500 | High $1,500 | Critical $5,000
> Avg bounty: $200–$250
> Response efficiency: 96% | Avg first response: N/A | Total paid: $179,243
> Last scope update: 2025-11-17

## Scope

- in:  *.kayak.com    # type: wildcard # max: critical
- in:  www.kayak.com    # type: url # max: critical
- in:  www.swoodoo.com    # type: url # max: critical
- in:  www.checkfelix.com    # type: url # max: critical
- in:  www.momondo.com    # type: url # max: critical
- in:  www.cheapflights.com    # type: url # max: critical
- in:  www.hotelscombined.com    # type: url # max: critical
- in:  www.mundi.com.br    # type: url # max: critical
- in:  business.kayak.com    # type: url # max: critical
- in:  kayak.ai    # type: url # max: critical
- in:  com.kayak.android    # type: android_app # max: critical
- in:  com.kayak.travel    # type: ios_app # max: critical
- out:  https://*.kayakairplanemode.com    # type: wildcard # max: none
- out:  klassereise.checkfelix.com    # type: url # max: none
- out:  kayak.com/hotelowner/*    # type: url # max: none
- out:  kayak.com/moira/ehoe/*    # type: url # max: none
- out:  kayak.com/guides/*    # type: url # max: none
- out:  affiliates.kayak.com    # type: url # max: none
- out:  cruises.kayak.com    # type: url # max: none
- out:  blue.kayak.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $179,243
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
