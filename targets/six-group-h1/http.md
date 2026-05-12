# SIX Group

> Platform: HackerOne — https://hackerone.com/six-group
> Type: BBP
> Bounty: Low $500 | Medium $1,500 | High $3,000 | Critical $7,500
> Avg bounty: $750–$999
> Response efficiency: 87% | Avg first response: N/A | Total paid: $84,488
> Last scope update: 2025-08-20

## Scope

- in:  www.six-group.com    # type: url # max: critical
- in:  www.bolsasymercados.es    # type: url # max: critical
- in:  https://www.sdx.com/    # type: url # max: critical
- in:  https://secure-test.six-swiss-exchange.com/    # type: url # max: critical
- in:  https://web3.sdx.com    # type: url # max: high
- in:  https://play.google.com/store/apps/details?id=com.sixgroup.debixplus    # type: android_app # max: critical
- in:  https://play.google.com/store/apps/details?id=com.sixgroup.id&hl=en_US&pli=1    # type: android_app # max: critical
- in:  https://play.google.com/store/apps/details?id=es.grupobme.bmeconecta    # type: android_app # max: critical
- in:  https://play.google.com/store/search?q=Schweizer+Finanzmuseum&c=apps    # type: android_app # max: critical
- in:  153.46.96.0/20    # type: cidr # max: critical
- in:  193.110.154.0/24    # type: cidr # max: critical
- in:  193.109.229.0/24    # type: cidr # max: critical
- in:  153.46.240.0/20    # type: cidr # max: critical
- in:  153.46.108.0/22    # type: cidr # max: critical
- in:  62.192.20.16/29    # type: cidr # max: critical
- in:  153.46.111.0/24    # type: cidr # max: critical
- in:  153.46.104.0/22    # type: cidr # max: critical
- in:  146.109.8.0/22    # type: cidr # max: critical
- in:  194.209.121.0/24    # type: cidr # max: critical
- in:  153.46.30.0/23    # type: cidr # max: critical
- in:  153.46.32.0/23    # type: cidr # max: critical
- in:  153.46.34.0/23    # type: cidr # max: critical
- in:  174.44.253.152/29    # type: cidr # max: critical
- in:  153.46.0.0/16    # type: cidr # max: critical
- in:  146.109.2.0/24    # type: cidr # max: critical
- in:  146.109.3.0/24    # type: cidr # max: critical
- in:  146.109.4.0/24    # type: cidr # max: critical
- in:  185.210.32.0/22    # type: cidr # max: critical
- in:  153.46.162.0/23    # type: cidr # max: critical
- in:  212.95.227.64/26    # type: cidr # max: critical
- in:  146.109.1.0/24    # type: cidr # max: critical
- in:  146.109.8.0/21    # type: cidr # max: critical
- in:  153.46.176.0/22    # type: cidr # max: critical
- in:  153.46.48.0/22    # type: cidr # max: critical
- in:  146.109.64.0/24    # type: cidr # max: critical
- in:  146.109.65.0/24    # type: cidr # max: critical
- in:  146.109.66.0/24    # type: cidr # max: critical
- in:  146.109.68.0/24    # type: cidr # max: critical
- in:  146.109.67.0/24    # type: cidr # max: critical
- in:  146.109.140.0/24    # type: cidr # max: critical
- in:  146.109.141.0/24    # type: cidr # max: critical
- in:  146.109.142.0/24    # type: cidr # max: critical
- in:  146.109.143.0/24    # type: cidr # max: critical
- in:  146.109.148.0/24    # type: cidr # max: critical
- in:  146.109.149.0/24    # type: cidr # max: critical
- in:  146.109.150.0/24    # type: cidr # max: critical
- in:  146.109.151.0/24    # type: cidr # max: critical
- in:  146.109.161.0/24    # type: cidr # max: critical
- in:  193.5.66.0/23    # type: cidr # max: critical
- in:  193.8.251.0/24    # type: cidr # max: critical
- in:  194.35.79.0/24    # type: cidr # max: critical
- in:  https://apps.apple.com/ch/app/debix/id1581440132?l=en-GB    # type: ios_app # max: critical
- in:  https://apps.apple.com/mx/app/debix/id1581440132    # type: ios_app # max: critical
- in:  https://apps.apple.com/mx/app/schweizer-finanzmuseum/id1225222871    # type: ios_app # max: critical
- in:  https://apps.apple.com/mx/app/six-id/id1620496931    # type: ios_app # max: critical
- in:  https://apps.apple.com/us/app/bme-conecta/id6443938949    # type: ios_app # max: critical
- in:  *.sdx.com    # type: wildcard # max: none
- in:  *.bolsasymercados.es    # type: wildcard # max: critical
- in:  test.six-dochub.com    # type: url # max: critical
- out:  *.sixidmobile.com    # type: wildcard # max: none
- out:  saferpay.com    # type: url # max: none
- out:  193.109.229.71    # type: url # max: none
- out:  153.46.254.150    # type: ip_address # max: none
- out:  213.41.106.0/24    # type: cidr # max: none
- out:  194.98.112.0/24    # type: cidr # max: none
- out:  http://*.six-group.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $84,488
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
