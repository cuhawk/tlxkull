# Remitly

> Platform: HackerOne — https://hackerone.com/remitly
> Type: BBP
> Bounty: Low $50 | Medium $400 | High $2,500 | Critical $9,000
> Avg bounty: $200–$250
> Response efficiency: 96% | Avg first response: N/A | Total paid: $129,179
> Last scope update: 2026-04-30

## Scope

- in:  *.int.remitly.com    # type: wildcard # max: critical
- in:  *.dev.remitly.com    # type: wildcard # max: high
- in:  remitly.com    # type: url # max: critical
- in:  blog.remitly.com    # type: url # max: critical
- in:  api.remitly.io    # type: url # max: critical
- in:  cards.remitly.io    # type: url # max: critical
- in:  rewire.com    # type: url # max: critical
- in:  app.rewire.to    # type: url # max: critical
- in:  cardpayments.remitly.io    # type: url # max: critical
- in:  access.remitly.com    # type: url # max: critical
- in:  auth.remitly.com    # type: url # max: critical
- in:  login.remitly.com    # type: url # max: critical
- in:  media.remitly.io    # type: url # max: high
- in:  partner-webhook.remitly.io    # type: url # max: high
- in:  ablink.info.remitly.com    # type: url # max: high
- in:  ir.remitly.com    # type: url # max: high
- in:  news.remitly.com    # type: url # max: high
- in:  access-sandbox.remitly.com    # type: url # max: high
- in:  rates.rewire.com    # type: url # max: medium
- in:  app3.rewire.to    # type: url # max: medium
- in:  careers.remitly.com    # type: url # max: medium
- in:  metrics.int.remitly.com    # type: url # max: medium
- in:  site.rewire.com    # type: url # max: medium
- in:  remitly.io    # type: url # max: medium
- in:  beamitmobile.com    # type: url # max: medium
- in:  getorigen.com    # type: url # max: medium
- in:  getsurenow.com    # type: url # max: medium
- in:  insuritly.com    # type: url # max: medium
- in:  origenapp.com    # type: url # max: medium
- in:  origenbanking.com    # type: url # max: medium
- in:  origencard.com    # type: url # max: medium
- in:  origendebit.com    # type: url # max: medium
- in:  origenfinance.com    # type: url # max: medium
- in:  remilty.net    # type: url # max: medium
- in:  remilty.org    # type: url # max: medium
- in:  remitir.com    # type: url # max: medium
- in:  remitiy.com    # type: url # max: medium
- in:  remitly-3pjs.com    # type: url # max: medium
- in:  remitly-vendor.com    # type: url # max: medium
- in:  remitly.ca    # type: url # max: medium
- in:  remitly.cash    # type: url # max: medium
- in:  remitly.co    # type: url # max: medium
- in:  remitly.co.uk    # type: url # max: medium
- in:  remitly.com.au    # type: url # max: medium
- in:  remitly.com.mx    # type: url # max: medium
- in:  remitly.de    # type: url # max: medium
- in:  remitly.es    # type: url # max: medium
- in:  remitly.eu    # type: url # max: medium
- in:  remitly.fr    # type: url # max: medium
- in:  remitly.jp    # type: url # max: medium
- in:  remitly.me    # type: url # max: medium
- in:  remitly.mx    # type: url # max: medium
- in:  remitly.net    # type: url # max: medium
- in:  remitly.org    # type: url # max: medium
- in:  remitly.uk    # type: url # max: medium
- in:  remitly.xyz    # type: url # max: medium
- in:  remitlyapi.com    # type: url # max: medium
- in:  remitlycard.com    # type: url # max: medium
- in:  remitlycredit.com    # type: url # max: medium
- in:  remitlydata.com    # type: url # max: medium
- in:  remitlyit.com    # type: url # max: medium
- in:  remitlypay.com    # type: url # max: medium
- in:  remitlypayments.com    # type: url # max: medium
- in:  remitlytest.com    # type: url # max: medium
- in:  remitlywallet.com    # type: url # max: medium
- in:  remitresearch.com    # type: url # max: medium
- in:  travelcash.money    # type: url # max: medium
- in:  whyisend.com    # type: url # max: medium
- in:  com.remitly.androidapp    # type: android_app # max: critical
- in:  674258465    # type: ios_app # max: critical
- in:  funding-webhooks.remitly.io    # type: api # max: high
- in:  hub-api-sandbox.remitly.io    # type: api # max: medium
- in:  branch.remitly.com    # type: url # max: critical
- in:  club.remitly.com    # type: url # max: critical
- out:  https://www.remitly.com/blog    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $129,179

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
