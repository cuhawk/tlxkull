# Anywhere Real Estate

> Platform: HackerOne — https://hackerone.com/anywhererealestate
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 95% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-04-13

## Scope

- in:  *.era.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.trgc.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.leadrouter.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.cartus.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.mycbdesk.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.anywhere.re    # type: wildcard # max: critical # not eligible for bounty
- in:  *.century21.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.realogy.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.bhgre.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.sothebysrealty.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.corcoran.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.cbcworldwide.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.nrtllc.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.coldwellbanker.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.century21global.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.c21.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.coldwellbanker.*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.cbcworldwide.*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.realogy.*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.bhgre.*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.corcoran.*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.sothebysrealty.*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.nrtllc.*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.century21.*    # type: wildcard # max: critical # not eligible for bounty
- in:  new.myzap.com    # type: url # max: critical # not eligible for bounty
- out:  century21.hk    # type: url # max: none
- out:  c21.hk    # type: url # max: none
- out:  mltest1.cbintouch.com    # type: url # max: none
- out:  *.cbintouch.com    # type: wildcard # max: none
- out:  www.cartus.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
