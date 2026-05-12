# Wise (ex-TransferWise) Bug Bounty — Bugcrowd BBP

**Program URL:** https://bugcrowd.com/engagements/wise  
**Category:** Finance / Safe harbor  
**Status:** ACTIVE  
**Started:** Jun 6, 2017  
**Scope rating:** 4 out of 4  
**Nondisclosure:** YES (non-disclosure policy in effect)  
**Avg payout:** ~$1,700 (last 3 months)

---

## Reward Tiers

| Priority | Range |
|----------|-------|
| P1 | $3,000 – $4,000 (max bonus: $6,000) |
| P2 | $1,000 – $1,500 |
| P3 | $300 – $500 |
| P4 | $100 – $150 |

P5 findings = no monetary reward.

---

## In-Scope Targets

- in: *.wise.com  # type: wildcard — primary target
- in: *.transferwise.com  # type: wildcard — legacy domain
- in: https://sandbox.transferwise.tech  # Wise API sandbox

---

## Out-of-Scope Targets

(Loading resources — full list not rendered; apply general OOS rules below)

---

## Account Setup

- Register at https://wise.com with `<bugcrowdusername>@bugcrowdninja.com`
- Alias emails for multi-account testing: `<bugcrowdusername>+1@bugcrowdninja.com`
- Test transactions: **< £20 or equivalent**; cancel via UI after flow completion
- Do NOT use real e-mail addresses unless specifically required for the bug

---

## Focus Areas

### Multi-User Access (MUA — High Priority)
- Business accounts allowing multiple users to access one account
- Managing users: invite/remove/role changes
- Bypassing role-based permissions
- Cross-account/profile unauthorized interaction
- Setup: create Wise for Business account (name clearly identifies test purpose)

### Wise API
- Docs: https://api-docs.wise.com
- Sandbox: https://sandbox.transferwise.tech
- API misuses with significant business/customer impact

### Multi-Factor Authentication (MFA)
- SMS and app-based authentication
- Device registration/deactivation flows
- MFA bypass vectors
- Note: SS7/SIM infrastructure vulnerabilities = OOS

### SCA / PSD2 (EEA Customers)
- SCA bypass for: statement downloads, money sends, profile obfuscation timeout, revealing PIN/card details
- Facebook/Google account holders in EEA now require password for above actions

### Wise Card
- Card management, account services, card freeze
- Requires verified account + multi-currency account

---

## Out-of-Scope Submission Types

- Missing SPF/DMARC on non-mail-sending domains
- Email spoofing where SPF/DKIM/DMARC configured but recipient ignores failures
- DoS via excessive requests
- Attacks against customer support (contact forms, phone lines)
- Vulnerabilities only in vendor-EOL browsers/platforms
- Public API keys by design (check vendor docs)
- X-Frame-Options header (deprecated), X-XSS-Protection, other missing HTTP security headers without PoC impact
- Sample secrets/passwords in GitHub if documentation marks them as samples
- Self-XSS, XSS requiring local access
- Physical attacks against premises/employees
- Rooted/jailbroken phone required attacks
- Typosquatting/punycode domain registrations (unless actually in use by Wise production)
- MITM attacks requiring 3rd-party CA installed on system
- Default scanner output without PoC
- Prometheus endpoint exposure
- KYC-related reports
- Public leaked credential databases (unless Wise employee credentials with successful internal login PoC)

### Usually P5 Unless PoC Demonstrates Real Impact
- Internal DNS/IP/path disclosures
- Descriptive error messages
- Clickjacking without PoC targeting Wise specifically
- Weak TLS configuration
- EXIF metadata on files (unless GPS on customer photos)
- Broken links to expired domains
- Android/iOS attacks requiring malicious co-installed app (if no feasible defense)
- Missing Secure/HttpOnly/SameSite cookie flags (non-secret storage cookies)
- Fingerprinting/banner/version disclosure
- CSRF on public forms
- Autocomplete/save password
- Cache-Control: private data leakage
- Missing best practices without realistic attack scenario

---

## Rules

- Automated scanners allowed but: exercise common sense, max 6 req/sec for targeted testing, use authenticated Bugcrowd test account, add User-Agent identifying as researcher
- Only interact with test accounts you own
- No extortion
- Use Bugcrowd channel for vulnerability discussion
- Wise employees cannot participate
- Third-party library bugs: forwarded without reward
- Remediation SLA: 1–180 days depending on severity

---

## Notes

- PGP: `C8A1 9A40 C078 006A 4FD2 5F88 EC52 91DC 8DC2 8D45` (pgp.mit.edu)
- SOC email: soc@wise.com
- Wise runs automated Acunetix/Zap/Nessus scans — targeted manual testing more valuable
- Some pay-in methods incur transaction fees (non-refundable); use bank transfers for no fees
- Wise has background/async fraud checks — PoC verification may require time
