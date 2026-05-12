# FanDuel

> Platform: HackerOne — https://hackerone.com/fanduel
> Type: BBP
> Bounty: Low $250 | Medium $600 | High $1,500 | Critical $3,500
> Avg bounty: $500–$500
> Response efficiency: 100% | Avg first response: N/A | Total paid: $211,675
> Last scope update: 2024-09-09

## Scope

- in:  *.fanduel.com    # type: wildcard # max: critical
- in:  *.mgmt.fndlsb.net    # type: wildcard # max: critical
- in:  *.prd.fndlsb.net    # type: wildcard # max: critical
- in:  *inf.fndlsb.net    # type: wildcard # max: critical
- in:  *.tvg.com    # type: wildcard # max: critical
- in:  login-4ngbets.us.betfair.com    # type: url # max: critical
- in:  www.4njbets.com    # type: url # max: critical
- in:  4njbets.com    # type: url # max: critical
- in:  4njbets.us.betfair.com    # type: url # max: critical
- in:  login-4njbets.us.betfair.com    # type: url # max: critical
- in:  com.fanduel.android.self    # type: android_app # max: critical
- in:  com.fanduel.sportsbook    # type: android_app # max: critical
- in:  com.fanduel.casino    # type: android_app # max: critical
- in:  com.fanduel.racing    # type: android_app # max: critical
- in:  com.fanduel.flywheelnativecontainer.picks    # type: android_app # max: critical
- in:  599664106    # type: ios_app # max: critical
- in:  1506229470    # type: ios_app # max: critical
- in:  1485539253    # type: ios_app # max: critical
- in:  6740879082    # type: ios_app # max: critical
- in:  1413721906    # type: ios_app # max: critical
- in:  https://*.tvg.com    # type: wildcard # max: critical
- in:  4njbets.tvg.com    # type: url # max: critical
- in:  login-pabets.tvg.com    # type: url # max: critical
- in:  tvg.com    # type: url # max: critical
- in:  www.tvg.com    # type: url # max: critical
- in:  ia.tvg.com    # type: url # max: critical
- in:  login.pabets.tvg.com    # type: url # max: critical
- in:  login-ia.tvg.com    # type: url # max: critical
- in:  login.tvg.com    # type: url # max: critical
- in:  m.4njbets.tvg.com    # type: url # max: critical
- in:  mobile-prod.tvg.com    # type: url # max: critical
- in:  pabets.tvg.com    # type: url # max: critical
- in:  promos.tvg.com    # type: url # max: critical
- in:  service.tvg.com    # type: url # max: critical
- in:  us.tvg.com    # type: url # max: critical
- in:  fanduel.com    # type: url # max: critical
- in:  *racing.fanduel.com    # type: wildcard # max: critical
- in:  sportsbook.fanduel.com    # type: url # max: critical
- in:  service.racing.fanduel.com    # type: url # max: critical
- in:  4njbets.tvgnetwork.com    # type: url # max: critical
- in:  b2b.tvgnetwork.com    # type: url # max: critical
- in:  com.fanduel.android.live    # type: url # max: critical
- in:  *.numberfire.com    # type: wildcard # max: critical
- in:  fanduel.design    # type: url # max: medium
- out:  *.fndl.dev    # type: wildcard # max: none
- out:  affiliates.fanduel.com    # type: url # max: none
- out:  equibase-store.fanduel.com    # type: url # max: none
- out:  *.pdx.tvg.com    # type: wildcard # max: none
- out:  *.canada.fanduel.com    # type: wildcard # max: none
- out:  *.east.fdbox.net    # type: wildcard # max: none
- out:  *.prod.fdbox.net    # type: wildcard # max: none
- out:  fdbox.net    # type: url # max: none
- out:  partners.fanduel.com    # type: url # max: none
- out:  newsroom.fanduel.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $211,675

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
