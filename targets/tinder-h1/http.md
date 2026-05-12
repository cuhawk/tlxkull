# Tinder

> Platform: HackerOne — https://hackerone.com/tinder
> Type: BBP
> Bounty: Low $2,000 | Medium $10,000 | High $20,000 | Critical $20,000
> Avg bounty: $500–$500
> Response efficiency: 97% | Avg first response: N/A | Total paid: $141,150
> Last scope update: 2024-03-06

## Scope

- in:  *.tinder.com    # type: wildcard # max: critical
- in:  *.gotinder.com    # type: wildcard # max: critical
- in:  *.tinderops.net    # type: wildcard # max: critical
- in:  *.tstaging.com    # type: wildcard # max: medium
- in:  *.tstaging.tools    # type: wildcard # max: medium
- in:  *.tinderwebstaging.com    # type: wildcard # max: medium
- in:  com.tinder    # type: android_app # max: critical
- in:  547702041    # type: ios_app # max: critical
- out:  go.tinder.com    # type: url # max: none
- out:  www.help.tinder.com    # type: url # max: none
- out:  gotinder.imgix.net    # type: url # max: none
- out:  console.gotinder.com    # type: url # max: none
- out:  AppsFlyer Subdomains    # type: other # max: none
- out:  invite.tinder.com    # type: url # max: none
- out:  open.tinder.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $141,150
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
