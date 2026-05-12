# Viator

> Platform: Bugcrowd — https://bugcrowd.com/engagements/viator
> Type: BBP
> Bounty: P1 $6000 | P2 $3000 | P3 $1000 | P4 $300
> Status: In progress (started Jun 06, 2022)

## Scope

- in:  https://www.viator.com   # type: url
- in:  https://*.viator.com   # type: url
- out: *.rc.viator.com   # type: wildcard
- out: *.sandbox.viator.com   # type: wildcard
- out: agentcenter.viator.com   # type: domain
- out: api.tapayments.com   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- validation within: 14 days
- avg payout: $300 (last 3 months)
- safe harbor: yes
- industry: Technology
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
