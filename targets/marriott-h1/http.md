# Marriott Bug Bounty Program

> Platform: HackerOne — https://hackerone.com/marriott
> Type: BBP
> Bounty: Low $599 | Medium $3,429 | High $8,000 | Critical $11,000
> Avg bounty: $300–$548
> Response efficiency: 99% | Avg first response: N/A | Total paid: $538,588
> Last scope update: 2025-11-05

## Scope

- in:  *gateway-apc.marriott.com    # type: wildcard # max: critical
- in:  *.dcfgateway.marriott.com    # type: wildcard # max: high
- in:  *.mgs.marriott.com    # type: wildcard # max: high
- in:  *.gateway.marriott.com    # type: wildcard # max: high
- in:  *.apigatewayc.marriott.com    # type: wildcard # max: high
- in:  *.apigwc.marriott.com    # type: wildcard # max: high
- in:  *.artifactory.marriott.com    # type: wildcard # max: high
- in:  *.sba.marriott.com    # type: wildcard # max: high
- in:  homes-and-villas.marriott.com    # type: url # max: critical
- in:  careers.marriott.com    # type: url # max: critical
- in:  sso.marriott.com    # type: url # max: critical
- in:  mgs.marriott.com    # type: url # max: critical
- in:  jobs.marriott.com    # type: url # max: critical
- in:  passwordchallenge.marriott.com    # type: url # max: critical
- in:  gateway*.marriott.com    # type: url # max: critical
- in:  dcfgateway*.marriott.com    # type: url # max: critical
- in:  marriottfranchisetransactions.marriott.com    # type: url # max: critical
- in:  lawmanager.marriott.com    # type: url # max: critical
- in:  all-inclusive.marriott.com    # type: url # max: critical
- in:  reservations.all-inclusive.marriott.com    # type: url # max: critical
- in:  marrtool.com    # type: url # max: critical
- in:  cpp.marriott.com    # type: url # max: critical
- in:  editionhotels.com    # type: url # max: critical
- in:  https://gatewaydsapdev2.marriott.com/    # type: url # max: critical
- in:  https://dcfgatewaytst1.marriott.com/    # type: url # max: critical
- in:  https://gatewaydsaptst1.marriott.com/    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  moments.marriottbonvoy.com    # type: url # max: critical
- in:  help.marriott.com    # type: url # max: critical
- in:  psp.marriott.com    # type: url # max: critical
- in:  esupplier.marriott.com    # type: url # max: critical
- in:  activities.marriott.com    # type: url # max: high
- in:  https://gatewaydsaptst2.marriott.com/    # type: url # max: high
- in:  www.ritzcarlton.com/    # type: url # max: high
- in:  *uat.marriott.com    # type: url # max: high
- in:  traveler.marriott.com    # type: url # max: high
- in:  travelagents.marriott.com/    # type: url # max: high
- in:  mipartnerprivileges.marriott.com    # type: url # max: high
- in:  efast.marriott.com    # type: url # max: high
- in:  eidhelp.marriott.com    # type: url # max: high
- in:  apcgateway.marriott.com    # type: url # max: high
- in:  auth-apc.marriott.com    # type: url # max: high
- in:  bpa2.marriott.com    # type: url # max: high
- in:  device.marriott.com    # type: url # max: high
- in:  ifast.marriott.com    # type: url # max: high
- in:  ssm-marriottms.saviyntcloud.com    # type: url # max: high
- in:  wechat.api.marriott.com    # type: url # max: high
- in:  hotel-deals.marriott.com    # type: url # max: medium
- in:  http://www.shopmarriott.com    # type: url # max: medium
- in:  smetrics.marriott.com    # type: url # max: medium
- in:  bsp.marriott.com    # type: url # max: medium
- in:  cache.marriott.com    # type: url # max: medium
- in:  channel-portal.homes-and-villas.marriott.com    # type: url # max: medium
- in:  ci-propertyconversionportal.marriott.com    # type: url # max: medium
- in:  contentportal.marriott.com    # type: url # max: medium
- in:  contentportalauth.marriott.com    # type: url # max: medium
- in:  globaldesign.marriott.com    # type: url # max: medium
- in:  join.marriott.com    # type: url # max: medium
- in:  joinrewards.marriott.com    # type: url # max: medium
- in:  oasisprod.marriott.com    # type: url # max: medium
- in:  ocijlbex1prd.marriott.com    # type: url # max: medium
- in:  owa.marriott.com    # type: url # max: medium
- in:  app-insiders.marriott.com    # type: url # max: medium
- in:  mds.marriott.com    # type: url # max: medium
- in:  meetmarriottbonvoy.marriott.com    # type: url # max: medium
- in:  prod-mipaasiaasservices.marriott.com    # type: url # max: medium
- in:  www.travel-brilliantly.marriott.com    # type: url # max: medium
- in:  uber.marriott.com    # type: url # max: medium
- in:  university.marriott.com    # type: url # max: medium
- in:  bilt.marriott.com    # type: url # max: medium
- in:  gifts.marriott.com    # type: url # max: medium
- in:  joinmarriottbonvoy.com    # type: url # max: medium
- in:  hotel-development.marriott.com    # type: url # max: medium
- in:  vacation.marriott.com    # type: url # max: low
- in:  moments.marriott.com    # type: url # max: low
- in:  www.giving.marriott.com    # type: url # max: low
- in:  www.members.marriott.com    # type: url # max: low
- in:  splunk-phantom-nlb.marriott.com    # type: url # max: low
- in:  455004730    # type: ios_app # max: critical
- in:  giftcards.marriott.com    # type: url # max: low # not eligible for bounty
- in:  clean.marriott.com    # type: url # max: medium
- in:  editionhotels.com    # type: url # max: critical
- in:  editionhotels.com    # type: url # max: critical
- in:  hotel-deals.marriott.com/*    # type: url # max: critical
- in:  hotel-deals.marriott.com/*    # type: url # max: critical
- in:  hotel-deals.marriott.com/*    # type: url # max: critical
- in:  homes-and-villas.marriott.com/*    # type: url # max: critical
- in:  homes-and-villas.marriott.com/*    # type: url # max: critical
- in:  modules.marriott.com/*    # type: url # max: critical
- in:  modules.marriott.com/*    # type: url # max: critical
- in:  modules.marriott.com/*    # type: url # max: critical
- in:  careers.marriott.com/*    # type: url # max: critical
- in:  careers.marriott.com/*    # type: url # max: critical
- in:  https://gatewaydsapprd.marriott.com/v2/    # type: url # max: critical
- in:  https://gatewaydsapprd.marriott.com/v2/    # type: url # max: critical
- in:  activities.marriott.com/*    # type: url # max: critical
- in:  activities.marriott.com/*    # type: url # max: critical
- in:  activities.marriott.com/*    # type: url # max: critical
- in:  activities.marriott.com/*    # type: url # max: critical
- in:  activities.marriott.com/*    # type: url # max: critical
- in:  activities.marriott.com/*    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- in:  www.marriott.com    # type: url # max: critical
- out:  vacations.marriott.com    # type: url # max: none
- out:  towneplacesuites.marriott.com    # type: url # max: none
- out:  www.travelagents.marriott.com    # type: url # max: none
- out:  *moxymix*.marriott.com    # type: url # max: none
- out:  mi.bookmarriott.com    # type: url # max: none
- out:  *.ritzcarltonyachtcollection.com    # type: url # max: none
- out:  *.phunware.com    # type: url # max: none
- out:  marriottlearnourbrands.com    # type: url # max: none
- out:  hotelexcellence.marriott.com    # type: url # max: none
- out:  meetings-excellence.marriott.com    # type: url # max: none
- out:  springhillsuites.marriott.com    # type: url # max: none
- out:  marriott.tech    # type: url # max: none
- out:  www.msg-gateway.marriott.com    # type: url # max: none
- out:  apps.ritzcarlton.com    # type: url # max: none
- out:  element-hotels.marriott.com    # type: url # max: none
- out:  milux.marriott.com    # type: url # max: none
- out:  luxurybrands.marriott.com    # type: url # max: none
- out:  www.github.com    # type: url # max: none
- out:  *.ritzcarlton.com    # type: other # max: none
- out:  Phoenix Platform    # type: other # max: none
- out:  Not-Listed Assets    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $538,588
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
