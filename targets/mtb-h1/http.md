# M&T Bank Vulnerability Disclosure

> Platform: HackerOne — https://hackerone.com/mtb
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-09-12

## Scope

- in:  *.mtb.com    # type: url # max: critical # not eligible for bounty
- in:  *.wilmingtontrust.com    # type: url # max: critical # not eligible for bounty
- in:  *.trustnota.com    # type: url # max: critical # not eligible for bounty
- in:  *.leafnow.com    # type: url # max: critical # not eligible for bounty
- in:  com.mtb.mbanking.sc.retail.prod    # type: android_app # max: critical # not eligible for bounty
- in:  com.mtb.mobilebanking.ncr    # type: android_app # max: critical # not eligible for bounty
- in:  397761931    # type: ios_app # max: critical # not eligible for bounty
- in:  1460176225    # type: ios_app # max: critical # not eligible for bounty
- in:  884242294    # type: ios_app # max: critical # not eligible for bounty
- in:  1449758462    # type: ios_app # max: critical # not eligible for bounty
- in:  884228815    # type: ios_app # max: critical # not eligible for bounty
- out:  ceros.leafnow.com    # type: url # max: none
- out:  com.mts.webtrading    # type: android_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
