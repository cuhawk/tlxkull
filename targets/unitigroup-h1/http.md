# Uniti

> Platform: HackerOne — https://hackerone.com/unitigroup
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 83% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-04-13

## Scope

- in:  *broadviewnet.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.windstream.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.windstream.net    # type: wildcard # max: critical # not eligible for bounty
- in:  *uniti.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *unitibenefits.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *unitisolutions.com    # type: wildcard # max: critical # not eligible for bounty
- in:  https://www.windstream.com/gokinetic    # type: url # max: critical # not eligible for bounty
- in:  we.windstream.com    # type: url # max: critical # not eligible for bounty
- in:  www.windstream.com    # type: url # max: critical # not eligible for bounty
- in:  paetec.net    # type: url # max: critical # not eligible for bounty
- in:  my.gokinetic.com    # type: url # max: critical # not eligible for bounty
- in:  gokinetic.com    # type: url # max: critical # not eligible for bounty
- in:  windstream.net    # type: url # max: critical # not eligible for bounty
- in:  windstreamenterprise.com    # type: url # max: critical # not eligible for bounty
- in:  windstreamwholesale.com    # type: url # max: critical # not eligible for bounty
- in:  unitiwholesale.com    # type: url # max: critical # not eligible for bounty
- out:  *.orderwindstream.com    # type: wildcard # max: none
- out:  *.windstreamoffers.com    # type: wildcard # max: none
- out:  *.windstreamsmallbusiness.com    # type: wildcard # max: none
- out:  *.getwindstream.com    # type: wildcard # max: none
- out:  *.windstreamdeals.com    # type: wildcard # max: none
- out:  *.Windstreambundledeals.com    # type: wildcard # max: none
- out:  Allworx    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
