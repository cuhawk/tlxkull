# EXNESS

> Platform: HackerOne — https://hackerone.com/exness
> Type: BBP
> Bounty: Low $1,000 | Medium $3,000 | High $7,500 | Critical $15,000
> Avg bounty: $200–$250
> Response efficiency: 95% | Avg first response: N/A | Total paid: $408,096
> Last scope update: 2025-10-10

## Scope

- in:  my.exness.com    # type: url # max: critical
- in:  pay.ibex.exchange    # type: url # max: critical
- in:  https://my.exness.com/webtrading/    # type: url # max: critical
- in:  exnessaffiliates.com    # type: url # max: critical
- in:  pwapi.ex2b.com    # type: url # max: critical
- in:  api.excalls.mobi    # type: url # max: critical
- in:  https://my.exness.com/pa/pim/manager    # type: url # max: high
- in:  social-trading.exness.com    # type: url # max: medium
- in:  https://my.exness.com/pa/socialtrading    # type: url # max: medium
- in:  exness.com    # type: url # max: medium
- in:  com.exness.android.pa    # type: android_app # max: critical
- in:  com.exness.investments    # type: android_app # max: medium
- in:  Exness Trade: Online Trading    # type: ios_app # max: critical
- in:  Exness Investor    # type: ios_app # max: critical
- in:  Exness Social Trading    # type: ios_app # max: medium
- in:  Any subdomain infrastructure issue    # type: other # max: critical # not eligible for bounty
- in:  Any subdomain application issue    # type: other # max: critical # not eligible for bounty
- in:  External service data leakage     # type: other # max: critical # not eligible for bounty
- in:  com.exness.investor    # type: android_app # max: critical
- in:  com.exness.android.pa    # type: other_apk # max: critical
- in:  1579331769    # type: ios_app # max: critical
- in:  1359763701    # type: ios_app # max: critical
- in:  1392465628    # type: ios_app # max: medium
- in:  Personal Area for Web Trading    # type: other # max: critical
- in:  Public Area for Web Trading    # type: other # max: medium
- in:  Portfolio Management    # type: other # max: high
- in:  Social Trading    # type: other # max: medium
- in:  Partnership    # type: other # max: critical
- in:  Web Terminal    # type: other # max: critical
- in:  Logical trading issues    # type: other # max: critical
- in:  1474969251    # type: ios_app # max: medium
- in:  com.exness.trader.watch    # type: android_app # max: medium
- in:  *.exness.tld    # type: wildcard # max: critical # not eligible for bounty
- in:  www.exnessaffiliates.com    # type: url # max: critical
- in:  api.exness.com    # type: url # max: critical
- in:  api.excalls.mobi    # type: url # max: critical
- in:  www.exness.com    # type: url # max: critical
- in:  www.exness.ru    # type: url # max: critical
- in:  www.exness.cn    # type: url # max: critical
- in:  API.EXNESS.COM    # type: url # max: critical
- in:  sf-magic.exness.com    # type: url # max: high
- in:  chat-mapper.exness.com    # type: url # max: high
- in:  beatbot.exness.com    # type: url # max: high
- in:  files.exness.co    # type: url # max: critical
- in:  quotes.exness.com    # type: url # max: medium
- in:  amazon-dsn-processor.exness.com    # type: url # max: low
- in:  www.exness-careers.com    # type: url # max: low
- in:  sip.exness.com    # type: url # max: critical
- in:  203.121.22.32/28    # type: cidr # max: low
- in:  223.27.131.168/29    # type: cidr # max: low
- in:  221.133.43.0/30    # type: cidr # max: low
- in:  185.170.234.32/28    # type: cidr # max: low
- in:  210.19.168.196/30    # type: cidr # max: low
- in:  91.184.201.0/29    # type: cidr # max: medium
- in:  173.0.152.64/28    # type: cidr # max: high
- in:  193.194.116.0/22    # type: cidr # max: critical
- in:  static.exness.com    # type: url # max: low
- in:  exness.bar    # type: url # max: medium
- in:  ticks.exness.com    # type: url # max: medium
- in:  vpn.exness.com    # type: url # max: medium
- in:  hubspot-forms.exness.com    # type: url # max: medium
- in:  bonus-stats.exness.com    # type: url # max: medium
- in:  mypartner.exness.com    # type: url # max: critical
- in:  msg.exness.com    # type: url # max: critical
- in:  admin.exness.com    # type: url # max: critical
- in:  partner.exness.com    # type: url # max: critical
- in:  ng2.exness.com    # type: url # max: none
- in:  ng.exness.com    # type: url # max: none
- in:  http://185.170.234.32/28    # type: url # max: low
- out:  my.exness.com    # type: url # max: none
- out:  www.exness.uk    # type: url # max: none
- out:  www.exness.web.id    # type: url # max: none
- out:  mypartner.exness.co.id    # type: url # max: none
- out:  hubspot-forms.exness.asia    # type: url # max: none
- out:  www.exness.co.id    # type: url # max: none
- out:  www.exness.asia    # type: url # max: none
- out:  www.exness.eu    # type: url # max: none
- out:  hubspot-forms.exness.co.id    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $408,096

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
