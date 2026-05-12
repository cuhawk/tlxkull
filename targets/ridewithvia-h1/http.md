# Via

> Platform: HackerOne — https://hackerone.com/ridewithvia
> Type: BBP
> Bounty: Low $200 | Medium $400 | High $1,000 | Critical $2,500
> Avg bounty: $150–$300
> Response efficiency: 94% | Avg first response: N/A | Total paid: $38,850
> Last scope update: 2024-07-22

## Scope

- in:  global-api.citymapper.com    # type: url # max: critical
- in:  eu.remix.com    # type: url # max: critical
- in:  platform.remix.com    # type: url # max: critical
- in:  https://metroconnect.app.ridewithvia.com    # type: url # max: critical
- in:  https://pt-runner.app.ridewithvia.com    # type: url # max: critical
- in:  via.rider    # type: android_app # max: critical
- in:   com.citymapper.app.release    # type: android_app # max: critical
- in:  ridewithvia.neoridelittlerock    # type: android_app # max: critical
- in:  ridewithvia.par.piercetransit    # type: android_app # max: critical
- in:  657777015    # type: ios_app # max: critical
- in:  469463298    # type: ios_app # max: critical
- in:  6449737830    # type: ios_app # max: critical
- in:  6464473474    # type: ios_app # max: critical
- in:  com.citymapper.app.release    # type: android_app # max: critical
- in:  1515005951    # type: ios_app # max: critical
- in:  com.ridewithvia.zuzu    # type: android_app # max: critical
- out:  *.drivewithvia.com    # type: wildcard # max: none
- out:  *.citymapper.com/    # type: wildcard # max: none
- out:  ridewithvia.okta.com    # type: url # max: none
- out:  ridewithvia.com    # type: url # max: none
- out:  citymapper.com    # type: url # max: none
- out:  remix.com    # type: url # max: none
- out:  citymapper.com/*    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $38,850

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
