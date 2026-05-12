# Inspectorio

> Platform: HackerOne — https://hackerone.com/inspectorio
> Type: BBP
> Bounty: Low $150 | Medium $500 | High $1,500 | Critical $3,000
> Avg bounty: $150–$150
> Response efficiency: 86% | Avg first response: N/A | Total paid: $31,137
> Last scope update: 2025-01-28

## Scope

- in:  app.stg.inspectorio.com    # type: url # max: critical
- in:  rise.stg.inspectorio.com    # type: url # max: critical
- in:  report-html-sight.stg.inspectorio.com    # type: url # max: critical
- in:  api.stg.inspectorio.com    # type: url # max: critical
- in:  rise-api.stg.inspectorio.com    # type: url # max: critical
- in:  docuflow.stg.inspectorio.com    # type: url # max: critical
- in:  id.stg.inspectorio.com    # type: url # max: critical
- in:  https://testflight.apple.com/join/vwFxXX7t    # type: testflight # max: critical
- in:  https://app.bitrise.io/app/51a95edaab331ec5/installable-artifacts/e5213e1a814bf0ba/public-install-page/bed0d33f048271d6828c5a4a979ecc96    # type: other_apk # max: critical
- in:  files-stg.inspectorio.com    # type: url # max: critical # not eligible for bounty
- in:  https://collabora.stg.inspectorio.com    # type: url # max: critical # not eligible for bounty
- in:  https://app.bitrise.io/app/51a95edaab331ec5/build/3e7a7f0d-95ec-42d1-8455-1d55731655c8/artifact/51ffc62a5160ec15/p/dad92b44dbe22c866cc7de48a020225c    # type: other_apk # max: critical
- in:  https://app.bitrise.io/app/db5275247ea7ce57/build/5771e23e-0d4c-47a8-a9fa-c0b490d3dbe1/artifact/f6ccdc7b82520813/p/33da99f03e5451b2f3aaa433d870f829    # type: other_ipa # max: critical
- in:  https://api.stg.inspectorio.com/inspectorio/pentaho/*    # type: wildcard # max: critical # not eligible for bounty
- in:  1533620438    # type: ios_app # max: critical
- in:  saas.ins.inspectorio.store    # type: android_app # max: critical
- in:  rise-api.inspectorio.com    # type: url # max: critical
- in:  https://kong-kube-stag.inspectorio.com/inspectorio/pentaho/*    # type: wildcard # max: critical # not eligible for bounty
- in:  www.inspectorio.com    # type: url # max: critical
- in:  kong-kube-stag.inspectorio.com    # type: url # max: critical

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $31,137
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
