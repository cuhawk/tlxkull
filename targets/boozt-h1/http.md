# Boozt Fashion AB

> Platform: HackerOne — https://hackerone.com/boozt
> Type: BBP
> Bounty: Low $150–$400 | Medium $500–$1,000 | High $1,500–$3,500 | Critical $3,000–$5,500
> Avg bounty: $348–$390
> Response efficiency: 95% | Avg first response: N/A | Total paid: $60,144
> Last scope update: 2024-12-17

## Scope

- in:  *.boozt.com    # type: wildcard # max: critical
- in:  *.booztlet.com    # type: wildcard # max: critical
- in:  kronor.io    # type: url # max: critical
- in:  com.boozt    # type: android_app # max: critical
- in:  com.booztlet    # type: android_app # max: critical
- in:  com.boozt.app    # type: ios_app # max: critical
- in:  com.boozt.booztlet    # type: ios_app # max: critical
- out:  analytics.boozt.com    # type: url # max: none
- out:  bmp.boozt.com    # type: url # max: none
- out:  www.kronor.io    # type: url # max: none
- out:  firmagaver.boozt.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $60,144
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
