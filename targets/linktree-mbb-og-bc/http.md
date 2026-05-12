# linktree-mbb-og — Linktree (Bugcrowd BBP)

## Program info
- URL: https://bugcrowd.com/engagements/linktree-mbb-og
- Type: bug_bounty
- Scope rating: 4/4
- Started: Feb 22, 2023

## Rewards
### Primary Targets
- P1: $5,000 – $7,500
- P2: $1,000 – $2,500
- P3: $250 – $600
- P4: $50 – $200

### Secondary Targets
- P1: $1,500 – $2,000
- P2: $800 – $1,000
- P3: $100 – $200
- P4: $25 – $50

## In scope (primary targets — table loading)
- type: web
  url: https://linktr.ee
  notes: Main Linktree platform
- type: web
  url: https://*.linktr.ee
  notes: All Linktree subdomains
- notes: plannthat.com removed from scope as of May 2025

## Out of scope
- Clickjacking, CSRF on unauthenticated forms
- GraphQL DoS (alias/directive overloading, batching, field duplication)
- Rate limiting on non-auth endpoints
- Cookie flag issues
- Subdomain takeover: max P3 severity
- XSS: max P3 (Medium) severity
- Access control bypass on link lock → public content: P4
- Bypassing individual feature account tier requirements

## Notes
- CVSS-based scoring: 10.0-9.0=P1, 8.9-7.0=P2, 6.9-4.0=P3, 3.9-2.0=P4
- Rate limit: 10,000 requests/hour max
- Registration: https://linktr.ee/register
- Bug bounty free trial: https://linktr.ee/register?couponId=BUGBOUNTY30FREE
- Response SLO: P1 triage <2 business days, P2-P5 <7 business days
