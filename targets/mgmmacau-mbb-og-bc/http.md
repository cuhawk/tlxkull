# MGM China Holdings Limited Managed Bug Bounty Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/mgmmacau-mbb-og
> Type: BBP
> Bounty: P1 $5500–$7500 | P2 $2500–$3500 | P3 $750–$1500 | P4 $250–$500
> Status: In progress

## Scope

- in:  https://mgm.mo   # type: url
- in:  https://booking.mgm.mo/   # type: url
- in:  https://jobs.mgm.mo   # type: url
- in:  https://static.mgm.mo   # type: url
- in:  https://Mlife.mo   # type: url
- in:  https://www.mgmmacau.com   # type: url
- in:  https://www.tickets.mgm.mo/   # type: url
- in:  https://apps.apple.com/mo/app/id6444925665   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=mo.mgm.app   # type: android_app
- in:  http://mobileapp-gaming.mgm.mo   # type: url
- in:  http://mobileapp-non-gaming.mgm.mo/   # type: url
- out: https://opay.icbc.com   # type: url
- out: https://mgmchinaholdings.com   # type: url
- out: https://hq.hero-cloud.com/   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
