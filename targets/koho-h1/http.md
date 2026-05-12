# KOHO

> Platform: HackerOne — https://hackerone.com/koho
> Type: BBP
> Bounty: Low $250 | Medium $750 | High $2,000 | Critical $5,000
> Avg bounty: $284–$326
> Response efficiency: 100% | Avg first response: N/A | Total paid: $70,412
> Last scope update: 2026-01-19

## Scope

- in:  web.koho.ca    # type: url # max: critical
- in:  http://api.koho.ca/1.0    # type: url # max: critical
- in:  http://api.koho.ca/partner    # type: url # max: critical
- in:  app.koho.ca    # type: url # max: critical
- in:  webgateway.koho.ca    # type: url # max: critical
- in:  www.koho.ca    # type: url # max: medium
- in:  usercontent.koho.ca    # type: url # max: medium
- in:  ca.koho    # type: android_app # max: critical
- in:  1091010942    # type: ios_app # max: critical
- out:  *.line-of-credit.koho.ca    # type: wildcard # max: none
- out:  *.koho.ca/cdn-cgi    # type: wildcard # max: none
- out:  admin.koho.ca    # type: url # max: none
- out:  shiny-admin.koho.ca    # type: url # max: none
- out:  ktools.koho.ca    # type: url # max: none
- out:  tampuli.koho.ca    # type: url # max: none
- out:  curaca.koho.ca    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $70,412

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
