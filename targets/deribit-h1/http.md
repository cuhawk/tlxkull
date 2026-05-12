# Deribit

> Platform: HackerOne — https://hackerone.com/deribit
> Type: BBP
> Bounty: Low $150–$300 | Medium $425–$1,000 | High $1,500–$10,000 | Critical $3,000–$50,000
> Avg bounty: $200–$250
> Response efficiency: 55% | Avg first response: N/A | Total paid: $30,000
> Last scope update: 2022-11-14

## Scope

- in:  *.deribit.com    # type: wildcard # max: medium
- in:  test.deribit.com    # type: url # max: critical
- in:  insights.deribit.com    # type: url # max: medium
- in:  pb.deribit.com    # type: url # max: medium
- in:  Tier 1    # type: other # max: critical
- in:  Tier 2    # type: other # max: critical
- in:  com.deribit    # type: android_app # max: critical
- in:  1293674041    # type: ios_app # max: critical
- in:  tools.deribit.com    # type: url # max: medium
- in:  metrics.deribit.com    # type: url # max: medium
- in:  legacy.deribit.com    # type: url # max: critical
- out:  *.chattest.deribit.com    # type: wildcard # max: none
- out:  deribit.zendesk.com    # type: url # max: none
- out:  office.deribit.com    # type: url # max: none
- out:  trust.deribit.com    # type: url # max: none
- out:  support.deribit.com    # type: url # max: none
- out:  veriscope.deribit.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $30,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
