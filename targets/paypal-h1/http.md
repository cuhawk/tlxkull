# PayPal

> Platform: HackerOne — https://hackerone.com/paypal
> Type: BBP
> Bounty: Low $1,000 | Medium $10,000 | High $20,000 | Critical $30,000
> Avg bounty: $1,600–$2,900
> Response efficiency: 96% | Avg first response: N/A | Total paid: $13,316,687
> Last scope update: 2026-03-19

## Scope

- in:  *.xoom.com    # type: url # max: critical
- in:  *.paypal.com    # type: url # max: critical
- in:  *.braintreegateway.com    # type: url # max: critical
- in:  *.paydiant.com    # type: url # max: critical
- in:  *.venmo.com    # type: url # max: critical
- in:  paypal.me    # type: url # max: critical
- in:  py.pl    # type: url # max: critical
- in:  *.braintreepayments.com    # type: url # max: critical
- in:  *.braintree-api.com    # type: url # max: critical
- in:  *.braintree.tools    # type: url # max: critical
- in:  *.paypalcorp.com    # type: url # max: critical
- in:  *.hyperwallet.com    # type: url # max: critical
- in:  *.paylution.com    # type: url # max: critical
- in:  paypalobjects.com    # type: url # max: medium
- in:  sandbox.braintreegateway.com    # type: url # max: medium
- in:  www.paypal-*.com    # type: url # max: low
- in:  prequal.swiftfinancial.com    # type: url # max: low
- in:  partner.swiftfinancial.com    # type: url # max: low
- in:  decision.swiftfinancial.com    # type: url # max: low
- in:  pigeon.swiftfinancial.com    # type: url # max: low
- in:  scrutiny.swiftfinancial.com    # type: url # max: low
- in:  www.swiftcapital.com    # type: url # max: low
- in:  www.loanbuilder.com    # type: url # max: low
- in:  www.swiftfinancial.com    # type: url # max: low
- in:  api.swiftfinancial.com    # type: url # max: low
- in:  my.swiftfinancial.com    # type: url # max: low
- in:  api.loanbuilder.com    # type: url # max: low
- in:  my.loanbuilder.com    # type: url # max: low
- in:  loanbuilder.com    # type: url # max: low
- in:  swiftfinancial.com    # type: url # max: low
- in:  swiftcapital.com    # type: url # max: low
- in:  Braintree SDK    # type: other # max: critical
- in:  PayPal SDK    # type: other # max: critical
- in:  com.xoom.android.app    # type: android_app # max: critical
- in:  com.paypal.merchant.client    # type: android_app # max: critical
- in:  com.paypal.android.p2pmobile    # type: android_app # max: critical
- in:  com.venmo    # type: android_app # max: critical
- in:  351727428    # type: ios_app # max: critical
- in:  com.xoom.app    # type: ios_app # max: critical
- in:  com.paypal.merchant    # type: ios_app # max: critical
- in:  com.yourcompany.PPClient    # type: ios_app # max: critical # not eligible for bounty
- in:  https://github.com/paypal/react-paypal-js    # type: repo # max: critical
- in:  Braintree SDKs    # type: repo # max: critical
- in:  *.paypalcorp.com    # type: url # max: critical
- in:  com.paypal.carica    # type: ios_app # max: critical
- in:  com.paypal.claro    # type: ios_app # max: critical
- in:  com.paypal.telcel    # type: ios_app # max: critical
- in:  com.paypal.android.carica    # type: android_app # max: critical
- in:  com.paypal.android.claro    # type: android_app # max: critical
- in:  com.paypal.android.telcel    # type: android_app # max: critical
- out:  *.paypal.cn    # type: url # max: none
- out:  braintree.com    # type: url # max: none
- out:  www.gopay.com    # type: url # max: none
- out:  *.atlassian.net    # type: other # max: none
- out:  com.paypal.here    # type: android_app # max: none
- out:  com.paypal.herehd    # type: ios_app # max: none
- out:  com.paypal.here    # type: ios_app # max: none
- out:  www.paypal.cn/    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $13,316,687
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
