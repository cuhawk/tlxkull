# Bitwarden

> Platform: HackerOne — https://hackerone.com/bitwarden
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  9pjsdv0vpk04    # type: windows_app_store_app_id # max: critical # not eligible for bounty
- in:  bitwarden.com    # type: url # max: critical # not eligible for bounty
- in:  api.bitwarden.com    # type: url # max: critical # not eligible for bounty
- in:  identity.bitwarden.com    # type: url # max: critical # not eligible for bounty
- in:  vault.bitwarden.com    # type: url # max: critical # not eligible for bounty
- in:  help.bitwarden.com    # type: url # max: critical # not eligible for bounty
- in:  v4.passwordless.dev    # type: url # max: critical # not eligible for bounty
- in:  docs.passwordless.dev    # type: url # max: critical # not eligible for bounty
- in:  https://github.com/bitwarden    # type: repo # max: critical # not eligible for bounty
- in:  https://chrome.google.com/webstore/detail/bitwarden-free-password-m/nngceckbapebfimnlniiiahkandclblb?hl=en    # type: other # max: critical # not eligible for bounty
- in:  https://addons.mozilla.org/en-US/firefox/addon/bitwarden-password-manager/    # type: other # max: critical # not eligible for bounty
- in:  https://addons.opera.com/extensions/details/bitwarden-free-password-manager/    # type: other # max: critical # not eligible for bounty
- in:  https://safari-extensions.apple.com/details/?id=com.bitwarden.safari-LTZ2PFU5D6    # type: other # max: critical # not eligible for bounty
- in:  https://www.npmjs.com/package/@bitwarden/mcp-server    # type: other # max: critical # not eligible for bounty
- in:  com.x8bit.bitwarden    # type: android_app # max: critical # not eligible for bounty
- in:  com.bitwarden.authenticator    # type: android_app # max: critical # not eligible for bounty
- in:  com.8bit.bitwarden    # type: ios_app # max: critical # not eligible for bounty
- in:  com.bitwarden.authenticator    # type: ios_app # max: critical # not eligible for bounty
- in:  https://github.com/bitwarden/desktop/releases/latest    # type: downloadable_executables # max: critical # not eligible for bounty
- in:  https://github.com/passwordless    # type: repo # max: critical # not eligible for bounty
- in:  https://github.com/bitwarden/cli/releases/latest    # type: downloadable_executables # max: critical # not eligible for bounty
- in:  https://www.microsoft.com/store/p/bitwarden-free-password-manager/9p6kxl0svnnl    # type: other # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
