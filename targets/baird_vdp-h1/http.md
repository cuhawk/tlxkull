# Baird

> Platform: HackerOne — https://hackerone.com/baird_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 98% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2025-04-24

## Scope

- in:  https://*.rwbaird.com    # type: wildcard # max: critical # not eligible for bounty
- in:  bairdwealth.com    # type: url # max: critical # not eligible for bounty
- in:  www.rwbaird.com    # type: url # max: medium # not eligible for bounty
- out:  http://bol.rwbaird.com    # type: url # max: none
- out:  http://www.rwbaird.com/docs    # type: url # max: none
- out:  http://uatclientdocs.rwbaird.com    # type: url # max: none
- out:  http://clientdocs.rwbaird.com    # type: url # max: none
- out:  http://content.rwbaird.com    # type: url # max: none
- out:  com.rwbaird.investorandroid    # type: android_app # max: none
- out:  777691707    # type: ios_app # max: none
- out:  Potentially Confidential Documents    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
