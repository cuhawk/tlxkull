# Plusgrade Loyalty Public Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/plusgrade-mbb-public
> Type: Bug Bounty
> Bounty: P1 $4200–$5000 | P2 $2000–$2500 | P3 $450–$600 | P4 $150–$200
> Status: ACTIVE

## Scope

# Target table loading resources — inferred from CrowdStream activity and program context
# Known target from CrowdStream: *.points.com
# Plusgrade = loyalty platform for travel & hospitality (powers partner loyalty programs)
# Additional vanity targets in Loyalty-Vanity-Targets.txt attached to brief (761 bytes, added Oct 2024)
- in:  *.points.com   # type: wildcard  # confirmed from CrowdStream accepted submissions

## Out of scope

- out:  Corporate email and file storage
- out:  Corporate VPN
- out:  3rd party applications and services
- out:  Partner systems (without written approval)

## Auth

- type: session
- creds: own legitimate loyalty account (no credentials provided)
- notes: Use your own verified loyalty account; no test creds provided; unauthenticated testing permitted

## Notes

- safe harbor: yes
- status: ACTIVE
- Max 6 req/sec for automated tools
- Deep/magic links must include how obtained; found in search engines = P5 only
- Same vulnerability across shared-codebase group endpoints = single reward (no duplicates)
- Download Loyalty-Vanity-Targets.txt from Resources tab for additional in-scope domains
