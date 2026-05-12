# Thomson Reuters

> Platform: HackerOne — https://hackerone.com/thomsonreuters-public
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 89% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2019-09-23

## Scope

- in:  *.thomsonreuters.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.reuters.com    # type: wildcard # max: critical # not eligible for bounty
- out:  *.outofscope.example.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
