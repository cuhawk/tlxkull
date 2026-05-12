# ABN AMRO Bank VDP

> Platform: HackerOne — https://hackerone.com/abn_amro_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2025-09-03

## Scope

- in:  *.abnamro.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.abnamro.nl    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tikkie.me    # type: wildcard # max: critical # not eligible for bounty
- in:  *.abnamrocomfin.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.abnamro.org    # type: wildcard # max: critical # not eligible for bounty
- in:  *.alfam.nl    # type: wildcard # max: critical # not eligible for bounty
- in:  *.bethmannbank.de    # type: wildcard # max: critical # not eligible for bounty
- in:  *neuflizeobc.fr    # type: wildcard # max: critical # not eligible for bounty
- in:  *abnamroprivatebanking.be    # type: wildcard # max: critical # not eligible for bounty
- in:  *.abnamro.be    # type: wildcard # max: critical # not eligible for bounty
- in:  *.abnamrolease.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.abnamroinvestmentsolutions.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.new10.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.buut.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.bux.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.getbux.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.bux2b.com    # type: wildcard # max: critical # not eligible for bounty
- in:  www.buut.com    # type: url # max: critical # not eligible for bounty
- in:  com.abnamro.nl.buut    # type: android_app # max: critical # not eligible for bounty
- in:  6698897106    # type: ios_app # max: critical # not eligible for bounty
- out:  *.aahg.nl    # type: wildcard # max: none
- out:  *.florius.nl    # type: wildcard # max: none
- out:  *.moneyou.nl    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
