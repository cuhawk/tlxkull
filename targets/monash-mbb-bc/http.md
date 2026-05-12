# monash-mbb — Monash University Bug Bounty (Bugcrowd)

platform: bugcrowd
program_url: https://bugcrowd.com/engagements/monash-mbb
category: bbp
safe_harbor: full
disclosure: coordinated (explicit permission required before disclosure)
credentials: none (publicly available targets)

## Rewards

| Tier | Special | P1 | P2 | P3 | P4 |
|------|---------|----|----|----|----|
| Tier 0 | $10,000 | $5,000–$7,500 | $2,500–$3,500 | $750–$1,500 | $250–$500 |
| Tier 1 | $5,000 | $2,100–$2,500 | $1,000–$1,200 | $400–$600 | $125 |
| Tier 2 | — | $1,000–$1,500 | $600–$1,200 | $150–$300 | $50 |
| API Targets | — | $2,100–$2,500 | $1,000–$1,200 | $400–$600 | $125 |

## Scope

### In-scope targets

- in: monash.edu (type: wildcard — *.monash.edu; confirmed via CrowdStream)
- in: partner.apps.monash.edu (confirmed accepted in CrowdStream)
- in: interviews.monash.edu (confirmed accepted in CrowdStream)
- in: collections.monash.edu (added Sep 2025 — Library and Archive)
- in: mids.monash.edu (added Jan 2025 — Staff Directory)
- in: ims.monash.edu (added Jan 2025 — Identity Management)
- in: research.monash.edu (added Jan 2025 — Research Portal)
- in: researchmgt.monash.edu (added Jan 2025 — PURE)
- in: move.monash.edu (added Jan 2025 — Monash Virtual Environment)

### Out-of-scope targets

- out: compulsoryunits.monash.edu (compromised credentials excluded)
- out: study.abroad.monash.edu (compromised credentials excluded)
- out: myapp.monash.edu (aura submissions excluded)

## Out-of-scope vulnerability types

- ALL XSS submissions (until further notice)
- Self-XSS
- Content spoofing
- DNS configuration issues
- Host header injection
- CSRF (low impact)
- Clickjacking
- Missing rate limiting
- SPF/DKIM/DMARC issues
- Missing security headers
- SSL/TLS configuration without a working exploit
- Subdomain takeover

## Notes

- Largest and most international Australian university
- Program started Mar 09, 2021
- Explicit permission required before any disclosure
- No test credentials provided; use publicly available access
- ALL XSS is OOS until further notice (important: even normally-high-value XSS)
