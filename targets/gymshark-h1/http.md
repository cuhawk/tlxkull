# Gymshark

> Platform: HackerOne — https://hackerone.com/gymshark
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-01-11

## Scope

- in:  *.gymshark.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.gymshark.io    # type: wildcard # max: critical # not eligible for bounty
- in:  com.gymshark.fitness    # type: android_app # max: critical # not eligible for bounty
- in:  com.gymshark.store    # type: android_app # max: critical # not eligible for bounty
- in:  1139155460    # type: ios_app # max: critical # not eligible for bounty
- in:  1139151320    # type: ios_app # max: critical # not eligible for bounty
- out:  gymshark.okta.com    # type: url # max: none
- out:  onboarding.gymshark.com    # type: url # max: none
- out:  creators.gymshark.com    # type: url # max: none
- out:  mobilecms.gymshark.com    # type: url # max: none
- out:  blogcms.gymshark.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
