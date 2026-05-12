# AT&T

> Platform: HackerOne — https://hackerone.com/att
> Type: BBP
> Bounty: Low $50 | Medium $400 | High $3,000 | Critical $5,000
> Avg bounty: $300–$400
> Response efficiency: 94% | Avg first response: N/A | Total paid: $6,556,950
> Last scope update: 2026-03-26

## Scope

- in:  Other Assets    # type: other # max: critical
- in:  Please refer to the policy page for scope    # type: other # max: critical
- out:  att.com/acctmgmt/*/stub*/*    # type: wildcard # max: none
- out:  att.com/acctmgmt/*/chunks/*    # type: wildcard # max: none
- out:  *tworks-att.com    # type: wildcard # max: none
- out:  prod-taxexempt.att.com    # type: url # max: none
- out:  projectone.att.com    # type: url # max: none
- out:  c2m-projectone.att.com    # type: url # max: none
- out:  wf-projectone.att.com    # type: url # max: none
- out:  *.sky.com.mx    # type: url # max: none
- out:  accbusinesspricing.att.com    # type: url # max: none
- out:  rcloud.social    # type: url # max: none
- out:  attdashboard.wireless.att.com    # type: url # max: none
- out:  https://clec.att.com/clec/    # type: url # max: none
- out:  attsuppliers.com    # type: url # max: none
- out:  attpurchasing.com    # type: url # max: none
- out:  authkeysmx01.att.com.mx    # type: url # max: none
- out:  https://40.233.66.139    # type: url # max: none
- out:  thedirectvmarketingzone.com    # type: url # max: none
- out:  att.suppliergateway.com    # type: url # max: none
- out:  plasma.att.com    # type: url # max: none
- out:  plasma-coreapi.att.com    # type: url # max: none
- out:  12.0.1.28    # type: other # max: none
- out:  DirecTV Owned Assets    # type: other # max: none
- out:  40.233.66.139    # type: ip_address # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $6,556,950
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
