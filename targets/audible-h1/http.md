# Audible

> Platform: HackerOne — https://hackerone.com/audible
> Type: BBP
> Bounty: Low $200 | Medium $600 | High $6,000 | Critical $25,000
> Avg bounty: $400–$600
> Response efficiency: 96% | Avg first response: N/A | Total paid: $134,000
> Last scope update: 2025-11-11

## Scope

- in:  tax.audible.com    # type: url # max: critical
- in:  *.audible.(TLD)    # type: other # max: critical
- in:  com.audible.application    # type: android_app # max: critical
- in:  379693831    # type: ios_app # max: critical
- in:  ws.audible.com    # type: url # max: critical
- in:  samples.audible.com    # type: url # max: critical
- in:  cds.audible.com    # type: url # max: critical
- in:  api.audible.com    # type: url # max: critical
- out:  *.acx.com    # type: wildcard # max: none
- out:  newsletters.audible.com    # type: url # max: none
- out:  www.audiblecareers.com    # type: url # max: none
- out:  https://www.audiblehub.com/submit    # type: url # max: none
- out:  https://www.audible.com/ep/podcast-development-program    # type: url # max: none
- out:  demdex.net    # type: url # max: none
- out:  omtrdc.net    # type: url # max: none
- out:  adobedtm.com    # type: url # max: none
- out:  All help centers across marketplaces    # type: other # max: none
- out:  All Audible blogs across marketplaces    # type: other # max: none
- out:  Affiliate Programs    # type: other # max: none
- out:  https://www.audible.ca/blog/en    # type: url # max: none
- out:  help.audible.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $134,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
