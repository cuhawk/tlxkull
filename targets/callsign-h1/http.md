# Callsign

> Platform: HackerOne — https://hackerone.com/callsign
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2022-04-04

## Scope

- in:  *.s02.callsign.com    # type: wildcard # max: critical # not eligible for bounty
- in:  app.s02.callsign.com    # type: url # max: critical # not eligible for bounty
- in:  b2b.s02.callsign.com    # type: url # max: critical # not eligible for bounty
- in:  southfields-v2.s02.t00-csglobal.a2develop.com    # type: url # max: low # not eligible for bounty
- in:  com.callsign.app.android    # type: android_app # max: critical # not eligible for bounty
- in:  *.*    # type: wildcard # max: low # not eligible for bounty
- in:  *.a2verify.com    # type: wildcard # max: low # not eligible for bounty
- in:  *.a2develop.com    # type: wildcard # max: low # not eligible for bounty
- out:  www.callsign.com    # type: url # max: none
- out:  programs.callsign.com    # type: url # max: none
- out:  pathway.callsign.com    # type: url # max: none
- out:  support.callsign.com    # type: url # max: none
- out:  dashboard.callsign.com    # type: url # max: none
- out:  connector.callsign.com    # type: url # max: none
- out:  portal.callsign.com    # type: url # max: none
- out:  *.a2org.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
