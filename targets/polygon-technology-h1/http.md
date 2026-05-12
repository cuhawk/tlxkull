# Polygon Technology

> Platform: HackerOne — https://hackerone.com/polygon-technology
> Type: BBP
> Bounty: Low $500 | Medium $2,000 | High $10,000 | Critical $20,000
> Avg bounty: $300–$300
> Response efficiency: 98% | Avg first response: N/A | Total paid: $71,908
> Last scope update: 2023-06-15

## Scope

- in:  staking-api.polygon.technology    # type: url # max: critical
- in:  faucet.polygon.technology    # type: url # max: critical
- in:  portal.polygon.technology    # type: url # max: critical
- in:  staking.polygon.technology    # type: url # max: critical
- in:  api-gateway.polygon.technology    # type: api # max: critical
- in:  faucet-api.polygon.technology/    # type: api # max: high
- in:  gasstation.polygon.technology/    # type: api # max: high
- in:  api-polygon-tokens.polygon.technology/    # type: api # max: high
- in:  balance-api.polygon.technology/    # type: api # max: high
- in:  https://github.com/0xPolygon/chain-indexer-framework     # type: repo # max: critical
- in:  https://github.com/0xPolygon/auto-claim-service    # type: repo # max: high
- in:  https://github.com/0xPolygon/lxly.js    # type: repo # max: high
- in:  https://github.com/0xPolygon/static    # type: repo # max: high
- in:   https://github.com/0xPolygon/proof-generation-api    # type: repo # max: high
- in:  https://github.com/agglayer/agglayer/    # type: url # max: critical # not eligible for bounty
- in:  https://agglayer-test.polygon.technology    # type: url # max: critical
- in:  wallet.polygon.technology    # type: url # max: critical
- in:  burn.polygon.technology    # type: url # max: critical
- in:  watchgod.polygon.technology    # type: url # max: critical
- in:  open-api.polygon.technology    # type: url # max: critical
- in:  mapper.polygon.technology    # type: url # max: critical
- in:  bridge-explorer.polygon.technology    # type: url # max: critical
- in:  bridge-api.matic.network    # type: url # max: critical
- in:  https://agglayer.polygon.technology/    # type: url # max: critical
- in:  mnt.matic.network    # type: url # max: critical
- in:  multisig-wallet.polygon.technology    # type: url # max: critical
- in:  *.api.matic.network    # type: wildcard # max: critical
- in:  bridge-api-node.matic.network    # type: url # max: critical
- out:  *.matic.network    # type: wildcard # max: none
- out:  https://github.com/maticnetwork/heimdall    # type: repo # max: none
- out:  https://github.com/maticnetwork/bor    # type: repo # max: none
- out:  https://github.com/maticnetwork/contracts    # type: repo # max: none
- out:  https://github.com/maticnetwork/matic-cli     # type: repo # max: none
- out:  https://github.com/0xPolygon/heimdall-v2    # type: repo # max: none
- out:  ecosystem-api.polygon.technology    # type: url # max: none
- out:  ecosystem.polygon.technology    # type: url # max: none
- out:  *.polygon.technology    # type: wildcard # max: none
- out:  https://github.com/maticnetwork/matic.js    # type: repo # max: none
- out:  https://github.com/maticnetwork/matic-scabbards    # type: repo # max: none
- out:  https://github.com/maticnetwork/*    # type: repo # max: none
- out:  https://github.com/maticnetwork/matic-scabbards    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $71,908
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
