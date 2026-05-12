# FetLife

> Platform: HackerOne — https://hackerone.com/fetlife
> Type: BBP
> Bounty: N/A (VDP)
> Avg bounty: $100–$100
> Response efficiency: 100% | Avg first response: N/A | Total paid: $63,902
> Last scope update: 2021-02-18

## Scope

- in:  *.fetlife.com    # type: wildcard # max: critical
- in:  fetlife.com    # type: url # max: critical
- in:  fetlifemail.com    # type: url # max: critical
- in:  *.fetlife.com    # type: url # max: critical
- in:  fetlife.com    # type: url # max: critical
- out:  *.bitlove.co    # type: wildcard # max: none
- out:  status.fetlife.com    # type: url # max: none
- out:  mail.fetlife.com    # type: url # max: none
- out:  n2.fetlife.com    # type: url # max: none
- out:  fetlifestatus.com    # type: url # max: none
- out:  bitlove.co    # type: url # max: none
- out:  com.bitlove.fetlife    # type: other_apk # max: none
- out:  Requests to our ad endpoints (on any server): `/ads/serve`, `/ads/application_serve*`, and `/ads/click/*`    # type: other # max: none
- out:  co.bitlove.opensource.FetLife    # type: ios_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $63,902

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
