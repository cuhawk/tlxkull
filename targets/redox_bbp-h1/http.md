# Redox

> Platform: HackerOne — https://hackerone.com/redox_bbp
> Type: BBP
> Bounty: Low $150–$400 | Medium $500–$1,000 | High $1,500–$3,000 | Critical $3,000–$7,500
> Avg bounty: $150–$200
> Response efficiency: 71% | Avg first response: N/A | Total paid: $35,809
> Last scope update: 2023-04-04

## Scope

- in:  test*.redoxengine.com    # type: wildcard # max: critical
- in:  10x.redoxengine.com    # type: url # max: critical
- in:  testapp.redoxengine.com    # type: url # max: critical
- in:  testapi.redoxengine.com    # type: url # max: critical
- in:  docs.redoxengine.com    # type: url # max: medium
- in:  fhir.redoxengine.com    # type: url # max: medium
- in:  explore.redoxengine.com    # type: url # max: medium
- in:  www.redoxengine.com    # type: url # max: medium
- in:  help.redoxengine.com    # type: url # max: medium
- in:  api.gamma.redoxstage.com    # type: url # max: critical
- in:  app.gamma.redoxstage.com    # type: url # max: critical
- in:  blob.gamma.redoxstage.com    # type: url # max: critical
- in:  clientcert.gamma.redoxstage.com    # type: url # max: critical
- in:  dashboard.gamma.redoxstage.com    # type: url # max: critical
- in:  eets-sftp-listener.gamma.redoxstage.com    # type: url # max: critical
- in:  eets.gamma.redoxstage.com    # type: url # max: critical
- in:  evening-earth.gamma.redoxstage.com    # type: url # max: critical
- in:  gamma.redoxstage.com    # type: url # max: critical
- in:  launch.gamma.redoxstage.com    # type: url # max: critical
- in:  sftp.gamma.redoxstage.com    # type: url # max: critical
- in:  webhooks.gamma.redoxstage.com    # type: url # max: critical
- out:  dashboard.redoxengine.com    # type: url # max: none
- out:  candi.redoxengine.com    # type: url # max: none
- out:  api.redoxengine.com    # type: url # max: none
- out:  sso.redoxengine.com    # type: url # max: none
- out:  redox.slack.com    # type: url # max: none
- out:  https://redoxengine.atlassian.net    # type: url # max: none
- out:  gamma.redoxengine.com    # type: url # max: none
- out:  testapi.redoxengine.com / testapp.redoxengine.com / 10x.redoxengine.com    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $35,809
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
