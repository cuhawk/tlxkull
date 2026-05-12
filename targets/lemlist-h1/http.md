# lemlist

> Platform: HackerOne — https://hackerone.com/lemlist
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2019-09-25

## Scope

- in:  app.lemlist.com    # type: url # max: critical # not eligible for bounty
- in:  app.lemcal.com    # type: url # max: critical # not eligible for bounty
- in:  app.lemwarm.com    # type: url # max: critical # not eligible for bounty
- in:  app.taplio.com    # type: url # max: critical # not eligible for bounty
- in:  app.tweethunter.io    # type: url # max: critical # not eligible for bounty
- out:  taplio.com    # type: url # max: none
- out:  tweethunter.io    # type: url # max: none
- out:  www.lemlist.com    # type: url # max: none
- out:  lemwarm.com    # type: url # max: none
- out:  www.lemcal.com    # type: url # max: none
- out:  api.lemlist.com    # type: url # max: none
- out:  api.taplio.com    # type: url # max: none
- out:  api.tweethunter.io    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
