# KHealth

> Platform: HackerOne — https://hackerone.com/khealth
> Type: BBP
> Bounty: Low $100–$150 | Medium $200–$400 | High $500–$2,500 | Critical $2,500–$6,000
> Avg bounty: $200–$200
> Response efficiency: 94% | Avg first response: N/A | Total paid: $50,000
> Last scope update: 2025-10-12

## Scope

- in:  https://*.khealth.com    # type: wildcard # max: critical
- in:  https://*.khealth.io/    # type: wildcard # max: critical
- in:  accounts.khealth.com    # type: url # max: critical
- in:  eligibility.khealth.com    # type: url # max: critical
- in:  treatments.khealth.com    # type: url # max: critical
- in:  www.kpharmacyllc.com    # type: url # max: critical
- in:  start.khealth.com    # type: url # max: critical
- in:  app.khealth.com    # type: url # max: critical
- in:  kaccount.khealth.com    # type: url # max: critical
- in:  ask.khealth.com    # type: url # max: critical
- in:  http://auth.khealth.com/khealth/sign-up    # type: url # max: critical
- in:  http://auth.khealth.com/cedars/sign-up    # type: url # max: critical
- in:  http://auth.khealth.com/mayo-la-crosse/sign-up    # type: url # max: critical
- in:  salesforce.khealth.com    # type: url # max: critical
- in:  http://clinical-quality.khealth.com/api/v1    # type: url # max: critical
- in:  api.khealth.com    # type: url # max: critical
- in:  auth.hhc247.org    # type: url # max: critical
- in:  Tier 1    # type: other # max: critical
- in:  Tier 2    # type: other # max: critical
- in:  ai.kanghealth    # type: android_app # max: critical
- in:  org.hartfordhealthcare.hhc247    # type: android_app # max: critical
- in:  1180400838    # type: ios_app # max: critical
- in:  https://apps.apple.com/us/app/hhc-24-7/id6741442288    # type: ios_app # max: critical
- in:  6741442288    # type: ios_app # max: critical
- in:  api.khealth.io    # type: url # max: critical
- in:  middle-force.khealth.io    # type: url # max: critical
- in:  https://*.khealth.us/    # type: wildcard # max: critical
- in:  anthem.khealth.com    # type: url # max: critical
- in:  http://payme-service.khealth.com/api/v3/api    # type: url # max: critical
- in:  payme-service.khealth.com    # type: url # max: critical
- in:  identity.khealth.us    # type: url # max: critical
- in:  api.khealth.us    # type: url # max: critical
- in:  payment.khealth.com    # type: url # max: critical
- in:  api.therapy.khealth.com    # type: url # max: critical
- in:  content-files.therapy.khealth.com    # type: url # max: critical
- in:  secure.therapy.khealth.com    # type: url # max: critical
- in:  vpn.therapy.khealth.com    # type: url # max: critical
- in:  files.therapy.khealth.com    # type: url # max: critical
- out:  careers.khealth.com    # type: url # max: none
- out:  khealth-test.com    # type: url # max: none
- out:  https://khealth.com/careers    # type: url # max: none
- out:  hhc247.org    # type: url # max: none
- out:  http://*.hydrogenhealth.com    # type: wildcard # max: none
- out:  api-2.khealth.io    # type: url # max: none
- out:  identity.khealth.io    # type: url # max: none
- out:  care.khealth.com    # type: url # max: none
- out:  careers.kheath.com    # type: url # max: none
- out:  pharmacy.khealth.com    # type: url # max: none
- out:  manage.kanghealth.com    # type: url # max: none
- out:  we.khealth.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $50,000

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
