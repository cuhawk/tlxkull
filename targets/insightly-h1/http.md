# Insightly

> Platform: HackerOne — https://hackerone.com/insightly
> Type: BBP
> Bounty: Low $50–$100 | Medium $100–$400 | High $500–$1,000 | Critical $750–$3,000
> Avg bounty: $100–$100
> Response efficiency: 75% | Avg first response: N/A | Total paid: $56,025
> Last scope update: 2026-01-21

## Scope

- in:  crm.na1.insightly.com    # type: url # max: critical
- in:  accounts.insightly.com    # type: url # max: critical
- in:  outlook.insightly.com    # type: url # max: critical
- in:  mobileapi.na1.insightly.com    # type: url # max: critical
- in:  http://api.insightly.com/v3.1/    # type: url # max: critical
- in:  login.insightly.com    # type: url # max: critical
- in:  mobileapi.insightly.com    # type: url # max: critical
- in:  http://api.na1.insightly.com/v3.1/    # type: url # max: critical
- in:  marketing.na1.insightly.com    # type: url # max: critical
- in:  app.unbounce.com    # type: url # max: critical
- out:  *.insight.ly    # type: wildcard # max: none
- out:  gmailaddon.insightly.com    # type: url # max: none
- out:  podapi.na1.insightly.com    # type: url # max: none
- out:  chloe.insightly.com    # type: url # max: none
- out:  frontdoorproxy.insightly.com    # type: url # max: none
- out:  webhook.insightly.com    # type: url # max: none
- out:  www.insightly.com    # type: url # max: none
- out:  www.insight.ly    # type: url # max: none
- out:  insightly.com    # type: url # max: none
- out:  insight.ly    # type: url # max: none
- out:  blog.insightly.com    # type: url # max: none
- out:  support.insightly.com    # type: url # max: none
- out:  help.insightly.com    # type: url # max: none
- out:  my.insightly.com    # type: url # max: none
- out:  newsletter.insightly.com    # type: url # max: none
- out:  com.insightly.droid    # type: android_app # max: none
- out:  563017797    # type: ios_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $56,025
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
