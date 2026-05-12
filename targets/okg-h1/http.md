# OKG

> Platform: HackerOne — https://hackerone.com/okg
> Type: BBP
> Bounty: Low $200–$600 | Medium $600–$2,000 | High $1,200–$5,000 | Critical $2,000–$1,000,000
> Avg bounty: $350–$500
> Response efficiency: 100% | Avg first response: N/A | Total paid: $260,000
> Last scope update: 2026-04-30

## Scope

- in:  *.okx.com    # type: wildcard # max: critical
- in:  *.oklink.com    # type: wildcard # max: critical
- in:  OKX Wallet Core Open Source    # type: repo # max: critical
- in:  Mac OS Executable    # type: other # max: critical
- in:  Windows OS Executable    # type: other # max: critical
- in:  OKX Android APK    # type: other # max: critical
- in:  OKX iOS APP    # type: other # max: critical
- in:  OKX Wallet Chrome Extension    # type: other # max: critical
- in:  OKX Wallet Edge Add-ons    # type: other # max: critical
- in:  OKX Wallet Safari Extension    # type: other # max: critical
- in:  https://github.com/okx/wallet-core    # type: repo # max: low
- in:  OKT Chain    # type: other # max: critical
- in:  Web3 DEX Open Source    # type: repo # max: critical
- in:  https://github.com/okx/WEB3-DEX-OPENSOURCE    # type: repo # max: critical
- in:  *.okcoin.com    # type: wildcard # max: medium
- in:  Okcoin Android APK    # type: other # max: medium
- in:  Okcoin iOS App    # type: other # max: medium
- in:  https://www.okx.com/docs-v5/en/#market-maker-program    # type: url # max: critical
- in:  https://www.okx.com/docs/en/    # type: url # max: critical
- in:  com.okex.OKExAppstoreFull    # type: ios_app # max: critical
- in:  com.okinc.okex.gp    # type: android_app # max: critical
- out:  *.okg.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $260,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
