# KeyBank

> Platform: HackerOne — https://hackerone.com/keybank
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-10-19

## Scope

- in:  *.key.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.key2businesscard.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.keyapsolutions.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.keybank.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.keydirect.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.keyequipmentfinance.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.laurelroad.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.xuppay-statement-analyzer.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.xuppay.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.xupservicing.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.xupsupport.com    # type: wildcard # max: critical # not eligible for bounty
- in:  com.key.android    # type: android_app # max: critical # not eligible for bounty
- in:  com.keycorp.kmf    # type: android_app # max: critical # not eligible for bounty
- in:  com.key.community.tablet    # type: android_app # max: critical # not eligible for bounty
- in:  com.laurelroad.android    # type: android_app # max: critical # not eligible for bounty
- in:  156.77.0.0/16    # type: cidr # max: critical # not eligible for bounty
- in:  com.keybank.mobile    # type: ios_app # max: critical # not eligible for bounty
- in:  com.keycorp.kmf    # type: ios_app # max: critical # not eligible for bounty
- in:  com.laurelRoad.mobile    # type: ios_app # max: critical # not eligible for bounty
- in:  *.xup-onboarding.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.xuphub.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.key.com    # type: url # max: critical # not eligible for bounty
- in:  *.keybank.com    # type: url # max: critical # not eligible for bounty
- in:  *.laurelroad.com    # type: url # max: critical # not eligible for bounty
- in:  510717503    # type: ios_app # max: critical # not eligible for bounty
- in:  1242358235    # type: ios_app # max: critical # not eligible for bounty
- in:  1090492316    # type: ios_app # max: critical # not eligible for bounty
- in:  479213995    # type: ios_app # max: critical # not eligible for bounty
- in:  *.bolstr.com    # type: url # max: critical # not eligible for bounty
- in:  *.hellowallet.com    # type: url # max: critical # not eligible for bounty
- in:  *.cainbrothers.com    # type: url # max: critical # not eligible for bounty
- in:  com.nclud.hellowallet    # type: android_app # max: critical # not eligible for bounty
- out:  ibxqv*.key.com    # type: url # max: none
- out:  pt*.key.com    # type: url # max: none
- out:  ua*.key.com    # type: url # max: none
- out:  *-uat.laurelroad.com    # type: url # max: none
- out:  *.dev.laurelroad.com    # type: url # max: none
- out:  *-dev.laurelroad.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
