# HostGator LATAM Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/hostgator-latam-bb
> Type: BBP
> Bounty: P1 $1,500–$2,500 | P2 $750–$1,500 | P3 $250–$450
> Status: In Progress | Started: Feb 01 2022
> Last scope update: 24 Apr 2026

## Scope

- in:  hostgator.com.br                     # type: domain  (main in-scope domain, per announcement)
- in:  authenticated subdomains of hostgator.com.br  # type: wildcard  (post-login flows with navigation)
- out: carrinho.hostgator.com.br            # type: domain  (removed Apr 2025)
- out: customer-controlled subdomains of hostgator.com.br  # type: wildcard
- out: any unlisted asset                   # type: other

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: no provided credentials; self-signup; no reimbursement for charges

## Notes

- payout speed: validation within 7 days
- status: ACTIVE
- Technology / web hosting; HostGator LATAM (Newfold Digital); Brazil market
- Safe harbor: yes (CFAA + DMCA exemptions)
- NDA: no disclosure allowed
- scope rating: 1/4
- uses CVSS scoring not VRT
- XSS max severity: medium (P3)
- out-of-scope: DMARC/SPF, DoS/DDoS/rate-limit, OAuth logout session token, open redirect, verbose errors, clickjacking, missing HTTP headers, HTTP/DNS cache poisoning, Cloudflare issues, self-XSS, broken links, external-sourced API keys, CSRF non-sensitive, <30d 0-days, chatboxes, third-party vuln components, anti-automation/captcha, source code disclosure, info.php, subdomain takeovers (use VDP)
- do not create multiple accounts; no brute force; no social engineering
- do not interact with real customer accounts
- Newfold Digital subsidiary — no employees/vendors eligible

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
