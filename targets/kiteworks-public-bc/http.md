# kiteworks-public — Kiteworks (Bugcrowd BBP)

> **STATUS: PAUSED** (Apr 15, 2026) — "Recent developments in the AI space" per announcement Apr 17. Expected to reopen in a few weeks.
> Targets are redacted. Do NOT test until program resumes.
> Previously named Accellion.

## Program info
- URL: https://bugcrowd.com/engagements/kiteworks-public
- Type: bug_bounty (on-premises enterprise content platform)
- Scope rating: 1/4
- Started: Oct 08, 2020
- Paused: 15 Apr 2026
- Expedited triage

## Rewards
- Bonus: $50,000
- P1: $11,000 – $25,000
- P2: $5,000 – $10,000
- P3: $600 – $3,000
- P4: $250 – $500

## In scope (from recent activity — paused)
- type: web
  url: https://kw-bugcrowd-pub.bounty.kiteworks.dev/
  notes: Bug bounty test instance; redacted targets but URL visible in recent accepted submissions

## Access (when active)
- 4 user profiles: Standard, Restricted, Recipient, Custom
- Email format: yourusername+standard@bugcrowdninja.com etc.
- Login: https://kw-bugcrowd-pub.bounty.kiteworks.dev/

## Out of scope
- Hypothetical flaws without exploitable POC
- Third-party apps/libraries
- Automated scanner reports without validation
- Admin-privilege-required vulns (down-rated to max CVSS 8.9)
- DoS, rate limiting, CSRF low-severity, clickjacking, open redirects (unchained)
- SSL/TLS best practices, missing security headers
- EXIF, SPF/DKIM/DMARC, domain takeover, race conditions

## Notes
- XSS: alert(1) not sufficient; must demonstrate actionable impact (account takeover, cookie exfil, etc.)
- Unauthenticated XSS = High; Authenticated XSS = Medium
- On-premises enterprise product; admin-privilege vulns down-rated
