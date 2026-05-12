# Faraday, Inc.

> Platform: HackerOne — https://hackerone.com/faraday_inc
> Type: BBP
> Bounty: Low $100 | Medium $300 | High $750 | Critical $1,550
> Avg bounty: $75–$100
> Response efficiency: 96% | Avg first response: N/A | Total paid: $14,285
> Last scope update: 2024-02-02

## Scope

- in:  app.faraday.ai    # type: url # max: critical
- in:  api.faraday.ai    # type: url # max: critical
- in:  vault2.faraday.ai    # type: url # max: critical
- in:  s3://faraday-uploads    # type: other # max: critical
- in:  s3://faraday-secret    # type: other # max: critical
- in:  gs://fdy-production-sdk-uploads    # type: other # max: critical
- in:  gs://faraday-secret    # type: other # max: critical
- in:  app.faraday.io    # type: url # max: critical
- out:  Support Live Chat    # type: other # max: none
- out:  faraday.io    # type: url # max: none
- out:  pay.faraday.io    # type: url # max: none
- out:  www.faraday.ai    # type: url # max: none
- out:  www.faraday.io    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $14,285
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
