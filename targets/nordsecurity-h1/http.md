# Nord Security

> Platform: HackerOne — https://hackerone.com/nordsecurity
> Type: BBP
> Bounty: Low $100 | Medium $500 | High $1,000 | Critical $50,000
> Avg bounty: $100–$250
> Response efficiency: 58% | Avg first response: N/A | Total paid: $270,000
> Last scope update: 2025-09-08

## Scope

- in:  *.nordvpn.com    # type: wildcard # max: critical
- in:  app.nordpass.com    # type: url # max: critical
- in:  com.nordvpn.android    # type: other_apk # max: critical
- in:  All Mobile Assets    # type: other # max: critical
- in:  NordVPN Browser Extension    # type: other # max: medium
- in:  com.nordvpn.android    # type: android_app # max: critical
- in:  com.nordpass.android.app.password.manager    # type: android_app # max: critical
- in:  Saily - Android    # type: android_app # max: critical
- in:  NordVPN - Windows Executable    # type: downloadable_executables # max: critical
- in:  NordVPN - MacOS Executable    # type: downloadable_executables # max: critical
- in:  NordVPN - Linux Executable    # type: downloadable_executables # max: critical
- in:  NordPass - Windows Executable    # type: downloadable_executables # max: critical
- in:  NordPass - MacOS Executable    # type: downloadable_executables # max: critical
- in:  NordPass - Linux Executable    # type: downloadable_executables # max: critical
- in:  905953485    # type: ios_app # max: critical
- in:  1486322860    # type: ios_app # max: critical
- in:  Saily - iOS    # type: ios_app # max: critical
- in:  https://apps.apple.com/us/app/saily-esim-data-for-travel/id6475045151    # type: ios_app # max: critical
- in:  NordLocker - Android Application    # type: android_app # max: critical
- in:  NordLocker - MacOS Executable    # type: downloadable_executables # max: critical
- in:  NordLocker - Windows Executable    # type: downloadable_executables # max: critical
- in:  cloud.nordlocker.com    # type: url # max: critical
- in:  com.nordlocker.android.encrypt.cloud    # type: android_app # max: critical
- in:  https://github.com/NordSecurity/storyblok-rich-text-astro-renderer    # type: repo # max: critical
- in:  1116599239    # type: ios_app # max: medium
- in:  Windows Executable    # type: downloadable_executables # max: medium
- in:  *.nordlocker.com    # type: wildcard # max: high

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $270,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
