# Deriv.com

> Platform: HackerOne — https://hackerone.com/deriv
> Type: BBP
> Bounty: Low $100 | Medium $500 | High $2,500 | Critical $5,000
> Avg bounty: $100–$100
> Response efficiency: 100% | Avg first response: N/A | Total paid: $49,635
> Last scope update: 2025-10-16

## Scope

- in:  *.deriv.com    # type: wildcard # max: critical
- in:  *.deriv.cloud    # type: wildcard # max: critical
- in:  *.derivws.com    # type: wildcard # max: critical
- in:  app.deriv.com    # type: url # max: critical
- in:  smarttrader.deriv.com    # type: url # max: critical
- in:  cashier.deriv.com    # type: url # max: critical
- in:  oauth.deriv.com    # type: url # max: critical
- in:  api.deriv.com    # type: url # max: critical
- in:  derivws.com    # type: url # max: critical
- in:  secure-dfadmin.deriv.com    # type: url # max: critical
- in:  github.com/binary-com    # type: repo # max: medium
- in:  github.com/deriv-com    # type: other # max: critical
- in:  ct.deriv.com    # type: url # max: critical # not eligible for bounty
- in:  dx-demo.deriv.com    # type: url # max: critical # not eligible for bounty
- in:  dx.deriv.com    # type: url # max: critical # not eligible for bounty
- in:  academy.deriv.com    # type: url # max: none # not eligible for bounty
- in:  deriv.partners    # type: url # max: none # not eligible for bounty
- in:  partners.deriv.com    # type: url # max: none # not eligible for bounty
- in:  http://partners.deriv.com    # type: url # max: none # not eligible for bounty
- in:  *.binary.com    # type: wildcard # max: low
- in:  secure-dfadmin.binary.com    # type: url # max: critical
- in:  *.binaryws.com    # type: wildcard # max: critical
- in:  webtrader.binary.com    # type: url # max: high
- in:  crypto-cashier.binary.com    # type: url # max: critical
- in:  cashier.binary.com    # type: url # max: critical
- in:  charts.binary.com    # type: url # max: medium
- in:  tradingview.binary.com    # type: url # max: medium
- in:  binary.bot    # type: url # max: high
- out:  *.home.deriv.com    # type: wildcard # max: none
- out:  *.api-core.deriv.com    # type: wildcard # max: none
- out:  deriv.slack.com    # type: url # max: none
- out:  tradingview.deriv.com    # type: url # max: none
- out:  besquare.deriv.com    # type: url # max: none
- out:  trade.mql5.com    # type: url # max: none
- out:  community.deriv.com    # type: url # max: none
- out:  https://deriv.atlassian.net/servicedesk/customer/user/signup    # type: url # max: none
- out:  deriv.ae    # type: url # max: none
- out:  help.deriv.com    # type: url # max: none
- out:  Any 3rd party managed domain    # type: other # max: none
- out:  com.binary.ticktrade    # type: other_apk # max: none
- out:  http://community.deriv.com    # type: url # max: none
- out:  *.binary.*    # type: wildcard # max: none
- out:  http://admin.binary.com    # type: url # max: none
- out:  home.deriv.com    # type: url # max: none
- out:  http://admin.binary.com    # type: url # max: none
- out:  xml.binary.com    # type: url # max: none
- out:  record.binary.com    # type: url # max: none
- out:  media.binary.com    # type: url # max: none
- out:  login.binary.com    # type: url # max: none
- out:  js.binary.com    # type: url # max: none
- out:  admin.binary.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $49,635

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
