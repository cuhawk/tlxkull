# Priceline

> Platform: HackerOne — https://hackerone.com/priceline
> Type: BBP
> Bounty: Low $100–$250 | Medium $150–$1,000 | High $250–$2,000 | Critical $500–$5,000
> Avg bounty: $250–$250
> Response efficiency: 91% | Avg first response: N/A | Total paid: $290,000
> Last scope update: 2025-09-03

## Scope

- in:  www.priceline.com    # type: url # max: critical
- in:  cruises.priceline.com    # type: url # max: critical
- in:  www.getaroom.com    # type: url # max: critical
- in:  flyiin.com    # type: url # max: critical
- in:  priceline.com    # type: url # max: critical
- in:  ir.bookingholdings.com    # type: url # max: critical
- in:  bookingholdings-coe.com    # type: url # max: critical
- in:  https://www.priceline.com/pwd/v0/pcln-graphql/    # type: url # max: critical
- in:  press.priceline.com    # type: url # max: medium
- in:  www.bookingholdings.com    # type: url # max: none
- in:  com.priceline.android.negotiator    # type: android_app # max: critical
- in:  336381998    # type: ios_app # max: critical
- in:  Penny    # type: other # max: critical
- in:  http://www.priceline.com/pwd/v0/pcln-graphql/    # type: url # max: critical
- in:  *.priceline.com    # type: wildcard # max: high
- in:  336381998    # type: ios_app # max: critical
- out:  secure.rezserver.com    # type: url # max: none
- out:  reservations.rezserver.com    # type: url # max: none
- out:  www.airportrentalcars.com    # type: url # max: none
- out:  api.rezserver.com    # type: url # max: none
- out:  admin.rezserver.com    # type: url # max: none
- out:  availability.getaroom.com    # type: url # max: none
- out:  extranet.getaroom.com    # type: url # max: none
- out:  breadcrumb.getaroom.com    # type: url # max: none
- out:  supply.getaroom.com    # type: url # max: none
- out:  stockroom.production.getaroom.com    # type: url # max: none
- out:  *.roomvaluesteam.com    # type: url # max: none
- out:  *.testaroom.com    # type: url # max: none
- out:  *.testaroom.cloud    # type: url # max: none
- out:  groupdeals.priceline.com    # type: url # max: none
- out:  careers.priceline.com    # type: url # max: none
- out:  weatherstatus.priceline.com    # type: url # max: none
- out:  img1.priceline.com    # type: url # max: none
- out:  url5932.travel.priceline.com    # type: url # max: none
- out:  tools.corp.priceline.com    # type: url # max: none
- out:  tools-qaa.corp.priceline.com    # type: url # max: none
- out:  remotecontrol.corp.priceline.com    # type: url # max: none
- out:  qaa.booking.priceline.com    # type: url # max: none
- out:  offers.priceline.com    # type: url # max: none
- out:  mail.corp.priceline.com    # type: url # max: none
- out:  localdealsemail.priceline.com    # type: url # max: none
- out:  links.deals.priceline.com    # type: url # max: none
- out:  jira.corp.priceline.com    # type: url # max: none
- out:  itsupport.corp.priceline.com    # type: url # max: none
- out:  ids-too.priceline.com    # type: url # max: none
- out:  ids-dev.priceline.com    # type: url # max: none
- out:  help.corp.priceline.com    # type: url # max: none
- out:  guse4-rc-qa.priceline.com    # type: url # max: none
- out:  google.corp.priceline.com    # type: url # max: none
- out:  experiences.priceline.com    # type: url # max: none
- out:  employeedeals.flightdeals.priceline.com    # type: url # max: none
- out:  dev.sales-ccp.priceline.com    # type: url # max: none
- out:  dev.customerservice-ccp.priceline.com    # type: url # max: none
- out:  dashboard.corp.priceline.com    # type: url # max: none
- out:  customerservice-ccp.priceline.com    # type: url # max: none
- out:  booking.priceline.com    # type: url # max: none
- out:  api-guse4-poc.priceline.com    # type: url # max: none
- out:  api-gnae1-poc.priceline.com    # type: url # max: none
- out:  ace-qa.corp.priceline.com    # type: url # max: none
- out:  1psb.priceline.com    # type: url # max: none
- out:  www.priceline.com/vp-web/*     # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $290,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
