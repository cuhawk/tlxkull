# Rockstar Games

> Platform: HackerOne — https://hackerone.com/rockstargames
> Type: BBP
> Bounty: Low $500 | Medium $1,000 | High $2,000 | Critical $25,000
> Avg bounty: $500–$500
> Response efficiency: 95% | Avg first response: N/A | Total paid: $425,550
> Last scope update: 2024-07-15

## Scope

- in:  socialclub.rockstargames.com    # type: url # max: critical
- in:  prod.ros.rockstargames.com    # type: url # max: critical
- in:  support.rockstargames.com    # type: url # max: critical
- in:  *.rockstargames.com    # type: url # max: critical
- in:  store.rockstargames.com    # type: url # max: critical
- in:  www.rockstargames.com    # type: url # max: critical
- in:  rockstarnorth.com    # type: url # max: medium
- in:  circolocorecords.com/    # type: url # max: medium
- in:  Rockstar Games Launcher    # type: downloadable_executables # max: critical
- in:  www.rockstargames.com    # type: url # max: critical
- in:  prod.cloud.rockstargames.com    # type: url # max: critical
- in:  patches.rockstargames.com    # type: url # max: critical
- in:  media.rockstargames.com    # type: url # max: critical
- in:  prod.hosted.cloud.rockstargames.com    # type: url # max: critical
- in:  prod.telemetry.ros.rockstargames.com    # type: url # max: critical
- in:  prod.conductor.ros.rockstargames.com    # type: url # max: critical
- out:  faspex.rockstargames.com    # type: url # max: none
- out:  emailcontent.rockstargames.com    # type: url # max: none
- out:  bomgar.rockstargames.com    # type: url # max: none
- out:  lifeinvader.com    # type: url # max: none
- out:  any-invalid-domains.rockstargames.com    # type: url # max: none
- out:  anomotion.com    # type: url # max: none
- out:  remote.rockstargames.com    # type: url # max: none
- out:  sip.rockstarnorth.com    # type: url # max: none
- out:  lync.rockstargames.com    # type: url # max: none
- out:  rockstarwarehouse.com    # type: url # max: none
- out:  cdn.sc.rockstargames.com    # type: url # max: none
- out:  updates.rockstargames.com    # type: url # max: none
- out:  downloads.rockstargames.com    # type: url # max: none
- out:  mindlink.rockstargames.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $425,550
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
