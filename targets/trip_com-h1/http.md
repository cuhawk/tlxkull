# Trip.com

> Platform: HackerOne — https://hackerone.com/trip_com
> Type: BBP
> Bounty: Low $100–$200 | Medium $300–$500 | High $1,000–$2,000 | Critical $1,500–$5,500
> Avg bounty: $100–$100
> Response efficiency: 96% | Avg first response: N/A | Total paid: $34,673
> Last scope update: 2026-01-13

## Scope

- in:  *.trip.com    # type: wildcard # max: critical
- in:  *.travix.com    # type: wildcard # max: critical
- in:  *.travix.io    # type: wildcard # max: critical
- in:  *.trainpal.com,*.mytrainpal.com    # type: wildcard # max: critical
- in:  *.cheaptickets.nl    # type: wildcard # max: critical
- in:  *.triplinkintl.com    # type: wildcard # max: critical
- in:  *.tyo-masters.co.jp    # type: wildcard # max: critical
- in:  *.budgetair.com    # type: wildcard # max: critical
- in:  *.flugladen.de    # type: wildcard # max: critical
- in:  *.vayama.com    # type: wildcard # max: critical
- in:  *.vliegwinkel.nl    # type: wildcard # max: critical
- in:  *.trip.biz    # type: wildcard # max: critical
- in:  app.blueskytravelvietnam.com    # type: url # max: critical
- in:  <locale>.trip.com    # type: other # max: critical
- in:  com.trip.android    # type: android_app # max: critical
- in:  com.trip.ios    # type: ios_app # max: critical
- in:  *.staging.travix.com    # type: other # max: critical # not eligible for bounty
- in:  trip.biz    # type: url # max: critical
- in:  *.mytrainpal.com    # type: wildcard # max: critical
- in:  *.trainpal.com    # type: wildcard # max: critical
- in:  trip.com    # type: url # max: critical
- in:  681752345    # type: ios_app # max: critical
- in:  locale.trip.com    # type: url # max: critical
- out:  *.stg.travix.com    # type: wildcard # max: none
- out:  *.dev.travix.com    # type: wildcard # max: none
- out:  *.development.travix.com    # type: wildcard # max: none
- out:  *.playground.travix.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $34,673
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
