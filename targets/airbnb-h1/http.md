# Airbnb

> Platform: HackerOne — https://hackerone.com/airbnb
> Type: BBP
> Bounty: Low $250 | Medium $5,000 | High $17,999 | Critical $25,000
> Avg bounty: $500–$750
> Response efficiency: 100% | Avg first response: N/A | Total paid: $3,174,353
> Last scope update: 2025-07-09

## Scope

- in:  *.hoteltonight.com    # type: wildcard # max: critical
- in:  *.airbnb.org    # type: wildcard # max: critical
- in:  *.musta.ch    # type: wildcard # max: critical
- in:  *.airbnbpayments.com    # type: wildcard # max: critical
- in:  www.airbnb.com    # type: url # max: critical
- in:  next.airbnb.com    # type: url # max: critical
- in:  api.airbnb.com    # type: url # max: critical
- in:  support-api.airbnb.com    # type: url # max: critical
- in:  assets.airbnb.com    # type: url # max: critical
- in:  m.airbnb.com    # type: url # max: critical
- in:  one.airbnb.com    # type: url # max: critical
- in:  open.airbnb.com    # type: url # max: critical
- in:  callbacks.airbnb.com    # type: url # max: critical
- in:  *.airbnb.com    # type: url # max: critical
- in:  *.airbnbcitizen.com    # type: url # max: critical
- in:  *.atairbnb.com    # type: url # max: critical
- in:  *.withairbnb.com    # type: url # max: critical
- in:  *.byairbnb.com    # type: url # max: critical
- in:  *.muscache.com    # type: url # max: critical
- in:  *.airbnb-aws.com    # type: url # max: critical
- in:  *.luxuryretreats.com    # type: url # max: critical
- in:  *.hoteltonight-test.com    # type: url # max: critical
- in:  www.hoteltonight.com    # type: url # max: critical
- in:  Localized airbnb sites listed at the link below:    # type: other # max: critical
- in:  com.airbnb.android    # type: android_app # max: critical
- in:  com.airbnb.app    # type: ios_app # max: critical
- in:  com.luxuryretreats.ios    # type: ios_app # max: critical
- out:  luckeyhomes.com    # type: url # max: none
- out:  luckey.fr    # type: url # max: none
- out:  luckey.app    # type: url # max: none
- out:  luckey.in    # type: url # max: none
- out:  demo.urbandoor.com    # type: url # max: none
- out:  provider.demo.urbandoor.com    # type: url # max: none
- out:  admin.demo.urbandoor.com    # type: url # max: none
- out:  luckey.partners    # type: url # max: none
- out:  omgpro.airbnb.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $3,174,353

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
