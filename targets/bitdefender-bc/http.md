# Bitdefender

> Platform: Bugcrowd — https://bugcrowd.com/engagements/bitdefender
> Type: BBP
> Bounty: P1 $3500–$15000 | P2 $1500–$5000 | P3 $200–$1000 | P4 $100–$500
> Status: In progress

## Scope

- in:  *.bitdefender.net   # type: wildcard
- in:  *.bitdefender.com   # type: wildcard
- in:  https://www.bitdefender.com/business/smb-products/business-security.html   # type: url
- out: businessinsights.bitdefender.com   # type: domain
- out: businessemail.bitdefender.com   # type: domain
- out: businessresources.bitdefender.com   # type: domain
- out: oemhub.bitdefender.com   # type: domain
- out: oemresources.bitdefender.com   # type: domain
- out: community.bitdefender.com/   # type: domain
- out: resellerportal.bitdefender.com/   # type: domain
- out: brand.bitdefender.com/   # type: domain
- out: stats.bitdefender.com/   # type: domain
- out: sstats.bitdefender.com/   # type: domain
- out: lsems.gravityzone.bitdefender.com/   # type: domain
- out: ssems.gravityzone.bitdefender.com/   # type: domain
- out: crp.bitdefender.com   # type: domain
- out: telcosuccess.bitdefender.com   # type: domain
- out: demo.bitdefender.com   # type: domain
- out: translate.bitdefender.com   # type: domain
- out: explore.bitdefender.com   # type: domain
- out: explore-lb.bitdefender.com   # type: domain
- out: partner-marketing.bitdefender.com   # type: domain
- out: seems.gravityzone.bitdefender.com   # type: domain

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
