# OANDA

> Platform: HackerOne — https://hackerone.com/oanda
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2021-11-29

## Scope

- in:  *.oanda.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.oanda.jp    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tms.pl    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tmsbrokers.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.coinpass.com    # type: wildcard # max: critical # not eligible for bounty
- in:  com.oanda.fxtrade    # type: android_app # max: critical # not eligible for bounty
- in:  370922777    # type: ios_app # max: critical # not eligible for bounty
- in:  coinpass.com    # type: url # max: critical # not eligible for bounty
- in:  *.investmentuniversity.pl    # type: wildcard # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
