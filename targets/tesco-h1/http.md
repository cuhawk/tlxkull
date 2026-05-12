# Tesco

> Platform: HackerOne — https://hackerone.com/tesco
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2025-09-23

## Scope

- in:  *.tesco.sk/*    # type: wildcard # max: critical # not eligible for bounty
- in:  https://www.booker.co.uk/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.itesco.cz/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.itesco.sk/*    # type: wildcard # max: critical # not eligible for bounty
- in:  https://www.onestop.co.uk/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ourtesco.com/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tesco-europe.com/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tesco.com/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tesco.hu/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tesco.ie/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tesco.org/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tescocloud.com/*    # type: wildcard # max: critical # not eligible for bounty
- in:  https://www.tescomobile.com/*    # type: wildcard # max: critical # not eligible for bounty
- in:  *.tescoplc.com/*    # type: wildcard # max: critical # not eligible for bounty
- in:  API Assets    # type: other # max: critical # not eligible for bounty
- in:  Cloud Assets    # type: other # max: critical # not eligible for bounty
- in:  Exposed Sensitive Documents    # type: other # max: critical # not eligible for bounty
- in:  Leaked & Default Credentials    # type: other # max: critical # not eligible for bounty
- in:  Medium, High and Critical Severity Issue on Out-Of-Scope Assets    # type: other # max: critical # not eligible for bounty
- in:  Third-Party Managed Assets    # type: other # max: critical # not eligible for bounty
- in:  Domain, Subdomain & Zone Takeovers    # type: other # max: medium # not eligible for bounty
- in:  com.tesco.grocery.view    # type: android_app # max: critical # not eligible for bounty
- in:  389581236    # type: ios_app # max: critical # not eligible for bounty
- in:  857834425    # type: ios_app # max: none # not eligible for bounty
- in:  Third-Party Managed Assets    # type: other # max: none # not eligible for bounty
- in:  Mobile Application Assets    # type: other # max: none # not eligible for bounty
- in:  Out-of-scope Assets    # type: other # max: none # not eligible for bounty
- in:  Tesco Mobile    # type: other # max: critical # not eligible for bounty
- in:  Tesco    # type: other # max: critical # not eligible for bounty
- in:  One Stop    # type: other # max: critical # not eligible for bounty
- in:  Booker    # type: other # max: critical # not eligible for bounty
- in:  Booker    # type: other # max: critical # not eligible for bounty
- out:  Dunnhumby (Non-Critical)    # type: other # max: none
- out:  Tesco Bank    # type: other # max: none
- out:  com.tescobank.mobile    # type: android_app # max: none
- out:  Core/Cloud/API/Subsidiary Assets    # type: other # max: none
- out:  Tesco Bank    # type: other # max: none
- out:  Dunnhumby    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
