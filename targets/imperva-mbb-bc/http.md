# Imperva - Thales Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/imperva-mbb
> Type: VDP
> Bounty: P1 $2100–$2500 | P2 $1000–$1250 | P3 $450–$600 | P4 $150–$200
> Status: In progress

## Scope

- in:  https://*.imperva.com   # type: url
- in:  https://*.cloudvector.com/   # type: url
- in:  https://www.cloudvector.com/   # type: url
- in:  https://*.incapsula.com   # type: url
- in:  https://supportportal.thalesgroup.com   # type: url
- out: http://docs.imperva.com/   # type: url
- out: http://docs-be.imperva.com/   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
