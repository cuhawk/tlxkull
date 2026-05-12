# M-Pesa Africa Limited

> Platform: HackerOne — https://hackerone.com/mpesa
> Type: BBP
> Bounty: Low $250 | Medium $500 | High $1,000 | Critical $3,000
> Avg bounty: $250–$500
> Response efficiency: 93% | Avg first response: N/A | Total paid: $18,250
> Last scope update: 2024-02-09

## Scope

- in:  *.m-pesa.com    # type: wildcard # max: critical
- in:  mpa.ekyc.backoffice.m-pesa.com    # type: url # max: critical
- in:  mpa.ekyc.selfregister.m-pesa.com    # type: url # max: critical
- in:  openapiportal.m-pesa.com    # type: url # max: critical
- in:  openapi.m-pesa.com    # type: url # max: critical
- in:  m-pesa.africa    # type: url # max: critical
- in:  mpa.qr.web.m-pesa.com    # type: other # max: critical
- in:  com.vodafone.mpesa.ls    # type: android_app # max: critical
- in:  com.vodafone.mpesa.mozambique    # type: android_app # max: critical
- in:  com.vodafone.mpesa.drc    # type: android_app # max: critical
- in:  1442121355    # type: ios_app # max: critical
- in:  1502222766    # type: ios_app # max: critical
- in:  https://mpa.ekyc.backoffice.m-pesa.com/    # type: url # max: critical
- in:  com.vodafone.mpesa.drc    # type: url # max: critical
- in:  com.vodafone.mpesa.mozambique    # type: url # max: critical
- out:  sso.m-pesa.vm.co.mz    # type: url # max: none
- out:  sso.pr.m-pesa.vm.co.mz    # type: url # max: none
- out:  business.m-pesa.com    # type: url # max: none
- out:  mz.m-pesa.com    # type: url # max: none
- out:  ra.ls.m-pesa.com    # type: url # max: none
- out:  com.vodacom.mpesa.ls.business    # type: android_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $18,250
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
