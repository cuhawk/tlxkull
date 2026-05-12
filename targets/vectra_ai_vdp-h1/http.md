# Vectra AI, Inc. (Response)

> Platform: HackerOne — https://hackerone.com/vectra_ai_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 86% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-12-05

## Scope

- in:  *.vectra-svc.ai    # type: wildcard # max: critical # not eligible for bounty
- in:  *.vectra.ai    # type: wildcard # max: critical # not eligible for bounty
- in:  vectra.ai    # type: url # max: critical # not eligible for bounty
- in:  api.vectranetworks.com    # type: url # max: critical # not eligible for bounty
- in:  metadata.vectranetworks.com    # type: url # max: critical # not eligible for bounty
- in:  rp.vectranetworks.com    # type: url # max: critical # not eligible for bounty
- in:  update2.vectranetworks.com    # type: url # max: critical # not eligible for bounty
- in:  vpn.vectranetworks.com    # type: url # max: critical # not eligible for bounty
- in:  https://203074349567.uw2.portal.vectra.ai/api    # type: api # max: critical # not eligible for bounty
- out:  partners.vectra.ai    # type: url # max: none
- out:  https://203074349567.uw2.portal.vectra.ai/    # type: api # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
