# Grab

> Platform: HackerOne — https://hackerone.com/grab
> Type: BBP
> Bounty: Low $500–$750 | Medium $2,000–$3,000 | High $5,000–$7,500 | Critical $10,000–$15,000
> Avg bounty: $200–$500
> Response efficiency: 99% | Avg first response: N/A | Total paid: $996,779
> Last scope update: 2025-06-24

## Scope

- in:  *.myteksi.com    # type: wildcard # max: critical
- in:  *.myteksi.net    # type: wildcard # max: critical
- in:  *.grab.com    # type: wildcard # max: critical
- in:  *.grabpay.com    # type: wildcard # max: critical
- in:  *.grab-sure.com    # type: wildcard # max: critical
- in:  *.ovofinansial.com    # type: wildcard # max: critical
- in:  *.ovo.id    # type: wildcard # max: high
- in:  *.grabtaxi.com    # type: wildcard # max: medium
- in:  *.grab.co    # type: wildcard # max: medium
- in:  p.grabtaxi.com    # type: url # max: critical
- in:  gamma.grab.co    # type: url # max: critical
- in:  manage.grab.co    # type: url # max: critical
- in:  jira.grab.com    # type: url # max: critical
- in:  wiki.grab.com    # type: url # max: critical
- in:  api.grabpay.com    # type: url # max: critical
- in:  xtramile.grabpay.com    # type: url # max: critical
- in:  gifts.grab.com    # type: url # max: critical
- in:  hungrygowhere.com    # type: url # max: high
- in:  grab.careers    # type: url # max: medium
- in:  kartaview.org    # type: url # max: medium
- in:  C100447517    # type: other # max: critical
- in:  C103149579    # type: other # max: critical
- in:  com.grabtaxi.passenger    # type: android_app # max: critical
- in:  com.grabtaxi.driver2    # type: android_app # max: critical
- in:  com.grab.merchant    # type: android_app # max: critical
- in:  ovo.id    # type: android_app # max: critical
- in:  com.moveit.app.customer    # type: android_app # max: critical
- in:  com.grabpay.merchant    # type: android_app # max: medium
- in:  647268330    # type: ios_app # max: critical
- in:  1257641454    # type: ios_app # max: critical
- in:  1142114207    # type: ios_app # max: critical
- in:  1481198245    # type: ios_app # max: critical
- in:  1343620481    # type: ios_app # max: medium
- in:  com.moveit.app.customer    # type: url # max: critical
- in:  ovofinansial.com    # type: url # max: critical
- in:  *.taralite.com    # type: wildcard # max: high
- in:  https://paysuite.grab.com/hub    # type: url # max: critical
- in:  *.grab-sure.com    # type: url # max: critical
- in:  hungrygowhere.com    # type: url # max: critical
- in:  *.openstreetcam.org    # type: wildcard # max: medium
- in:  mos.grabpay.com    # type: url # max: medium
- in:  drive.grab.co    # type: url # max: critical
- in:  *.grabtaxi.io    # type: wildcard # max: low
- in:  *.stg-myteksi.com    # type: wildcard # max: low
- in:  hub.grab.com    # type: url # max: critical
- in:  drivegrab.com    # type: url # max: critical
- in:  graballstars.com    # type: url # max: critical
- in:  1360970802    # type: ios_app # max: medium
- in:  com.grab.food.dax    # type: android_app # max: medium
- in:  1353289014    # type: ios_app # max: none # not eligible for bounty
- in:  com.grab.food.pax    # type: android_app # max: none # not eligible for bounty
- in:  1354806922    # type: ios_app # max: critical
- in:  com.grabtaxi.cycle.adr    # type: android_app # max: critical
- in:  1305547714    # type: ios_app # max: medium
- in:  1205883254    # type: ios_app # max: medium
- in:  com.ionicframework.grabshuttle856802    # type: android_app # max: medium
- in:  com.grab.shuttleplus    # type: android_app # max: medium
- in:  com.grab.food.dax    # type: url # max: critical
- in:  com.grab.shuttleplus    # type: url # max: critical
- in:  com.grabtaxi.cycle.adr    # type: url # max: critical
- in:  parcel.grab.com    # type: url # max: high
- out:  *.qms.grab.com    # type: wildcard # max: none
- out:  *.uat.qms.grab.com    # type: wildcard # max: none
- out:  kios.grab.com    # type: url # max: none
- out:  parcel.grab.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $996,779
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
