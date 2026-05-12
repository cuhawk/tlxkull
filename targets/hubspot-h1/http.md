# HubSpot

> Platform: HackerOne — https://hackerone.com/hubspot
> Type: BBP
> Bounty: Low $50 | Medium $250 | High $1,500 | Critical $10,000
> Avg bounty: $250–$250
> Response efficiency: 98% | Avg first response: N/A | Total paid: $175,300
> Last scope update: 2024-11-25

## Scope

- in:  app*.hubspot.com    # type: wildcard # max: critical
- in:  api*.hubspot.com    # type: wildcard # max: critical
- in:  api*.hubapi.com    # type: wildcard # max: critical
- in:  *.hubspotemail.net    # type: wildcard # max: medium
- in:  *.hs-sites(-eu1)?.com    # type: wildcard # max: low
- in:  *.hubspotpagebuilder.com    # type: wildcard # max: low
- in:  *.hubspotpagebuilder.eu    # type: wildcard # max: low
- in:  chatspot.ai    # type: url # max: medium
- in:  hubspot.net    # type: url # max: medium
- in:  Customer Connected Domain    # type: other # max: medium
- in:  HubSpot Sales Office 365 add-in    # type: other # max: medium
- in:  Customer Portal    # type: other # max: low
- in:  Other HubSpot-owned (sub)domains not listed as Out of Scope    # type: other # max: low
- in:  HubSpot Android Mobile App    # type: android_app # max: high
- in:  HubSpot iOS Mobile App    # type: ios_app # max: high
- in:  app.hubspot.com    # type: url # max: critical
- in:  api.hubspot.com    # type: url # max: critical
- in:  api.hubapi.com    # type: url # max: critical
- in:  app-eu1.hubspot.com    # type: url # max: critical
- out:  connect.com    # type: url # max: none
- out:  shop.hubspot.com    # type: url # max: none
- out:  trust.hubspot.com    # type: url # max: none
- out:  thespot.hubspot.com    # type: url # max: none
- out:  ir.hubspot.com    # type: url # max: none
- out:  events.hubspot.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $175,300
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
