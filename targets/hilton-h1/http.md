# Hilton

> Platform: HackerOne — https://hackerone.com/hilton
> Type: BBP
> Bounty: Low $75 | Medium $300 | High $3,000 | Critical $6,000
> Avg bounty: $100–$300
> Response efficiency: 96% | Avg first response: N/A | Total paid: $272,700
> Last scope update: 2025-10-10

## Scope

- in:  *.hilton.com    # type: wildcard # max: critical
- in:  *.hilton.io    # type: wildcard # max: critical
- in:  *.hiltonbusinessonline.com    # type: wildcard # max: critical
- in:  *.hiltonlocalbiz.com    # type: wildcard # max: critical
- in:  hilton.com    # type: url # max: critical
- in:  hilton.io    # type: url # max: critical
- in:  hiltonbusinessonline.com    # type: url # max: critical
- in:  hiltonlocalbiz.com    # type: url # max: critical
- in:  167.187.0.0/16    # type: cidr # max: critical
- in:  192.251.123.0/24    # type: cidr # max: critical
- in:  192.251.124.0/24    # type: cidr # max: critical
- in:  192.251.125.0/24    # type: cidr # max: critical
- in:  192.251.126.0/24    # type: cidr # max: critical
- in:  82.196.42.196/28    # type: cidr # max: critical
- in:  203.79.37.2/29    # type: cidr # max: critical
- in:  62.216.152.46/29    # type: cidr # max: critical
- in:  121.200.237.36/29    # type: cidr # max: critical
- in:  hiltonhotels.jp    # type: url # max: critical
- in:  hilton.com.tr    # type: url # max: critical
- in:  *.hilton.com.tr    # type: wildcard # max: critical
- in:  hiltonmanage.com    # type: url # max: critical
- in:  *.hiltonmanage.com    # type: wildcard # max: critical
- in:  hiltonhawaiianvillage.jp    # type: url # max: critical
- in:  hiltonjapan.co.jp    # type: url # max: critical
- in:  *.hiltonjapan.co.jp    # type: wildcard # max: critical
- in:  hiltonwedding.jp    # type: url # max: critical # not eligible for bounty
- in:  hilton.com.cn    # type: url # max: critical # not eligible for bounty
- in:  waldorfastoria.hilton.co.kr    # type: url # max: critical # not eligible for bounty
- in:  http://192.251.123.0/24    # type: url # max: critical
- out:  *.hiltonhotels.jp    # type: wildcard # max: none
- out:  https://jobs.hilton.com    # type: url # max: none
- out:  hiltongrandvacations.com    # type: url # max: none
- out:  hiltonnet.hilton.com    # type: url # max: none
- out:  onqinsider.hilton.com    # type: url # max: none
- out:  pim.hilton.com    # type: url # max: none
- out:  eis.hilton.com    # type: url # max: none
- out:  guestfeedback.hilton.com    # type: url # max: none
- out:  hgv.com    # type: url # max: none
- out:  hiltonfoundation.org    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $272,700
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
