# BitMEX

> Platform: HackerOne — https://hackerone.com/bitmex
> Type: BBP
> Bounty: Low $900 | Medium $4,500 | High $15,000 | Critical $30,000
> Avg bounty: $300–$300
> Response efficiency: 90% | Avg first response: N/A | Total paid: $235,337
> Last scope update: 2025-02-11

## Scope

- in:  *.bitmex.com    # type: wildcard # max: critical
- in:  testnet.bitmex.com    # type: url # max: critical
- in:  www.bitmex.com    # type: url # max: critical
- in:  All Other BitMEX Assets    # type: other # max: critical
- in:  https://play.google.com/store/apps/details?id=com.bitmex.app.android.testnet    # type: other # max: critical
- in:  https://testflight.apple.com/join/533gFghn    # type: other # max: critical
- in:  com.bitmex.app.android    # type: android_app # max: critical
- in:  1589023233    # type: ios_app # max: critical
- in:  public.bitmex.com    # type: url # max: critical
- out:  support.bitmex.com    # type: url # max: none
- out:  status.bitmex.com    # type: url # max: none
- out:  public.bitmex.com    # type: url # max: none
- out:  public-testnet.bitmex.com    # type: url # max: none
- out:  bitmex.freshdesk.com    # type: url # max: none
- out:  bitmex-org.freshworks.com    # type: url # max: none
- out:  academy.bitmex.com    # type: url # max: none
- out:  blog.bitmex.com    # type: url # max: none
- out:  research.bitmex.com    # type: url # max: none
- out:  affiliates.bitmex.com    # type: url # max: none
- out:  analytics.bitmex.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $235,337
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
