# Gearset: Managed Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/gearset-mbb
> Type: BBP
> Bounty: P1 $5000–$6000 | P2 $1500–$4000 | P3 $600–$850 | P4 $200–$250
> Status: In progress (started Feb 02, 2021)
> Last scope update: 10 Apr 2026

## Scope

- in:  https://staging.gearset.com/   # type: url
- in:  https://hipaa.staging.gearset.com/   # type: url
- in:  https://staging.claytonapp.com   # type: url
- in:  https://staging.claytonapp.com/api   # type: url
- out: api.gearset.com   # type: domain
- out: app.gearset.com   # type: domain
- out: us.app.gearset.com   # type: domain
- out: eu.app.gearset.com   # type: domain
- out: ap.app.gearest.com   # type: domain
- out: gearset.com   # type: domain
- out: app.clayton.io   # type: domain
- out: getclayton.com   # type: domain
- out: api.clayton.io   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- validation within: 14 days
- avg payout: $821 (last 3 months)
- vulns rewarded: 114
- safe harbor: yes
- disclosure: standard Bugcrowd terms
- industry: Technology
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
