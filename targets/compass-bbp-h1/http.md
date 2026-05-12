# Compass

> Platform: HackerOne — https://hackerone.com/compass-bbp
> Type: BBP
> Bounty: Low $300 | Medium $800 | High $3,000 | Critical $6,000
> Avg bounty: $300–$500
> Response efficiency: 94% | Avg first response: N/A | Total paid: $127,815
> Last scope update: 2026-04-28

## Scope

- in:  www.compass.com    # type: url # max: critical
- in:  com.compass.compass    # type: android_app # max: critical
- in:  https://apps.apple.com/us/app/compass-real-estate-homes/id692766504    # type: ios_app # max: critical
- out:  *.sothebysrealty.com    # type: wildcard # max: none
- out:  *.realogy.com    # type: wildcard # max: none
- out:  *.nrtllc.com    # type: wildcard # max: none
- out:  *.mycbdesk.com    # type: wildcard # max: none
- out:  *.leadrouter.com    # type: wildcard # max: none
- out:  *.era.com    # type: wildcard # max: none
- out:  *.corcoran.com    # type: wildcard # max: none
- out:  *.coldwellbanker.com    # type: wildcard # max: none
- out:  *.century21global.com    # type: wildcard # max: none
- out:  *.century21.com    # type: wildcard # max: none
- out:  *.cbcworldwide.com    # type: wildcard # max: none
- out:  *.cartus.com    # type: wildcard # max: none
- out:  *.c21.com    # type: wildcard # max: none
- out:  *.bhgre.com    # type: wildcard # max: none
- out:  *.porchlightgroup.com    # type: wildcard # max: none
- out:  *.ctccal.com    # type: wildcard # max: none
- out:  *.chartwellescrow.com    # type: wildcard # max: none
- out:  *.legacytexastitle.com    # type: wildcard # max: none
- out:  *.firstalliancetitle.com    # type: wildcard # max: none
- out:  *.sqstitle.com    # type: wildcard # max: none
- out:  *.attorneyskeytitle.com    # type: wildcard # max: none
- out:  *.kvstitle.com    # type: wildcard # max: none
- out:  *.anywhere.re    # type: wildcard # max: none
- out:  *.trgc.com    # type: wildcard # max: none
- out:  http://www.compass.com/contact/    # type: url # max: none
- out:  http://www.compass.com/api/v3/lead_forms/agent_profile    # type: url # max: none
- out:  century21.hk    # type: url # max: none
- out:  c21.hk    # type: url # max: none
- out:  glide.com    # type: url # max: none
- out:  Christie’s International Real Estate    # type: other # max: none
- out:   @properties    # type: other # max: none
- out:  Consumer’s Title of California     # type: other # max: none
- out:  Chartwell    # type: other # max: none
- out:  LegacyTexas Title    # type: other # max: none
- out:  SQS Square Settlements    # type: other # max: none
- out:  KVS Title     # type: other # max: none
- out:  Glide     # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $127,815
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
