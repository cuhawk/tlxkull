# Rapyd

> Platform: Bugcrowd — https://bugcrowd.com/engagements/rapyd
> Type: BBP
> Bounty: Tier3/API: P1 $5,000–$7,500 | P2 $1,500–$4,500 | P3 $600–$1,400 | P4 $100–$500 | Tier2/Dashboard: P1 $2,800–$5,500 | P2 $1,300–$2,500 | P3 $400–$1,200 | P4 $100–$400 | Tier1: P1 $1,250–$3,000 | P2 $650–$1,200 | P3 $300–$600 | P4 $100–$300
> Status: In Progress | Started: Nov 01 2022
> Last scope update: 10 Mar 2026

## Scope

- in:  api.rapyd.net                    # type: api       (Tier 3 — highest bounty; sandbox only for API testing)
- in:  dashboard.rapyd.net              # type: domain    (Tier 2 — Client Portal; sandbox + production)
- in:  *.rapyd.org                      # type: wildcard  (Tier 1)
- in:  checkout pages (rapyd.net)       # type: domain    (Tier 2)
- in:  verify.rapyd.net (iframe)        # type: domain    (Tier 2)
- out: *.neatcommerce.com               # type: wildcard  (removed Mar 2026)
- out: *.neattest.com                   # type: wildcard  (removed Mar 2026)
- out: *.neat.com.hk                    # type: wildcard  (removed Mar 2026)
- out: *.neat.hk                        # type: wildcard  (removed Mar 2026)
- out: *.neat.wtf                       # type: wildcard  (removed Mar 2026)
- out: third-party hosted support forms # type: other
- out: contact/submission form automation

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: sign up at dashboard.rapyd.net; select Iceland as country for production mode
- note: select UK as country for Rapyd Verify testing

## Notes

- payout speed: validation within 6 days
- status: ACTIVE
- Finance / FinTech-as-a-service; cross-border payments + stablecoin (USDC)
- Safe harbor: no (not listed)
- request header required: X-Bugcrowd-<Username> on every request (Burp config available: rapyd-burp-configuration.json)
- Stablecoin promotion ended Apr 20 2026 (bonus: P1 +$1000, P2 +$500)
- API tier gets highest bounty; use sandbox only for api.rapyd.net
- PCI findings (card data disclosure) get +$500 minimum bonus
- No disclosure allowed (NDA program)
- out-of-scope: DNS attacks, UDP flood, social engineering, automated form scanning, clickjacking on no-action pages, CSRF on unauthed forms, MITM-only, old libs without PoC, CSV injection without PoC, SSL/TLS best practices, DoS, rate-limit on non-auth endpoints, HttpOnly/Secure cookie flags, missing SPF/DKIM/DMARC, tabnabbing, open redirect without extra impact
- Rate limiting enforced on cloud; do not exceed normal request rates
- Must include HTTP request+response in every report
- Include operation ID if provided in response

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
