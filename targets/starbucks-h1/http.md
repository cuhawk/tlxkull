# Starbucks

> Platform: HackerOne — https://hackerone.com/starbucks
> Type: BBP
> Bounty: Low $100–$200 | Medium $500–$800 | High $1,000–$2,000 | Critical $4,000–$6,000
> Avg bounty: $500–$600
> Response efficiency: 82% | Avg first response: N/A | Total paid: $1,350,000
> Last scope update: 2022-03-30

## Scope

- in:  www.starbucksreserve.com    # type: url # max: critical
- in:  www.starbucks.ca    # type: url # max: critical
- in:  www.starbucks.com    # type: url # max: critical
- in:  app.starbucks.com    # type: url # max: critical
- in:  openapi.starbucks.com    # type: url # max: critical
- in:  secureui.starbucks.com    # type: url # max: critical
- in:  Subdomain Takeover (SDTO)    # type: other # max: critical
- in:  com.starbucks.mobilecard    # type: android_app # max: critical
- in:  com.starbucks.mystarbucks    # type: ios_app # max: critical
- in:  Other assets    # type: other # max: critical # not eligible for bounty
- in:  www.starbucks.co.kr    # type: url # max: critical
- in:  www.starbucks.co.uk    # type: url # max: critical
- in:  www.starbucks.fr    # type: url # max: critical
- in:  www.starbucks.de    # type: url # max: critical
- in:  www.starbucks.com.cn    # type: url # max: critical
- in:  www.starbucks.co.jp    # type: url # max: critical
- in:  login.starbucks.co.jp    # type: url # max: critical
- in:  gift.starbucks.co.jp    # type: url # max: critical
- in:  com.starbucks.br    # type: android_app # max: critical
- in:  com.starbucks.de    # type: android_app # max: critical
- in:  com.starbucks.fr    # type: android_app # max: critical
- in:  com.starbucks.cn    # type: android_app # max: critical
- in:  com.starbucks.jp    # type: android_app # max: critical
- in:  com.starbucks.br    # type: ios_app # max: critical
- in:  com.starbucks.de    # type: ios_app # max: critical
- in:  com.starbucks.fr    # type: ios_app # max: critical
- in:  com.starbuckschina.mystarbucksmoments    # type: ios_app # max: critical
- in:  com.starbucks.jp    # type: ios_app # max: critical
- in:  com.starbucks.mystarbucks.kr    # type: ios_app # max: critical
- in:  com.starbucks.sbuxsingapore    # type: ios_app # max: critical
- in:  www.starbucks.com.sg    # type: url # max: critical
- in:  card.starbucks.com.sg    # type: url # max: critical
- in:  com.starbucks.singapore    # type: android_app # max: critical
- in:  www.starbucks.com.br    # type: url # max: critical
- in:  cart.starbucks.co.jp    # type: url # max: critical
- in:  Information Disclosures    # type: other # max: critical
- in:  Other non domain specific items    # type: other # max: critical
- out:  apply.starbucks.com    # type: url # max: none
- out:  careers.starbucks.com    # type: url # max: none
- out:  lsstar.starbucks.com    # type: url # max: none
- out:  Teavana    # type: other # max: none
- out:  preview.starbucks.com    # type: url # max: none
- out:  ec.starbucks.com.cn    # type: url # max: none
- out:  www.teavana.com    # type: url # max: none
- out:  customerservice.starbucks.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $1,350,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
