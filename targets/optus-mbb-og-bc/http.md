# Optus Managed Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/optus-mbb-og
> Type: BBP
> Bounty: P1 $4,200–$5,000 | P2 $2,000–$2,500 | P3 $250–$600 | P4 $150–$200
> Status: In Progress | Started: Jan 17 2023
> Last scope update: 24 Mar 2026

## Scope

- in:  optus.com.au (main domain + subdomains per scope groups)   # type: wildcard
- in:  My Optus app (iOS/Android)                                 # type: other
- in:  Optus AI Search (My Optus app LLM feature)                 # type: other
- in:  Infrastructure targets (speed test regional subdomains)    # type: domain
- out: Optus Sport Pre Production                                  # type: domain
- out: Optus Sport Production                                      # type: domain
- out: third-party provider subdomains of in-scope domains         # type: wildcard
- note: full target lists load dynamically — check Bugcrowd brief for current list

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: self sign-up where applicable; no refunds for charges incurred

## Notes

- payout speed: validation within 4 days
- status: ACTIVE
- Telecommunications / Australia; 310 vulns rewarded historically
- Safe harbor: yes (CFAA + DMCA exemptions)
- request header required: BUGCROWD: <username> on all traffic
- do NOT use live support chat on target website — use Bugcrowd support portal only
- throttle automated scanning tools carefully
- AI Search focus areas: prompt injection, insecure LLM output handling, sensitive info disclosure
- app-level DDoS: submit finding first and request permission before PoC
- out-of-scope: network DoS/DDoS, third-party providers, leaked/customer credentials
- infrastructure targets share codebase — duplicates if in template

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
