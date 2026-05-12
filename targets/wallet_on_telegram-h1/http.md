# Wallet on Telegram

> Platform: HackerOne — https://hackerone.com/wallet_on_telegram
> Type: BBP
> Bounty: Low $200 | Medium $500 | High $3,000 | Critical $100,000
> Avg bounty: $300–$300
> Response efficiency: 100% | Avg first response: N/A | Total paid: $19,900
> Last scope update: 2025-05-20

## Scope

- in:  walletbot.me    # type: url # max: critical
- in:  wallettg.com    # type: url # max: critical
- in:  wallettg.net    # type: url # max: critical
- in:  p2p.walletbot.me    # type: url # max: critical
- in:  pay.wallet.tg    # type: url # max: high
- in:  wallet.tg    # type: url # max: low
- in:  Crypto infrastructure for cold and hot wallets    # type: other # max: critical
- in:  Extreme Severity    # type: other # max: critical
- in:  pay.wallet.tg/wpay    # type: api # max: high
- in:  walletbot.me/api/v1/    # type: api # max: critical
- in:  walletbot.me/p2p    # type: api # max: critical
- in:  walletbot.me/v2api    # type: api # max: critical
- in:  walletbot.me/scwapi    # type: api # max: critical
- in:  walletbot.me/users    # type: api # max: critical
- in:  t.me/wallet_news    # type: other # max: medium
- in:  t.me/wallet_supportbot    # type: other # max: medium
- in:  t.me/wallet    # type: other # max: critical
- in:  api.neocrypto.net    # type: api # max: critical
- in:  neocrypto.net    # type: url # max: critical
- in:  https://walletbot.me/p2p    # type: api # max: critical
- in:  https://walletbot.me/api/v1/*    # type: api # max: critical
- out:  wallet.helpscoutdocs.com    # type: url # max: none
- out:  docs.wallet.tg    # type: url # max: none
- out:  toncenter.walletbot.me    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $19,900
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
