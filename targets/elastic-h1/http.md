# Elastic

> Platform: HackerOne — https://hackerone.com/elastic
> Type: BBP
> Bounty: Low $100–$700 | Medium $100–$1,500 | High $100–$4,000 | Critical $100–$9,000
> Avg bounty: $245–$500
> Response efficiency: 80% | Avg first response: N/A | Total paid: $893,103
> Last scope update: 2026-02-19

## Scope

- in:  *.elastic.co    # type: wildcard # max: critical
- in:  *.found.io    # type: wildcard # max: critical
- in:  *.swiftype.com    # type: wildcard # max: critical
- in:  *.elstc.co    # type: wildcard # max: critical
- in:  *.elasticnet.co    # type: wildcard # max: critical
- in:  *.eops.nl    # type: wildcard # max: critical
- in:  *.elastic.dev    # type: wildcard # max: critical
- in:  *.ela.st    # type: wildcard # max: critical
- in:  *.elastic.wtf    # type: wildcard # max: critical
- in:  *.elasticacademy.com    # type: wildcard # max: critical
- in:  *.elasticaccelerationzone.co    # type: wildcard # max: critical
- in:  *.elasticapm.co    # type: wildcard # max: critical
- in:  *.elasticbeats.wtf    # type: wildcard # max: critical
- in:  *.elasticcloud.wtf    # type: wildcard # max: critical
- in:  *.elasticgov.com    # type: wildcard # max: critical
- in:  *.elasticloud.wtf    # type: wildcard # max: critical
- in:  *.elasticon.co    # type: wildcard # max: critical
- in:  *.elasticon.com    # type: wildcard # max: critical
- in:  *.elasticpartneracademy.com    # type: wildcard # max: critical
- in:  *.elasticps.co    # type: wildcard # max: critical
- in:  *.elasticsearch.com    # type: wildcard # max: critical
- in:  *.elasticsearch.fr    # type: wildcard # max: critical
- in:  *.elasticsearch.jp    # type: wildcard # max: critical
- in:  *.elasticsearch.org    # type: wildcard # max: critical
- in:  *.elasticsearch.wtf    # type: wildcard # max: critical
- in:  *.estccdn.com    # type: wildcard # max: critical
- in:  *.insight.io    # type: wildcard # max: critical
- in:  *.kibana.wtf    # type: wildcard # max: critical
- in:  *.logstash.net    # type: wildcard # max: critical
- in:  *.logstash.wtf    # type: wildcard # max: critical
- in:  *.prelert.com    # type: wildcard # max: critical
- in:  *.theelasticast.com    # type: wildcard # max: critical
- in:  cloud.elastic.co    # type: url # max: critical
- in:  Other    # type: other # max: critical
- in:  Elastic Package Registry    # type: other # max: critical
- in:  Elastic Synthetics Monitoring    # type: other # max: critical
- in:  Software Supply Chain    # type: other # max: critical
- in:  Elastic Clients    # type: other # max: critical
- in:  elastic.co credentials    # type: other # max: low
- in:  Beats - Auditbeat    # type: downloadable_executables # max: critical
- in:  Beats - Filebeat    # type: downloadable_executables # max: critical
- in:  Beats - Heartbeat    # type: downloadable_executables # max: critical
- in:  Beats - Metricbeat    # type: downloadable_executables # max: critical
- in:  Beats - Packetbeat    # type: downloadable_executables # max: critical
- in:  Beats - Winlogbeat    # type: downloadable_executables # max: critical
- in:  Elastic Agent    # type: downloadable_executables # max: critical
- in:  Elastic Cloud Enterprise (ECE)    # type: downloadable_executables # max: critical
- in:  Elastic Cloud on Kubernetes (ECK)    # type: downloadable_executables # max: critical
- in:  Elastic Enterprise Search    # type: downloadable_executables # max: critical
- in:  Elastic Maps Server    # type: downloadable_executables # max: critical
- in:  Elasticsearch    # type: downloadable_executables # max: critical
- in:  Logstash    # type: downloadable_executables # max: critical
- in:  Observability - APM Agents    # type: downloadable_executables # max: critical
- in:  Observability - APM Server    # type: downloadable_executables # max: critical
- in:  Fleet Server    # type: downloadable_executables # max: critical
- in:  Kibana    # type: downloadable_executables # max: critical
- in:  Beats    # type: downloadable_executables # max: critical
- in:  Elastic Defend    # type: downloadable_executables # max: critical
- in:  Beats - Osquerybeat    # type: downloadable_executables # max: critical
- in:  Elastic Distributions of OpenTelemetry (EDOT)    # type: downloadable_executables # max: critical
- in:  www.elastic.co    # type: url # max: critical
- in:  Elastic Behavior Detections    # type: repo # max: medium
- in:  All Elastic Products    # type: other # max: critical
- in:  https://github.com/elastic/logstash    # type: repo # max: critical
- in:  elasticsearch-ci.elastic.co    # type: url # max: critical
- in:  https://github.com/elastic/beats    # type: repo # max: critical
- in:  https://github.com/elastic/kibana    # type: repo # max: critical
- in:  https://github.com/elastic/elasticsearch    # type: repo # max: critical
- in:  https://cloud.elastic.co    # type: url # max: critical
- in:  *.elastic-cloud.com    # type: wildcard # max: critical
- in:  elastic-cloud.com    # type: url # max: critical
- out:  https://github.com/elastic/*/wiki    # type: wildcard # max: none
- out:  https://github.com/swiftype/*/wiki    # type: wildcard # max: none
- out:  *.es.io    # type: wildcard # max: none
- out:  *.jina.ai    # type: wildcard # max: none
- out:  *.keephq.dev    # type: wildcard # max: none
- out:  *.kbndev.co    # type: wildcard # max: none
- out:  learn.elastic.co    # type: url # max: none
- out:  link.email.elastic.co    # type: url # max: none
- out:  track.email.elastic.co    # type: url # max: none
- out:  sendgrid.elastic.co    # type: url # max: none
- out:  community.elastic.co    # type: url # max: none
- out:  discuss.elastic.co    # type: url # max: none
- out:  *.ip.es.io    # type: wildcard # max: none
- out:  *.elasticsearch.cn    # type: wildcard # max: none
- out:  training.elastic.co    # type: url # max: none
- out:  partners.elastic.co    # type: url # max: none
- out:  jobs.elastic.co    # type: url # max: none
- out:  info.elastic.co    # type: url # max: none
- out:  elasticon.elastic.co    # type: url # max: none
- out:  wiki.elastic.co    # type: url # max: none
- out:  go.es.co    # type: url # max: none
- out:  ip.es.io    # type: url # max: none
- out:  buy.elastic.co    # type: url # max: none
- out:  platform.keephq.dev    # type: url # max: none
- out:  https://github.com/elastic/protections-artifacts/tree/main/behavior/rules/windows    # type: repo # max: none
- out:  *.ctf.elstc.co    # type: wildcard # max: none
- out:  discuss.elastic.co    # type: url # max: none
- out:  elastic.co    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $893,103
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
