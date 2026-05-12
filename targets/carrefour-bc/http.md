# carrefour — Majid Al Futtaim Retail / Carrefour UAE Bug Bounty (Bugcrowd)

platform: bugcrowd
program_url: https://bugcrowd.com/engagements/carrefour
category: bbp
safe_harbor: full
disclosure: nondisclosure (no public disclosure allowed)
credentials: self-register with @bugcrowdninja.com email

## Rewards

| P1 | P2 | P3 | P4 (upgraded to P3) |
|----|----|----|----|
| $3,000–$4,000 | $2,100–$2,500 | $150–$750 | $150–$200 |

Note: Valid P4 reports upgraded to P3 and paid at $150–$200.

## Scope

### In-scope targets (MAF-Retail group)

- in: Carrefour UAE web e-commerce UAT instance — type: web (targets geo-blocked by Akamai; use VPN from brief)
- in: Carrefour UAE mobile applications (iOS + Android) — type: mobile (APIs point to production)
- in: APIs used by in-scope mobile applications — type: api

Note: UAT web instance has full production functionality including product sorting, purchase, and payment.

## Credentials / Access

- Register with @bugcrowdninja.com email
- Targets geo-blocked by Akamai — use VPN connection provided at bottom of the brief
- Test cards (checkout only): https://www.cybersource.com/developers/other_resources/quick_references/test_cc_numbers/ (Visa + Mastercard test cards)
- Authentication issues on identity.majidalfuttaim.com → report to MPASS program instead

## Focus Areas

- Payment cycle: buying without completing payment, manipulation of payment amount
- Ability to buy goods without payment
- Unauthorized reward points modification (earning or burning)
- Remote access to other user's PCI/credit card details
- Remote access to other user's personal details
- Exfiltration of personal data or credit card data
- Remote unauthorized access to MAF Carrefour database
- Voucher/promo code abuse
- RCE and defacement

## OOS

- Placing real cash on delivery orders (PROHIBITED — has disrupted business operations)
- Modifying data in accounts not belonging to you
- Accessing/downloading data beyond 1-2 records
- DoS / volumetric attacks
- Malicious software / backdoors
- Social engineering / phishing
- Interacting with real end users
- Credential stuffing / leaked credentials
- DMARC issues
- Third-party integrations
- System configuration changes
- Public zero-day vulns within 15 business days of official patch

## Notes

- Part of Majid Al Futtaim group (same as majidalfuttaim-loyalty but separate program)
- identity.majidalfuttaim.com auth issues → MPASS program
- Nondisclosure
- Program occasionally paused during high-traffic events (e.g., Anniversary Sale)
