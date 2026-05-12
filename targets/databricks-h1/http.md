# Databricks

> Platform: HackerOne — https://hackerone.com/databricks
> Type: BBP
> Bounty: Low $100 | Medium $200–$400 | High $650–$3,000 | Critical $1,000–$10,000
> Avg bounty: $200–$200
> Response efficiency: 89% | Avg first response: N/A | Total paid: $263,095
> Last scope update: 2026-04-17

## Scope

- in:  databricks.com    # type: url # max: critical
- in:  accounts.cloud.databricks.com    # type: url # max: critical
- in:  https://dbc-9a3f8ed1-7608.cloud.databricks.com    # type: url # max: critical
- in:  Databricks Free Edition    # type: other # max: critical
- in:  Open Scope    # type: other # max: critical
- in:  Other In-Scope Assets    # type: other # max: critical
- in:  Databricks Product    # type: other # max: critical
- in:  docs.databricks.com    # type: url # max: critical
- in:  help.databricks.com    # type: url # max: critical
- in:  kb.databricks.com    # type: url # max: critical
- in:  partners.databricks.com    # type: url # max: critical
- in:  support.databricks.com    # type: url # max: critical
- in:  https://community.cloud.databricks.com/    # type: url # max: critical
- in:  advocates.databricks.com    # type: url # max: critical
- in:  community.databricks.com    # type: url # max: critical
- in:  customer-academy.databricks.com    # type: url # max: critical
- in:  labs.databricks.com    # type: url # max: critical
- in:  marketplace.databricks.com    # type: url # max: critical
- in:  demo.cloud.databricks.com    # type: url # max: critical
- in:  academy.databricks.com    # type: url # max: critical
- in:  https://dbc-a1ba5468-749b.staging.cloud.databricks.com/    # type: url # max: critical
- in:  connect.databricks.com    # type: url # max: critical
- in:  databricks-prod-cloudfront.cloud.databricks.com    # type: url # max: critical
- in:  databricks-staging-cloudfront.staging.cloud.databricks.com    # type: url # max: critical
- in:  e.databricks.com    # type: url # max: critical
- in:  files.training.databricks.com    # type: url # max: critical
- in:  go.corp.databricks.com    # type: url # max: critical
- in:  gw1-ap.corp.databricks.com    # type: url # max: critical
- in:  gw1-eu.corp.databricks.com    # type: url # max: critical
- in:  gw1-us.corp.databricks.com    # type: url # max: critical
- in:  gw2-us.corp.databricks.com    # type: url # max: critical
- in:  homebrew-tap.dev.databricks.com    # type: url # max: critical
- in:  ideas.databricks.com    # type: url # max: critical
- in:  ideas.staging.databricks.com    # type: url # max: critical
- in:  info.databricks.com    # type: url # max: critical
- in:  maintenance.databricks.com    # type: url # max: critical
- in:  pages.databricks.com    # type: url # max: critical
- in:  pgg11o.hubspot.databricks.com    # type: url # max: critical
- in:  preferences.databricks.com    # type: url # max: critical
- in:  signup.cloud.mrkt.databricks.com    # type: url # max: critical
- in:  signup.dev.mrkt.databricks.com    # type: url # max: critical
- in:  sparkhub.databricks.com    # type: url # max: critical
- in:  unsubscribe.corp.databricks.com    # type: url # max: critical
- in:  vpn-us.corp.databricks.com    # type: url # max: critical
- in:  waf-test.corp.databricks.com    # type: url # max: critical
- in:  delta.io    # type: url # max: critical
- in:  docs.delta.io    # type: url # max: critical
- in:  spark-summit.org    # type: url # max: critical
- in:  staging.spark-summit.org    # type: url # max: critical
- in:  spark-portal.org    # type: url # max: critical
- in:  spark-summit.com    # type: url # max: critical
- in:  https://dbc-a1ba5468-749b.staging.cloud.databricks.com,https://community.cloud.databricks.com/    # type: url # max: critical
- in:  connect.databricks.com,databricks-staging-cloudfront.staging.cloud.databricks.com,docs-admin.databricks.com,docs-user.databricks.com,e.databricks.com,go.databricks.com,go.dev.databricks.com,homebrew-tap.dev.databricks.com,ideas.staging.databricks.com,info.databricks.com,it.corp.databricks.com,ok.databricks.com,pages.databricks.com,partnermarketing.databricks.com,signup.cloud.mrkt.databricks.com,signup.dev.mrkt.databricks.com,ssh.databricks.com,ssh.spark-summit.org,staging.spark-summit.org,tools.sec-sf.databricks.com,training.databricks.com,uberlyft-ns.dev.databricks.com,waf-test.corp.databricks.com,academy.databricks.com,accounts.cloud.databricks.com,databricks-prod-cloudfront.cloud.databricks.com,delta.io,demo.cloud.databricks.com,docs.cloud.databricks.com,docs.databricks.com,docs.delta.io,files.training.databricks.com,ftp.databricks.com,go.corp.databricks.com,gw1-ap.corp.databricks.com,gw1-eu.corp.databricks.com,gw1-us.corp.databricks.com,gw2-us.corp.databricks.com    # type: url # max: critical
- in:  help.corp.databricks.com,help.databricks.com,ideas.databricks.com,kb.azuredatabricks.net,kb.databricks.com,maintenance.databricks.com,partners.databricks.com,pgg11o.hubspot.databricks.com,preferences.databricks.com,sophos.corp.databricks.com,spark-portal.org,spark-summit.com,spark-summit.org,sparkhub.databricks.com,support.databricks.com,unsubscribe.corp.databricks.com,vpn-us.corp.databricks.com,www.databricks.com,www.sparkhub.databricks.com    # type: url # max: critical
- out:  *.cloud.databricks.com    # type: wildcard # max: none
- out:  *.azuredatabricks.net    # type: wildcard # max: none
- out:  *.gcp.databricks.com    # type: wildcard # max: none
- out:  Other subdomains of *.azuredatabricks.net and other ‘o’ parameters    # type: other # max: none
- out:  go.databricks.com    # type: url # max: none
- out:  feedback.databricks.com    # type: url # max: none
- out:  forums.databricks.com    # type: url # max: none
- out:  https://databricks-prod-cloudfront.cloud.databricks.com/public/*    # type: wildcard # max: none
- out:  https://pr-29555.dev.databricks.com/*    # type: wildcard # max: none
- out:  pr-31861.dev.databricks.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $263,095
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
