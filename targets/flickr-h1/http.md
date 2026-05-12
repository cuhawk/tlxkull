# Flickr

> Platform: HackerOne — https://hackerone.com/flickr
> Type: BBP
> Bounty: Low $300 | Medium $700 | High $4,000 | Critical $8,500
> Avg bounty: $300–$341
> Response efficiency: 81% | Avg first response: N/A | Total paid: $141,112
> Last scope update: 2022-03-15

## Scope

- in:  *.flickr.com    # type: wildcard # max: critical
- in:  www.whatismode.com    # type: url # max: critical
- in:  modefestival.com    # type: url # max: critical
- in:  com.yahoo.mobile.client.android.flickr    # type: android_app # max: critical
- in:  328407587    # type: ios_app # max: critical
- out:  *.flickr.net    # type: wildcard # max: none
- out:  blog.flickr.com    # type: url # max: none
- out:  amt.flickr.com    # type: url # max: none
- out:  appletv.flickr.com    # type: url # max: none
- out:  blogtest.flickr.com    # type: url # max: none
- out:  bluebird.flickr.com    # type: url # max: none
- out:  code.flickr.com    # type: url # max: none
- out:  csp.flickr.com    # type: url # max: none
- out:  guce.flickr.com    # type: url # max: none
- out:  stage.guce.flickr.com    # type: url # max: none
- out:  trunk.guce.flickr.com    # type: url # max: none
- out:  health.flickr.com    # type: url # max: none
- out:  help.flickr.com    # type: url # max: none
- out:  parkorbird.flickr.com    # type: url # max: none
- out:  links.flickr.com    # type: url # max: none
- out:  flickrhelp.com    # type: url # max: none
- out:  Zero Day Vulnerabilities/Security Upgrades    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $141,112
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
