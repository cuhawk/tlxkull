# Asana Bug Bounty — Bugcrowd BBP

**Program URL:** https://bugcrowd.com/engagements/asana  
**Category:** Computer Software / Partial safe harbor  
**Status:** ACTIVE  
**Started:** Jul 16, 2020  
**Scope rating:** 4 out of 4  
**Avg payout:** ~$670 (last 3 months)

---

## Reward Tiers

### Asana Targets (Main App)
| Priority | Range |
|----------|-------|
| P1 | $2,500 – $6,500 |
| P2 | $1,000 – $2,500 |
| P3 | $500 – $1,000 |
| P4 | $100 – $500 |

### Asana Enterprise Technology Scope
| Priority | Reward |
|----------|--------|
| P1 | $3,000 |
| P2 | $1,500 |
| P3 | $500 |
| P4 | $250 |

Subdomain takeovers accepted as P4 for Enterprise Technology scope.

---

## In-Scope Targets

- in: https://app.asana.com  # type: url — primary app target
- in: *.asana.com  # type: wildcard — general Asana domains
- in: *.asana.plus  # type: wildcard — only apps MADE BY Asana (see following page for app list)
- in: *.integrations.asana.plus  # type: wildcard — EXCEPT Jira instances (jira-prod.integrations.asana.plus is OOS)

**Note:** Enterprise Technology targets load separately — includes *.asana.com subdomains operated by Enterprise Technology team.

---

## Out-of-Scope Targets

- out: assets.asana.biz
- out: form.asana.com / form-beta.asana.biz (unless you created the form yourself)
- out: jira-prod.integrations.asana.plus (and any Jira instances on integrations.asana.plus)
- out: Any Asana property/subdomain not listed above

---

## Account / Credentials

- Self sign up at https://asana.com/create-account using `<username>@bugcrowdninja.com`
- Free 30-day trial of Premium/Business auto-applied (no credit card required)
- After trial: create new account with `username+1@bugcrowdninja.com`

**Submit with each report (if applicable):**
- Domain Type (organization/workspace)
- Domain ID(s) used
- Domain Tier (free/premium/business/enterprise)
- Attacker membership level(s)
- Victim membership level(s)
- Security Impact
- Emails of testing accounts used

---

## OOS Submission Types (Main App)

- Any repetitive network requests (DoS, rate limit testing)
- Forms on form.asana.com/form-beta.asana.biz you didn't create
- If you find credentials: report but do NOT log in (will be validated by Asana)
- Leaked passwords/tokens → points only, no money
- Leaked documents/files → points only
- Broken links, unowned domain links → points only
- HTTP 404 / non-200 codes
- Fingerprinting / banner disclosure
- Clickjacking
- Security best practices without exploitation PoC
- Weak login/signup/password without impact
- Cookie issues without impact
- Missing HTTP security headers
- Missing Secure/HttpOnly cookie flags
- 30-day zero-day grace period (publicly known vulns < 30 days old)
- Descriptive error messages
- EXIF data stripping
- Data destruction/corruption attacks
- Extending trial licenses

## OOS for Enterprise Technology Targets

- Clickjacking
- Broken link hijacking
- Firebase API key leakage without impact
- Session expiration issues (after logout, timeout, invalid on reset)
- Known vulnerable libraries without PoC
- Business logic issues without impact
- Unrestricted file upload without impact
- Google Maps/MapBox API key leaks
- External service interaction without impact
- Password complexity issues
- Post-based XSS without impact
- Blind SSRF without impact
- Self-XSS without impact
- CSRF on unauthenticated/non-sensitive forms
- MITM / physical access required
- Known vulnerable libraries without PoC
- CSV injection without PoC
- SSL/TLS configuration best practices
- Content spoofing without modifying HTML/CSS
- Rate limiting / brute force
- Missing CSP best practices
- Missing HttpOnly/Secure cookie flags
- Missing SPF/DKIM/DMARC
- Outdated browser only (< 2 versions behind latest stable)
- Software version/banner disclosure
- Zero-day with patch < 1 month old
- Tabnabbing, unlikely user interaction required, HTML injection without impact
- CRLF injection without impact
- Automated scanner reports
- DoS/DDoS activities
- Cache poisoning without impact
- Robots.txt/Sitemap.xml without impact
- User/email enumeration
- Cleartext password over HTTP without impact
- Dependency confusion
- EXIF geolocation data
- WordPress user disclosure
- Improper Cache-Control
- WordPress xmlrpc.php
- Open redirect without impact

---

## Focus Areas

### Role-Based Access Control (RBAC)
- Limited access member gaining access to restricted projects/areas
- Users elevating their own access levels
- Viewers commenting when they shouldn't

### Asana as OAuth Provider
- OAuth vulns in integrations built into Asana: https://app.asana.com/-/oauth_authorize
- Asana-made integrations (see integration list page)
- App components in integrations

### Admin Enforcement Bypass
- Enterprise domains with SAML/GSSO required — bypass during login/signup
- Admin settings: https://asana.com/features/admin-security/admin-console

### Prompt Injection (AI)
- Must have measurable security impact to Asana, not just model manipulation
- https://asana.com/product/ai, https://help.asana.com/s/article/ai-studio

### XSS + CSP
- Asana uses nonce-based CSP
- XSS blocked by CSP but P4 without CSP → reward as P4

---

## Notes

- Testing scope: all Asana.com domains except explicit exclusions
- Non-Asana-made apps on *.asana.plus → OOS (only Asana-built apps)
- Enterprise Technology: accepts subdomain takeovers (P4)
- Safe harbor: partial — comply with applicable laws
