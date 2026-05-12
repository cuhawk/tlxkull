# Evernote

> Platform: HackerOne — https://hackerone.com/evernote
> Type: BBP
> Bounty: Low $150–$250 | Medium $300–$750 | High $750–$2,000 | Critical $1,500–$5,000
> Avg bounty: $300–$500
> Response efficiency: 76% | Avg first response: N/A | Total paid: $134,250
> Last scope update: 2021-10-26

## Scope

- in:  9wzdncrfj3mb    # type: windows_app_store_app_id # max: critical
- in:  www.evernote.com    # type: url # max: critical
- in:  accounts.evernote.com    # type: url # max: critical
- in:  api.evernote.com    # type: url # max: critical
- in:  com.evernote    # type: android_app # max: critical
- in:  406056744    # type: downloadable_executables # max: critical
- in:  281796108    # type: ios_app # max: critical
- in:  accounts.stage.evernote.com    # type: url # max: critical # not eligible for bounty
- in:  api.stage.evernote.com    # type: url # max: critical # not eligible for bounty
- in:  VDP Reports    # type: other # max: none
- in:  Beta React Native Android Application    # type: other # max: critical
- in:  Beta React Native iOS Application    # type: other # max: critical
- out:  help.evernote.com    # type: url # max: none
- out:  com.evernote.android    # type: android_app # max: none
- out:  VDP assets    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $134,250
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
