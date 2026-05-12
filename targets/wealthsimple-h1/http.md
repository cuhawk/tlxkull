# Wealthsimple

> Platform: HackerOne — https://hackerone.com/wealthsimple
> Type: BBP
> Bounty: Low $500 | Medium $1,000 | High $5,000 | Critical $20,000
> Avg bounty: $500–$500
> Response efficiency: 88% | Avg first response: N/A | Total paid: $300,000
> Last scope update: 2025-04-15

## Scope

- in:  *.wealthsimple.com    # type: wildcard # max: critical
- in:  *.simpletax.ca    # type: wildcard # max: critical
- in:  com.wealthsimple    # type: android_app # max: critical
- in:  com.wealthsimple.wealthsimple    # type: ios_app # max: critical
- in:  www.wealthsimple.com    # type: url # max: critical
- in:  api.production.wealthsimple.com    # type: url # max: critical
- in:  cs-tools.wealthsimple.com    # type: url # max: critical
- in:  assets.wealthsimple.com    # type: url # max: critical
- in:  api.wealthsimple.com    # type: url # max: critical
- in:  app.simpletax.ca    # type: url # max: critical
- in:  trade-service.wealthsimple.com    # type: url # max: critical
- in:  api-legacy.wealthsimple.com    # type: url # max: critical
- in:  fundowner.wealthsimple.com    # type: url # max: critical
- in:  api.sandbox.wealthsimple.com    # type: url # max: critical
- in:  empower.wealthsimple.com    # type: url # max: critical
- in:  ads-engine-service.wealthsimple.com    # type: url # max: critical
- in:  support.wealthsimple.com    # type: url # max: high
- in:  staging.wealthsimple.com    # type: url # max: high
- in:  grow.wealthsimple.com    # type: url # max: high
- in:  cs-tools-staging.wealthsimple.com    # type: url # max: medium
- in:  api-staging.wealthsimple.com    # type: url # max: medium
- in:  work-staging.wealthsimple.com    # type: url # max: high
- in:  www-staging.wealthsimple.com    # type: url # max: high
- in:  www2-staging.wealthsimple.com    # type: url # max: high
- in:  staging-aws.wealthsimple.com    # type: url # max: high
- in:  review.wealthsimple.com    # type: url # max: medium
- in:  faq.wealthsimple.com    # type: url # max: high
- in:  Crypto    # type: other # max: critical
- in:  Beta Product C     # type: other # max: critical
- in:  work.wealthsimple.com    # type: url # max: critical
- out:  help.wealthsimple.com    # type: url # max: none
- out:  support.wealthsimple.com    # type: url # max: none
- out:  work.wealthsimple.com    # type: url # max: none
- out:  tldr-archive.wealthsimple.com    # type: url # max: none
- out:  help.wealthsimple.com    # type: url # max: none
- out:  info.wealthsimple.com    # type: url # max: none
- out:  new.wealthsimple.com    # type: url # max: none
- out:  fabric.wealthsimple.com    # type: url # max: none
- out:  code.wealthsimple.com    # type: url # max: none
- out:  image.email.wealthsimple.com    # type: url # max: none
- out:  rwwssaibhreas.wealthsimple.com    # type: url # max: none
- out:  mta.email.wealthsimple.com    # type: url # max: none
- out:  view.email.wealthsimple.com    # type: url # max: none
- out:  w4a.wealthsimple.com    # type: url # max: none
- out:  click.email.wealthsimple.com    # type: url # max: none
- out:  email.wealthsimple.com    # type: url # max: none
- out:  o1.em.wealthsimple.com    # type: url # max: none
- out:  Social engineering    # type: other # max: none
- out:  Denial of Service / Brute Force    # type: other # max: none
- out:  Email    # type: other # max: none
- out:  DNS    # type: other # max: none
- out:  uk-brokerage.prod.iad.wealthsimple.com    # type: url # max: none
- out:  uk-brokerage.staging.iad.wealthsimple.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $300,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
