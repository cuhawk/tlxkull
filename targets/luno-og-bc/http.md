# Luno Bug Bounty Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/luno-og
> Type: BBP
> Bounty: Mobile: P1 $4,500–$7,500 | P2 $2,250–$3,000 | P3 $825–$1,000 | P4 $225–$375 | Web: P1 $2,500–$3,000 | P2 $1,500–$1,800 | P3 $500–$650 | P4 $100–$200
> Status: In Progress | Started: Nov 04 2020
> Last scope update: 07 Jan 2026

## Scope

- in:  *.staging.luno.com                  # type: wildcard  (web testing — staging only)
- in:  Luno iOS app (Swift, Swift UI)       # type: ios_app   (production — no staging mobile)
- in:  Luno Android app (Kotlin/Java)       # type: android_app  (production — no staging mobile)
- out: any non-Luno third-party services    # type: other
- note: full target list loads dynamically — check Bugcrowd brief for current domains

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: sign up at https://staging.luno.com/en/signup using @bugcrowdninja.com
- note: OpenAPI spec available for download from https://www.luno.com/en/developers

## Notes

- payout speed: validation within 7 days
- status: ACTIVE
- Finance / crypto investment platform; AWS + Cloudflare + Nginx stack
- Safe harbor: yes (CFAA + DMCA exemptions)
- scope rating: 3/4
- request headers required:
  - x-luno-bugcrowd-id: {bugcrowd_username}  (5% bonus for including this)
  - x-luno-announcement-id: {announcement_id}  (when testing specific announcement)
- web targets use STAGING only: prefix all endpoints to https://staging.luno.com
- mobile targets are production (no staging mobile apps); no integrity/stability testing
- focus: auth/authz, session management, IDOR, misconfigs, RCE, exposed buckets, endpoints bypassing Cloudflare, leaked source code, business logic
- N-day policy: in-scope 14 days after public release
- out-of-scope: DoS, rate limit bypass, email bombing, mobile malicious-app installs, no-impact submissions, scanner output
- leaked credentials: points-only (no cash)
- do NOT test production for web (staging only)
- iOS uses HMAC + passkeys + 2FA; Android uses cert pinning + HMAC + passkeys + 2FA

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
