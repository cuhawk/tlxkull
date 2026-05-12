# Lovable VDP

> Platform: HackerOne — https://hackerone.com/lovable-vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 86% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2025-06-25

## Scope

- in:  lovable.dev    # type: url # max: critical # not eligible for bounty
- in:  oauth.lovable.dev    # type: url # max: critical # not eligible for bounty
- in:  api.lovable.dev    # type: url # max: critical # not eligible for bounty
- in:  mcp.lovable.dev    # type: url # max: critical # not eligible for bounty
- in:  auth.lovable.dev    # type: url # max: critical # not eligible for bounty
- in:  training    # type: other # max: critical # not eligible for bounty
- out:  lovable.app    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
