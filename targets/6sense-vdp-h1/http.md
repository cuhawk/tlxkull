# 6sense VDP

> Platform: HackerOne — https://hackerone.com/6sense-vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 70% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2024-06-06

## Scope

- in:  https://6sense.com/platform/sales/signup    # type: url # max: critical # not eligible for bounty
- in:  https://chromewebstore.google.com/detail/6sense-si-extension-for-c/mkpoonlmiaknmcdcmdhbnehhglndcolf?hl=en    # type: url # max: critical # not eligible for bounty
- in:  Security vulnerabilities that are identified in 6sense products or in website domains owned, operated, or controlled by 6sense are in scope    # type: other # max: critical # not eligible for bounty
- in:  https://api.6sense.com/docs/#introduction    # type: api # max: critical # not eligible for bounty
- out:  revcity.6sense.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
