# Ubiquiti Inc.

> Platform: HackerOne — https://hackerone.com/ui
> Type: BBP
> Bounty: Low $150 | Medium $995 | High $8,959 | Critical $30,000
> Avg bounty: $150–$200
> Response efficiency: 99% | Avg first response: N/A | Total paid: $1,740,000
> Last scope update: 2025-10-22

## Scope

- in:  *.ubnt.com    # type: wildcard # max: critical
- in:  *.ui.com    # type: wildcard # max: critical
- in:  *.uisp.com    # type: wildcard # max: critical
- in:  store.ui.com    # type: url # max: critical
- in:  community.ui.com    # type: url # max: critical
- in:  account.ui.com    # type: url # max: critical
- in:  fw-update.ubnt.com    # type: url # max: critical
- in:  rma.ui.com    # type: url # max: critical
- in:  design.ui.com    # type: url # max: critical
- in:  uisp.com    # type: url # max: critical
- in:  unifi.ui.com    # type: url # max: critical
- in:  careers.ui.com    # type: url # max: critical
- in:  ispdesign.ui.com    # type: url # max: critical
- in:  UniFi Cloud    # type: other # max: critical
- in:  UID    # type: other # max: critical
- in:  airMAX    # type: firmware # max: critical
- in:  UniFi    # type: firmware # max: critical
- in:  EdgeMAX    # type: firmware # max: critical
- in:  airFiber    # type: firmware # max: critical
- in:  UFiber    # type: firmware # max: critical
- in:  AmpliFi    # type: firmware # max: critical
- in:  UniFi Talk    # type: firmware # max: critical
- in:  UniFi Protect    # type: firmware # max: critical
- in:  UniFi Switches    # type: firmware # max: critical
- in:  UniFi Wireless Access Points    # type: firmware # max: critical
- in:  UniFi Gateways (UDM, UXG, USG)    # type: firmware # max: critical
- in:  Cloudkey    # type: firmware # max: critical
- in:  UniFi LED    # type: firmware # max: critical
- in:  UniFi Access    # type: firmware # max: critical
- in:  UniFi Connect    # type: firmware # max: critical
- in:  com.ubnt.easyunifi    # type: android_app # max: critical
- in:  com.ubnt.umobile    # type: android_app # max: critical
- in:  com.ubnt.discovery.app    # type: android_app # max: critical
- in:  UniFi Network Application    # type: downloadable_executables # max: critical
- in:  UCRM    # type: downloadable_executables # max: critical
- in:  UNMS    # type: downloadable_executables # max: critical
- in:  UISP    # type: downloadable_executables # max: critical
- in:   UniFi OS Server    # type: downloadable_executables # max: critical
- in:  https://*.ui.com/distributors/    # type: wildcard # max: none # not eligible for bounty
- in:  https://*.ui.com/training/partners/    # type: wildcard # max: none # not eligible for bounty
- in:  ir.ui.com    # type: url # max: critical # not eligible for bounty
- in:  help.ui.com    # type: url # max: critical # not eligible for bounty
- in:  blog.ui.com    # type: url # max: critical # not eligible for bounty
- in:  training.ui.com    # type: url # max: medium # not eligible for bounty
- in:  dev-training.ui.com    # type: url # max: medium # not eligible for bounty
- in:  wiki.ui.com    # type: url # max: none # not eligible for bounty
- in:  https://ui.com/distributors/    # type: url # max: none # not eligible for bounty
- in:  https://ui.com/training/partners/    # type: url # max: none # not eligible for bounty
- in:  help.uisp.com    # type: url # max: none # not eligible for bounty
- in:  com.ubnt.ucrm    # type: android_app # max: critical # not eligible for bounty
- in:  ca.store.ui.com    # type: url # max: critical
- in:  me.store.ui.com    # type: url # max: critical
- in:  com.ubnt.plc    # type: android_app # max: critical # not eligible for bounty
- in:  EtherMagic    # type: firmware # max: critical # not eligible for bounty
- in:  com.ubnt.plc    # type: url # max: critical # not eligible for bounty
- in:  translate.ubnt.com    # type: url # max: critical # not eligible for bounty
- out:  *.go.ubnt.com    # type: wildcard # max: none
- out:  forum-es.ui.com    # type: url # max: none
- out:  forum-pt.ui.com    # type: url # max: none
- out:  security.community.ui.com    # type: url # max: none
- out:  UniFi Video Cloud    # type: other # max: none
- out:  UniFi Video    # type: firmware # max: none
- out:  mFi    # type: firmware # max: none
- out:  UniFi Talk Conference Speaker - UT-Conference     # type: firmware # max: none
- out:  UniFi Voip    # type: firmware # max: none
- out:  com.ubnt.unifivideo    # type: android_app # max: none
- out:  com.ubnt.unifi.edu    # type: android_app # max: none
- out:  com.ubnt.mpower    # type: android_app # max: none
- out:  AirControl    # type: downloadable_executables # max: none
- out:  UniFi Video Server    # type: downloadable_executables # max: none
- out:  com.ubnt.sunmax.install    # type: android_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $1,740,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
