# Bolt Technology OÜ

> Platform: Bugcrowd — https://bugcrowd.com/engagements/bolt-og
> Type: BBP
> Bounty: P1 $6100–$6500 | P2 $2000–$3500 | P3 $500–$850 | P4 $200–$500
> Status: In progress (started Mar 09, 2021)

## Scope

- in:  https://apps.apple.com/ee/app/bolt-fast-affordable-rides/id675033630   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=ee.mtakso.client   # type: android_app
- in:  https://apps.apple.com/ee/app/bolt-food/id1451492388   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.bolt.deliveryclient   # type: android_app
- in:  https://taxify.eu/   # type: url
- in:  https://bolt.eu/   # type: url
- out: https://play.google.com/store/apps/details?id=ee.mtakso.driver   # type: android_app
- out: https://apps.apple.com/ee/app/bolt-driver/id897442736   # type: ios_app
- out: *.test.bolt.eu   # type: wildcard
- out: *.test.taxify.eu   # type: wildcard
- out: business-old.bolt.eu   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- validation within: 8 days
- avg payout: $583 (last 3 months)
- vulns rewarded: 163
- safe harbor: yes
- industry: Technology
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
