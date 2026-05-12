# Payoneer

> Platform: HackerOne — https://hackerone.com/payoneer
> Type: BBP
> Bounty: Low $100 | Medium $750 | High $2,000 | Critical $5,000
> Avg bounty: $750–$750
> Response efficiency: 83% | Avg first response: N/A | Total paid: $165,700
> Last scope update: 2021-11-15

## Scope

- in:  *.payoneer.com    # type: url # max: critical
- in:  payoneer.com.cn    # type: url # max: critical
- in:  http://greenchannel.payoneer.com.cn/gcportal    # type: url # max: critical
- in:  myaccount-cn.payoneer.com    # type: url # max: critical
- in:  myaccount.payoneer.com    # type: url # max: critical
- out:  blog.payoneer.com    # type: url # max: none
- out:  community.payoneer.com    # type: url # max: none
- out:  affiliates.payoneer.com    # type: url # max: none
- out:  tracks.payoneer.com    # type: url # max: none
- out:  explore.payoneer.com    # type: url # max: none
- out:  register.payoneer.com    # type: url # max: none
- out:  duediligence.payoneer.com    # type: url # max: none
- out:  skuad.io    # type: url # max: none
- out:  brand.payoneer.com    # type: url # max: none
- out:  investorday.payoneer.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $165,700
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
