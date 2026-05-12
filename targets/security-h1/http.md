# HackerOne

> Platform: HackerOne — https://hackerone.com/security
> Type: BBP
> Bounty: Low $200 | Medium $1,000–$1,500 | High $3,000–$7,000 | Critical $6,000–$15,000
> Avg bounty: $500–$500
> Response efficiency: 100% | Avg first response: N/A | Total paid: $1,986,889
> Last scope update: 2026-02-03

## Scope

- in:  hackerone.com    # type: url # max: critical
- in:  api.hackerone.com    # type: url # max: critical
- in:  www.hackerone.com    # type: url # max: critical
- in:  app.pullrequest.com    # type: url # max: critical
- in:  reviewer.pullrequest.com    # type: url # max: critical
- in:  hackerone-us-west-2-production-attachments.s3.us-west-2.amazonaws.com    # type: url # max: critical
- in:  www.wearehackerone.com    # type: url # max: critical
- in:  mta-sts.wearehackerone.com    # type: url # max: critical
- in:  errors.hackerone.net    # type: url # max: high
- in:  https://*.hackerone-ext-content.com    # type: url # max: medium
- in:  a5s.hackerone-ext-content.com    # type: url # max: medium
- in:  b5s.hackerone-ext-content.com    # type: url # max: medium
- in:  hackerone-ext-content.com    # type: url # max: medium
- in:  https://*.hackerone-user-content.com/    # type: url # max: low
- in:  ctf.hacker101.com    # type: url # max: low
- in:  hackathon-photos.hackerone-user-content.com    # type: url # max: low
- in:  cover-photos.hackerone-user-content.com    # type: url # max: low
- in:  hackathon-photos-us-east-2.hackerone-user-content.com    # type: url # max: low
- in:  profile-photos.hackerone-user-content.com    # type: url # max: low
- in:  hackerone-user-content.com    # type: url # max: low
- in:  profile-photos-us-east-2.hackerone-user-content.com    # type: url # max: low
- in:  cover-photos-us-east-2.hackerone-user-content.com    # type: url # max: low
- in:  hackerone.live    # type: url # max: low
- in:  *.vpn.hackerone.net    # type: other # max: critical
- in:  https://github.com/Hacker0x01/react-datepicker    # type: other # max: critical # not eligible for bounty
- in:  66.232.20.0/23    # type: cidr # max: critical
- in:  206.166.248.0/23    # type: cidr # max: critical
- in:  hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  hackerone.com    # type: url # max: critical # not eligible for bounty
- in:  https://ctf.hacker101.com    # type: url # max: low
- in:  https://reviewer.pullrequest.com    # type: url # max: critical
- in:  https://app.pullrequest.com    # type: url # max: critical
- in:  https://hackerone-us-west-2-production-attachments.s3-us-west-2.amazonaws.com/    # type: url # max: critical
- in:  *.hackerone-ext-content.com    # type: other # max: medium
- in:  *.hackerone-user-content.com    # type: other # max: low
- in:  http://hackerone.com/graphql    # type: url # max: critical # not eligible for bounty
- in:  hackerone-attachments.s3.amazonaws.com    # type: url # max: critical
- out:  support.hackerone.com    # type: url # max: none
- out:  go.hacker.one    # type: url # max: none
- out:  info.hacker.one    # type: url # max: none
- out:  ma.hacker.one    # type: url # max: none
- out:  h1.community    # type: url # max: none
- out:  www.h1.community    # type: url # max: none
- out:  www.hackeronestatus.com    # type: url # max: none
- out:  hackerone-swag.com    # type: url # max: none
- out:  app.qualified.dev    # type: url # max: none
- out:  qualified.dev    # type: url # max: none
- out:  https://ma.hacker.one    # type: url # max: none
- out:  https://info.hacker.one/    # type: url # max: none
- out:  https://www.hackeronestatus.com/    # type: url # max: none
- out:  https://go.hacker.one    # type: url # max: none
- out:  events.hackerone.com    # type: url # max: none
- out:  hackerone-test.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $1,986,889
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
