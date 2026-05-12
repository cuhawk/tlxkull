# Robinhood Markets Bounty

> Platform: HackerOne — https://hackerone.com/robinhood
> Type: BBP
> Bounty: Low $500 | Medium $3,000–$5,000 | High $3,000–$10,000 | Critical $6,000–$25,000
> Avg bounty: $966–$1,431
> Response efficiency: 89% | Avg first response: N/A | Total paid: $320,000
> Last scope update: 2026-02-11

## Scope

- in:  https://*.saytechnologies.com    # type: wildcard # max: medium
- in:  api.robinhood.com    # type: url # max: critical
- in:  cashier.robinhood.com    # type: url # max: critical
- in:  minerva.robinhood.com    # type: url # max: critical
- in:  nummus.robinhood.com    # type: url # max: critical
- in:  identi.robinhood.com    # type: url # max: critical
- in:  www.bitstamp.net    # type: url # max: critical
- in:  *.rhinternal.net    # type: other # max: critical
- in:  *.robinhood.com    # type: other # max: critical
- in:  *.robinhood.net    # type: other # max: critical
- in:  Tier 3    # type: other # max: critical
- in:  *.say.rocks    # type: other # max: medium
- in:  *.saytechnologies.com    # type: other # max: medium
- in:  com.robinhood.android    # type: android_app # max: critical
- in:  com.robinhood.gateway    # type: android_app # max: critical
- in:  com.robinhood.money    # type: android_app # max: critical
- in:  net.bitstamp.app    # type: android_app # max: critical
- in:  com.robinhood.global Android    # type: android_app # max: critical
- in:  1634080733    # type: ios_app # max: critical
- in:  6462308655    # type: ios_app # max: critical
- in:  938003185    # type: ios_app # max: critical
- in:  Id1406825640    # type: ios_app # max: critical
- in:  fusion.tradepmr.com    # type: url # max: critical # not eligible for bounty
- in:  www.tradepmr.com    # type: url # max: critical # not eligible for bounty
- in:  insight2.tradepmr.com    # type: url # max: critical # not eligible for bounty
- in:  Tier 4    # type: other # max: critical
- in:  https://*.say.rocks    # type: wildcard # max: critical
- in:  *.x1creditcard.com    # type: wildcard # max: critical
- in:  *.x1.co    # type: wildcard # max: critical
- in:  oak.robinhood.net    # type: url # max: critical
- in:  *.rhapollo.net    # type: other # max: critical
- out:  auth-sandbox.tradepmr.com    # type: url # max: none
- out:  7671800.bitstamp.net    # type: url # max: none
- out:  7671800.team.bitstamp.net    # type: url # max: none
- out:  _16928ca3f53f40a48a751be40fa24e4c.bitstamp.net    # type: url # max: none
- out:  _domainconnect.bitstamp.net    # type: url # max: none
- out:  autodiscover.bitstamp.net    # type: url # max: none
- out:  bounces.bitstamp.net    # type: url # max: none
- out:  em1198.bitstamp.net    # type: url # max: none
- out:  em4296.team.bitstamp.net    # type: url # max: none
- out:  em9457.team.bitstamp.net    # type: url # max: none
- out:  enterpriseenrollment.bitstamp.net    # type: url # max: none
- out:  enterpriseregistration.bitstamp.net    # type: url # max: none
- out:  status.bitstamp.net    # type: url # max: none
- out:  url6884.team.bitstamp.net    # type: url # max: none
- out:  https://www.saytechnologies.com/contact/sales    # type: url # max: none
- out:  shop.robinhood.com    # type: url # max: none
- out:  fleet.infra.robinhood.net    # type: url # max: none
- out:  content.research.robinhood.com    # type: url # max: none
- out:  events.robinhood.com    # type: url # max: none
- out:  affiliates.robinhood.com    # type: url # max: none
- out:  vgs-api.robinhood.com    # type: url # max: none
- out:  share.robinhood.com    # type: url # max: none
- out:  esg.robinhood.com    # type: url # max: none
- out:  startinvesting.robinhood.com    # type: url # max: none
- out:  go.robinhood.com    # type: url # max: none
- out:  underthehoodpod.robinhood.com    # type: url # max: none
- out:  press.robinhood.com    # type: url # max: none
- out:  roadshow.robinhood.com    # type: url # max: none
- out:  weareallinvestors.robinhood.com    # type: url # max: none
- out:  careers.robinhood.com    # type: url # max: none
- out:  earlytalent.robinhood.com    # type: url # max: none
- out:  api-sandbox.tradepmr.com    # type: url # max: none
- out:  fusion-demo.tradepmr.com    # type: url # max: none
- out:  fusion-demo.uat.tradepmr.com    # type: url # max: none
- out:  fusion-demo.uat2.tradepmr.com    # type: url # max: none
- out:  fusion.uat.tradepmr.com    # type: url # max: none
- out:  fusion.uat2.tradepmr.com    # type: url # max: none
- out:  fusion.uat3.tradepmr.com    # type: url # max: none
- out:  auth-validation.tradepmr.com    # type: url # max: none
- out:  api-validation.tradepmr.com    # type: url # max: none
- out:  auth.tradepmr.com    # type: url # max: none
- out:  api.tradepmr.com    # type: url # max: none
- out:  sandbox.bitstamp.net    # type: url # max: none
- out:  Tier 2    # type: other # max: none
- out:  Tier 1    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $320,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
