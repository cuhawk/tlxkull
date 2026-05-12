# Yoti

> Platform: HackerOne — https://hackerone.com/yoti
> Type: BBP
> Bounty: Low $300 | Medium $1,000 | High $2,000 | Critical $4,000
> Avg bounty: $200–$300
> Response efficiency: 20% | Avg first response: N/A | Total paid: $60,925
> Last scope update: 2024-02-13

## Scope

- in:  core.yoti.com    # type: url # max: critical
- in:  api.yoti.com    # type: url # max: critical
- in:  ccloud.yoti.com    # type: url # max: critical
- in:  code.yoti.com    # type: url # max: critical
- in:  www.yotisign.com    # type: url # max: critical
- in:  hub.yoti.com    # type: url # max: critical
- in:  identity.yoti.com    # type: url # max: critical
- in:  com.yoti.mobile.android.live    # type: android_app # max: critical
- in:  983980808    # type: ios_app # max: critical
- in:  frankd.yoti.com    # type: url # max: critical
- in:  https://www.yoti.com    # type: url # max: critical
- in:  https://chrome.google.com/webstore/detail/yoti-password-manager/ajgehecfkfhindkhdcjmifbngkfdflla    # type: other # max: critical
- in:  https://addons.mozilla.org/en-US/firefox/addon/yoti-password-manager/    # type: other # max: critical
- in:  static.yoti.com    # type: url # max: critical
- out:  www.yoti.com    # type: url # max: none
- out:  developers.yoti.com    # type: url # max: none
- out:  Yoti Password Manager browser extension    # type: other # max: none
- out:  Yoti liveness detection campaign    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $60,925

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
