# BILL VDP

> Platform: HackerOne — https://hackerone.com/bill_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 84% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2025-07-30

## Scope

- in:  *.bill.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.divvy.co    # type: wildcard # max: critical # not eligible for bounty
- in:  *.2go.com    # type: wildcard # max: critical # not eligible for bounty
- in:  app.bill.com    # type: url # max: critical # not eligible for bounty
- in:  app.divvy.co    # type: url # max: critical # not eligible for bounty
- in:  Other BILL assets    # type: other # max: critical # not eligible for bounty
- in:  com.bdc.bill    # type: android_app # max: critical # not eligible for bounty
- in:  com.divvypay.Divvy    # type: android_app # max: critical # not eligible for bounty
- in:  com.invoice2go.invoice2goplus    # type: android_app # max: critical # not eligible for bounty
- in:  id980353334    # type: ios_app # max: critical # not eligible for bounty
- in:  id1114962353    # type: ios_app # max: critical # not eligible for bounty
- in:  *.finmark.com    # type: wildcard # max: critical # not eligible for bounty
- out:  *.zipbooks.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
