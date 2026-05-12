# Netflix

> Platform: HackerOne — https://hackerone.com/netflix
> Type: BBP
> Bounty: Low $600 | Medium $600–$2,000 | High $2,000–$5,000 | Critical $5,000–$25,000
> Avg bounty: $600–$600
> Response efficiency: 99% | Avg first response: N/A | Total paid: $320,988
> Last scope update: 2024-07-22

## Scope

- in:  *.nflxext.com    # type: wildcard # max: critical
- in:  api*.netflix.com    # type: wildcard # max: critical
- in:  *.prod.ftl.netflix.com    # type: wildcard # max: critical
- in:  *.prod.cloud.netflix.com    # type: wildcard # max: critical
- in:  *.nflxvideo.net    # type: wildcard # max: critical
- in:  *.prod.dradis.netflix.com    # type: wildcard # max: critical
- in:  *.nflximg.net    # type: wildcard # max: critical
- in:  *.nflxso.net    # type: wildcard # max: critical
- in:  www.netflix.com    # type: url # max: critical
- in:  beacon.netflix.com    # type: url # max: critical
- in:  customerevents.netflix.com    # type: url # max: critical
- in:  secure.netflix.com    # type: url # max: critical
- in:  help.netflix.com    # type: url # max: critical
- in:  ichnaea.netflix.com    # type: url # max: critical
- in:  presentationtracking.netflix.com    # type: url # max: critical
- in:  nmtracking.netflix.com    # type: url # max: critical
- in:  meechum.netflix.com    # type: url # max: critical
- in:  Open Source - Atlas    # type: repo # max: critical
- in:  Corporate Assets    # type: other # max: critical
- in:  Open Source - Zuul    # type: other # max: critical
- in:  Microsites    # type: other # max: critical
- in:  Open Source - Spectator    # type: other # max: critical
- in:  Secondary Assets    # type: other # max: critical
- in:  Content Authorization Targets    # type: other # max: critical
- in:  Netflix Mobile Application for Android    # type: android_app # max: critical
- in:  Netflix Mobile Application for iOS    # type: ios_app # max: critical
- in:  Affiliates or entities such as recently acquired companies    # type: other # max: critical # not eligible for bounty
- in:  Content authorization vulnerabilities affecting only the in-browser player    # type: other # max: critical # not eligible for bounty
- in:  Low impact, individually exposed Google Docs with no common root cause (see “Publicly accessible Google Document or Drive Links” in the “Corporate Targets” section)    # type: other # max: critical # not eligible for bounty
- in:  Netflix Gaming Target    # type: other # max: critical # not eligible for bounty
- in:  *.nlfxvideo.net    # type: wildcard # max: critical
- in:  com.netflix.mediaclient    # type: android_app # max: critical
- in:  363590051    # type: ios_app # max: critical
- in:  com.netflix.Netflix    # type: ios_app # max: critical
- in:  https://github.com/Netflix/atlas    # type: repo # max: critical
- in:  Mobile Targets    # type: other # max: critical
- in:  Primary Targets    # type: other # max: critical
- in:  test_not_a_real_domain_at_netflix.netflix.com    # type: url # max: critical
- out:  ir.netflix.com    # type: url # max: none
- out:  ir.netflix.net    # type: url # max: none
- out:  netflixinvestor.com    # type: url # max: none
- out:  Open Source - Consoleme    # type: other # max: none
- out:  Open Source - Weep    # type: other # max: none
- out:  Open Source - Dispatch    # type: other # max: none
- out:  Third party websites or systems hosted by non-Netflix entities Out of Scope    # type: other # max: none
- out:  Set-top-boxes, smart TVs, streaming sticks Out of Scope    # type: other # max: none
- out:  Assets associated with ReadyPlayerMe     # type: other # max: none
- out:  Secondary Asset Vendor    # type: other # max: none
- out:  "Third party websites or systems hosted by non-Netflix entities Out of Scope"    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $320,988
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
