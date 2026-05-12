# Roblox

> Platform: HackerOne — https://hackerone.com/roblox
> Type: BBP
> Bounty: Low $300 | Medium $1,000 | High $5,000 | Critical $20,000
> Avg bounty: $500–$650
> Response efficiency: 87% | Avg first response: N/A | Total paid: $1,110,000
> Last scope update: 2026-01-20

## Scope

- in:  *.roblox.com    # type: wildcard # max: critical
- in:  *.rbx.com    # type: wildcard # max: critical
- in:  *.ra.roblox.com    # type: wildcard # max: low
- in:  blox.link    # type: url # max: low
- in:  Roblox Client    # type: downloadable_executables # max: critical
- in:  Roblox Studio    # type: downloadable_executables # max: critical
- in:  Roblox Engine    # type: downloadable_executables # max: critical
- in:  Campaign    # type: other # max: critical
- in:  Guilded    # type: downloadable_executables # max: critical
- out:  *.guilded.gg    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $1,110,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
