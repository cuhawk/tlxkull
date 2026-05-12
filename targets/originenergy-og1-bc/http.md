# Origin Energy

> Platform: Bugcrowd — https://bugcrowd.com/engagements/originenergy-og1
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  https://www.originenergy.com.au/   # type: url
- in:  *.origindigital-pac.com.au   # type: wildcard
- in:  *.odcdn.com.au   # type: wildcard
- in:  dataportal.originenergy.com.au   # type: domain
- in:  *.support.originenergy.com.au   # type: wildcard
- in:  *.api.originenergy.com.au   # type: wildcard
- in:  *.download.originenergy.com.au   # type: wildcard
- in:  https://api.rx.originenergy.com.au/v1/gateway/schema/graphql   # type: url
- in:  https://api.rx.originenergy.com.au/v1/gateway/schema/kraken/graphql   # type: url
- in:  https://api.rx.originenergy.com.au/v1/lpg/graphql   # type: url
- in:  https://www.winconnect.com.au/moving-out/   # type: url
- in:  https://www.winconnect.com.au/get-connected/   # type: url
- in:  https://customerportal.winconnect.com.au/login   # type: url
- in:  portal.myconnect.com.au   # type: domain
- in:  myconnect.com.au   # type: domain
- in:  portal.myconnect.com.au/new-connection   # type: domain
- in:  hub.myconnect.com.au   # type: domain
- in:  ssu.staging.myconnect.com.au   # type: domain
- in:  portal.anz.kinergysolutions.com   # type: domain
- in:  portal-api.anz.kinergysolutions.com   # type: domain
- in:  portal.originzero.com.au   # type: domain
- in:  api-portal.originzero.com.au   # type: domain
- in:  sign.originzero.com.au   # type: domain
- in:  businessportal.origin.com.au   # type: domain
- in:  api-businessportal.origin.com.au   # type: domain
- out: https://www.originenergy.com.au/moving/   # type: url
- out: https://auth.api.originenergy.com.au/**   # type: url
- out: https://origin-energy.formstack.com/**   # type: url
- out: https://ssu.myconnect.com.au/   # type: url
- out: https://www.compareandconnect.com.au/   # type: url
- out: https://agent.compareandconnect.com.au/   # type: url
- out: https://fastconnect.co.nz   # type: url
- out: https://Yourporter.com.au   # type: url
- out: https://raywhitehomenow.com/   # type: url
- out: solarquotes.com.au/leads   # type: domain
- out: solarquotes.com.au/suppliers   # type: domain
- out: solarquotes.com.au/wp-admin   # type: domain
- out: manufacturers.solarquotes.com.au   # type: domain
- out: solarquotes.com.au/quote/start   # type: domain
- out: solarquotes.com.au/quotesv2   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
