# Nubank Brasil Managed Bug Bounty Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/nubank
> Type: BBP
> Bounty: P1 $2000–$4000 | P2 $1000–$2000 | P3 $300–$600 | P4 $50–$100
> Status: In progress (started Aug 31, 2023)
> Last scope update: 12 Mar 2026

## Scope

- in:  https://play.google.com/store/apps/details?id=com.nu.production&hl=pt_BR&gl=US&pli=1   # type: android_app
- in:  https://apps.apple.com/br/app/nubank-conta-e-cart%C3%A3o/id814456780   # type: ios_app
- in:  prod-*.nubank.com.br   # type: domain
- in:  prod-*.nu.com.mx   # type: domain
- in:  prod-*.nu.com.co   # type: domain
- in:  https://nubank.com.br/   # type: url
- in:  https://nubank.com.mx   # type: url
- in:  https://nubank.com.co   # type: url
- in:  https://www.nuinvest.com.br/   # type: url
- out: *.nuinternational.com   # type: wildcard
- out: *.nat-a.nubank.com.br   # type: wildcard
- out: international.nubank.com.br   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- validation within: 7 days
- avg payout: $4,000 (last 3 months)
- vulns rewarded: 77
- safe harbor: yes
- disclosure: NOT allowed
- industry: Finance
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
