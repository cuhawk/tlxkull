# Expedia Group Bug Bounty

> Platform: HackerOne — https://hackerone.com/expediagroup_bbp
> Type: BBP
> Bounty: Low $300 | Medium $1,000 | High $3,000 | Critical $6,000
> Avg bounty: $300–$750
> Response efficiency: 67% | Avg first response: N/A | Total paid: $742,813
> Last scope update: 2025-10-15

## Scope

- in:  *.vrbo.com    # type: wildcard # max: critical
- in:  *.carrentals.com    # type: wildcard # max: critical
- in:  *.wotif.com    # type: wildcard # max: critical
- in:  *.cheaptickets.com    # type: wildcard # max: critical
- in:  *.lastminute.co.nz    # type: wildcard # max: critical
- in:  *.lastminute.com.au    # type: wildcard # max: critical
- in:  *.travelocity.com    # type: wildcard # max: critical
- in:  *.travelocity.ca    # type: wildcard # max: critical
- in:  *.expediapartnercentral.com    # type: wildcard # max: critical
- in:  www.hotels.com    # type: url # max: critical
- in:  www.expedia.com    # type: url # max: critical
- in:  www.vrbo.com    # type: url # max: critical
- in:  www.hotwirepartnercentral.com    # type: url # max: critical
- in:  www.orbitz.com    # type: url # max: critical
- in:  www.ebookers.com    # type: url # max: critical
- in:  www.ebookers.fi    # type: url # max: critical
- in:  www.mrjet.se    # type: url # max: critical
- in:  www.carrentals.com    # type: url # max: critical
- in:  www.wotif.com    # type: url # max: critical
- in:  www.cheaptickets.com    # type: url # max: critical
- in:  www.lastminute.co.nz    # type: url # max: critical
- in:  www.lastminute.com.au    # type: url # max: critical
- in:  www.travelocity.com    # type: url # max: critical
- in:  www.travelocity.ca    # type: url # max: critical
- in:  www.abritel.fr    # type: url # max: critical
- in:  www.bookabach.co.nz    # type: url # max: critical
- in:  www.fewo-direkt.de    # type: url # max: critical
- in:  www.stayz.com.au    # type: url # max: critical
- in:  www.expediagroup.com    # type: url # max: critical
- in:  www.flights.com    # type: url # max: critical
- in:  www.expedia-aarp.com    # type: url # max: critical
- in:  www.expediataap.com    # type: url # max: high
- in:  com.hotwire.hotels    # type: android_app # max: critical
- in:  com.ebookers    # type: android_app # max: critical
- in:  com.orbitz    # type: android_app # max: critical
- in:  com.expedia.bookings    # type: android_app # max: critical
- in:  com.wotif.android    # type: android_app # max: critical
- in:  com.cheaptickets    # type: android_app # max: critical
- in:  com.travelocity.android    # type: android_app # max: critical
- in:  com.hcom.android    # type: android_app # max: critical
- in:  com.vrbo.android    # type: android_app # max: critical
- in:  566635048    # type: ios_app # max: critical
- in:  403546234    # type: ios_app # max: critical
- in:  483394780    # type: ios_app # max: critical
- in:  427916203    # type: ios_app # max: critical
- in:  531549799    # type: ios_app # max: critical
- in:  880759727    # type: ios_app # max: critical
- in:  284803487    # type: ios_app # max: critical
- in:  284971959    # type: ios_app # max: critical
- in:  1245772818    # type: ios_app # max: critical
- in:  www.hotwire.com    # type: url # max: critical # not eligible for bounty
- in:  com.expediapartnercentral    # type: android_app # max: critical # not eligible for bounty
- in:  987675995    # type: ios_app # max: critical # not eligible for bounty
- in:  *.hotwire.com    # type: wildcard # max: critical
- in:  www.expediapartnercentral.com    # type: url # max: critical
- in:  www.expediacruises.com    # type: url # max: critical
- in:  http://www.cruiseshipcenters.com/api/searchcenter    # type: url # max: critical
- in:  www.egadvertising.com    # type: url # max: critical
- in:  *.ean.com    # type: url # max: critical
- in:  www.ebookers.fr    # type: url # max: critical
- in:  www.ebookers.de    # type: url # max: critical
- in:  www.ebookers.ch    # type: url # max: critical
- in:  www.ebookers.ie    # type: url # max: critical
- in:  *.hoteis.com    # type: url # max: critical
- in:  *.hoteles.com    # type: url # max: critical
- in:  *.hotels.com    # type: url # max: critical
- in:  *.escapia.com    # type: wildcard # max: critical
- out:  *.expediacruises.com    # type: wildcard # max: none
- out:  https://*.expedia.com/    # type: wildcard # max: none
- out:  www.expediapartnersolutions.com    # type: url # max: none
- out:  www.expediaagents.com    # type: url # max: none
- out:  bookus.expediacruises.com    # type: url # max: none
- out:  thailand.airasiago.com    # type: url # max: none
- out:  china.airasiago.com    # type: url # max: none
- out:  https://www.abritel.fr/api/track    # type: url # max: none
- out:  support.ean.com    # type: url # max: none
- out:  resources.ean.com    # type: url # max: none
- out:  comms.ean.com    # type: url # max: none
- out:  taapacademy.expediapartnersolutions.com    # type: url # max: none
- out:  taap-ui-bundles.expediapartnersolutions.com    # type: url # max: none
- out:  taap-ui-bundles-test.expediapartnersolutions.com    # type: url # max: none
- out:  sure.expediapartnersolutions.com    # type: url # max: none
- out:  support.expediapartnersolutions.com    # type: url # max: none
- out:  status.expediapartnersolutions.com    # type: url # max: none
- out:  info.expediapartnersolutions.com    # type: url # max: none
- out:  gco.expediapartnersolutions.com    # type: url # max: none
- out:  gco-get.expediapartnersolutions.com    # type: url # max: none
- out:  discoveryhub.expediapartnersolutions.com    # type: url # max: none
- out:  apartmentjet.com    # type: url # max: none
- out:  blog.hotels.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $742,813
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
