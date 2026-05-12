# SingleStore

> Platform: HackerOne — https://hackerone.com/singlestore
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 68% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2026-03-06

## Scope

- in:  cell-agent.*.svc.singlestore.com    # type: wildcard # max: critical # not eligible for bounty
- in:  notebook-gateway.*.svc.singlestore.com    # type: wildcard # max: critical # not eligible for bounty
- in:  bottle-api.*.svc.singlestore.com    # type: wildcard # max: critical # not eligible for bounty
- in:  bottle-dup.*.svc.singlestore.com    # type: wildcard # max: critical # not eligible for bounty
- in:  nova-gateway.*.svc.singlestore.com    # type: wildcard # max: critical # not eligible for bounty
- in:  ai.*.svc.singlestore.com    # type: wildcard # max: critical # not eligible for bounty
- in:  apps.*.svc.singlestore.com    # type: wildcard # max: critical # not eligible for bounty
- in:  https://portal.singlestore.com/    # type: url # max: critical # not eligible for bounty
- in:  https://portal.singlestore.com/admin    # type: url # max: critical # not eligible for bounty
- in:  auth.singlestore.com    # type: url # max: critical # not eligible for bounty
- in:  api.singlestore.com    # type: url # max: critical # not eligible for bounty
- in:  backend.singlestore.com    # type: url # max: critical # not eligible for bounty
- in:  authsvc.singlestore.com    # type: url # max: critical # not eligible for bounty
- in:  nimbus-gateway.singlestore.com    # type: url # max: critical # not eligible for bounty
- in:  phone-home.singlestore.com    # type: url # max: critical # not eligible for bounty
- in:  singlestore.com    # type: url # max: high # not eligible for bounty
- in:  singlestoredb-server    # type: downloadable_executables # max: critical # not eligible for bounty
- in:  singlestore-operator    # type: downloadable_executables # max: critical # not eligible for bounty
- in:  https://hub.docker.com/r/memsql/node    # type: downloadable_executables # max: critical # not eligible for bounty
- in:  https://auth.singlestore.com/    # type: url # max: critical # not eligible for bounty
- out:  *.labs.singlestore.com    # type: wildcard # max: none
- out:  *.ito.singlestore.com    # type: wildcard # max: none
- out:  https://portal-staging.dev.helios.singlestore.com/    # type: url # max: none
- out:  api-dev.singlestore.com    # type: url # max: none
- out:  studio.singlestore.com    # type: url # max: none
- out:  support.singlestore.com    # type: url # max: none
- out:  training.singlestore.com    # type: url # max: none
- out:  docs.singlestore.com    # type: url # max: none
- out:  backend-dev.singlestore.com    # type: url # max: none
- out:  authsvc-staging.singlestore.com    # type: url # max: none
- out:  bifrost.singlestore.com    # type: url # max: none
- out:  login.internal.singlestore.com    # type: url # max: none
- out:  status.singlestore.com    # type: url # max: none
- out:  *.svc.singlestore.com    # type: wildcard # max: none
- out:  https://authsvc-staging.singlestore.com    # type: url # max: none
- out:  https://backend-dev.singlestore.com/    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
