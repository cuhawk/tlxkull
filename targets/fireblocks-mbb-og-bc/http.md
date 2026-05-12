# Fireblocks Web Managed Bug Bounty Engagement

> Platform: Bugcrowd — https://bugcrowd.com/engagements/fireblocks-mbb-og
> Type: BBP
> Bounty: P1 $7,000–$12,000 | P2 $1,000–$9,000 | P3 $300–$1,500 | P4 $20–$300
> Status: In Progress | Started: Sep 09 2025
> Last scope update: 12 Feb 2026

## Scope

- in:  sandbox-api.fireblocks.io          # type: api   (confirmed via CrowdStream)
- in:  app.fireblocks.com (web console)   # type: domain
- out: any non-Fireblocks property        # type: other
- note: target list loads dynamically — check Bugcrowd brief for full list

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email — required for registration
- note: register at https://console.fireblocks.io using @bugcrowdninja.com ONLY
- docs: https://developers.fireblocks.com/docs/sandbox-quickstart
- docs: https://developers.fireblocks.com/docs/postman-guide

## Notes

- payout speed: validation within 13 days
- status: ACTIVE
- Computer Software / crypto custody platform (MPC + SGX); enterprise-grade
- Safe harbor: yes (CFAA + DMCA exemptions)
- scope rating: 1/4
- focus areas: unauthorized funds transfer, PII disclosure, XSS, CSRF (sensitive privileged), RCE, auth/authz bypass, IDOR, SQLi/XMLi, directory traversal, security misconfig
- N-day policy: in-scope 14 days after public release
- out-of-scope: P5, DoS/DDoS, rate limit, email bombing, social engineering, phishing, physical attacks, third-party providers, post-exploitation modification/destruction
- leaked credentials: points-only compensation, no cash bounty

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
