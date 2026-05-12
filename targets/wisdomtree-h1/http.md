# WisdomTree, Inc.

> Platform: HackerOne — https://hackerone.com/wisdomtree
> Type: BBP
> Bounty: Low $150–$500 | Medium $500–$1,500 | High $2,500–$5,500 | Critical $4,000–$6,500
> Avg bounty: $1,000–$1,500
> Response efficiency: 100% | Avg first response: N/A | Total paid: $81,050
> Last scope update: 2026-04-24

## Scope

- in:  api.wisdomtreeprimeapp.com    # type: url # max: critical
- in:  https://app.wisdomtreeconnect.com/api/    # type: url # max: critical
- in:  https://app.wisdomtreeconnect.com/o/token/    # type: url # max: critical
- in:  https://app.wisdomtreeconnect.com    # type: url # max: critical
- in:  com.wisdomtree.wtprime    # type: testflight # max: critical
- in:  com.wisdomtree.wtprime    # type: other_apk # max: critical
- out:  wisdomtree.com    # type: url # max: none
- out:  wisdomtree.eu    # type: url # max: none
- out:  dataspanapi.wisdomtree.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $81,050
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
