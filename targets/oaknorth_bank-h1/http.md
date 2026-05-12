# OakNorth Bank

> Platform: HackerOne — https://hackerone.com/oaknorth_bank
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 43% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-08-10

## Scope

- in:  *.oaknorth.co.uk    # type: wildcard # max: critical # not eligible for bounty
- in:  *.oaknorth-it.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.oaknorth-prod.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.oaknorth.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.oaknorth.us    # type: wildcard # max: critical # not eligible for bounty
- in:  *.oaknorthbank.co.uk    # type: wildcard # max: critical # not eligible for bounty
- in:  https://api.deposits.oaknorth.co.uk    # type: url # max: critical # not eligible for bounty
- in:  com.oaknorth.businessbanking    # type: android_app # max: critical # not eligible for bounty
- in:  com.oaknorth.oaknorthmobilebanking    # type: android_app # max: critical # not eligible for bounty
- in:  https://apps.apple.com/gb/app/oaknorth-business/id1633477300    # type: ios_app # max: critical # not eligible for bounty
- in:  https://apps.apple.com/gb/app/oaknorth-mobile-banking/id1476387507    # type: ios_app # max: critical # not eligible for bounty
- in:  test.com    # type: other # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
