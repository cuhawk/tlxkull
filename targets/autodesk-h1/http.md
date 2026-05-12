# Autodesk

> Platform: HackerOne — https://hackerone.com/autodesk
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 96% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  Desktop Tier    # type: other # max: medium # not eligible for bounty
- out:  https://profile-stg.autodesk.com/security    # type: url # max: none
- out:  https://stg-manage.autodesk.com/usage-report-v2    # type: url # max: none
- out:  app.formit.autodesk.com/    # type: url # max: none
- out:  https://gcpay.com/    # type: url # max: none
- out:  http://www.gcpay.com/    # type: url # max: none
- out:  http://quote.oc.autodesk.com/    # type: api # max: none
- out:  https://amart.oc.autodesk.com    # type: api # max: none
- out:  https://checkoutservice-stg.autodesk.com    # type: api # max: none
- out:  https://payment-profile-gateway.oc.autodesk.com    # type: api # max: none
- out:  https://payment-profile-gateway.ocstg.autodesk.com/v1    # type: api # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
