# Paystack Vulnerability Disclosure

> Platform: HackerOne — https://hackerone.com/paystack-vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 89% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-05-11

## Scope

- in:  *.paystack.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.paystackintegrations.com    # type: url # max: critical # not eligible for bounty
- in:  nigerialogos.com    # type: url # max: critical # not eligible for bounty
- in:  decodefintech.com    # type: url # max: critical # not eligible for bounty
- in:  checkout.paystack.com    # type: url # max: critical # not eligible for bounty
- in:  api.paystack.co    # type: url # max: critical # not eligible for bounty
- in:  dashboard.paystack.com    # type: url # max: critical # not eligible for bounty
- in:  standard.paystack.co    # type: url # max: critical # not eligible for bounty
- in:  zap.money    # type: url # max: critical # not eligible for bounty
- in:  paystackintegrations.com    # type: url # max: critical # not eligible for bounty
- in:  paystackmfb.com    # type: url # max: critical # not eligible for bounty
- in:  paystack.shop    # type: url # max: critical # not eligible for bounty
- in:  Assets which are owned by Paystack are in scope for this Vulnerability Disclosure Program    # type: other # max: critical # not eligible for bounty
- in:  com.paystack.zap    # type: android_app # max: critical # not eligible for bounty
- in:  legacy.paystack.co    # type: url # max: critical # not eligible for bounty
- in:  *.payable.com    # type: other # max: critical # not eligible for bounty
- in:  *.indiehackers.com    # type: other # max: critical # not eligible for bounty
- in:  Stripe Radar    # type: other # max: critical # not eligible for bounty
- in:  Stripe Sigma    # type: other # max: critical # not eligible for bounty
- in:  Stripe Atlas    # type: other # max: critical # not eligible for bounty
- in:  Stripe SDKs    # type: other # max: critical # not eligible for bounty
- in:  Stripe Open Source    # type: other # max: critical # not eligible for bounty
- in:  Stripe Billing    # type: other # max: critical # not eligible for bounty
- in:  Stripe Checkout    # type: other # max: critical # not eligible for bounty
- in:  Stripe Connect    # type: other # max: critical # not eligible for bounty
- in:  Stripe Terminal    # type: other # max: critical # not eligible for bounty
- in:  com.stripe.android.dashboard    # type: android_app # max: critical # not eligible for bounty
- in:  Stripe Issuing    # type: other # max: critical # not eligible for bounty
- in:  Stripe Dashboard    # type: other # max: critical # not eligible for bounty
- in:  Stripe Elements    # type: other # max: critical # not eligible for bounty
- in:  Stripe Payments    # type: other # max: critical # not eligible for bounty
- in:  978516833    # type: ios_app # max: critical # not eligible for bounty
- in:  *.touchtechpayments.com    # type: other # max: critical # not eligible for bounty
- in:  js.stripe.com    # type: url # max: critical # not eligible for bounty
- in:  api.taxjar.com    # type: url # max: critical # not eligible for bounty
- in:  app.taxjar.com    # type: url # max: critical # not eligible for bounty
- in:  api.stripe.com    # type: url # max: critical # not eligible for bounty
- in:  *.stripe.com    # type: other # max: critical # not eligible for bounty
- in:  dashboard.stripe.com    # type: url # max: critical # not eligible for bounty
- in:  connect.stripe.com    # type: url # max: critical # not eligible for bounty
- in:  com.stripe.android.dashboard    # type: other_apk # max: critical # not eligible for bounty
- out:  *.paystack.com    # type: other # max: none
- out:  *.runkit.com    # type: other # max: none
- out:  *.teapot.co    # type: other # max: none
- out:  *.totems.co    # type: other # max: none
- out:  *.helmservices.com    # type: other # max: none
- out:  *.index.com    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
