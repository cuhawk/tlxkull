# volkswagen-vwfs-mbb-og — New Blue Website (NBW) - VWFS Bug Bounty Program

**Platform:** Bugcrowd BBP  
**Program URL:** https://bugcrowd.com/engagements/volkswagen-vwfs-mbb-og  
**Started:** Nov 28, 2023  
**Disclosure:** Coordinated (explicit permission required)  
**Safe Harbor:** Yes (CFAA + DMCA exempt)  

---

## Rewards

| Priority | Reward |
|----------|--------|
| P1 | $3,500 – $4,500 |
| P2 | $1,500 – $2,500 |
| P3 | $500 – $750 |
| P4 | $175 – $225 |

Average payout: $500 (last 3 months). Validation: ~21 days.

---

## Authentication

- Testing is **unauthenticated only**
- Add custom header on every request: `x-bugcrowd-tester: <your-Bugcrowd-username>`

---

## In-Scope Targets

VWFS New Blue Websites — international platform for VW Financial Services subsidiaries (vwfs.*):
- in: https://www.vwfs.de (primary — VW Financial Services Germany)
- in: https://www.vwfs.es (Spain)
- in: https://www.vwfs.pt (Portugal)
- in: https://www.vwfs.mx (Mexico)
- Pattern: https://www.vwfs.* — www subdomain only

**CRITICAL:** Only test `www` subdomain. All other subdomains = Out-of-Scope and will be marked OOS.

All VWFS NBW apps use the same codebase — submit one report per vulnerability, not multiple per site (duplicates).

---

## Focus Areas

- Injection of faulty/malicious data into customer journeys
- Attacks that impair other customers
- Application self-DoS (in scope unlike network DoS)

---

## Out-of-Scope

- All subdomains other than www.*
- Social engineering of any kind
- Contacting agents/customer support
- Third-party applications and scripts (unless VWFS misconfiguration)
- Load testing and rate limiting
- D/DoS (application self-DoS is in scope)
- Third-party services hosted on VWFS subdomains (report to 3rd party directly)

---

## Notes

- VW Financial Services AG — largest provider of automotive financial services worldwide
- Transitioned to public Oct 28, 2025
- Program paused Dec 15 – Jan 3 (holiday season annually)
