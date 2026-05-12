# Exodus

> Platform: HackerOne — https://hackerone.com/exodus
> Type: BBP
> Bounty: Low $500–$2,500 | Medium $1,500–$5,000 | High $5,000–$9,000 | Critical $10,000–$18,000
> Avg bounty: $350–$500
> Response efficiency: 96% | Avg first response: N/A | Total paid: $136,790
> Last scope update: 2025-12-29

## Scope

- in:  *.grateful.me    # type: wildcard # max: critical
- in:  *.exodus.io    # type: wildcard # max: high
- in:  *.a.exodus.io    # type: wildcard # max: high
- in:  *.exodus.com    # type: wildcard # max: high
- in:  Passkey Wallet    # type: other # max: critical
- in:  https://play.google.com/store/apps/details?id=exodusmovement.exodus&hl=en_IN    # type: android_app # max: critical
- in:  https://play.google.com/store/apps/details?id=com.exodus.grateful    # type: android_app # max: critical
- in:  Exodus Desktop Wallet    # type: downloadable_executables # max: critical
- in:  exodus-movement.exodus    # type: ios_app # max: critical
- in:  https://apps.apple.com/us/app/exodus-crypto-bitcoin-wallet/id1414384820    # type: ios_app # max: critical
- in:  https://apps.apple.com/us/app/grateful-by-exodus/id6754093889    # type: ios_app # max: critical
- in:  exodusmovement.exodus    # type: android_app # max: critical
- in:  Exodus Browser Extension    # type: other # max: critical
- in:  sunflower.ot.exodus.com    # type: url # max: critical
- out:  get.exodus.*    # type: wildcard # max: none
- out:  www.exodus.com/job-application/*    # type: wildcard # max: none
- out:  *.atp-exodus.com    # type: wildcard # max: none
- out:  support.exodus.com    # type: url # max: none
- out:  http://www.exodus.com/contact-support    # type: url # max: none
- out:  support-helpers.a.exodus.io    # type: url # max: none
- out:  slack-invite.exodus.com    # type: url # max: none
- out:  exodus.atlassian.net    # type: url # max: none
- out:  exodusstore.blob.core.windows.net    # type: url # max: none
- out:  safeguard.a.exodus.io    # type: url # max: none
- out:  https://exodus.atlassian.net    # type: url # max: none
- out:  http://exodus.com/keybase.txt    # type: url # max: none
- out:  Exodus Browser Extension    # type: downloadable_executables # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $136,790

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
