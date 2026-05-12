# 1Password - CTF

> Platform: HackerOne — https://hackerone.com/1password_ctf
> Type: BBP
> Bounty: Low N/A | Medium N/A | High N/A | Critical $1,000,000
> Avg bounty: N/A
> Response efficiency: 73% | Avg first response: N/A | Total paid: $10,000
> Last scope update: 2024-12-03

## Scope

- in:  https://bugbounty-ctf.1password.com/    # type: url # max: critical
- out:  *.agilebits.com    # type: wildcard # max: none
- out:  https://support.1password.com    # type: url # max: none
- out:  https://www.1password.com/    # type: url # max: none
- out:  All other domains, subdomains, and 1Password Accounts that are not owned by you, including accounts where you are a user but not the owner, are out of scope.    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $10,000

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
