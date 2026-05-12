# MetaMask

> Platform: HackerOne — https://hackerone.com/metamask
> Type: BBP
> Bounty: Low $125–$500 | Medium $250–$1,250 | High $1,000–$15,000 | Critical $3,000–$50,000
> Avg bounty: $400–$500
> Response efficiency: 67% | Avg first response: N/A | Total paid: $666,555
> Last scope update: 2026-04-30

## Scope

- in:  https://*.metamask.io    # type: wildcard # max: critical
- in:  *.api.cx.metamask.io    # type: wildcard # max: critical
- in:  metamask.io    # type: url # max: critical
- in:  snaps.metamask.io    # type: url # max: critical
- in:  signature-insights.api.cx.metamask.io    # type: url # max: critical
- in:  wallet.web3auth.io    # type: url # max: critical
- in:  api-wallet.web3auth.io    # type: url # max: critical
- in:  https://github.com/Web3Auth/web3auth-web    # type: repo # max: critical
- in:  MetaMask Browser Extension    # type: other # max: critical
- in:  MetaMask SDK    # type: other # max: critical
- in:  https://metamask.github.io/phishing-warning/<vX.Y.Z>    # type: other # max: critical
- in:  Snaps    # type: other # max: critical
- in:  mUSD Stablecoin    # type: other # max: critical
- in:  io.metamask    # type: android_app # max: critical
- in:  io.metamask.Metamask    # type: ios_app # max: critical
- in:  Third Party Snaps    # type: other # max: none # not eligible for bounty
- in:  Authentication component    # type: other # max: critical
- in:  MetaMask Message Signing Snap    # type: other # max: critical
- in:  https://metamask.github.io/*    # type: wildcard # max: critical # not eligible for bounty
- in:  Firefox Extension: https://addons.mozilla.org/en-US/firefox/addon/ether-metamask/    # type: other # max: critical
- out:  community.metamask.io    # type: url # max: none
- out:  portfolio.metamask.io (app.metamask.io)    # type: url # max: none
- out:  https://mmi-support.metamask.io/    # type: url # max: none
- out:  https://support.metamask.io/    # type: url # max: none
- out:  permissionless.snaps.metamask.io    # type: url # max: none
- out:  https://user-storage.api.cx.metamask.io    # type: url # max: none
- out:  developer.metamask.io    # type: url # max: none
- out:  dashboard.web3auth.io    # type: url # max: none
- out:  api-dashboard.web3auth.io    # type: url # max: none
- out:  card.metamask.io    # type: url # max: none
- out:  travel.metamask.io    # type: url # max: none
- out:  Snaps Development Packages    # type: repo # max: none
- out:  https://www.npmjs.com/search?q=%40metamask    # type: other # max: none
- out:  Metamask Flask Extension    # type: other # max: none
- out:  https://metamask.github.io/    # type: other # max: none
- out:  Core Tier Assets    # type: other # max: none
- out:  Non-Core Tier Assets    # type: other # max: none
- out:  Wallet Tier Assets    # type: other # max: none
- out:  Message signing snap    # type: other # max: none
- out:  metamask.github.io    # type: url # max: none
- out:  Secret Recovery Phrase brute-forcing    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $666,555
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
