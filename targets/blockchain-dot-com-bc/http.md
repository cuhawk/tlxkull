# Blockchain.com Managed Bug Bounty Engagement

> Platform: Bugcrowd — https://bugcrowd.com/engagements/blockchain-dot-com
> Type: BBP
> Bounty: P1 $7,000–$10,000 | P2 $3,000–$5,000 | P3 $700–$1,250 | P4 $100–$250
> Status: In Progress | Started: Apr 01 2025
> Last scope update: 22 Jan 2026

## Scope

- in:  blockchain.com (main platform + wallet + explorer + API)  # type: domain  (confirmed via CrowdStream)
- out: email-clicks.blockchain.com  (SendGrid)   # type: domain  (third-party; report to vendor first)
- out: support.blockchain.com       (ZenDesk)    # type: domain  (third-party; report to vendor first)
- out: blog.blockchain.com          (Medium)     # type: domain  (third-party; report to vendor first)
- out: docs.blockchain.com          (GitBook)    # type: domain  (third-party; report to vendor first)
- note: own DNS records for subdomains pointing to third-party ARE in scope

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: register at https://www.blockchain.com/wallet using @bugcrowdninja.com
- note: Security Learning Portal available for new researchers

## Notes

- payout speed: validation within 9 days
- status: ACTIVE
- Technology / crypto — wallet, explorer, API; pioneer since 2011
- Safe harbor: yes (CFAA + DMCA exemptions)
- scope rating: 2/4
- request header required: X-Bug-Bounty:<bugcrowdusername>
- N-day policy: in-scope 14 days after public release
- registering multiple wallets with same email is an intended feature (not a bug)
- out-of-scope: P5, DoS/DDoS, rate limit bypass, email bombing, social engineering, phishing, physical attacks, post-exploitation modification, third-party app vulns (without vendor report first)
- leaked credentials: points-only (no cash)
- third-party DNS subdomains of blockchain.com are in scope even if hosted by third parties

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
