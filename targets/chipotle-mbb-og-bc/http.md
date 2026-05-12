# Chipotle Managed Bug Bounty Engagement

> Platform: Bugcrowd — https://bugcrowd.com/engagements/chipotle-mbb-og
> Type: BBP
> Bounty: P1 $3500–$4500 | P2 $1500–$2500 | P3 $500–$750 | P4 $175–$225
> Status: In progress (started Aug 13, 2024)

## Scope

- in:  https://www.chipotle.com   # type: url
- in:  https://www.chipotle.co.uk   # type: url
- in:  https://catering.chipotle.com   # type: url
- in:  https://services.chipotle.com   # type: url
- in:  https://apps.apple.com/us/app/chipotle-fresh-food/id327228455   # type: ios_app
- in:  https://play.google.com/store/search?q=chipotle+mexican+grill&c=apps   # type: android_app

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- validation within: 5 days
- avg payout: $300 (last 3 months)
- vulns rewarded: 55
- safe harbor: yes
- industry: Hospitality
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
