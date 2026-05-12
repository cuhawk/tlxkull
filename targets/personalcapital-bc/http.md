# personalcapital — Empower Personal Wealth (Bugcrowd BBP)

> **STATUS: PAUSED** (Apr 8, 2026) — "Pausing for program revamp"
> Previously known as Personal Capital; rebranded to Empower in Feb 2023.
> Targets are redacted. Do NOT test until program resumes.

## Program info
- URL: https://bugcrowd.com/engagements/personalcapital
- Type: bug_bounty
- Scope rating: 1/4
- Started: Aug 17, 2017
- Paused: 08 Apr 2026

## Rewards
- P1: $3,000 – $4,000
- P2: $1,200 – $2,000
- P3: $550 – $700
- P4: $150 – $250

## Known testing URLs (from description — verify when program resumes)
- Registration: https://devstaging.pcapcloud.com/page/login/registerUser
- Login: https://devstaging.pcapcloud.com/page/login/goHome

## In scope (redacted — paused)
- type: web
  url: ████ (redacted — Empower Personal Wealth web app)
  notes: Java/jQuery backend, HTML5 SPA; paused for revamp

## Out of scope (from description)
- Any denial of service attacks
- User/email enumeration (known/allowed)
- Attacks requiring user's computer to be compromised first
- Live production systems (use devstaging env)

## Focus areas (when active)
- Server-side APIs (primary focus)
- Authentication bypass / MFA subversion
- PII/financial data disclosure
- Credentials and access control
- Empower Personal Cash (banking tab) + joint account invite flows

## Notes
- Blackout: Thursdays 12:00–4:00 PM Pacific (environment refresh)
- Use @bugcrowdninja.com email for test accounts
- Test financial institution: "Dag Site", ID=pcap.site16441.3, Password=site16441.3
