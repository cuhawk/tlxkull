# Tripadvisor

> Platform: Bugcrowd — https://bugcrowd.com/engagements/tripadvisor-bb-og
> Type: BBP
> Bounty: P1 $5000 | P2 $1250 | P3 $900 | P4 $250
> Status: In progress (started Jan 14, 2019)

## Scope

- in:  https://api.production.cde.tamg.cloud   # type: url
- in:  https://partnerapi.tapayments.com   # type: url
- in:  https://partnerapi1.tapayments.com   # type: url
- in:  https://partnerapi2.tapayments.com   # type: url
- in:  https://walletproxy.tapayments.com   # type: url
- in:  https://walletproxy1.tapayments.com   # type: url
- in:  https://walletproxy2.tapayments.com   # type: url
- in:  https://www.tripadvisor.com   # type: url
- in:  https://api.tripadvisor.com   # type: url
- in:  https://service.platform.tripadvisor.com   # type: url
- in:  https://gwapi.tripadvisor.com   # type: url
- in:  https://gwapi1.tripadvisor.com   # type: url
- in:  https://gwapi2.tripadvisor.com   # type: url
- in:  https://play.google.com/store/apps/details?id=com.tripadvisor.tripadvisor&hl=en   # type: android_app
- in:  https://apps.apple.com/us/app/tripadvisor-plan-book-trips/id284876795   # type: ios_app
- in:  https://rentals.tripadvisor.com   # type: url
- in:  https://*.vacationhomerentals.com   # type: url
- in:  https://*.holidaylettings.com   # type: url
- in:  https://*.flipkey.com   # type: url
- in:  https://*.niumba.com   # type: url
- in:  https://*.housetrip.com   # type: url
- in:  https://itunes.apple.com/us/app/vacation-rentals-owner-app-by-tripadvisor/id1045663228?mt=8   # type: ios_app
- in:  http://marlo.ext.tripadvisor.com   # type: url
- in:  https://*.bokundemo.com   # type: url
- in:  https://*.bokuntest.com   # type: url
- out: *.bokun.eu   # type: wildcard
- out: *.bokun.website   # type: wildcard
- out: *.bokun.tools   # type: wildcard
- out: *.bokun.team   # type: wildcard
- out: ir.tripadvisor.com   # type: domain
- out: *.tripadviser.at   # type: wildcard
- out: *.tripadvisor.cn   # type: wildcard
- out: *.tripadvisor.*/Trips   # type: wildcard
- out: *.tripadvisor.*/Mobile*   # type: wildcard
- out: *.tripadvisor.*/engineering   # type: wildcard
- out: *.tripadvisor.*/WidgetEmbed-*   # type: wildcard
- out: spotlight-dev.tripadvisor.com   # type: domain
- out: spotlight.tripadvisor.*   # type: domain
- out: careers.tripadvisor.com   # type: domain
- out: *.tripadvisoradexpress.*   # type: wildcard
- out: *.tripadvisorwifi.*   # type: wildcard
- out: *.bokun.io   # type: wildcard
- out: *.bokun.is   # type: wildcard
- out: *.bokun.com   # type: wildcard
- out: *.bokun.app   # type: wildcard
- out: taplus.*   # type: domain
- out: tripadvisor-plus.*   # type: domain
- out: tripadvisorplus.*   # type: domain
- out: *.experiences.zone   # type: wildcard
- out: travelermail.com   # type: domain
- out: *.bokunmobile.website   # type: wildcard

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- validation within: 7 days
- avg payout: $400 (last 3 months)
- vulns rewarded: 427
- safe harbor: yes
- industry: Technology
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
