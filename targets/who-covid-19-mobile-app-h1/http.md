# WHO COVID-19 Mobile App

> Platform: HackerOne — https://hackerone.com/who-covid-19-mobile-app
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2020-12-15

## Scope

- in:  *.whocoronavirus.org    # type: wildcard # max: critical # not eligible for bounty
- in:  hack.whocoronavirus.org    # type: url # max: critical # not eligible for bounty
- in:  https://github.com/WorldHealthOrganization/app    # type: repo # max: critical # not eligible for bounty
- in:  org.who.WHOMyHealth    # type: android_app # max: critical # not eligible for bounty
- in:  int.who.WHOMyHealth    # type: ios_app # max: critical # not eligible for bounty
- out:  *.who.int    # type: wildcard # max: none
- out:  covid19app.who.int    # type: url # max: none
- out:  who.int    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
