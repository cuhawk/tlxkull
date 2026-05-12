# Tucows (VDP)

> Platform: HackerOne — https://hackerone.com/tucows_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 90% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  *.opensrs.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.hover.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.exacthosting.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ting.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tingmobile.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.enom.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ascio.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tucowsdomains.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.wavelo.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.simplybits.com    # type: wildcard # max: critical # not eligible for bounty
- in:  https://www.tucows.com    # type: url # max: critical # not eligible for bounty
- in:  https://*.opensrs.com    # type: wildcard # max: critical # not eligible for bounty
- out:  *.tucows.com    # type: wildcard # max: none
- out:  Third Party Credential Listing    # type: other # max: none
- out:  Third Party Support Sites    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
