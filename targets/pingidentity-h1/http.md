# Ping Identity

> Platform: HackerOne — https://hackerone.com/pingidentity
> Type: BBP
> Bounty: Low $300 | Medium $600 | High $4,000 | Critical $10,000
> Avg bounty: $300–$300
> Response efficiency: 72% | Avg first response: N/A | Total paid: $118,100
> Last scope update: 2021-07-01

## Scope

- in:  https://ort-admin.pingone.com/*    # type: wildcard # max: critical
- in:  https://openam-bug-bounty-stag.forgeblocks.com/*    # type: wildcard # max: critical
- in:  https://ort-authenticator.pingone.com/*    # type: wildcard # max: high
- in:  https://ort-desktop.pingone.com/*    # type: wildcard # max: high
- in:  api.ort-one-pingone.com    # type: url # max: critical
- in:  console.ort-one-pingone.com    # type: url # max: critical
- in:  apps.ort-one-pingone.com    # type: url # max: critical
- in:  auth.ort-one-pingone.com    # type: url # max: critical
- in:  https://console.ort-one-pingone.com/?env=361b34ef-2725-4fd9-af1b-a2b189df3d05    # type: url # max: critical
- in:  https://console.ort-one-pingone.com/?env=7f327541-54e0-4ba4-8335-65eac2a25b5e    # type: url # max: critical
- in:  https://test-admin.pingone.com    # type: url # max: high
- out:  https://*.pingidentity.com    # type: wildcard # max: none
- out:  https://*.pingidentity.io    # type: wildcard # max: none
- out:  https://*.pingidentity.net    # type: wildcard # max: none
- out:  https://developer.pingidentity.com/*    # type: wildcard # max: none
- out:  admin.pingone.com    # type: url # max: none
- out:  api.pingone.com    # type: url # max: none
- out:  authenticator.pingone.com    # type: url # max: none
- out:  console.pingone.com    # type: url # max: none
- out:  uploads.pingone.com    # type: url # max: none
- out:  uploads-staging.pingone.com    # type: url # max: none
- out:  api-staging.pingone.com    # type: url # max: none
- out:  console-staging.pingone.com    # type: url # max: none
- out:  desktop.pingone.com    # type: url # max: none
- out:  test-desktop.pingone.com    # type: url # max: none
- out:  test-sso.connect.pingidentity.com    # type: url # max: none
- out:  privilege.ort-one-pingone.com    # type: url # max: none
- out:  https://console-staging.pingone.com/*    # type: wildcard # max: none
- out:  https://api-staging.pingone.com/*    # type: wildcard # max: none
- out:  https://apps-staging.pingone.com/*    # type: wildcard # max: none
- out:  test-admin.pingone.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $118,100
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
