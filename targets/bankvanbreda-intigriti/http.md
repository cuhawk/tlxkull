# Bank J.Van Breda & C°

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/bankvanbreda/bankvanbreda/detail
> Type: BBP | Public | Open
> Bounty: Low €150 | Medium €750 | High €2,000 | Critical €5,000 | Exceptional €10,000 (Tier 1); Low €100 | Medium €400 | High €1,000 | Critical €2,000 | Exceptional €4,000 (Tier 2)
> Avg payout: €1,031 | Total paid: €31,950
> Response: avg first response < 2 weeks | avg to decide < 2 weeks
> Last scope update: unknown

## Scope

- in:  *.mobile.bankdekremer.be   # type: wildcard | tier: Tier 1
- in:  *.mobile.bankvanbreda.be   # type: wildcard | tier: Tier 1
- in:  be.bankvanbreda.mobile (Android)   # type: android_app | tier: Tier 1
- in:  https://apps.apple.com/be/app/apple-store/id1382705162 (iOS)   # type: ios_app | tier: Tier 1
- in:  https://apps.apple.com/nl/app/vanbredaonline/id1029442542 (iOS)   # type: ios_app | tier: Tier 1
- in:  be.bankdekremer.mobile (Android)   # type: android_app | tier: Tier 1
- in:  secure.bankdekremer.be   # type: url | tier: Tier 1
- in:  secure.bankvanbreda.be   # type: url | tier: Tier 1
- in:  web-xs2a.bankvanbreda.be   # type: url | tier: Tier 1
- in:  *.bankdekremer.be   # type: wildcard | tier: Tier 2
- in:  *.bankvanbreda.be   # type: wildcard | tier: Tier 2
- in:  *.vanbredacarfinance.be   # type: wildcard | tier: Tier 2
- in:  secure.vanbredavendor.com   # type: url | tier: Tier 2
- in:  vpn.jvanbreda.be   # type: url | tier: Tier 2
- out: any domain not listed above   # type: domain

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: credentials via online contact form at bankvanbreda.be/contact — mention Intigriti researcher

## Notes

- payout speed: avg to decide < 2 weeks
- Belgian bank; wealth management for entrepreneurs and liberal professions
- ID check required for program participation
- focus areas: confidential data breach, performing financial transactions
- IDOR in scope but UUIDs that must be guessed (no structural leak) are out of scope
- mobile: no cert pinning, jailbreak/root detection issues are out of scope

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
