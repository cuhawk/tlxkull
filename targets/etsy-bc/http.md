# Etsy

> Platform: Bugcrowd — https://bugcrowd.com/engagements/etsy
> Type: VDP
> Bounty: P1 $5000–$10000 | P2 $1000–$5000 | P3 $300–$800 | P4 $100–$200
> Status: In progress

## Scope

- in:  https://www.etsy.com   # type: url
- in:  https://www.etsy.com/mobile   # type: url
- in:  https://www.etsy.com/developers/documentation/getting_started/api_basics   # type: url
- in:  https://etsypayments.com   # type: url
- in:  https://blog.etsy.com   # type: url
- in:  https://careers.etsy.com   # type: url
- in:  https://help.etsy.com   # type: url
- in:  https://community.etsy.com   # type: url
- in:  *.etsy.com   # type: wildcard
- out: icht.etsysecure.com   # type: domain

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
