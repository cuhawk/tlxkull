# Expedia Group VDP

> Platform: HackerOne — https://hackerone.com/expediagroup
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 55% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-10-06

## Scope

- in:  *.expedia.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.hotwire.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.orbitz.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.hotels.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.homeaway.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.cheaptickets.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.travelocity.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.wotif.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.cruiseshipcenters.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.lastminute.com.au    # type: wildcard # max: critical # not eligible for bounty
- in:  *.carrentals.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.expediapartnercentral.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.abritel.fr    # type: wildcard # max: critical # not eligible for bounty
- in:  *.bookabach.co.nz    # type: wildcard # max: critical # not eligible for bounty
- in:  *.fewo-direkt.de    # type: wildcard # max: critical # not eligible for bounty
- in:  *.stayz.com.au    # type: wildcard # max: critical # not eligible for bounty
- in:  *.expediagroup.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.flights.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.vrbo.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.hotwirepartnercentral.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ebookers.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.mrjet.se    # type: wildcard # max: critical # not eligible for bounty
- in:  *.expediapartnersolutions.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ean.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.lastminute.co.nz    # type: wildcard # max: critical # not eligible for bounty
- in:  *.travelocity.ca    # type: wildcard # max: critical # not eligible for bounty
- in:  http://www.cruiseshipcenters.com/api/searchcenter    # type: url # max: critical # not eligible for bounty
- in:  www.vrbo.com    # type: url # max: critical # not eligible for bounty
- in:  www.ebookers.fi    # type: url # max: critical # not eligible for bounty
- in:  www.expedia-aarp.com    # type: url # max: critical # not eligible for bounty
- in:  Other Expedia-owned Asset     # type: other # max: critical # not eligible for bounty
- in:  com.expediapartnercentral    # type: android_app # max: critical # not eligible for bounty
- in:  987675995    # type: ios_app # max: critical # not eligible for bounty
- in:  thailand.airasiago.com    # type: url # max: critical # not eligible for bounty
- in:  china.airasiago.com    # type: url # max: critical # not eligible for bounty
- in:  https://*.expedia.com/    # type: wildcard # max: critical # not eligible for bounty
- in:  *.egencia.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *apartmentjet.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.aliceplatform.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.aliceapp.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.trover.com    # type: wildcard # max: critical # not eligible for bounty
- out:  *.egadvertising.com    # type: wildcard # max: none
- out:  *.hoteles.com    # type: wildcard # max: none
- out:  *.hoteis.com    # type: wildcard # max: none
- out:  *.expediaagents.com    # type: wildcard # max: none
- out:  *.expediacruises.com    # type: wildcard # max: none
- out:  https://www.abritel.fr/api/track    # type: url # max: none
- out:  *.lastminute.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
