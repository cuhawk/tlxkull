# TheFork Managed Bug Bounty — Bugcrowd

**URL:** https://bugcrowd.com/engagements/thefork-mbb-og
**Category:** BBP
**Safe harbor:** Yes
**Disclosure:** Coordinated (explicit permission required)
**Started:** 2025-12-09
**Industry:** Hospitality

## CRITICAL RULE
USE ONLY TEST RESTAURANTS. Testing on live production restaurants or their systems is strictly prohibited — will result in program ban.

## Auth / account setup
- B2C: Register with @bugcrowdninja.com email
- B2B: Use credentials provided by TheFork inside the program file (DO NOT change restaurant password)
- User-Agent: include string "bugcrowd"; add "bugcrowd" to form fields not requiring account info
- Automated testing: max 25 req/sec
- Test restaurants: 500 test restaurants provided (link in program resources)
- Payment testing (TFPay): log in with @bugcrowd.com or @bugcrowdninja.com, make reservation at test restaurant, payment window opens at dining time for max 3hrs, max 2 payments per reservation

## Current OOS (temp)
- B2B assets are temporarily OOS as of 2026-04-23 (internal review) — B2B credentials no longer valid

## Targets

### B2C (P1=$2,500–3,500)
- in: https://www.thefork.com
- in: TheFork iOS App
- in: TheFork Android App
- in: api.thefork.com (B2C API)
- in: google-reserve-api.thefork.io

### B2B (P1=$2,500–3,500) — TEMP OOS
- in: manager.thefork.com (B2B web app) — temp OOS
- in: TheFork Manager iOS App — temp OOS
- in: TheFork Manager Android App — temp OOS

### B2C Low Reward (P1=$500–1,000)
- in: *.tools.thefork.tech (internal tools, some reachable only internally)
- in: developer.thefork.io (all issues ranked P4)
- in: www.restaurant-information.com

### B2B Low Reward (P1=$500–1,000)
- in: *.tools.thefork.tech

## Rewards
| Tier | P1 | P2 | P3 | P4 |
|------|-----|-----|-----|-----|
| B2C / B2B (main) | $2,500–3,500 | $1,500–1,750 | $500–700 | $150–300 |
| B2C / B2B (low reward) | $500–1,000 | $200–400 | $100–200 | $50–100 |

## Out of scope
- All lafourchette.com domains (api.lafourchette.com, etc.)
- Other TheFork brand domains: www.lafourchette.com, www.eltenedor.es, thefork.* variants not listed
- DoS / DDoS
- Social engineering
- Mass account creation / spamming
- Content fraud (rating inflation/deflation)
- Rate limiting
- HTTP security headers
- SSL/TLS issues
- 3rd party vulnerabilities (Stripe, Amilon)
- Contacting customer support
- IDORs: currently P5 Informational (B2C only; B2B ranked normally) — fix in progress
- BACs: currently P5 Informational — fix in progress
- Broken social media links (Social Broken Link) = Informational

## Expected/non-vuln behaviors
- Booking only requires email + first/last name + phone; ownership not verified
- Email enumeration is expected behavior
- Booking with someone else's email is expected
- 5-min session invalidation delay after logout/password reset = expected
- Weak password policy = not a vuln

## Technical notes
- B2B JWT TTL: 5 minutes; sessions invalidated 5 min after logout or password reset
- B2B API: black box only (no documentation available)
- Redirection to *.theforkmanager.com may occur during auth — that domain is OOS
- developer.thefork.io: all findings ranked P4

## Focus areas
- B2C: account manipulation, auth bypass, password reset, payment (TFPay, gift cards, Yums), XSS, CSRF, IDOR, SQLi, JWT, GraphQL, PII exposure
- B2B: account manipulation, auth, PII, JWT/GraphQL
- Cross-platform: B2C↔B2B data leakage, privilege escalation, shared auth vulns
