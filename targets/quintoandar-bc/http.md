# quintoandar — QuintoAndar Managed Bug Bounty Engagement

**Platform:** Bugcrowd BBP  
**Program URL:** https://bugcrowd.com/engagements/quintoandar  
**Started:** Jul 02, 2024  
**Disclosure:** Coordinated (explicit permission required)  
**Safe Harbor:** Yes (CFAA + DMCA exempt)  

---

## Rewards (P4/P5 = no reward)

| Priority | Reward |
|----------|--------|
| P1 | $500 – $1,000 |
| P2 | $300 – $500 |
| P3 | $100 – $300 |
| P4/P5 | No reward (marked Low/Informational) |

Average payout: $1,525 (last 3 months). Validation: ~17 days.

---

## Authentication

- Use @bugcrowdninja.com email for any test accounts
- Add custom header: `X-Bug-Bounty: Bugcrowd-<Username>`

---

## In-Scope Targets

Full target list is in the resource section PDF (Quinto_Andar_Target_Info.pdf).  
Known in-scope from CrowdStream activity and announcements:

- in: https://www.quintoandar.com.br/*
- in: rental-api.quintoandar.com.br (BAC issues temporarily OOS as of Apr 29, 2026)

Note: `proprietario.quintoandar.com.br` temporarily removed from scope as of Mar 13, 2026.

---

## Company Context

QuintoAndar Group — leading real estate ecosystem in Latin America. Presence in Argentina, Brazil, Ecuador, Mexico, Panama, Peru. 10+ years experience.

---

## Important Notes

- Social engineering exploits treated as P4 (not P1-P3)
- Same root-cause variants may be deduplicated
- Leaked credentials addressed case-by-case
- Services hosted by third parties for QuintoAndar = OOS
- Rewards temporarily reduced (as of Mar 2026)

---

## Out-of-Scope

- Business-logic access that is intrinsic to intended functionality
- Credential leaks not from QuintoAndar resources
- Social engineering
- CSRF on unauthenticated forms
- MITM/physical access attacks
- Known vulnerable libraries without PoC
- CSV injection without PoC
- Missing SSL/TLS best practices
- DoS
- Content spoofing without HTML/CSS modification
- Rate limiting on non-auth endpoints
- Missing CSP, HttpOnly, Secure cookie flags
- Missing SPF/DKIM/DMARC
- Outdated browser issues
- Version/banner disclosure
- Tabnabbing
- Subdomain takeover on out-of-scope subdomains
- Open redirect without additional impact
