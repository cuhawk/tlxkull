# Braze, Inc.

> Platform: HackerOne — https://hackerone.com/braze_inc
> Type: BBP
> Bounty: Low $500 | Medium $1,200 | High $2,500 | Critical $5,000
> Avg bounty: $250–$250
> Response efficiency: 98% | Avg first response: N/A | Total paid: $24,195
> Last scope update: 2025-05-07

## Scope

- in:  https://bug-bounty-dashboard.k8s.tools-001.d-use-1.braze-dev.com/    # type: url # max: critical
- in:  https://bug-bounty-api.k8s.tools-001.d-use-1.braze-dev.com/    # type: api # max: critical
- in:  https://bug-bounty-rest.k8s.tools-001.d-use-1.braze-dev.com/    # type: api # max: critical
- out:  *.appboy.com    # type: wildcard # max: none
- out:  *.braze.co.jp    # type: wildcard # max: none
- out:  *.braze.com    # type: wildcard # max: none
- out:  braze-dev.com    # type: url # max: none
- out:  braze-images.com    # type: url # max: none
- out:  braze.eu    # type: url # max: none
- out:  https://dashboard-09.braze.com/    # type: url # max: none
- out:  https://try.braze.com/free_trial    # type: url # max: none
- out:  Other    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $24,195
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
