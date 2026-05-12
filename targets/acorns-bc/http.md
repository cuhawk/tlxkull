# Acorns Grow, Inc.

> Platform: Bugcrowd — https://bugcrowd.com/engagements/acorns
> Type: BBP
> Bounty: P1 $2,000–$4,000 | P2 $750–$1,750 | P3 $350–$650 | P4 $200
> Status: In progress (started Nov 23, 2015)

## Scope

- in:  https://acorns.com/   # type: wildcard — *.acorns.com
- in:  https://apps.apple.com/us/app/acorns-invest-spare-change/id883324671   # type: ios_app
- in:  https://graphql.acorns.com   # type: url — GraphQL API
- in:  https://play.google.com/store/apps/details?id=com.acorns.android&hl=en_US&gl=US   # type: android_app
- in:  https://www.gohenry.com/   # type: url — added Jul 2024
- in:  https://www.pixpay.fr/   # type: url
- out: share.acorns.com
- out: grow.acorns.com
- out: store.acorns.com

## Auth

- type: signup
- creds: Self-signup using @bugcrowdninja.com email address
- note: Add "bugcrowd" to user-agent string to force 2FA challenge during testing

## Notes

- safe harbor: yes (CFAA + DMCA)
- disclosure: NOT allowed (nondisclosure)
- status: ACTIVE
- Average payout $300; validation within 9 days; report confirmed within 2 days
- Focus: customer data disclosure, broken auth/authz, XSS, CSRF, SQLi, RCE, API issues, MFA
- Reports without PoC = ineligible for reward (scan reports not accepted)

## OOS

- Rate limiting on endpoints
- Social engineering attacks
- DoS attacks
- share.acorns.com, grow.acorns.com, store.acorns.com
