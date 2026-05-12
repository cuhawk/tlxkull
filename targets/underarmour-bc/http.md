# Under Armour Product Security

> Platform: Bugcrowd — https://bugcrowd.com/engagements/underarmour
> Type: BBP
> Bounty: P1 $1200–$2500 | P2 $1000–$1200 | P3 $400–$600 | P4 $125
> Status: In Progress (started Sep 08, 2016)
> Last scope update: Dec 01, 2025

## Scope

- in:  www.underarmour.com   # type: wildcard
- in:  www.underarmour.co.uk   # type: wildcard
- in:  UA Shop iOS (https://apps.apple.com/us/app/under-armour/id1092704571)   # type: ios_app
- in:  UA Shop Android (https://play.google.com/store/apps/details?id=com.ua.shop)   # type: android_app
- in:  https://api.shop.ua.com/graphql   # type: api
- in:  https://www.underarmournext.co.uk/   # type: url
- in:  https://underarmournext.com/   # type: url
- in:  *.api.ua.com   # type: wildcard
- in:  https://consumer-sustainability.underarmour.com/en   # type: url
- in:  vpe-us.underarmour.com   # type: domain
- in:  *.underarmour.cn   # type: wildcard
- in:  www.underarmour.com.sg   # type: domain
- in:  underarmour.co.kr   # type: domain
- in:  https://armourhouse.underarmour.com   # type: url
- out: www.underarmour.com/en-us/affiliate-home   # type: url
- out: www.uabiz.com   # type: domain
- out: investor.underarmour.com   # type: domain
- out: productsafety.underarmour.com   # type: domain
- out: uabusiness.force.com   # type: domain
- out: www.underarmour.jobs   # type: domain
- out: blog.underarmour.com   # type: domain
- out: www.uateamcatalogs.com   # type: domain
- out: www.uaretail.com   # type: domain
- out: www.plankindustries.com   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- payout speed: 7 days (validation)
- status: ACTIVE
- request header required: X-Request-Purpose: BugcrowdResearch
- Retail industry; safe harbor program
- Test accounts must use @bugcrowdninja.com email
- Blackout period: Nov 20 – Dec 3 (no active testing)
- Out of scope: SPF/DMARC issues, DoS/DDoS, attacking other users, admin portals, infra attacks
- API base: api.shop.ua.com/graphql; developer portal at developer.underarmour.com
- Focus areas: athlete data integrity, availability, confidentiality

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
