# MyFitnessPal Managed Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/myfitnesspal-mbb
> Type: BBP
> Bounty: P1 $3500–$4500 | P2 $1500–$2500 | P3 $200–$300 | P4 $50
> Status: In progress (started Mar 31, 2022)

## Scope

- in:  https://market.android.com/details?id=com.myfitnesspal.android&rdid=com.myfitnesspal.android   # type: url
- in:  https://apps.apple.com/us/app/myfitnesspal-calorie-counter/id341232718   # type: ios_app
- in:  *.myfitnesspal.com   # type: wildcard
- out: https://community.myfitnesspal.com   # type: url
- out: https://community-stage.myfitnesspal.com   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- validation within: 7 days
- avg payout: $2,260 (last 3 months)
- safe harbor: yes
- industry: Healthcare
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
