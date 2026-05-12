# NBA Public Bug Bounty

> Platform: HackerOne — https://hackerone.com/nba-public
> Type: BBP
> Bounty: Low N/A | Medium $500 | High $3,000 | Critical $6,000
> Avg bounty: $300–$400
> Response efficiency: 98% | Avg first response: N/A | Total paid: $39,750
> Last scope update: 2024-07-25

## Scope

- in:  www.nba.com    # type: url # max: critical
- in:  gleague.nba.com    # type: url # max: critical
- in:  bal.nba.com    # type: url # max: critical
- in:  content-api-nextgen-prod.nba.com    # type: url # max: critical
- in:  content-api-prod.nba.com    # type: url # max: critical
- in:  core-api.nba.com    # type: url # max: critical
- in:  id.nba.com    # type: url # max: critical
- in:  stats-trafficcop-prod.nba.com    # type: url # max: critical
- in:  cdn.nba.com    # type: url # max: critical
- in:  cms.nba.com    # type: url # max: critical
- in:  stats.nba.com    # type: url # max: critical
- in:  identity.nba.com    # type: url # max: critical
- in:  www.wnba.com    # type: url # max: critical
- in:  teamportal.nba.com    # type: url # max: critical
- in:  cweb-ott.nba.com    # type: url # max: critical
- in:  syndication.nba.com    # type: url # max: critical
- in:  stats.wnba.com    # type: url # max: critical
- in:  stats.gleague.nba.com    # type: url # max: critical
- in:  cdn-bal.nba.com    # type: url # max: critical
- in:  corp-dev.nba.com    # type: url # max: critical
- in:  manage.nba.com    # type: url # max: critical
- in:  manage-teams.nba.com    # type: url # max: critical
- in:  nbafedsvc.nba.com    # type: url # max: critical
- in:  vote.nba.com    # type: url # max: critical
- in:  mcd.nba.com    # type: url # max: critical
- in:  mcdalerts.nba.com    # type: url # max: critical
- in:  elm.nba.com    # type: url # max: critical
- in:  lockervision.nba.com    # type: url # max: critical
- in:  adb.nba.com    # type: url # max: critical
- in:  br.nba.com    # type: url # max: critical
- in:  cares.nba.com    # type: url # max: critical
- in:  cl.nba.com    # type: url # max: critical
- in:  gamenotes.nba.com    # type: url # max: critical
- in:  grae.nba.com    # type: url # max: critical
- in:  gleague-dev.nba.com    # type: url # max: critical
- in:  gleague-qa.nba.com    # type: url # max: critical
- in:  www-dev.wnba.com    # type: url # max: critical
- in:  www-dev.nba.com    # type: url # max: critical
- in:  www-qa.wnba.com    # type: url # max: critical
- in:  www-qa.nba.com    # type: url # max: critical
- in:  socialimpact.nba.com    # type: url # max: critical
- in:  www-uat.nba.com    # type: url # max: critical
- in:  www-ng.nba.com    # type: url # max: critical
- in:  vth.nba.com    # type: url # max: critical
- in:  teamdirectory.nba.com    # type: url # max: critical
- in:  bal-dev.nba.com    # type: url # max: critical
- in:  bal-qa.nba.com    # type: url # max: critical
- in:  bal-uat.nba.com    # type: url # max: critical
- in:  mcd-dev.nba.com    # type: url # max: critical
- in:  mcd-devint.nba.com    # type: url # max: critical
- in:  mcd-perf.nba.com    # type: url # max: critical
- in:  mcd-qa.nba.com    # type: url # max: critical
- in:  mcd-uat.nba.com    # type: url # max: critical
- in:  mcdalerts-dev.nba.com    # type: url # max: critical
- in:  mcdalerts-devint.nba.com    # type: url # max: critical
- in:  mcdalerts-perf.nba.com    # type: url # max: critical
- in:  mcdalerts-qa.nba.com    # type: url # max: critical
- in:  mcdalerts-uat.nba.com    # type: url # max: critical
- in:  content-api-dev.nba.com    # type: url # max: critical
- in:  content-api-nextgen-dev.nba.com    # type: url # max: critical
- in:  content-api-nextgen-qa.nba.com    # type: url # max: critical
- in:  content-api-nextgen-uat.nba.com    # type: url # max: critical
- in:  content-api-qa.nba.com    # type: url # max: critical
- in:  content-api-sandbox.nba.com    # type: url # max: critical
- in:  content-api-uat.nba.com    # type: url # max: critical
- in:  core-api-dev.nba.com    # type: url # max: critical
- in:  core-api-devint.nba.com    # type: url # max: critical
- in:  core-api-qa.nba.com    # type: url # max: critical
- in:  core-api-sandbox.nba.com    # type: url # max: critical
- in:  core-api-uat-uc.nba.com    # type: url # max: critical
- in:  core-api-uat.nba.com    # type: url # max: critical
- in:  core-api-uc.nba.com    # type: url # max: critical
- in:  cweb-ott-dev.nba.com    # type: url # max: critical
- in:  cweb-ott-devint.nba.com    # type: url # max: critical
- in:  cweb-ott-qa.nba.com    # type: url # max: critical
- in:  cweb-ott-uat-uc.nba.com    # type: url # max: critical
- in:  cweb-ott-uc.nba.com    # type: url # max: critical
- in:  identity-uat.nba.com    # type: url # max: critical
- in:  identity-qa.nba.com    # type: url # max: critical
- in:  identity-ng.nba.com    # type: url # max: critical
- in:  identity-dev.nba.com    # type: url # max: critical
- in:  manage-dev.nba.com    # type: url # max: critical
- in:  manage-teams-dev.nba.com    # type: url # max: critical
- in:  manage-teams-qa.nba.com    # type: url # max: critical
- in:  manage-teams-uat.nba.com    # type: url # max: critical
- in:  manage-uat.nba.com    # type: url # max: critical
- in:  nbafedsvc-dev.nba.com    # type: url # max: critical
- in:  nbafedsvc-qa.nba.com    # type: url # max: critical
- in:  auth-identity.nba.com    # type: url # max: critical
- in:  auth-identity-dev.nba.com    # type: url # max: critical
- in:  auth-identity-qa.nba.com    # type: url # max: critical
- in:  auth-identity-uat.nba.com    # type: url # max: critical
- in:  aces-dev.wnba.com    # type: url # max: critical
- in:  aces-qa.wnba.com    # type: url # max: critical
- in:  aces.wnba.com    # type: url # max: critical
- in:  dream-dev.wnba.com    # type: url # max: critical
- in:  dream-qa.wnba.com    # type: url # max: critical
- in:  dream.wnba.com    # type: url # max: critical
- in:  fever-dev.wnba.com    # type: url # max: critical
- in:  fever-qa.wnba.com    # type: url # max: critical
- in:  fever.wnba.com    # type: url # max: critical
- in:  fire-dev.wnba.com    # type: url # max: critical
- in:  fire-qa.wnba.com    # type: url # max: critical
- in:  fire.wnba.com    # type: url # max: critical
- in:  liberty-dev.wnba.com    # type: url # max: critical
- in:  liberty-qa.wnba.com    # type: url # max: critical
- in:  liberty.wnba.com    # type: url # max: critical
- in:  lynx-dev.wnba.com    # type: url # max: critical
- in:  lynx-qa.wnba.com    # type: url # max: critical
- in:  lynx.wnba.com    # type: url # max: critical
- in:  mercury-dev.wnba.com    # type: url # max: critical
- in:  mercury-qa.wnba.com    # type: url # max: critical
- in:  mercury.wnba.com    # type: url # max: critical
- in:  mystics-dev.wnba.com    # type: url # max: critical
- in:  mystics-qa.wnba.com    # type: url # max: critical
- in:  mystics.wnba.com    # type: url # max: critical
- in:  portland-dev.wnba.com    # type: url # max: critical
- in:  portland-qa.wnba.com    # type: url # max: critical
- in:  portland.wnba.com    # type: url # max: critical
- in:  sky-dev.wnba.com    # type: url # max: critical
- in:  sky-qa.wnba.com    # type: url # max: critical
- in:  sky.wnba.com    # type: url # max: critical
- in:  sparks-dev.wnba.com    # type: url # max: critical
- in:  sparks-qa.wnba.com    # type: url # max: critical
- in:  sparks.wnba.com    # type: url # max: critical
- in:  storm-dev.wnba.com    # type: url # max: critical
- in:  storm-qa.wnba.com    # type: url # max: critical
- in:  storm.wnba.com    # type: url # max: critical
- in:  sun-dev.wnba.com    # type: url # max: critical
- in:  sun-qa.wnba.com    # type: url # max: critical
- in:  sun.wnba.com    # type: url # max: critical
- in:  tempo-dev.wnba.com    # type: url # max: critical
- in:  tempo-qa.wnba.com    # type: url # max: critical
- in:  tempo.wnba.com    # type: url # max: critical
- in:  valkyries-dev.wnba.com    # type: url # max: critical
- in:  valkyries-qa.wnba.com    # type: url # max: critical
- in:  valkyries.wnba.com    # type: url # max: critical
- in:  wings-dev.wnba.com    # type: url # max: critical
- in:  wings-qa.wnba.com    # type: url # max: critical
- in:  wings.wnba.com    # type: url # max: critical
- in:  cweb-slot6-preview-ott-dev.nba.com    # type: url # max: critical
- in:  cweb-slot6-ott-dev.nba.com    # type: url # max: critical
- in:  cweb-slot5-ott-dev.nba.com    # type: url # max: critical
- in:  cweb-slot4-ott-dev.nba.com    # type: url # max: critical
- in:  cweb-slot3-ott-dev.nba.com    # type: url # max: critical
- in:  cweb-slot2-ott-dev.nba.com    # type: url # max: critical
- in:  cweb-slot1-ott-dev.nba.com    # type: url # max: critical
- in:  cweb-qa-aws-preview.nba.com    # type: url # max: critical
- in:  cweb-ott-uc-preview.nba.com    # type: url # max: critical
- in:  cweb-ott-uat-uc-preview.nba.com    # type: url # max: critical
- in:  cweb-ott-uat-preview.nba.com    # type: url # max: critical
- in:  cweb-ott-preview.nba.com    # type: url # max: critical
- in:  cweb-ott-qa-aws.nba.com    # type: url # max: critical
- in:  cweb-ott-qa-preview.nba.com    # type: url # max: critical
- in:  cweb-ott-aws-qa.nba.com    # type: url # max: critical
- in:  cweb-ott-aws-uat-uw2.nba.com    # type: url # max: critical
- in:  cweb-ott-aws-uat.nba.com    # type: url # max: critical
- in:  cweb-ott-dev-aws.nba.com    # type: url # max: critical
- in:  cweb-ott-dev-preview.nba.com    # type: url # max: critical
- in:  core-api-aws-dev.nba.com    # type: url # max: critical
- in:  core-api-aws-prod-east1.nba.com    # type: url # max: critical
- in:  core-api-aws-prod.nba.com    # type: url # max: critical
- in:  core-api-aws-qa.nba.com    # type: url # max: critical
- in:  core-api-aws-uat.nba.com    # type: url # max: critical
- in:  auth-identity-dev-ping.nba.com    # type: url # max: critical
- in:  auth-identity-ping.nba.com    # type: url # max: critical
- in:  auth-identity-qa-ping.nba.com    # type: url # max: critical
- in:  auth-identity-uat-ping.nba.com    # type: url # max: critical
- in:  identity-ping.nba.com    # type: url # max: critical
- in:  identity-server-dev.nba.com    # type: url # max: critical
- in:  identity-server-ping-dev.nba.com    # type: url # max: critical
- in:  identity-server-ping-qa.nba.com    # type: url # max: critical
- in:  identity-server-ping-uat.nba.com    # type: url # max: critical
- in:  identity-server-ping.nba.com    # type: url # max: critical
- in:  identity-server-qa.nba.com    # type: url # max: critical
- in:  identity-server-uat.nba.com    # type: url # max: critical
- in:  identity-server.nba.com    # type: url # max: critical
- in:  login-dev.nba.com    # type: url # max: critical
- in:  login-qa.nba.com    # type: url # max: critical
- in:  login-sandbox.nba.com    # type: url # max: critical
- in:  login-uat.nba.com    # type: url # max: critical
- in:  login.nba.com    # type: url # max: critical
- in:  stats-dev.nba.com    # type: url # max: critical
- in:  stats-trafficcop-aws-dev.nba.com    # type: url # max: critical
- in:  stats-trafficcop-aws-prod-east1.nba.com    # type: url # max: critical
- in:  stats-trafficcop-aws-prod.nba.com    # type: url # max: critical
- in:  stats-trafficcop-aws-qa.nba.com    # type: url # max: critical
- in:  stats-trafficcop-aws-uat.nba.com    # type: url # max: critical
- in:  stats-trafficcop-dev.nba.com    # type: url # max: critical
- in:  stats-trafficcop-qa.nba.com    # type: url # max: critical
- in:  stats-trafficcop-uat.nba.com    # type: url # max: critical
- in:  stats-qa.nba.com    # type: url # max: critical
- in:  aces-qa2.wnba.com    # type: url # max: critical
- in:  dream-qa2.wnba.com    # type: url # max: critical
- in:  fever-qa2.wnba.com    # type: url # max: critical
- in:  liberty-qa2.wnba.com    # type: url # max: critical
- in:  wings-qa2.wnba.com    # type: url # max: critical
- in:  sun-qa2.wnba.com    # type: url # max: critical
- in:  storm-qa2.wnba.com    # type: url # max: critical
- in:  sparks-qa2.wnba.com    # type: url # max: critical

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $39,750
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
