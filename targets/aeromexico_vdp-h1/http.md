# Aeromexico VDP

> Platform: HackerOne — https://hackerone.com/aeromexico_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 89% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2024-10-10

## Scope

- in:  www.aeromexico.com*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.aeromexico.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.amlab7.com    # type: wildcard # max: medium # not eligible for bounty
- in:  https://www.aeromexicobusiness.com    # type: url # max: critical # not eligible for bounty
- in:  https://www.aeromexicovacations.com    # type: url # max: critical # not eligible for bounty
- in:  https://www.aeromexicorewards.com    # type: url # max: critical # not eligible for bounty
- in:  https://www.aeromexico.com/es-mx/aeromexico-rewards    # type: url # max: critical # not eligible for bounty
- in:  https://amfacturacion.aeromexico.com    # type: url # max: critical # not eligible for bounty
- in:  https://facturacion.aeromexico.com    # type: url # max: critical # not eligible for bounty
- in:  https://portalfacturacioncargo.aeromexico.com    # type: url # max: critical # not eligible for bounty
- in:  http://www.aeromexico-delta.com    # type: url # max: medium # not eligible for bounty
- in:  http://www.delta-aeromexico.com    # type: url # max: medium # not eligible for bounty
- in:  http://www.vuela.aeromexico.com    # type: url # max: low # not eligible for bounty
- in:  aeromexico.com    # type: url # max: critical # not eligible for bounty
- out:  *www.aeromexico.com    # type: wildcard # max: none
- out:  https://www.aeromexico.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
