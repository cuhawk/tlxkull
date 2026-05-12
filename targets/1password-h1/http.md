# 1Password - Enterprise Password Manager

> Platform: HackerOne — https://hackerone.com/1password
> Type: BBP
> Bounty: Low $300 | Medium $600 | High $6,000 | Critical $30,000
> Avg bounty: $100–$100
> Response efficiency: 94% | Avg first response: N/A | Total paid: $19,950
> Last scope update: 2024-12-03

## Scope

- in:  http://--your-own-1password-account--.1password.com    # type: url # max: critical
- in:  <Your own 1Password account> —> Latest stable, beta, or nightly Command Line Interface (CLI)    # type: other # max: critical
- in:  <Your own 1Password account> —> Latest stable, beta, or nightly Browser Extension (Chrome, Brave, Firefox, Edge, and Safari)    # type: other # max: critical
- in:  https://events.1password.com/api/    # type: api # max: critical
- in:  https://events.1password.com/    # type: api # max: critical
- out:  *.agilebits.com    # type: wildcard # max: none
- out:  https://support.1password.com    # type: url # max: none
- out:  https://www.1password.com/    # type: url # max: none
- out:  All other domains, subdomains, and 1Password Accounts that are not owned by you, including accounts where you are a user but not the owner, are out of scope.    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $19,950

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
