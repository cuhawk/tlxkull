# REI VDP

> Platform: HackerOne — https://hackerone.com/rei_vdp
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 91% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2024-08-01

## Scope

- in:  rei.com    # type: url # max: critical # not eligible for bounty
- in:  engineering.rei.com    # type: url # max: critical # not eligible for bounty
- in:  login.rei.com    # type: url # max: critical # not eligible for bounty
- in:  http://collaboration.rei.com    # type: url # max: critical # not eligible for bounty
- in:  Any public cloud resource or infrastructure operated and managed by REI    # type: other # max: critical # not eligible for bounty
- in:  Android & iOS App for REI Customers    # type: other # max: critical # not eligible for bounty
- in:  http://rei.com/events    # type: url # max: critical # not eligible for bounty
- in:  http://rei.com/adventures    # type: url # max: critical # not eligible for bounty
- in:  http://rei.com/learn/expert-advice    # type: url # max: critical # not eligible for bounty
- out:  *.rentals.rei.com    # type: wildcard # max: none
- out:  http://rei.com/rei-garage    # type: url # max: none
- out:  http://rei.com/used    # type: url # max: none
- out:  http://rei.com/blog    # type: url # max: none
- out:  http://rei.com/rentals    # type: url # max: none
- out:  rei.jobs    # type: url # max: none
- out:  reifund.org    # type: url # max: none
- out:  destinations.rei.com    # type: url # max: none
- out:  partners2.rei.com    # type: url # max: none
- out:  greenvestrentals.rei.com    # type: url # max: none
- out:  wpvip.rei.com    # type: url # max: none
- out:  desktop.rei.com    # type: url # max: none
- out:  foryourbenefit-rei.com/    # type: url # max: none
- out:  test-login.rei.com    # type: url # max: none
- out:  vpn.rei.com    # type: url # max: none
- out:  http://www.rei.com/learn/expert-advice    # type: url # max: none
- out:  reia.my.site.com    # type: url # max: none
- out:  future-login.rei.com    # type: url # max: none
- out:  reiadventures.force.com    # type: url # max: none
- out:  www.greenvestrentals.rei.com    # type: url # max: none
- out:  reicasting.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
