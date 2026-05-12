# SpaceX/Starlink

> Platform: Bugcrowd — https://bugcrowd.com/engagements/spacex
> Type: BBP
> Bounty: Web/net P1 up to $50,000 | Hardware up to $100,000
> Status: In progress (started Oct 22, 2020)
> Self-managed: SpaceX triages all submissions (not Bugcrowd)

## Scope

### Web / Network
- in:  *.spacex.com   # type: wildcard — except shop.spacex.com
- in:  *.starlink.com   # type: wildcard — except gear.starlink.com and customer.*.isp.starlink.com
- in:  https://apps.apple.com/   # type: ios_app — Official Starlink iOS app
- in:  https://play.google.com/   # type: android_app — Official Starlink Android app
- in:  192.31.242.0/23   # type: cidr
- in:  206.214.229.128/29   # type: cidr
- in:  135.129.252.112/31   # type: cidr
- in:  206.214.239.8/30   # type: cidr
- in:  63.208.93.16/29   # type: cidr
- in:  66.9.191.192/28   # type: cidr
- in:  199.175.188.0/24   # type: cidr
- in:  4.7.106.0/28   # type: cidr
- in:  4.34.86.130/31   # type: cidr
- in:  4.34.86.132/31   # type: cidr
- in:  4.34.86.134/32   # type: cidr

### Product / Infrastructure (report to vulnerabilityreporting@spacex.com, not Bugcrowd)
- in:  *.starlinkisp.net   # type: wildcard — except customer.*.pop.starlinkisp.net
- in:  2620:134:b000::/40   # type: cidr_v6
- in:  Hardware owned/authorized (Starlink Dish/Router)

### Excluded IPs (within above CIDR ranges — OOS)
- out: 192.31.242.107/108/109/111/112/113/115/116/120
- out: customer.*.pop.starlinkisp.net
- out: customer.*.isp.starlink.com
- out: shop.spacex.com
- out: gear.starlink.com

## Auth

- type: signup
- creds: Self-signup on starlink.com with personal email for Starlink hardware (paid)
- note: No credentials/hardware provided by SpaceX for testing

## Notes

- safe harbor: yes (CFAA + DMCA)
- disclosure: coordinated (requires explicit request per submission)
- status: ACTIVE
- Self-managed by SpaceX — average payout $5,634 (very high)
- Hardware/satellite issues: email vulnerabilityreporting@spacex.com directly (with GPG encryption if needed)
- AI-assisted reports: SpaceX reserves right to reject low-quality AI-generated reports
- Physical attacks against larger infrastructure: PROHIBITED; own Dish testing OK
- Do NOT chain exploits or post-exploit on satellites — stop and report immediately

## Reward Structure (Web/Network)

- RCE: up to $50,000
- SQLi: $500–$50,000
- XSS: $100–$10,000
- CSRF: $100–$5,000
- Auth bypass: up to $50,000
- Horizontal priv esc: $500–$10,000
- Vertical priv esc: $500–$50,000
- Hardware (Dish/satellite): case-by-case up to $100,000

## OOS Vuln Types

- Lack of MFA, open redirects, internal IP disclosure
- Non-sensitive file exposure (robots.txt, .gitignore, etc.)
- Social engineering / phishing, self-XSS
- environment.js file exposure (intentionally public)
- Text injection, email spoofing
- Descriptive error messages, fingerprinting/banner disclosure
- Clickjacking, CSRF without account integrity impact
- Login brute force, rate limiting/DoS
- Missing security headers, TLS/SSL issues (except Starlink hardware edge cases)
- Standard WPA cracking, phpinfo() leaks (without creds)
- Physical attacks on SpaceX facilities
- Leaked customer credentials from client-side issues
