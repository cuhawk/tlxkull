# Verisign Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/verisign
> Type: BBP
> Bounty: P1 $100–$10,000 | P2 $2,500 | P3 $1,500 | P4 $100–$500
> Status: In Progress
> Last scope update: (see program brief)

## Scope

- in:  *.verisign.com                      # type: wildcard  (confirmed via CrowdStream — primary domain)
- in:  www.verisign.com (website; non-DNS related)  # type: domain  (confirmed via CrowdStream)
- in:  blog.verisign.com (website; non-DNS related)  # type: domain  (confirmed via CrowdStream)
- in:  *.namestudio.com                    # type: wildcard  (confirmed via CrowdStream — domain name studio)
- note: DNS infrastructure itself has special handling (critical infrastructure)

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing

## Notes

- payout speed: validation within 4 days
- status: ACTIVE
- Technology / critical internet infrastructure; .com and .net registry; DNSSEC
- Safe harbor: yes (CFAA + DMCA exemptions)
- scope rating: 4/4
- 92 vulns rewarded; avg payout $1,333
- CrowdStream target labels note "(Website; non-DNS related)" — DNS infrastructure likely has stricter handling

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
