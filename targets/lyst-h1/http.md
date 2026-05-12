# Lyst

> Platform: HackerOne — https://hackerone.com/lyst
> Type: BBP
> Bounty: Low $100 | Medium $300 | High $1,000 | Critical $5,000
> Avg bounty: $100–$150
> Response efficiency: 86% | Avg first response: N/A | Total paid: $32,950
> Last scope update: 2021-12-06

## Scope

- in:  *.lyst.com    # type: wildcard # max: critical
- in:  *.lystit.com    # type: wildcard # max: critical
- in:  *.lyst.co    # type: wildcard # max: critical
- in:  cdna.lystit.com    # type: url # max: critical
- in:  mobileapi.lystit.com    # type: url # max: critical
- in:  com.lyst.lystapp    # type: android_app # max: critical
- in:  597940518    # type: ios_app # max: critical
- out:  help.lyst.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $32,950
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
