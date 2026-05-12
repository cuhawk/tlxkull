# Moov

> Platform: HackerOne — https://hackerone.com/moov
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-09-20

## Scope

- in:  email-zendesk    # type: other # max: none # not eligible for bounty
- in:  dashboard.moov.io    # type: url # max: critical # not eligible for bounty
- in:  api.moov.io    # type: url # max: critical # not eligible for bounty
- in:  cards.moov.io    # type: url # max: critical # not eligible for bounty
- in:  gateway.moov.io    # type: url # max: critical # not eligible for bounty
- in:  infra-oss.moov.io    # type: url # max: critical # not eligible for bounty
- in:  moov.io    # type: url # max: critical # not eligible for bounty
- in:  oss.moov.io    # type: url # max: critical # not eligible for bounty
- in:  34.133.2.41    # type: ip_address # max: critical # not eligible for bounty
- in:  35.188.92.133    # type: ip_address # max: critical # not eligible for bounty
- in:  35.223.161.83    # type: ip_address # max: critical # not eligible for bounty
- in:  34.68.224.212    # type: ip_address # max: critical # not eligible for bounty
- out:  support.moov.io    # type: url # max: none
- out:  slack.moov.io    # type: url # max: none
- out:  tools.cards.moov.io    # type: url # max: none
- out:  tools.moov.io    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
