# Doppler

> Platform: HackerOne — https://hackerone.com/doppler
> Type: BBP
> Bounty: Low $250 | Medium $750 | High $2,500 | Critical $10,000
> Avg bounty: $250–$250
> Response efficiency: 82% | Avg first response: N/A | Total paid: $35,625
> Last scope update: 2023-02-27

## Scope

- in:  doppler.team    # type: url # max: critical
- in:  api.doppler.com    # type: url # max: critical
- in:  dashboard.doppler.com    # type: url # max: critical
- in:  share.doppler.com    # type: url # max: critical
- in:  https://github.com/DopplerHQ/cli    # type: repo # max: critical
- in:  doppler    # type: downloadable_executables # max: critical
- in:  *.doppler.com    # type: wildcard # max: critical
- out:  http://calendly.com/doppler/enterprise    # type: url # max: none
- out:  docs.doppler.com    # type: url # max: none
- out:  doppler.com    # type: url # max: none
- out:  community.doppler.com    # type: url # max: none
- out:  support.doppler.com    # type: url # max: none
- out:  https://github.com/DopplerHQ/awesome-bots    # type: other # max: none
- out:  docs.doppler.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $35,625
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
