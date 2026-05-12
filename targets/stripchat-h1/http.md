# Stripchat

> Platform: HackerOne — https://hackerone.com/stripchat
> Type: BBP
> Bounty: Low $200 | Medium $500 | High $1,250 | Critical $3,000
> Avg bounty: $200–$200
> Response efficiency: 99% | Avg first response: N/A | Total paid: $26,620
> Last scope update: 2025-10-21

## Scope

- in:  *.stripchat.com    # type: wildcard # max: critical
- in:  go.stripchat.com    # type: url # max: none
- in:  my.club    # type: url # max: critical
- out:  https://stripchat.com/page*    # type: wildcard # max: none
- out:  mta*.stripchat.com    # type: wildcard # max: none
- out:  pxl.stripchat.com    # type: url # max: none
- out:  support.stripchat.com    # type: url # max: none
- out:  https://stripchat.com/wiki    # type: url # max: none
- out:  wiki.stripchat.com    # type: url # max: none
- out:  ext.stripchat.com    # type: url # max: none
- out:  extensions.stripchat.com    # type: url # max: none
- out:  websocket-apps.sc-apps.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $26,620

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
