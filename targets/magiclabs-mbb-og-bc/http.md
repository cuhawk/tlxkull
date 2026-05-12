# Magic Labs Managed Bug Bounty Engagement

> Platform: Bugcrowd — https://bugcrowd.com/engagements/magiclabs-mbb-og
> Type: BBP
> Bounty: P1 $3,000 | P2 $1,000 | P3 $500 | P4 $250
> Status: In Progress | Started: Dec 09 2025
> Last scope update: 22 Jan 2026

## Scope

- in:  dashboard.magic.link   # type: domain  (developer dashboard — sign up here)
- in:  auth.magic.link        # type: domain  (main product — passwordless login orchestration)
- in:  api.magic.link         # type: api     (backend API — wallet generation, signing, private key exports)
- out: docs.fortmatic.com     # type: domain  (external provider)
- out: any Typeform integrations  # type: other  (external provider)

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: sign up at https://dashboard.magic.link using @bugcrowdninja.com
- note: magic link / OTP flow — user enters email, receives link, verifies, logs in

## Notes

- payout speed: validation within 7 days (triage 3 business days, bounty 10 business days from triage)
- status: ACTIVE
- Computer Software / web3 wallet infrastructure; passwordless auth (magic links, WebAuthn, OAuth)
- Safe harbor: yes (CFAA + DMCA exemptions)
- NDA: no disclosure without express consent
- scope rating: 1/4
- focus: developer/user sensitive info, asset/platform security, key management systems, new/beta features
- testing is on PRODUCTION — do not affect other users' data; do not DoS; do not delete/edit site content
- no AI-generated or low-effort reports; must show original analysis
- N-day policy: in-scope 14 days after public release
- race conditions only in scope if they result in unauthorized fund transfer or private key exposure
- out-of-scope: P5, DoS/DDoS, rate limit, email bombing, social engineering, old libs without PoC, UX issues, email security records, MiTM, blockchain functionality abuse, external provider features
- leaked credentials: case-by-case only if tied to actual security impact; do NOT use leaked creds during testing (disqualification)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
