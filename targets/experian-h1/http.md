# Experian

> Platform: HackerOne — https://hackerone.com/experian
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 88% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- out:  *.smartbusinessreports.com    # type: wildcard # max: none
- out:  *.accdata.experian.co.uk    # type: wildcard # max: none
- out:  www.businesscreditfacts.com    # type: url # max: none
- out:  www.smallbusiness.experian.com    # type: url # max: none
- out:  contactorcheck.com    # type: url # max: none
- out:  suppliercheck.com    # type: url # max: none
- out:  bi.experian.ie    # type: url # max: none
- out:  bi,experian.ie    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
