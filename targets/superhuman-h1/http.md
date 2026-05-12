# Superhuman (formerly Grammarly)

> Platform: HackerOne — https://hackerone.com/superhuman
> Type: BBP
> Bounty: Low $250–$500 | Medium $500–$5,000 | High $1,000–$13,000 | Critical $3,000–$100,000
> Avg bounty: $500–$500
> Response efficiency: 100% | Avg first response: N/A | Total paid: $981,606
> Last scope update: 2025-11-27

## Scope

- in:  *.grammarly.io    # type: wildcard # max: critical
- in:  *.grammarlyaws.com    # type: wildcard # max: critical
- in:  *.grammarly.com    # type: wildcard # max: critical
- in:  *.superhuman.com    # type: wildcard # max: critical
- in:  *.coda.io    # type: wildcard # max: critical
- in:  app.grammarly.com    # type: url # max: critical
- in:  superhuman.com    # type: url # max: critical
- in:  gateway.superhuman.com    # type: url # max: critical
- in:  id.superhuman.com    # type: url # max: critical
- in:  settings.superhuman.com    # type: url # max: critical
- in:  codacontent.io    # type: url # max: critical
- in:  codahosted.io    # type: url # max: critical
- in:  coda.grammarly.com    # type: url # max: critical
- in:  coda.io    # type: url # max: critical
- in:  Grammarly Browser Extensions    # type: other # max: critical
- in:  Capture the Flag    # type: other # max: critical
- in:  Superhuman Go    # type: other # max: critical
- in:  Coda Chrome Extension    # type: other # max: high
- in:  com.grammarly.android.keyboard    # type: android_app # max: critical
- in:  io.coda.codaapp    # type: android_app # max: critical
- in:  Grammarly Desktop for Windows    # type: downloadable_executables # max: critical
- in:  Grammarly Desktop for macOS    # type: downloadable_executables # max: critical
- in:  com.grammarly.keyboard    # type: ios_app # max: critical
- in:  io.coda    # type: ios_app # max: critical
- in:  accounts.superhuman.com    # type: url # max: critical
- in:  https://coda.io/*    # type: wildcard # max: critical
- in:  https://*.coda.io/*    # type: wildcard # max: medium
- in:  https://airflow-prod.coda.io/*    # type: wildcard # max: medium
- in:  https://airflow-prod.ops.coda.io/*    # type: wildcard # max: medium
- in:  https://data.coda.io/*    # type: wildcard # max: medium
- in:  https://head.coda.io/*    # type: wildcard # max: medium
- in:  https://infra.coda.io/*    # type: wildcard # max: medium
- in:  https://shiny.ops.coda.io/*    # type: wildcard # max: medium
- in:  https://staging.coda.io/*    # type: wildcard # max: medium
- in:  https://user-profile-prod.coda.io/*    # type: wildcard # max: medium
- in:  https://user-profile-test.coda.io/*    # type: wildcard # max: low
- in:  https://coda.io/signup/email    # type: url # max: critical
- in:  dox.grammarly.com    # type: url # max: critical
- in:  auth.grammarly.com    # type: url # max: critical
- in:  institution.grammarly.com    # type: url # max: critical
- in:  capi.grammarly.com    # type: url # max: critical
- in:  grammarly.ai    # type: url # max: low
- in:  dapi.grammarly.com    # type: url # max: critical
- in:  irbis.grammarly.com    # type: url # max: critical
- in:  gnar.grammarly.com    # type: url # max: critical
- in:  data.grammarly.com    # type: url # max: critical
- in:  datareport.grammarly.com    # type: url # max: critical
- in:  subscription.grammarly.com    # type: url # max: critical
- in:  g-mail.grammarly.com    # type: url # max: critical
- in:  goldengate.grammarly.com    # type: url # max: critical
- in:  tokens.grammarly.com    # type: url # max: critical
- in:  developer.grammarly.com    # type: url # max: critical
- in:  Grammarly for Microsoft Word    # type: downloadable_executables # max: critical
- in:  AppActions    # type: other # max: critical
- in:  Grammarly Business Features    # type: other # max: critical
- in:  Grammarly Auth Services    # type: other # max: critical
- in:  Grammarly AI Assistant    # type: other # max: critical
- in:   MS Office Add-In    # type: other # max: critical
- in:  Tier 1 Assets    # type: other # max: critical
- in:  auth.grammarly.com    # type: url # max: critical
- in:  app.grammarly.com    # type: url # max: critical
- in:  capi.grammarly.com    # type: url # max: critical
- in:  auth.grammarly.com    # type: url # max: critical
- in:  Grammarly Assistant    # type: other # max: critical
- in:  App Actions    # type: other # max: critical
- in:  Log4j RCE    # type: other # max: critical
- in:  food.grammarly.io    # type: url # max: low
- in:  admin-panel.grammarly.com    # type: url # max: critical
- in:  www.grammarly.com    # type: url # max: critical
- in:  *.grammarly.net    # type: wildcard # max: critical
- in:  account.grammarly.com    # type: url # max: critical
- in:  Standard Scope    # type: other # max: critical
- in:  Focus Scope    # type: other # max: critical
- in:  Tier 1    # type: other # max: critical
- in:  proofit.com    # type: url # max: critical
- in:  *.proofit.com    # type: wildcard # max: critical
- in:  felog.grammarly.com    # type: url # max: critical
- in:  atool.proofit.grammarlyaws.com    # type: url # max: critical
- in:  answers.grammarly.com    # type: url # max: critical
- in:  blog.grammarly.com    # type: url # max: critical
- in:  http://www.grammarly.com/edu    # type: url # max: critical
- in:  http://www.grammarly.com/business    # type: url # max: critical
- in:  Grammarly for Chrome    # type: other # max: critical
- in:  Grammarly for Safari    # type: other # max: critical
- in:  Grammarly for Microsoft Edge    # type: other # max: critical
- out:  status.coda.io    # type: url # max: none
- out:  Third party external services    # type: other # max: none
- out:  Superhuman Mail    # type: other # max: none
- out:  Grammarly Editor for MacOS    # type: downloadable_executables # max: none
- out:  r.superhuman.com    # type: other # max: none
- out:  Grammarly Editor for Windows    # type: downloadable_executables # max: none
- out:  *.qagr.io    # type: wildcard # max: none
- out:  *.ppgr.io    # type: wildcard # max: none
- out:  Grammarly for Developers Text Editor SDK    # type: repo # max: none
- out:  *.stgr.io    # type: wildcard # max: none
- out:  *.cpgr.io    # type: wildcard # max: none
- out:  anagram.grammarly.io    # type: url # max: none
- out:  tech.grammarly.com    # type: url # max: none
- out:  Tier 2    # type: other # max: none
- out:  Password and email policy    # type: other # max: none
- out:  support.grammarly.com    # type: url # max: none
- out:  status.grammarly.com    # type: url # max: none
- out:  calendar.grammarly.com    # type: url # max: none
- out:  send.grammarly.com    # type: url # max: none
- out:  email.grammarly.com    # type: url # max: none
- out:  campaign.grammarly.com    # type: url # max: none
- out:  beamlink.grammarly.com    # type: url # max: none
- out:  Mobile Keyboards    # type: other # max: none
- out:  All Other Assets    # type: other # max: none
- out:  Desktop Editor    # type: other # max: none
- out:  Other Native apps and clients    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $981,606
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
