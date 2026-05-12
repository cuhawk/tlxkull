# FIS Bug Bounty — Bugcrowd BBP

**Program URL:** https://bugcrowd.com/engagements/fis  
**Category:** Finance / Safe harbor  
**Status:** ACTIVE  
**Started:** Aug 10, 2021  
**Avg payout:** $8,642.50  
**Nondisclosure:** YES

---

## Reward Tiers

| Priority | Range |
|----------|-------|
| P1 | $10,000 – $20,000 |
| P2 | $2,500 – $10,000 |
| P3 | $200 – $2,500 |
| P4 | $0 – $200 |

---

## Required Headers

All requests **must** include:
```
X-Bug-Bounty: Bugcrowd-<your-username>
```
- Missing header → **75% reward reduction**
- Repeat offense (2nd+ time missing) → **non-payment**
- Include `Bugcrowd Bug Bounty` in plaintext in all requests for SOC deconfliction

---

## In-Scope Targets

- in: **Any FIS asset is in scope** (broad scope — all FIS-owned assets unless explicitly excluded below)

---

## Out-of-Scope Targets

### Specific OOS Domains / Assets

**Bank portals & third-party portals:**
- out: ap.acg.aaa.com
- out: creditportal.arvest.com
- out: *.avantgardportal.com
- out: *.avantgardsolutions.com
- out: *.avantgardtreasury.com
- out: *.automatedfinancial.com
- out: *.internet-estatements.com
- out: woseforms.fisglobal.com
- out: *.regulatoryu.com (Regulatory University)
- out: relius.net / Relius assets
- out: FIS IdP Codebase/Assets
- out: Sungard assets
- out: Sedgwick assets
- out: AvantGard assets (all)

**Payrix assets** (all Payrix-branded infrastructure)

**Worldpay assets** (all Worldpay-branded infrastructure)

**WSO2 applications** (all WSO2-branded instances)

**All GitHub / Postman repos** → OOS  
**All credential leaks** → OOS (closed, not paid)

---

## Rules & Constraints

### Rate Limiting
- Max **5 requests/second** automated tooling
- Non-US IPs and Digital Ocean IPs may be **restricted / blocked**

### RCE Handling
- Must **report within 3 hours** of exploitation
- Only non-intrusive PoC allowed: `whoami`, `hostname`, `ls` — no destructive commands

### ATO (Account Takeover)
- Do **NOT** actually take over accounts
- Contact **Bugcrowd Support first** before demonstrating ATO

### Temporarily OOS (as of Apr 18, 2026)
- **Auth bypass** vulnerabilities — temporarily OOS during remediation review
  (re-check status before submitting)

### Permanently OOS (by type)
- Mobile application vulnerabilities
- Reflected XSS
- DOM XSS
- Subdomain takeovers
- CSRF
- Open redirects
- Brute force / credential stuffing / leaked/guessed credentials
- End-user credential usage
- PII in reports → closed and not paid (must redact all screenshots)

### Production Write Actions
- Forbidden **except** on self-created test records

### Scope Cooldown
- If a target accumulates $50k in payouts within 30 days → **scope removal for evaluation**

---

## Notes

- Program averages ~$8.6k per valid submission — high signal expected
- Broad "any FIS asset" scope means subdomain enumeration is valuable
- Auth bypass temp OOS: check program brief before submitting auth bypass chains
- Non-US/DO IPs blocked from some FIS infrastructure — test from US IP
