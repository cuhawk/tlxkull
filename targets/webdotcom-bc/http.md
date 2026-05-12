# Web.com Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/webdotcom
> Type: BBP
> Bounty: P1 $2,000–$3,000 | P2 $1,000–$1,500 | P3 $250–$600 | max $5,000
> Status: In Progress | Started: Apr 13 2017
> Last scope update: 08 May 2026

## Scope

- in:  www.web.com                       # type: domain
- in:  www.networksolutions.com          # type: domain  (confirmed via CrowdStream)
- in:  www.bluehost.com                  # type: domain  (confirmed via CrowdStream)
- in:  www.hostgator.com                 # type: domain  (confirmed via CrowdStream)
- in:  authenticated subdomains of above after login flow  # type: wildcard
- out: *.bluehost.com (subdomains)       # type: wildcard  (per Mar 2024 scope change)
- out: *.hostgator.com (subdomains)      # type: wildcard  (per Mar 2024 scope change)
- out: app.gator.com                     # type: domain
- out: any unlisted assets               # type: other
- note: VDP available for NetworkSolutions/HostGator/Bluehost unlisted assets

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: no reimbursement for charges incurred during signup

## Notes

- payout speed: validation within 5 days
- status: ACTIVE
- Technology / web hosting; Newfold Digital subsidiary brands; 716 vulns rewarded
- Safe harbor: yes (CFAA + DMCA exemptions)
- NDA: no disclosure allowed
- scope rating: 1/4
- request headers required:
  - X-Request-Purpose: Research  (required)
  - X-Bugcrowd-Ninja: [username]  (optional)
- scan only during regular business hours (PDT) — production sites
- XSS in user-controlled website builder HTML pages not eligible for bounty
- XSS max severity: medium (P3)
- uses CVSS scoring not VRT
- report format: must use ordered list of reproduction steps
- out-of-scope: DDoS/AppDoS, DMARC/SPF, OAuth logout session token, open redirect, verbose errors/version disclosure, clickjacking, email spoofing, missing HTTP headers, HTTP/DNS cache poisoning, Cloudflare issues, self-XSS, broken links, external-source API key leaks, CSRF on non-sensitive forms, <30d 0-days, chatbox testing, third-party vuln components, anti-automation/captcha/rate-limit, source code disclosure, info.php, subdomain takeovers (use VDP)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
