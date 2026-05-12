# PagerDuty

> Platform: HackerOne — https://hackerone.com/pagerduty
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 69% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-10-04

## Scope

- in:  *.pagerduty.com    # type: wildcard # max: critical # not eligible for bounty
- in:  events.pagerduty.com    # type: url # max: critical # not eligible for bounty
- in:  api.pagerduty.com    # type: url # max: critical # not eligible for bounty
- in:  pentest-uat.pushbot.com    # type: url # max: critical # not eligible for bounty
- in:  https://hub.docker.com/r/rundeck/rundeck/    # type: url # max: critical # not eligible for bounty
- in:  https://hub.docker.com/r/rundeckpro/enterprise    # type: url # max: critical # not eligible for bounty
- in:  https://hub.docker.com/r/rundeckpro/runner    # type: url # max: critical # not eligible for bounty
- in:  hackerone.stg.runbook.pagerduty.cloud    # type: url # max: critical # not eligible for bounty
- in:  www.pagerduty.com    # type: url # max: high # not eligible for bounty
- in:  https://github.com/rundeck/rundeck-cli    # type: repo # max: critical # not eligible for bounty
- in:  https://github.com/rundeck/rundeck    # type: repo # max: critical # not eligible for bounty
- in:  https://packagecloud.io/pagerduty/rundeckpro/packages/rpm_any/rpm_any/rundeckpro-enterprise-4.14.1.20230622-1.noarch.rpm/download.rpm?distro_version_id=227    # type: downloadable_executables # max: critical # not eligible for bounty
- in:  https://packagecloud.io/pagerduty/rundeckpro/packages/java/com.rundeck.sidecar/pd-runner-0.1.46.jar    # type: downloadable_executables # max: critical # not eligible for bounty
- in:  https://packagecloud.io/pagerduty/rundeckpro/packages/java/com.rundeck.enterprise/rundeckpro-enterprise-4.14.1-20230622.war/artifacts/rundeckpro-enterprise-4.14.1-20230622.war/download     # type: downloadable_executables # max: critical # not eligible for bounty
- in:  https://packagecloud.io/pagerduty/rundeckpro/packages/any/any/rundeckpro-enterprise_4.14.1.20230622-1_all.deb/download.deb?distro_version_id=35     # type: downloadable_executables # max: critical # not eligible for bounty
- in:  https://packagecloud.io/pagerduty/rundeck/packages/rpm_any/rpm_any/rundeck-4.14.1.20230622-1.noarch.rpm/download.rpm?distro_version_id=227    # type: downloadable_executables # max: critical # not eligible for bounty
- in:  https://packagecloud.io/pagerduty/rundeck/packages/java/org.rundeck/rundeck-4.14.1-20230622.war/artifacts/rundeck-4.14.1-20230622.war/download     # type: downloadable_executables # max: critical # not eligible for bounty
- in:  https://packagecloud.io/pagerduty/rundeck/packages/any/any/rundeck_4.14.1.20230622-1_all.deb/download.deb?distro_version_id=35    # type: downloadable_executables # max: critical # not eligible for bounty
- out:  http://www.pagerduty.com/support/    # type: url # max: none
- out:  university.pagerduty.com    # type: url # max: none
- out:  community.pagerduty.com    # type: url # max: none
- out:  www.pagerduty.com/contact-us/    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
