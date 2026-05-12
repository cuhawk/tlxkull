# Mintel

> Platform: HackerOne — https://hackerone.com/mintel
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 89% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  *.mintel.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.mintel.cloud    # type: wildcard # max: critical # not eligible for bounty
- in:  *.gnpd.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.comperemedia.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.mintel.co.uk    # type: wildcard # max: critical # not eligible for bounty
- in:  https://clients.mintel.com    # type: url # max: critical # not eligible for bounty
- in:  https://cms.mintel.com/    # type: url # max: critical # not eligible for bounty
- in:  https://www.comperemedia.com    # type: url # max: critical # not eligible for bounty
- in:  https://omni.comperemedia.com/    # type: url # max: critical # not eligible for bounty
- in:  https://data.mintel.com    # type: url # max: critical # not eligible for bounty
- in:  https://api.mintel.com    # type: url # max: critical # not eligible for bounty
- in:  https://cds.mintel.com/    # type: url # max: critical # not eligible for bounty
- in:  https://portal.mintel.com/    # type: url # max: critical # not eligible for bounty
- in:  https://www.gnpd.com/    # type: url # max: critical # not eligible for bounty
- in:  https://oauth.mintel.com/    # type: url # max: critical # not eligible for bounty
- in:  https://marketsizes.mintel.com/    # type: url # max: critical # not eligible for bounty
- in:  https://shibboleth.mintel.com    # type: url # max: critical # not eligible for bounty
- in:  https://www.mintel.com/    # type: url # max: critical # not eligible for bounty
- in:  https://internal-auth.mintel.com/    # type: url # max: critical # not eligible for bounty
- in:  https://qa-server-inventory.mintel.com/    # type: url # max: critical # not eligible for bounty
- in:  https://store.mintel.com/    # type: url # max: critical # not eligible for bounty
- in:  https://reports.mintel.com/    # type: url # max: critical # not eligible for bounty
- in:  https://lon-dc-pdf.mintel.com    # type: url # max: critical # not eligible for bounty
- in:  https://lon-dc-ppt.mintel.com    # type: url # max: critical # not eligible for bounty
- in:  https://policy-agent.mintel.com    # type: url # max: critical # not eligible for bounty
- in:  https://whoswho.mintel.com/    # type: url # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
