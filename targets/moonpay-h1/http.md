# MoonPay 

> Platform: HackerOne — https://hackerone.com/moonpay
> Type: BBP
> Bounty: Low $250 | Medium $1,000 | High $5,000 | Critical $20,000
> Avg bounty: $250–$250
> Response efficiency: 90% | Avg first response: N/A | Total paid: $93,620
> Last scope update: 2023-03-17

## Scope

- in:  *.moonpaycloud.com    # type: wildcard # max: critical
- in:  *.hypermint.com    # type: wildcard # max: critical
- in:  *.moonpay.com    # type: wildcard # max: critical
- in:  moonpay.com    # type: url # max: critical
- in:  hypermint.com    # type: url # max: critical
- in:  web3.moonpay.com    # type: url # max: critical
- in:  sell.moonpay.com    # type: url # max: critical
- in:  buy.moonpay.com    # type: url # max: critical
- in:  auth.moonpay.com    # type: url # max: critical
- in:  app.moonpay.com    # type: url # max: critical
- in:  api.moonpay.com    # type: url # max: critical
- in:  https://github.com/moonpay    # type: repo # max: critical
- in:  https://play.google.com/store/apps/details?id=com.moonpay    # type: android_app # max: critical
- in:  https://apps.apple.com/app/id1635031432    # type: ios_app # max: critical
- in:  https://apps.apple.com/app/moonpay-buy-bitcoin-ethereum/id1635031432    # type: ios_app # max: critical
- in:  com.moonpay    # type: android_app # max: high
- in:  1635031432    # type: ios_app # max: critical
- in:  https://github.com/moonpay-hypermint    # type: repo # max: critical
- in:  com.moonpay    # type: android_app # max: high
- in:  support.moonpay.com    # type: url # max: none
- in:  https://github.com/moonpay-hypermint    # type: other # max: critical
- in:  dashboard.moonpay.com    # type: url # max: critical
- in:  sell.moonpay.com    # type: url # max: critical
- in:  buy.moonpay.com    # type: url # max: critical
- in:  private-api.moonpay.com    # type: url # max: critical
- in:  api.moonpay.com    # type: url # max: critical
- out:  *.plexlabs.io    # type: wildcard # max: none
- out:  clicks.moonpay.com    # type: url # max: none
- out:  qr.moonpay.com    # type: url # max: none
- out:  page.moonpay.com    # type: url # max: none
- out:  support.moonpay.com    # type: url # max: none
- out:  docs.moonpay.com    # type: url # max: none
- out:  plexlabs.io    # type: url # max: none
- out:  request-headers-no-proxy.moonpay.com    # type: url # max: none
- out:  request-headers.moonpay.com    # type: url # max: none
- out:  docs.hypermint.com    # type: url # max: none
- out:  help.moonpay.com    # type: url # max: none
- out:  storefront.hypermint.com    # type: url # max: none
- out:  ethpass.xyz    # type: url # max: none
- out:  dev.moonpay.com    # type: url # max: none
- out:  payload-marketing.moonpay.com    # type: url # max: none
- out:  https://github.com/moonpay/moonpay-sign    # type: repo # max: none
- out:  https://github.com/moonpay/moonpay-demo-integrations    # type: repo # max: none
- out:  https://github.com/moonpay/devops-challenge    # type: repo # max: none
- out:  docs.hypeermint.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $93,620

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
