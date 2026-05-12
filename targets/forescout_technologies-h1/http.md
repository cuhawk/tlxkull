# ForeScout Technologies

> Platform: HackerOne — https://hackerone.com/forescout_technologies
> Type: BBP
> Bounty: Low $500 | Medium $1,000 | High $2,000 | Critical $4,000
> Avg bounty: $600–$1,000
> Response efficiency: 50% | Avg first response: N/A | Total paid: $112,600
> Last scope update: 2022-11-09

## Scope

- in:  www.forescout.com    # type: url # max: critical
- in:  datapod-2-ingest.acceptance.forescoutcloud.net    # type: url # max: critical
- in:  datapod-2-query.acceptance.forescoutcloud.net    # type: url # max: critical
- in:  datapod-1-ingest.production.forescoutcloud.net    # type: url # max: critical
- in:  datapod-1-query.production.forescoutcloud.net    # type: url # max: critical
- in:  mgmtpod-1-dashboard.production.forescoutcloud.net    # type: url # max: critical
- in:  mgmtpod-1.production.forescoutcloud.net    # type: url # max: critical
- in:  logstash-props.devicecloud.acceptance.forescoutcloud.net    # type: url # max: critical
- in:  datapod-1-100-druid-ingest.development.forescoutcloud.net    # type: url # max: critical
- in:  datapod-1-100-druid-query.development.forescoutcloud.net    # type: url # max: critical
- in:  datapod-1-100-druid-ingest.testing.forescoutcloud.net    # type: url # max: critical
- in:  datapod-1-druid-ingest.production.forescoutcloud.net    # type: url # max: critical
- in:  datapod-1-100-druid-query.production.forescoutcloud.net    # type: url # max: critical
- in:  datapod-2-druid-ingest.production.forescoutcloud.net    # type: url # max: critical
- in:  https://telemetry-polling.devicecloud.acceptance.forescoutcloud.net/v1/upload    # type: url # max: critical
- in:  https://telemetry-polling.devicecloud.acceptance.forescoutcloud.net/v1/polling    # type: url # max: critical
- in:  https://telemetry-polling.devicecloud.acceptance.forescoutcloud.net/v1/package    # type: url # max: critical
- in:  http://logstash-props.devicecloud.production.forescoutcloud.net/api/v1/properties    # type: url # max: critical
- in:  http://backend-api.devicecloud.production.forescoutcloud.net/api/v1/settings    # type: url # max: critical
- in:  http://datapod-1-druid-ingest.production.forescoutcloud.net/v1/upload    # type: url # max: critical
- in:  http://mgmtpod-1.production.forescoutcloud.net/oauth/token    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v2/query/grouptogroup    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v2/query/firstreporttimeentry    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v2/query/iplist    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v3/matrixoverview    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v3/query/overlappingzones    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v1/query/agg    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v1/polling    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v2/query/overlappinggroups    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v2/matrixoverview    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v3/query/zonetozone    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v2/deletestatus    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v2/query/ips/bysrc    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v2/service-list    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v2/query/ips/bydst/details    # type: url # max: critical
- in:  http://datapod-1-druid-query.production.forescoutcloud.net/v2/services    # type: url # max: critical
- in:  iris-testing-us-east-1-nlb-4df4bbde6f6e2bbb.elb.us-east-1.amazonaws.com    # type: url # max: critical
- in:  updates.forescout.com    # type: url # max: critical
- in:  streaming.iris.acceptance.forescoutcloud.net    # type: url # max: critical
- in:  mgmt-sensors.iris.acceptance.forescoutcloud.net    # type: url # max: critical
- in:  obs-sensors.iris.acceptance.forescoutcloud.net    # type: url # max: critical
- in:  streaming-api.iris.acceptance.forescoutcloud.net    # type: url # max: critical
- in:  aebddc74953f248bc8455665b0f7d47b-78af959a11e5d0c1.elb.us-east-1.amazonaws.com    # type: url # max: critical
- in:  streaming.iris.production.forescoutcloud.net    # type: url # max: critical
- in:  mgmt-sensors.iris.production.forescoutcloud.net    # type: url # max: critical
- in:  obs-sensors.iris.production.forescoutcloud.net    # type: url # max: critical
- in:  streaming-api.iris.production.forescoutcloud.net    # type: url # max: critical
- in:  ab2b0c50cdc7b445391f99d4957850c5-cd4ccfdb37dfafad.elb.us-east-1.amazonaws.com    # type: url # max: critical
- in:  streaming-gw.iris.production.forescoutcloud.net    # type: url # max: critical
- in:  community.forescout.com    # type: url # max: critical
- in:  us.forescout.cloud    # type: url # max: critical
- in:  uk.forescout.cloud    # type: url # max: critical
- in:  de.forescout.cloud    # type: url # max: critical
- in:  cloud.forescout.com    # type: url # max: critical
- in:  CounterAct 9.x    # type: firmware # max: high
- in:  38.140.238.56/29    # type: cidr # max: critical
- in:  97.105.243.96/28    # type: cidr # max: critical
- in:  64.47.18.80/29    # type: cidr # max: critical
- in:  194.90.25.80/29    # type: cidr # max: critical
- in:  194.90.151.192/28    # type: cidr # max: critical
- in:  194.90.89.165/32    # type: cidr # max: critical
- in:  212.143.112.81/29    # type: cidr # max: critical
- in:  64.84.60.0/24    # type: cidr # max: critical
- in:  a360f0bcc63ca11ea92550aeac091f3d-1101372245.us-east-1.elb.amazonaws.com    # type: url # max: critical
- in:  CounterAct 8.4    # type: firmware # max: critical
- in:  app.iris.production.forescoutcloud.net    # type: url # max: critical
- in:  app.iris.acceptance.forescoutcloud.net    # type: url # max: critical
- in:  cysiv.com    # type: url # max: critical
- in:  app.command.cysiv.com    # type: url # max: critical
- in:  pulsar.eyesightx.testing.forescoutcloud.net    # type: url # max: critical
- in:  obs-sensors.eyesightx.testing.forescoutcloud.net    # type: url # max: critical
- in:  mgmt-sensors.eyesightx.testing.forescoutcloud.net    # type: url # max: critical
- in:  risk-api.eyesightx.testing.forescoutcloud.net    # type: url # max: critical
- in:  app.eyesightx.testing.forescoutcloud.net    # type: url # max: critical
- in:  agatha.eyesightx.testing.forescoutcloud.net    # type: url # max: critical
- in:  135.84.145.0/27    # type: cidr # max: critical
- in:  silentdefense-training.forescout.com    # type: url # max: critical
- in:  74.201.95.0/27    # type: cidr # max: critical
- in:  sensors.eyesightx.testing.forescoutcloud.net    # type: url # max: critical
- in:  datapod-1-ingest.forescoutcloud.net    # type: url # max: critical
- in:  12.156.228.240/29    # type: cidr # max: critical
- in:  mgmtpod-1.forescoutcloud.net    # type: url # max: critical
- in:  http://97.105.243.96/28    # type: url # max: critical
- out:  datapod-1-100-ingest.development.forescoutcloud.net    # type: url # max: none
- out:  datapod-1-100-query.development.forescoutcloud.net    # type: url # max: none
- out:  mgmtpod-1-100-dashboard.development.forescoutcloud.net    # type: url # max: none
- out:  mgmtpod-1-100.development.forescoutcloud.net    # type: url # max: none
- out:  datapod-1-100-ingest.testing.forescoutcloud.net    # type: url # max: none
- out:  datapod-1-100-query.testing.forescoutcloud.net    # type: url # max: none
- out:  datapod-1-ingest.acceptance.forescoutcloud.net    # type: url # max: none
- out:  datapod-1-query.acceptance.forescoutcloud.net    # type: url # max: none
- out:  CounterAct 8.3    # type: firmware # max: none
- out:  forescout.service-now.com    # type: url # max: none
- out:  datapod-1-query.forescoutcloud.net    # type: url # max: none
- out:  192.151.146.64/26    # type: cidr # max: none
- out:  www.forescout.jp    # type: url # max: none
- out:  194.90.25.82    # type: url # max: none
- out:  194.90.25.83    # type: url # max: none
- out:  194.90.151.193    # type: url # max: none
- out:  fs-ds-beta-query-dapi.beta.forescoutcloud.com    # type: url # max: none
- out:  fsios.forescout.com    # type: url # max: none
- out:  mgmtpod1-auth-sd.beta.forescoutcloud.com    # type: url # max: none
- out:  fs-ds-beta-ingestion-dapi.beta.forescoutcloud.com    # type: url # max: none
- out:  212.143.112.83    # type: url # max: none
- out:  dapi-query-db06.forescoutcloud.net    # type: url # max: none
- out:  194.90.25.81    # type: url # max: none
- out:  34.235.209.211    # type: url # max: none
- out:  34.194.26.17    # type: url # max: none
- out:  212.143.112.84    # type: url # max: none
- out:  mgmtpod1-mgmt-auth.beta.forescoutcloud.com    # type: url # max: none
- out:  3.92.115.87    # type: url # max: none
- out:  3.86.127.226    # type: url # max: none
- out:  212.143.112.85    # type: url # max: none
- out:  3.219.10.206    # type: url # max: none
- out:  194.90.89.165    # type: url # max: none
- out:  fr-forescout.ser.netvision.net.il    # type: url # max: none
- out:  3.218.235.180    # type: url # max: none
- out:  odap-199-203-102-106.bb.netvision.net.il    # type: url # max: none
- out:  sra-emea1.forescout.com    # type: url # max: none
- out:  3.218.206.196    # type: url # max: none
- out:  199.203.102.106    # type: url # max: none
- out:  194.90.151.197    # type: url # max: none
- out:  212.179.243.144    # type: url # max: none
- out:  38.140.238.56/29    # type: other # max: none
- out:  www.forescouttechnologies.mx    # type: url # max: none
- out:  107.154.80.169    # type: url # max: none
- out:  194.90.25.84    # type: url # max: none
- out:  212.143.112.86    # type: url # max: none
- out:  3.208.210.205    # type: url # max: none
- out:  3.212.205.107    # type: url # max: none
- out:  3.215.110.36    # type: url # max: none
- out:  3.215.76.104    # type: url # max: none
- out:  3.217.118.139    # type: url # max: none
- out:  3.217.5.237    # type: url # max: none
- out:  194.90.25.86    # type: url # max: none
- out:  mgmtpod1-dashboard.beta.forescoutcloud.com    # type: url # max: none
- out:  97.105.243.96/28    # type: other # max: none
- out:  api.fem.forescout.com    # type: url # max: none
- out:  mgmtpod1-mapi.beta.forescoutcloud.com    # type: url # max: none
- out:  fs0.forescout.com    # type: url # max: none
- out:  bzq-219-243-144.static.bezeqint.net    # type: url # max: none
- out:  www.forescout.de    # type: url # max: none
- out:  www.forescout.fr    # type: url # max: none
- out:  www.forescout.kr    # type: url # max: none
- out:  zh.forescout.com    # type: url # max: none
- out:  api.fem-stage-inc.forescout.com    # type: url # max: none
- out:  api-stage-inc.forescout.com    # type: url # max: none
- out:  207.232.12.9    # type: url # max: none
- out:  svc23.forescout.com    # type: url # max: none
- out:  dapi-ingest-db06.forescoutcloud.net    # type: url # max: none
- out:  64.47.18.80/29    # type: other # max: none
- out:  54.85.213.6    # type: url # max: none
- out:  74.201.95.0/27    # type: other # max: none
- out:  52.201.2.226    # type: url # max: none
- out:  54.173.159.83    # type: url # max: none
- out:  135.84.145.0/27    # type: other # max: none
- out:  144.178.70.80/29    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $112,600
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
