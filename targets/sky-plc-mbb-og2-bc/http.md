# Sky DACH Vulnerability Disclosure Program — Bugcrowd BBP

**Program URL:** https://bugcrowd.com/engagements/sky-plc-mbb-og2  
**Category:** Entertainment / Safe harbor  
**Status:** ACTIVE (transitioned to public Jan 1, 2026)  
**Started:** Jan 1, 2026  
**Scope rating:** 1 out of 4

---

## Reward Tiers

| Priority | Range |
|----------|-------|
| P1 | $500 – $1,000 |
| P2–P4 | Points-based |

---

## In-Scope Targets

- in: **All internet-facing Sky DACH assets** (broad scope — Sky DACH properties)

**Required header for all traffic:**
```
X-Bug-Bounty: <bugcrowdusername>
```
Include your IP address in P1/P2 reports.

---

## Out-of-Scope Targets

### Subscriber IP Ranges / Hostnames
- out: All subscriber-owned IPs (hostnames resolving to .sky but managed by subscribers)
- out: skybroadband.com (customer-hosted, not Sky-owned)
- out: See attached `Sky Excluded IPs.xlsx` (uploaded Jan 7, 2026, 25.5 KB)

### OOS Sky Subsidiaries
- out: NBCUniversal → report to cyber@nbcuni.com
- out: Comcast
- out: Sky Italy → report to Sky Italy VDP programme
- out: Sky UK/ROI → report to Sky UK/ROI VDP programme

---

## OOS Submission Types

- 3rd party endpoints / brand licensing / marketing/analytics endpoints
- Server misconfigurations with no impact
- Email spoofing (SPF/DKIM/DMARC)
- Automated scan reports without PoC
- CSRF on unauthenticated forms or forms with no sensitive actions
- CSV injection without demonstrating vulnerability
- Open redirect (unless additional security impact demonstrated)
- Self-XSS, Flash-required XSS
- CORS without exploitation
- Swagger-UI XSS (accepted as P5 informational, not eligible for bounty)
- Exposed credentials no longer valid / no risk to in-scope asset
- API keys with no security impact
- Outdated browser-only vulnerabilities
- Descriptive error messages without PoC
- SSL/TLS scan reports
- Missing CSP / cookie flags best practices

## OOS Activity Types

- Load testing / DoS / DDoS
- Clickjacking on non-sensitive pages
- Banner grabbing, scanner outputs, password complexity, user enumeration
- Tabnabbing / content spoofing without HTML/CSS modification
- Account lockout, brute force, rate limiting on non-auth endpoints
- MITM or physical access requirements
- Publicly accessible login panels (unless proven impact)
- Dark web leaked credentials (points only, not money)
- Social engineering
- Current/recent employees of Sky Group
- Protocol flaws without PoC
- Theoretical issues without PoC
- Hardware: open chassis (I/O devices like USB, SIM, SD card in scope)
- Pre-release/Beta product vulnerabilities
- Already-known vulnerabilities (unless first external reporter)
- Tools used to crack/validate secrets

---

## Rules & Notes

- N-day policy: bugs in scope 30 days after public disclosure
- Credentials: sign up with @bugcrowdninja.com email
- Stolen/breached credentials → points only, not money rewards
- Reporting Sky properties not in scope but demonstrably Sky Group → ineligible for reward
- Excluded IPs file: `Sky%20Excluded%20IPs.xlsx` (attached to brief)
