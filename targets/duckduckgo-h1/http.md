# DuckDuckGo

> Platform: HackerOne — https://hackerone.com/duckduckgo
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 58% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  *.duckduckgo.com    # type: wildcard # max: critical # not eligible for bounty
- in:  https://github.com/duckduckgo/duckduckgo-privacy-extension    # type: repo # max: critical # not eligible for bounty
- in:  com.duckduckgo.mobile.android    # type: android_app # max: critical # not eligible for bounty
- in:  com.duckduckgo.mobile.ios    # type: ios_app # max: critical # not eligible for bounty
- in:  https://staging.netp.duckduckgo.com/servers    # type: url # max: low # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
