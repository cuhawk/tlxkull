# Coinbase

> Platform: HackerOne — https://hackerone.com/coinbase
> Type: BBP
> Bounty: Low $201 | Medium $2,001 | High $15,001 | Critical $1,000,000
> Avg bounty: $200–$200
> Response efficiency: 96% | Avg first response: N/A | Total paid: $2,740,338
> Last scope update: 2025-04-10

## Scope

- in:  *.coinbase-corp.com    # type: wildcard # max: critical
- in:  *.coinbase.com    # type: url # max: critical
- in:  *.cbhq.net    # type: url # max: critical
- in:  pro.coinbase.com    # type: url # max: critical
- in:  custody.coinbase.com    # type: url # max: critical
- in:  commerce.coinbase.com    # type: url # max: critical
- in:  prime.coinbase.com    # type: url # max: critical
- in:  institutional.coinbase.com    # type: url # max: critical
- in:  api.coinbase.com    # type: url # max: critical
- in:  api.custody.coinbase.com    # type: url # max: critical
- in:  cloud.coinbase.com    # type: url # max: critical
- in:  coinbase.com    # type: url # max: critical
- in:  nft.coinbase.com    # type: url # max: critical
- in:  http://coinbase.com    # type: url # max: high
- in:  international.coinbase.com    # type: url # max: high
- in:  https://github.com/coinbase/cb-mpc    # type: repo # max: critical
- in:  https://base.org    # type: other # max: critical
- in:  https://chrome.google.com/webstore/detail/coinbase-wallet-extension/hnfanknocfeofbddgcijnmhnfnkdnaad    # type: other # max: critical
- in:  Web3 Smart Contracts    # type: other # max: critical
- in:  Coinbase WaaS (Wallet as a Service)    # type: other # max: critical
- in:  *.base.org    # type: other # max: high
- in:  Other    # type: other # max: medium
- in:  com.coinbase.android    # type: android_app # max: critical
- in:  org.toshi    # type: android_app # max: critical
- in:  com.coinbase.wallite    # type: android_app # max: low
- in:  54.175.255.192/27    # type: cidr # max: critical
- in:  org.toshi.distribution    # type: ios_app # max: critical
- in:  com.vilcsak.bitcoin2    # type: ios_app # max: critical
- in:  https://github.com/coinbase/cb-mpc-go    # type: repo # max: critical # not eligible for bounty
- in:  com.coinbase.ios    # type: ios_app # max: critical
- in:  com.shiftpayments.shiftcard    # type: ios_app # max: critical
- in:  base.org    # type: url # max: critical
- in:  com.shiftpayments.shiftcard    # type: url # max: critical
- in:  org.toshi.distribution    # type: url # max: critical
- in:  api.coinbase.com    # type: url # max: critical
- in:  buy.coinbase.com    # type: url # max: critical
- in:  ws-feed.gdax.com    # type: url # max: critical
- in:  api.gdax.com    # type: url # max: critical
- in:  static.coinbase.com    # type: url # max: critical
- in:  fix.gdax.com    # type: url # max: critical
- in:  *.commerce.coinbase.com    # type: other # max: critical
- in:  assets.coinbase.com    # type: url # max: critical
- in:  images.coinbase.com    # type: url # max: critical
- in:  ws.coinbase.com    # type: url # max: critical
- in:  www.gdax.com    # type: url # max: critical
- in:  eio-feed.gdax.com    # type: url # max: critical
- out:  support.coinbase.com    # type: url # max: none
- out:  blog.coinbase.com    # type: url # max: none
- out:  engineering.coinbase.com    # type: url # max: none
- out:  developers.coinbase.com    # type: url # max: none
- out:  status.coinbase.com    # type: url # max: none
- out:  support.pro.coinbase.com    # type: url # max: none
- out:  *.blockspring.com    # type: url # max: none
- out:  tagomi.com    # type: url # max: none
- out:  paradex.io    # type: url # max: none
- out:  N/A - Not Coinbase owned or operated    # type: other # max: none
- out:  com.coinbase.pro    # type: android_app # max: none
- out:  com.coinbase.pro    # type: ios_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $2,740,338
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
