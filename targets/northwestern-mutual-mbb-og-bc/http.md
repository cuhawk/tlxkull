# Northwestern Mutual - Public Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/northwestern-mutual-mbb-og
> Type: BBP
> Bounty: P1 $4000–$6000 | P2 $1000–$3000 | P3 $500–$1000 | P4 $200–$300
> Status: In progress

## Scope

- in:  216.20.176.0/20   # type: cidr
- in:  https://northwesternmutual.com   # type: url
- in:  https://*.nml.com   # type: url
- in:  https://*.nmfn.com   # type: url
- in:  https://play.google.com/store/apps/details?id=com.nm.nm&hl=en_US&gl=US   # type: android_app
- in:  https://apps.apple.com/us/app/northwestern-mutual/id1132579006   # type: ios_app
- out: northwesternmutual.com/find-a-financial-advisor/   # type: domain
- out: northwesternmutual.com/financial/advisor/*   # type: domain
- out: northwesternmutual.com/careers-apply/   # type: domain
- out: northwesternmutual.com/report-a-death/   # type: domain
- out: northwesternmutual.com/notice-of-long-term-care-form/   # type: domain
- out: northwesternmutual.com/financial-professionals/?name=*   # type: domain
- out: northwesternmutual.com/notice-of-disability-form/   # type: domain
- out: northwesternmutual.com/notice-of-group-disability-form/   # type: domain

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
