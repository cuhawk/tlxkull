# Klarna

> Platform: HackerOne — https://hackerone.com/klarna
> Type: BBP
> Bounty: Low $175–$300 | Medium $750–$1,000 | High $2,000–$3,000 | Critical $3,000–$7,000
> Avg bounty: $900–$950
> Response efficiency: 94% | Avg first response: N/A | Total paid: $100,810
> Last scope update: 2025-10-28

## Scope

- in:  xs2a.banking.playground.klarna.com    # type: url # max: critical
- in:  pricerunner.com    # type: url # max: critical
- in:  portal.openbanking.playground.klarna.com    # type: url # max: critical
- in:  klarnacdn.net    # type: url # max: critical
- in:  api.klarna.com    # type: url # max: critical
- in:  js.klarna.com    # type: url # max: critical
- in:  klarna.com    # type: url # max: critical
- in:  klarna.net    # type: url # max: critical
- in:  Merchant Portal    # type: other # max: critical
- in:  Klarna Android App (com.myklarnamobile)    # type: android_app # max: critical
- in:  Klarna iOS App (com.klarna.app)    # type: ios_app # max: critical
- in:  app.klarna.com    # type: api # max: critical
- out:  locker.klarna.com    # type: url # max: none
- out:  https://app.klarna.com/us/api/connected_card_bff/    # type: url # max: none
- out:  https://api.pricerunner.com/swagger-ui.html    # type: url # max: none
- out:  https://api-us.pricerunner.com/swagger-ui.html    # type: url # max: none
- out:  https://api-stage.pricerunner.com/swagger-ui.html    # type: url # max: none
- out:  nuji.com    # type: url # max: none
- out:  jobs.pricerunner.com    # type: url # max: none
- out:  Kustom    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $100,810
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
