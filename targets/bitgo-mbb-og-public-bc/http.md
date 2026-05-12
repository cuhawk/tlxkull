# BitGo Managed Public Bug Bounty Engagement

> Platform: Bugcrowd — https://bugcrowd.com/engagements/bitgo-mbb-og-public
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  https://app.bitgo.com website crypto   # type: url
- in:  https://app.bitgo-test.com website crypto test   # type: url
- in:  *.bitgo.com website crypto   # type: wildcard

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

## Notes (appended)

- status: ACTIVE (since Oct 2024)
- app.bitgo.com = production web app for customers
- app.bitgo-test.com = test environment (2FA token "000000" works here)
- Required header: X-Bug-Bounty: Bugcrowd-<Username>
- Testing rate limits is NOT in scope for any target
- Passkey feature is NOT in scope (testing phase)
- If you find credentials: STOP testing, don't validate, submit report with location
- Leaked creds from third parties reviewed case by case, no guarantee of reward
- Eligibility: current/former employees (12mo), family members, contractors with source access are NOT eligible
