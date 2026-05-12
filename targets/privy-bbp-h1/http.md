# Privy (Bounty)

> Platform: HackerOne — https://hackerone.com/privy-bbp
> Type: BBP
> Bounty: Low $500 | Medium $2,500 | High $5,000 | Critical $10,000
> Avg bounty: $250–$250
> Response efficiency: 97% | Avg first response: N/A | Total paid: $60,000
> Last scope update: 2025-01-20

## Scope

- in:  auth.privy.io    # type: url # max: critical
- in:  dashboard.privy.io    # type: url # max: critical
- in:  home.privy.io    # type: url # max: critical
- in:  recovery.privy.io    # type: url # max: critical
- in:  api.privy.io    # type: url # max: critical
- in:  https://www.npmjs.com/package/@privy-io/react-auth    # type: repo # max: critical
- in:  https://www.npmjs.com/package/@privy-io/js-sdk-core    # type: other # max: critical
- in:  https://www.npmjs.com/package/@privy-io/expo    # type: other # max: critical
- in:  https://www.npmjs.com/package/@privy-io/wagmi    # type: other # max: critical
- in:  https://www.npmjs.com/package/@privy-io/cross-app-connect    # type: other # max: critical
- in:  https://www.npmjs.com/package/@privy-io/cross-app-provider    # type: other # max: critical
- in:  @privy-io controlled namespace dependencies    # type: other # max: critical
- in:  console.privy.io    # type: url # max: critical
- out:  privy.io    # type: url # max: none
- out:  blog.privy.io    # type: url # max: none
- out:  demo.privy.io    # type: url # max: none
- out:  docs.privy.io    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $60,000

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
