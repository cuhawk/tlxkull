# LATAM Airlines

> Platform: HackerOne — https://hackerone.com/latamairlines
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 89% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2024-10-28

## Scope

- in:  http://*.appslatam.com    # type: wildcard # max: critical # not eligible for bounty
- in:  http://*.latamairlines.com    # type: wildcard # max: critical # not eligible for bounty
- in:  http://*.lanchile.cl    # type: wildcard # max: critical # not eligible for bounty
- in:  http://*.lanchile.com    # type: wildcard # max: critical # not eligible for bounty
- in:  http://*.latam.com    # type: wildcard # max: critical # not eligible for bounty
- in:  http://*.lan.com    # type: wildcard # max: critical # not eligible for bounty
- in:  http://*.latampass.cl    # type: wildcard # max: critical # not eligible for bounty
- in:  http://*.latampass.com    # type: wildcard # max: critical # not eligible for bounty
- in:  https://nimbus2.appslatam.com    # type: url # max: critical # not eligible for bounty
- in:  http://prs.appslatam.com    # type: url # max: critical # not eligible for bounty
- in:  https://srtlatam.appslatam.com/    # type: url # max: critical # not eligible for bounty
- in:  https://lataminit.appslatam.com/    # type: url # max: critical # not eligible for bounty
- in:  https://amelia.appslatam.com    # type: url # max: critical # not eligible for bounty
- in:  https://portal.api.latampass.com/    # type: url # max: critical # not eligible for bounty
- in:  https://autoemb.appslatam.com/    # type: url # max: critical # not eligible for bounty
- in:  airtalk.appslatam.com    # type: url # max: critical # not eligible for bounty
- in:  https://passelivre.intg.appslatam.com    # type: url # max: critical # not eligible for bounty
- in:  https://pci-xp-bff-audit.st.latamairlines.com    # type: url # max: critical # not eligible for bounty
- in:  https://qa.latampass.com/    # type: url # max: critical # not eligible for bounty
- in:  https://latampass.com/facilidades/compra-milhas/lp?pt=pp    # type: url # max: critical # not eligible for bounty
- in:  https://passplay.intg.appslatam.com    # type: url # max: critical # not eligible for bounty
- in:  https://partnerportal.intg.appslatam.com/    # type: url # max: critical # not eligible for bounty
- in:  https://beta.latampass.latam.com/    # type: url # max: critical # not eligible for bounty
- in:  https://skills-manager.dev.appslatam.com    # type: url # max: critical # not eligible for bounty
- in:  https://latamvideos.appslatam.com    # type: url # max: high # not eligible for bounty
- in:  https://partnercenter.intg.appslatam.com/    # type: url # max: high # not eligible for bounty
- in:  https://gte.appslatam.com    # type: url # max: high # not eligible for bounty
- in:  https://recognizeme.appslatam.com/    # type: url # max: high # not eligible for bounty
- in:  https://wtm.intg.appslatam.com    # type: url # max: high # not eligible for bounty
- in:  https://mtxgreen.lan.com    # type: url # max: critical # not eligible for bounty
- out:  http://dcci.latam.com    # type: url # max: none
- out:  https://dcci.latam.com    # type: url # max: none
- out:  https://dc-stage.latam.com    # type: url # max: none
- out:  https://dc-cert.latam.com    # type: url # max: none
- out:  https://dcci-cert.latam.com    # type: url # max: none
- out:  https://dcci-stage.latam.com    # type: url # max: none
- out:  http://dcci-stage.latam.com/    # type: url # max: none
- out:  http://dc-cert.latam.com    # type: url # max: none
- out:  https://www.latamcargo.com/    # type: url # max: none
- out:  http://*.latamcargo.com    # type: wildcard # max: none
- out:  lancargo.com    # type: url # max: none
- out:  https://flightwatch.lancargo.com/flightwatchweb-2.0/login.jsf    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
