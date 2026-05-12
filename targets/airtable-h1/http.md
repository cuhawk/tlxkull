# Airtable

> Platform: HackerOne — https://hackerone.com/airtable
> Type: BBP
> Bounty: Low $200 | Medium $400 | High $750 | Critical $3,500
> Avg bounty: $100–$150
> Response efficiency: 91% | Avg first response: N/A | Total paid: $137,504
> Last scope update: 2021-08-09

## Scope

- in:  *.staging-airtableblocks.com    # type: wildcard # max: critical
- in:  *.staging.airtable.com    # type: wildcard # max: critical
- in:  staging.airtable.com    # type: url # max: critical
- in:  api-staging.airtable.com    # type: url # max: critical
- in:  airtable.js SDK (https://www.npmjs.com/package/airtable)    # type: repo # max: critical
- in:  https://staging.airtable.com/staging    # type: url # max: critical
- in:  https://staging.airtable.com/admin    # type: url # max: critical
- out:  blog.airtable.com    # type: url # max: none
- out:  support.airtable.com    # type: url # max: none
- out:  guide.airtable.com    # type: url # max: none
- out:  airtable.com    # type: url # max: none
- out:  dl.airtable.com    # type: url # max: none
- out:  dl.getforma.com    # type: url # max: none
- out:  community.airtable.com    # type: url # max: none
- out:  Airtable macOS app    # type: other # max: none
- out:  Airtable Windows app    # type: other # max: none
- out:  com.formagrid.airtable    # type: android_app # max: none
- out:  com.FormaGrid.Hyperbase    # type: ios_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $137,504
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
