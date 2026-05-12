# Whoop Bug Bounty

> Platform: HackerOne — https://hackerone.com/whoop_bug_bounty
> Type: BBP
> Bounty: Low $150 | Medium $500 | High $1,500 | Critical $3,000
> Avg bounty: $500–$500
> Response efficiency: 84% | Avg first response: N/A | Total paid: $33,350
> Last scope update: 2025-02-26

## Scope

- in:  api.prod.whoop.com    # type: url # max: critical
- in:  app.whoop.com    # type: url # max: critical
- in:  shop.whoop.com    # type: url # max: critical
- in:  WHOOP 4.0 STRAP    # type: other # max: critical
- in:  join.whoop.com    # type: other # max: critical
- in:  WHOOP 5.0/MG STRAP    # type: other # max: critical
- in:  com.whoop.android    # type: android_app # max: critical
- in:  com.whoop.iphone    # type: ios_app # max: critical
- in:  **.whoop.com    # type: wildcard # max: critical
- in:  *.whoop.com    # type: wildcard # max: critical
- in:  https://support.whoop.com/Battery_Pack_Updater    # type: other # max: medium
- out:  okta.whoop.com    # type: url # max: none
- out:  Support System    # type: other # max: none
- out:  Azure AD, Google Drive, Link Sharing Websites    # type: other # max: none
- out:  Credit/Debit Card Testing    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $33,350
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
