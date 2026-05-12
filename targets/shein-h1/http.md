# SHEIN

> Platform: HackerOne — https://hackerone.com/shein
> Type: BBP
> Bounty: Low $100–$200 | Medium $350–$500 | High $750–$1,000 | Critical $2,000
> Avg bounty: $350–$375
> Response efficiency: 88% | Avg first response: N/A | Total paid: $93,924
> Last scope update: 2023-03-30

## Scope

- in:  *.shein.com    # type: wildcard # max: critical
- in:  *.romwe.com    # type: wildcard # max: critical
- in:  *.sheingsp.com    # type: wildcard # max: critical
- in:  com.zzkko    # type: android_app # max: critical
- in:  com.romwe    # type: android_app # max: critical
- in:  878577184    # type: ios_app # max: critical
- in:  1080248000    # type: ios_app # max: critical
- in:  *.shein.in    # type: wildcard # max: critical # not eligible for bounty
- out:  security.shein.com    # type: url # max: none
- out:  1277098572    # type: ios_app # max: none
- out:  com.fun.funmart    # type: android_app # max: none
- out:  link-us.romwe.com    # type: url # max: none
- out:  api.foutlet.com    # type: url # max: none
- out:  *.makemechic.com    # type: wildcard # max: none
- out:  *.dotfashion.cn    # type: wildcard # max: none
- out:  *.emmacloth.com    # type: wildcard # max: none
- out:  *.sheinoutlet.com    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $93,924
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
