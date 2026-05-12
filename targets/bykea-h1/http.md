# Bykea

> Platform: HackerOne — https://hackerone.com/bykea
> Type: BBP
> Bounty: Low $50 | Medium $50–$200 | High $300–$1,500 | Critical $600–$5,000
> Avg bounty: $50–$100
> Response efficiency: 100% | Avg first response: N/A | Total paid: $10,000
> Last scope update: 2026-01-30

## Scope

- in:  *.bykea.net    # type: wildcard # max: critical
- in:  https://googleplace*.bykea.net    # type: wildcard # max: critical
- in:  https://kronos*.bykea.net    # type: wildcard # max: critical
- in:  https://loadboard*.bykea.net/    # type: wildcard # max: critical
- in:  https://raptor*.bykea.net    # type: wildcard # max: critical
- in:  https://*test*.bykea.net    # type: wildcard # max: critical
- in:  bykea.com    # type: url # max: critical
- in:  https://maps.bykea.net    # type: url # max: critical
- in:  https://leaflet-map.bykea.net    # type: url # max: critical
- in:  https://nominatim.bykea.net    # type: url # max: critical
- in:  https://geocode-beta.bykea.net    # type: url # max: critical
- in:  https://api.bykea.net    # type: url # max: critical
- in:  tomoe.bykea.net    # type: url # max: critical
- in:  com.bykea.pk    # type: android_app # max: critical
- in:  com.bykea.pk.partner    # type: android_app # max: critical
- in:  1351179184    # type: ios_app # max: critical
- in:  belaz.bykea.net    # type: url # max: medium
- in:  bykea.store    # type: url # max: low
- in:  https://bykea.shop    # type: url # max: low
- in:  food-*.bykea.net    # type: wildcard # max: low
- in:  1351179184    # type: android_app # max: critical
- in:  *.bykea.com    # type: wildcard # max: critical # not eligible for bounty
- out:  *.tellocast.com    # type: wildcard # max: none
- out:  www.tilismtechservices.com    # type: url # max: none
- out:  naughty.bykea.net    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $10,000

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
