# DailyPay VDP

> Platform: HackerOne — https://hackerone.com/dailypay_vdp
> Type: VDP | Self-managed | Standard safe harbor
> Bounty: VDP (no bounties) | Response efficiency: 77%
> Last scope update: April 29, 2026

## Scope

- in:  DailyPay On-Demand Pay   # type: ios_app
- in:  DailyPay On-Demand Pay   # type: android_app
- in:  PNC EarnedIt   # type: ios_app
- in:  PNC Earnedit   # type: android_app
- in:  extend-api.dailypay.com   # type: domain
- in:  app.dailypay.com/   # type: domain
- in:  api.dpfriday.com   # type: domain
- in:  api.dailypay.com   # type: domain
- in:  https://github.com/dailypay/*   # type: repo
- in:  get.dailypay.com   # type: domain
- out: iam.staging.dailypay.com   # type: domain
- out: dailypay.com   # type: domain
- out: Archived Repositories   # type: other

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- payout speed: unknown
- Launched: Jan 2026

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
