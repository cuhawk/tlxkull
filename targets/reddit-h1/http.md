# Reddit

> Platform: HackerOne — https://hackerone.com/reddit
> Type: BBP
> Bounty: Low $250–$500 | Medium $500–$1,000 | High $2,500–$7,500 | Critical $5,000–$15,000
> Avg bounty: $500–$500
> Response efficiency: 97% | Avg first response: N/A | Total paid: $1,004,725
> Last scope update: 2024-06-26

## Scope

- in:  *.snooguts.net    # type: wildcard # max: critical
- in:  *.reddit.com    # type: wildcard # max: critical
- in:  *.redditmedia.com    # type: wildcard # max: high
- in:  *.redditinc.com    # type: wildcard # max: medium
- in:  *.redditblog.com    # type: wildcard # max: medium
- in:  *.reddithelp.com    # type: wildcard # max: medium
- in:  *.spiketrap.io    # type: wildcard # max: medium
- in:  new.reddit.com    # type: url # max: critical
- in:  api.reddit.com    # type: url # max: critical
- in:  mod.reddit.com    # type: url # max: critical
- in:  ads.reddit.com    # type: url # max: critical
- in:  gql.reddit.com    # type: url # max: critical
- in:  accounts.reddit.com    # type: url # max: critical
- in:  gateway.reddit.com    # type: url # max: critical
- in:  strapi.reddit.com    # type: url # max: critical
- in:  m.reddit.com    # type: url # max: critical
- in:  amp.reddit.com    # type: url # max: critical
- in:  sh.reddit.com    # type: url # max: critical
- in:  matrix.redditspace.com    # type: url # max: critical
- in:  developers.reddit.com    # type: url # max: critical
- in:  business.reddithelp.com    # type: url # max: critical
- in:  meta-api.reddit.com    # type: url # max: high
- in:  redditforbusiness.com    # type: url # max: medium
- in:  Core Assets    # type: other # max: critical
- in:  Non-Core Assets    # type: other # max: critical
- in:  Android App    # type: other # max: high
- in:  iOS App    # type: other # max: high
- in:  *.memorable.io    # type: wildcard # max: medium
- in:  http://ads.reddit.com    # type: url # max: critical
- in:  1064216828    # type: ios_app # max: high
- in:  ads-api.reddit.com    # type: url # max: critical
- in:  oauth.reddit.com    # type: url # max: critical
- in:  s.reddit.com    # type: url # max: critical
- in:  www.reddit.com    # type: url # max: critical
- in:  old.reddit.com    # type: url # max: critical
- in:  com.reddit.frontpage    # type: android_app # max: critical
- in:  www.spiketrap.io    # type: url # max: medium
- in:  app.spiketrap.io    # type: url # max: medium
- in:  *.redditgifts.com    # type: wildcard # max: critical
- in:  www.dubsmash.com    # type: url # max: low
- in:  918820076    # type: ios_app # max: high
- in:  gateway-production.dubsmash.com    # type: url # max: high
- in:  com.mobilemotion.dubsmash    # type: android_app # max: high
- out:  reddit.secure.force.com    # type: url # max: none
- out:  memorable.io    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $1,004,725
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
