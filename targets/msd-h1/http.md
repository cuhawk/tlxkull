# Merck & Co., Inc., Rahway, NJ, USA

> Platform: HackerOne — https://hackerone.com/msd
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 89% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-03-31

## Scope

- in:  *.merck.com    # type: url # max: critical # not eligible for bounty
- in:  *.msd.com    # type: url # max: critical # not eligible for bounty
- in:  All other applications (web sites, web applications, web services, and mobile applications) owned by Merck & Co., Inc., Rahway, NJ, USA    # type: other # max: critical # not eligible for bounty
- out:  uniauth.merck.com    # type: url # max: none
- out:  auth-uat.merck.com    # type: url # max: none
- out:  uat-accesscodes.msd.com    # type: url # max: none
- out:  *.merckgroup.com    # type: other # max: none
- out:  Assets owned by Merck KGaA, Darmstadt, Germany (EMD Group)    # type: other # max: none
- out:  engagezone.msd.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
