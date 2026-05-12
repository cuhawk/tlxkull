# Tools for Humanity

> Platform: HackerOne — https://hackerone.com/toolsforhumanity
> Type: BBP
> Bounty: Low $300–$500 | Medium $1,000–$2,000 | High $3,000–$12,500 | Critical $10,000–$25,000
> Avg bounty: $300–$500
> Response efficiency: 84% | Avg first response: N/A | Total paid: $113,325
> Last scope update: 2025-06-20

## Scope

- in:  *.worldcoin.org    # type: wildcard # max: critical
- in:  *.consumer.worldcoin.org    # type: wildcard # max: critical
- in:  *.worldcoin-distributors.com    # type: wildcard # max: critical
- in:  *.worldcoin.dev    # type: wildcard # max: critical
- in:  *.toolsforhumanity.com    # type: wildcard # max: critical
- in:  toolsforhumanity.com    # type: url # max: critical
- in:  worldcoin.org    # type: url # max: critical
- in:  developer.worldcoin.org    # type: url # max: critical
- in:  world.org    # type: url # max: critical
- in:  https://github.com/worldcoin    # type: repo # max: critical
- in:  https://github.com/worldcoin/orb-software    # type: repo # max: critical
- in:  https://github.com/worldcoin/orb-firmware    # type: repo # max: critical
- in:  https://github.com/worldcoin/orb-core    # type: repo # max: critical
- in:  https://github.com/worldcoin/orb-messages    # type: repo # max: critical
- in:  https://github.com/worldcoin/orb-secure-element    # type: repo # max: critical
- in:  https://github.com/worldcoin/orb-relay-messages    # type: repo # max: critical
- in:  https://github.com/worldcoin/orb-rustzone    # type: repo # max: critical
- in:  https://docs.world.org/world-chain/reference/address-book    # type: other # max: critical
- in:  Secondary Assets    # type: other # max: critical
- in:  Primary Assets    # type: other # max: critical
- in:  https://play.google.com/store/apps/details?id=com.worldcoin    # type: android_app # max: critical
- in:  https://apps.apple.com/no/app/world-app-worldcoin-wallet/id1560859847    # type: ios_app # max: critical
- in:  getworldcoin.com    # type: url # max: critical
- in:  id.worldcoin.org    # type: url # max: critical
- in:  bioid-management.app    # type: url # max: critical
- in:  https://github.com/worldcoin/world-id-contracts    # type: other # max: critical
- in:  https://github.com/worldcoin/world-id-state-bridge    # type: other # max: critical
- in:  http://id.worldcoin.eth    # type: other # max: critical
- in:  https://api.consumer.worldcoin.org/v1/graphql    # type: url # max: critical
- in:  config.consumer.worldcoin.org    # type: url # max: critical
- in:  signup.crypto.worldcoin.org    # type: url # max: critical
- in:  auth.orb.worldcoin.org    # type: url # max: critical
- in:  api.operator.worldcoin.org    # type: url # max: critical
- in:  api.consumer.worldcoin.org    # type: url # max: critical
- in:  *.orb.worldcoin.org    # type: wildcard # max: critical
- in:  *.operator.worldcoin.org    # type: wildcard # max: critical
- in:  posthog.consumer.worldcoin.org    # type: url # max: critical
- in:  test.com    # type: url # max: critical
- in:  h1test.com    # type: url # max: critical
- out:  support.worldcoin.com    # type: url # max: none
- out:  support.world.org    # type: url # max: none
- out:  https://github.com/worldcoin/orb-hardware    # type: repo # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $113,325
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
