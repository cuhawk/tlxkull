# Penn Entertainment

> Platform: HackerOne — https://hackerone.com/penn_entertainment
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 92% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  *.thescore.com    # type: wildcard # max: critical # not eligible for bounty
- in:  thescore.com    # type: url # max: critical # not eligible for bounty
- in:  thescore.bet    # type: url # max: critical # not eligible for bounty
- in:  pennentertainment.com    # type: url # max: critical # not eligible for bounty
- in:  pennplaycasino.com    # type: url # max: critical # not eligible for bounty
- in:  thescoreesports.com    # type: url # max: critical # not eligible for bounty
- in:  hollywoodcasino.com    # type: url # max: critical # not eligible for bounty
- in:  about.thescore.bet    # type: url # max: critical # not eligible for bounty
- in:  com.fivemobile.thescore    # type: android_app # max: critical # not eligible for bounty
- in:  6463805689    # type: ios_app # max: critical # not eligible for bounty
- in:  285692706    # type: ios_app # max: critical # not eligible for bounty
- out:  *.pgs.casino    # type: wildcard # max: none
- out:  espnbet.com    # type: url # max: none
- out:  about.espnbet.com    # type: url # max: none
- out:  campaignmanager.thescore.com    # type: url # max: none
- out:  com.espn.bet    # type: android_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
