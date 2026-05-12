# Wells Fargo Bounty

> Platform: HackerOne — https://hackerone.com/wellsfargo-bbp
> Type: BBP
> Bounty: Low $300–$600 | Medium $2,000–$4,000 | High $4,000–$7,500 | Critical $7,500–$15,000
> Avg bounty: $500–$750
> Response efficiency: 95% | Avg first response: N/A | Total paid: $271,800
> Last scope update: 2025-06-18

## Scope

- in:  *.wellsfargo.com    # type: wildcard # max: critical
- in:  connect.secure.wellsfargo.com    # type: url # max: critical
- in:  http://wellsfargo.com    # type: url # max: critical
- in:  com.wellsfargo.ceomobile    # type: android_app # max: critical
- in:  com.wf.wellsfargomobile    # type: android_app # max: critical
- in:  com.wf.mobilebanking    # type: ios_app # max: critical
- in:  com.wf.ceomobile    # type: ios_app # max: critical
- in:  *.wf.com    # type: wildcard # max: critical # not eligible for bounty
- in:  http://wf.com    # type: url # max: critical # not eligible for bounty
- in:  homeloans.wellsfargo.com    # type: url # max: critical # not eligible for bounty
- in:  accountoffers.wellsfargo.com    # type: url # max: critical # not eligible for bounty
- in:  *.advisor-connection.com    # type: other # max: critical # not eligible for bounty
- in:  *.mworld.com    # type: other # max: critical # not eligible for bounty
- in:  *.wellsfargoadvisors.com    # type: other # max: critical # not eligible for bounty
- in:  *.wystar.com    # type: other # max: critical # not eligible for bounty
- in:  com.wf.wellsfargomobile    # type: ios_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $271,800
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
