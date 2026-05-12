# Affirm

> Platform: HackerOne — https://hackerone.com/affirm
> Type: BBP
> Bounty: Low $300 | Medium $600 | High $2,500 | Critical $5,000
> Avg bounty: $300–$500
> Response efficiency: 89% | Avg first response: N/A | Total paid: $63,236
> Last scope update: 2024-11-19

## Scope

- in:  sandbox.affirm.com    # type: url # max: critical
- in:  com.affirm.internal.hackerone    # type: other # max: critical
- in:  com.affirm.central.audit    # type: android_app # max: critical
- in:  helpcenter.affirm.ca    # type: url # max: critical
- in:  helpcenter.affirm.com    # type: url # max: critical
- in:  hackerone.affirm-odin.com    # type: url # max: critical
- in:  direct-hackerone.affirm-odin.com    # type: url # max: none # not eligible for bounty
- in:  vcn-hackerone.affirm-odin.com    # type: url # max: none # not eligible for bounty
- in:  com.affirm.internal.hackerone    # type: ios_app # max: critical
- out:  *.affirm.com    # type: wildcard # max: none
- out:  dashboard.dev.return.ly    # type: url # max: none
- out:  *.return.ly    # type: wildcard # max: none
- out:  test-store-subdomain.dev.return.ly    # type: url # max: none
- out:  dashboard.returnly.com    # type: url # max: none
- out:  test-store-subdomain.returnly.com    # type: url # max: none
- out:  *.returnly.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $63,236
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
