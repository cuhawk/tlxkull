# UserTesting

> Platform: HackerOne — https://hackerone.com/usertesting
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 50% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-02-07

## Scope

- in:  www.usertesting.com/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.usermuse.com    # type: wildcard # max: critical # not eligible for bounty
- out:  *.teston.io    # type: wildcard # max: none
- out:  *.usertesting.com    # type: wildcard # max: none
- out:  http://www.usertesting.com/blog    # type: url # max: none
- out:  qa.usertesting.com    # type: url # max: none
- out:  help.usertesting.com    # type: url # max: none
- out:  https://apps.apple.com/us/app/usertesting/id1485452102    # type: url # max: none
- out:  https://play.google.com/store/apps/details?id=com.usertesting.recorder.krsna    # type: url # max: none
- out:  https://chrome.google.com/webstore/detail/usertestingcom-screen-rec/onlhphabpmijgblopkcjmphbbmeliagn    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
