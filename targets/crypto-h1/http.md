# Crypto.com

> Platform: HackerOne — https://hackerone.com/crypto
> Type: BBP
> Bounty: Low $2–$400 | Medium $4–$2,000 | High $6–$10,000 | Critical $5,000–$1,000,000
> Avg bounty: $463–$576
> Response efficiency: 99% | Avg first response: N/A | Total paid: $1,549,917
> Last scope update: 2026-05-01

## Scope

- in:  *.crypto.com    # type: wildcard # max: critical
- in:  *.mona.co    # type: wildcard # max: critical
- in:  https://crypto.com/exchange    # type: url # max: critical
- in:  app.mona.co    # type: url # max: critical
- in:  web.crypto.com    # type: url # max: critical
- in:  og.com    # type: url # max: critical
- in:  merchant.crypto.com    # type: url # max: medium
- in:  https://crypto.com/price    # type: url # max: medium
- in:  nadex.com    # type: url # max: medium
- in:  js.crypto.com    # type: url # max: low
- in:  tax.crypto.com    # type: url # max: low
- in:  https://crypto.com/nft    # type: url # max: low
- in:  developer-platform-api.crypto.com    # type: url # max: low
- in:  developer.crypto.com    # type: url # max: low
- in:  developer-api.crypto.com    # type: url # max: low
- in:  travel.crypto.com    # type: url # max: low
- in:  https://etherscan.io/token/0xfe18ae03741a5b84e39c295ac9c856ed7991c38e    # type: other # max: critical
- in:  https://explorer.cronos.org/token/0x2e53c5586e12a99d4CAE366E9Fc5C14fE9c6495d    # type: other # max: critical
- in:  Crypto.com Wallet Extension    # type: other # max: medium
- in:  co.mona.android    # type: android_app # max: high
- in:  com.defi.wallet    # type: android_app # max: medium
- in:  com.monaco.mobile    # type: ios_app # max: high
- in:  com.defi.wallet    # type: ios_app # max: medium
- in:  Crypto.com mobile app APIs that require an account    # type: api # max: critical
- in:  Crypto.com Exchange APIs that require an account    # type: api # max: critical
- in:  pay.crypto.com    # type: url # max: high
- in:  auth.crypto.com    # type: url # max: critical
- in:  www.crypto.com    # type: url # max: critical
- in:  https://crypto.com/defi/    # type: url # max: critical
- in:   https://github.com/crypto-org-chain/chain-main    # type: repo # max: critical
- in:  crypto.org    # type: url # max: critical
- in:  testnet-croeseid-4.crypto.org    # type: url # max: critical
- in:  https://crypto.org/desktopwallet    # type: url # max: critical
- in:  https://github.com/crypto-com/chain-tx-enclave    # type: repo # max: critical
- in:  mco.crypto.com    # type: url # max: critical
- out:  https://github.com/crypto-com/cro-staking    # type: repo # max: none
- out:  https://github.com/crypto-com/swap-contracts-periphery    # type: repo # max: none
- out:  https://github.com/crypto-com/swap-contracts-core    # type: repo # max: none
- out:  https://github.com/crypto-com/chain-desktop-wallet    # type: repo # max: none
- out:  https://github.com/crypto-com/sample-chain-wallet    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $1,549,917

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
