# Kong

> Platform: HackerOne — https://hackerone.com/kong
> Type: BBP
> Bounty: Low N/A | Medium $100 | High $500 | Critical $1,000
> Avg bounty: $100–$200
> Response efficiency: 84% | Avg first response: N/A | Total paid: $11,200
> Last scope update: 2025-04-03

## Scope

- in:  https://*.api.konghq.com    # type: wildcard # max: critical
- in:  https://us.identity.konghq.com/*    # type: wildcard # max: critical
- in:  https://app.insomnia.rest/    # type: url # max: critical
- in:  http://cloud.konghq.com    # type: url # max: critical
- in:  developer.konghq.com    # type: url # max: high
- in:  konghq.com    # type: url # max: high
- in:  Subdomain Takeover - konghq.com    # type: other # max: high
- in:  GitHub Actions in our Public Repositories     # type: other # max: none
- in:  Insomnia CLI (inso)    # type: downloadable_executables # max: critical
- in:  Insomnia Desktop Client    # type: downloadable_executables # max: critical
- in:  Kong Mesh    # type: downloadable_executables # max: critical
- in:  Kong Gateway Plugins (Kong-Supported Only)    # type: downloadable_executables # max: critical
- in:  Kong Gateway Enterprise    # type: downloadable_executables # max: critical
- in:  Kong Gateway OSS    # type: downloadable_executables # max: medium # not eligible for bounty
- in:  kong.my.site.com    # type: url # max: critical
- in:  Kong Gateway    # type: downloadable_executables # max: critical
- in:  Kong Gateway (OSS and Enterprise)    # type: downloadable_executables # max: critical
- in:  GitHub Actions    # type: other # max: critical
- in:  https://cloud.konghq.com    # type: url # max: critical
- in:  Insomnia Desktop Client    # type: other # max: critical
- out:  https://*.konghq.tech    # type: wildcard # max: none
- out:  *.gateways.konghq.com    # type: wildcard # max: none
- out:  *.*.edge.gateways.konghq.com    # type: wildcard # max: none
- out:  https://konghq.com/    # type: url # max: none
- out:  https://kuma.io/    # type: url # max: none
- out:  https://insomnia.rest/    # type: url # max: none
- out:  https://docs.konghq.com    # type: url # max: none
- out:  https://httpbin.konghq.com/    # type: url # max: none
- out:  Non-Kong GitHub Repositories    # type: other # max: none
- out:  Non-Kong Plugins    # type: downloadable_executables # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $11,200
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
