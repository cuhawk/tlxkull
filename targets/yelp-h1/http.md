# Yelp

> Platform: HackerOne — https://hackerone.com/yelp
> Type: BBP
> Bounty: Low $1,250 | Medium $4,000 | High $6,000 | Critical $10,000
> Avg bounty: $300–$500
> Response efficiency: 96% | Avg first response: N/A | Total paid: $330,000
> Last scope update: 2022-09-30

## Scope

- in:  *.yelp.com    # type: wildcard # max: critical
- in:  *.yelp-support.com    # type: wildcard # max: high
- in:  *.yelpwifi.com    # type: wildcard # max: low
- in:  yelptop100.com    # type: url # max: low
- in:  com.yelp.android.biz    # type: android_app # max: critical
- in:  com.yelp.android    # type: android_app # max: critical
- in:  284910350    # type: ios_app # max: critical
- in:  936983378    # type: ios_app # max: critical
- in:  542767785    # type: ios_app # max: critical
- in:  app.yelpwifi.com    # type: url # max: critical # not eligible for bounty
- in:  yelp.nowait.com    # type: url # max: critical # not eligible for bounty
- in:  restaurants.yelp.com    # type: url # max: low
- in:  biz-app.yelp.com    # type: url # max: critical
- in:  api.yelp.com    # type: url # max: critical
- in:  mobile-api.yelp.com    # type: url # max: critical
- in:  auto-api.yelp.com    # type: url # max: critical
- in:  www.yelpreservations.com    # type: url # max: critical
- in:  biz.yelp.com    # type: url # max: critical
- in:  m.yelp.com    # type: url # max: critical
- in:  api.yelp.com    # type: other # max: critical
- out:  www.yelp-ir.com    # type: url # max: none
- out:  cloud.e.yelp-business.com    # type: url # max: none
- out:  yelp-press.com    # type: url # max: none
- out:  yelp.careers    # type: url # max: none
- out:  blog.yelp.com    # type: url # max: none
- out:  engineeringblog.yelp.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $330,000

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
