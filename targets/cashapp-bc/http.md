# Cash App Bug Bounty (Block, Inc.)

## Target
- program: cashapp (Bugcrowd)
- category: bbp
- started: Jun 02, 2020
- nondisclosure: true (no disclosure without Block approval)
- full_safe_harbor: true

## Scope
- in: cash.app (web)
- in: Cash App iOS app (https://itunes.apple.com/us/app/cash-app/id711923939)
- in: Cash App Android app (https://play.google.com/store/apps/details?id=com.squareup.cash)
- in: *.cashstaging.app (no credentials provided; if accessible, submit)
- in: Any Block-confirmed subdomain not in scope (accepted upon review, may have different rewards)
- out: Square.online, square.links, square.site, Weebly assets
- out: Targets covered under Square, Block Open Source, Tidal, Afterpay programs

## Bounties
- P1: $5,000-18,000
- P2: $1,000-5,000
- P3: $250-500
- P4: $100-200

### Subdomain Takeover Payouts (different from above)
- High Impact Subdomain Takeover: P2 $2,500 (reputational/technical risk + access to sensitive data on parent domain)
- Basic Subdomain Takeover: P3 $250-500 (reputational/technical risk, no sensitive data access on parent domain)
- Concession award: P4 $100 (publicity risk only)

## Auth
- Self-register with @bugcrowdninja.com email
- No credentials provided
- Flags are long — brute force won't work

## Focus: Authentication Flows
- Login flows: MFA, account access mechanisms, potential auth bypass
- Account recovery: recovery questions, email/phone/$CashTag-based recovery, recovery bypass

## Rules of Engagement
- If you access/modify customer personal data → contact Block IMMEDIATELY; no post-exploitation
- Do NOT use/share/disclose/publish info obtained during research; must delete all copies after submission
- No DoS attacks
- Do NOT use ChatGPT, DeepSeek, Google Gemini, or any AI tools during research; cannot disclose to these platforms
- Do NOT contact Cash App/Block/Block aliases to follow up; use support@bugcrowd.com for escalations (violations: point reduction or program expulsion)
- Similar issues in multiple locations → COMBINE into single submission; separate submissions may be closed as duplicates

## OOS Findings
- 3rd party software vulnerabilities
- Physical attacks against Square property/data centers
- Logout CSRF
- Autocomplete attribute on web forms
- Missing cookie flags on non-sensitive cookies
- No maximum password length
- Email/phone/username oracle for single-account lookup (mass enumeration IS valid)
- Spoofed emails for phishing
- 2FA TOTP code not expiring
- DoS attacks
- Cache poisoning causing DoS
- Public information about Square customers not specific to Cash App

## Submission Quality
- Detailed step-by-step reproduction steps, screenshots, links, video demos
- Always include linked account name, email, or SMS
- Browser, OS, mobile app version
- Concrete attack scenario with clear evidence

## Notes
- Cryptocurrency issues: submit immediately; may be rewarded above standard rates
- Part of Block Inc. (related programs: Square, Tidal, Afterpay, Block Open Source)
- Info stealer log credential findings: accepted, rewarded case-by-case
