# Krisp

> Platform: HackerOne — https://hackerone.com/krisp
> Type: BBP
> Bounty: Low $100 | Medium $250–$500 | High $750–$1,000 | Critical $1,500–$5,000
> Avg bounty: $100–$100
> Response efficiency: 100% | Avg first response: N/A | Total paid: $40,000
> Last scope update: 2025-03-08

## Scope

- in:  *.krisp.ai    # type: wildcard # max: critical
- in:  krisp.ai    # type: url # max: critical
- in:  account.krisp.ai    # type: url # max: critical
- in:  api.krisp.ai    # type: url # max: critical
- in:  teams.krisp.ai    # type: url # max: critical
- in:  download.krisp.ai    # type: url # max: critical
- in:  analytics.krisp.ai    # type: url # max: critical
- in:  upld.krisp.ai    # type: url # max: critical
- in:  app.krisp.ai    # type: url # max: critical
- in:  Other    # type: other # max: critical
- in:  https://download.krisp.ai/win    # type: downloadable_executables # max: critical
- in:  https://download.krisp.ai/mac    # type: downloadable_executables # max: critical
- in:  help.krisp.ai    # type: url # max: critical # not eligible for bounty
- in:  help-jp.krisp.ai    # type: url # max: low # not eligible for bounty
- in:  resources.krisp.ai    # type: url # max: none # not eligible for bounty
- in:  contact.krisp.ai    # type: url # max: none # not eligible for bounty
- in:  jobs.krisp.ai    # type: url # max: none # not eligible for bounty
- out:  *dev*.krisp.ai    # type: wildcard # max: none
- out:  whatsnew.krisp.ai    # type: url # max: none
- out:  url5145.krisp.ai    # type: url # max: none
- out:  voice-ai-newsletter.krisp.ai    # type: url # max: none
- out:  sdk-docs.krisp.ai    # type: url # max: none
- out:  metabase.krisp.ai    # type: url # max: none
- out:  *.env.krisp.ai    # type: wildcard # max: none
- out:  *.feature-test.*.krisp.ai    # type: wildcard # max: none
- out:  *.mdev.krisp.ai    # type: wildcard # max: none
- out:  new.*.krisp.ai    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $40,000

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
