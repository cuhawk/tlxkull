# USPS - United States Postal Service

> Platform: HackerOne — https://hackerone.com/usps
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-01-23

## Scope

- in:  iv.usps.com    # type: url # max: critical # not eligible for bounty
- in:  id.usps.com    # type: url # max: critical # not eligible for bounty
- in:  gateway.usps.com    # type: url # max: critical # not eligible for bounty
- in:  reg.usps.com    # type: url # max: critical # not eligible for bounty
- in:  pi.usps.com    # type: url # max: critical # not eligible for bounty
- in:  retail-pi.usps.com    # type: url # max: critical # not eligible for bounty
- in:  store.usps.com    # type: url # max: critical # not eligible for bounty
- in:  internationalclaims.usps.com    # type: url # max: critical # not eligible for bounty
- in:  https://www.usps.com/postalone/    # type: url # max: critical # not eligible for bounty
- in:  ncoa.usps.gov    # type: url # max: critical # not eligible for bounty
- in:  moversguide.usps.com    # type: url # max: critical # not eligible for bounty
- in:  https://holdmail.usps.com/holdmail/    # type: url # max: critical # not eligible for bounty
- in:  https://redelivery.usps.com/redelivery/    # type: url # max: critical # not eligible for bounty
- in:  https://about.usps.com/what/government-services/election-mail/    # type: url # max: critical # not eligible for bounty
- in:  www.usps.com    # type: url # max: critical # not eligible for bounty
- in:  www.liteblue.usps.gov    # type: url # max: critical # not eligible for bounty
- in:  www.usps.gov    # type: url # max: critical # not eligible for bounty
- in:  http://special.usps.com/testkits    # type: url # max: critical # not eligible for bounty
- in:  *.usps.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  informeddelivery.usps.com    # type: url # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
