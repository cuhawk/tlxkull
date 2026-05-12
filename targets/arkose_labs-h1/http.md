# Arkose Labs

> Platform: HackerOne — https://hackerone.com/arkose_labs
> Type: BBP
> Bounty: Low $100–$300 | Medium $300–$750 | High $500–$5,000 | Critical $750–$7,000
> Avg bounty: $300–$400
> Response efficiency: 81% | Avg first response: N/A | Total paid: $26,107
> Last scope update: 2025-10-10

## Scope

- in:  client-api.arkoselabs.com    # type: url # max: critical
- in:  cdn.arkoselabs.com    # type: url # max: critical
- in:  customer-sessions.arkoselabs.com    # type: url # max: critical
- in:  portal.arkoselabs.com    # type: url # max: critical
- in:  verify.arkoselabs.com    # type: url # max: critical
- in:  iframe.arkoselabs.com    # type: url # max: critical
- in:  www.arkoselabs.com    # type: url # max: critical
- in:  demo.arkoselabs.com    # type: url # max: critical
- in:  Marketing WebApps    # type: other # max: critical
- in:  www.arkoselabs.com    # type: url # max: critical
- in:  demo.arkoselabs.com    # type: url # max: critical
- out:  https://status.arkoselabs.com/    # type: url # max: none
- out:  developer.arkoselabs.com    # type: url # max: none
- out:  http://client-api.arkose.com.cn    # type: url # max: none
- out:  client-api.arkose.com.cn    # type: url # max: none
- out:  Out of Scope    # type: other # max: none
- out:  status.arkoselabs.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $26,107
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
