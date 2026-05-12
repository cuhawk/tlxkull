# Moovit Managed Bug Bounty Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/moovit-mbb-og
> Type: BBP
> Bounty: P1 $2,000–$3,500 | P2 $1,000–$2,000 | P3 $250–$750 | P4 $100–$250
> Status: In Progress | Started: Jan 16 2024
> Last scope update: 12 Feb 2026

## Scope

- in:  Moovit iOS app (App Store)                          # type: ios_app
- in:  Moovit Android app (Google Play)                    # type: android_app
- in:  Moovit Web app (app.moovit.com likely)              # type: domain
- in:  Moovit API (backend)                                # type: api
- out: moovitapp.com (WordPress)                           # type: domain
- out: any non-Moovit mobile app                           # type: other
- note: full target list loads dynamically — check Bugcrowd brief

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: self-provision accounts using @bugcrowdninja.com email

## Notes

- payout speed: validation within 6 days
- status: ACTIVE
- Utilities / MaaS — public transit app; 1.5B+ users, 3,500+ cities
- Safe harbor: yes (CFAA + DMCA exemptions)
- NDA required: researchers must maintain confidentiality of findings
- no automated scanners
- focus: auth/authz, unrestricted API access, privacy/data protection
- out-of-scope: clickjacking, CSV injection, SSL/TLS, brute force, DoS, scanner output, physical access, spam/social engineering, tab-nabbing, third-party app bugs, password policy, path disclosure, info disclosure, CSRF unauthenticated, missing security headers, MiTM, WordPress bugs (report to WordPress program)
- do not create excessive accounts; do not test against other users
- double bounty promotion ran Jul 7–22 2025 (expired)
- scope rating 1/4 (narrow scope)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
