# Credit Karma

> Platform: HackerOne — https://hackerone.com/creditkarma
> Type: BBP
> Bounty: Low $250 | Medium $700 | High $2,250 | Critical $5,000
> Avg bounty: $250–$700
> Response efficiency: 90% | Avg first response: N/A | Total paid: $108,650
> Last scope update: 2023-10-10

## Scope

- in:  https://*.creditkarma.com    # type: wildcard # max: critical
- in:  http://*.creditkarma.co.uk    # type: wildcard # max: critical
- in:  https://*.creditkarma.ca    # type: wildcard # max: critical
- in:  accounts.creditkarma.com    # type: url # max: critical
- in:  www.creditkarma.ca    # type: url # max: critical
- in:  api.creditkarma.com    # type: url # max: critical
- in:  https://www.creditkarma.com/reviews/    # type: url # max: critical
- in:  blog.creditkarma.com    # type: url # max: critical
- in:  https://www.creditkarma.com/savings    # type: url # max: critical
- in:  support.creditkarma.ca    # type: url # max: critical
- in:  com.creditkarma.mobile    # type: android_app # max: critical
- in:  com.creditkarma.mobile.international    # type: android_app # max: critical
- in:  com.creditkarma.mobile    # type: ios_app # max: critical
- in:  com.creditkarma.mobile.international    # type: ios_app # max: critical
- in:  com.creditkarma.canada    # type: ios_app # max: critical
- in:  help.creditkarma.co.uk    # type: url # max: critical
- in:  https://help.creditkarma.co.uk/    # type: url # max: critical
- in:  https://*.creditkarma.co.uk    # type: url # max: critical
- in:  https://*.creditkarma.co.uk    # type: url # max: critical
- in:  https://*.creditkarma.co.uk    # type: url # max: critical
- in:  https://*.creditkarma.co.uk    # type: url # max: critical
- in:  https://*.creditkarma.co.uk    # type: url # max: critical
- out:  https://www.creditkarma.com/article/*    # type: wildcard # max: none
- out:  tax.creditkarma.com    # type: url # max: none
- out:  help.creditkarma.com    # type: url # max: none
- out:  https://www.creditkarma.com/all/advice    # type: url # max: none
- out:  appsflyer.com    # type: url # max: none
- out:  crashlytics.com    # type: url # max: none
- out:  taplytics.com    # type: url # max: none
- out:  socialverification.creditkarma.com    # type: url # max: none
- out:  socialverification.stage.creditkarma.com    # type: url # max: none
- out:  taxsupport.creditkarma.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $108,650
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
