# 23andMe Bug Bounty

> Platform: HackerOne — https://hackerone.com/23andme_bbp
> Type: BBP
> Bounty: Low $200–$350 | Medium $400–$1,000 | High $750–$3,500 | Critical $1,000–$5,500
> Avg bounty: $125–$250
> Response efficiency: 100% | Avg first response: N/A | Total paid: $18,618
> Last scope update: 2026-04-15

## Scope

- in:  api.23andme.com    # type: url # max: critical
- in:  auth.23andme.com    # type: url # max: critical
- in:  blog.23andme.com    # type: url # max: critical
- in:  education.23andme.com    # type: url # max: critical
- in:  mediacenter.23andme.com    # type: url # max: critical
- in:  medical.23andme.com    # type: url # max: critical
- in:  store.23andme.com    # type: url # max: critical
- in:  you.23andme.com    # type: url # max: critical
- in:  www.23andme.com    # type: url # max: critical
- in:  merch.23andme.com    # type: url # max: critical
- in:  portal.23andme.com    # type: url # max: critical
- in:  style.23andme.com    # type: url # max: critical
- in:  fulfillment.23andme.com    # type: url # max: critical
- in:  discover.23andme.com    # type: url # max: critical
- in:  trust.23andme.com    # type: url # max: critical
- in:  23andmeresearchinstitute.org    # type: url # max: critical
- in:  refer.23andme.com    # type: url # max: critical
- in:  research.23andme.com    # type: url # max: medium
- in:  therapeutics.23andme.com    # type: url # max: critical
- in:  clinic.lemonaidhealth.com    # type: url # max: critical
- in:  sapi-live.lh.us-west-2.prd.23andme.us    # type: url # max: critical
- in:  pd-api.polkadoc.com    # type: url # max: critical
- in:  healthaid.lemonaidhealth.com    # type: url # max: critical
- in:  lemonaidhealth.com    # type: url # max: critical
- in:  *.lemonaidhealth.com    # type: wildcard # max: critical
- in:  *.lemonaid.com    # type: wildcard # max: critical
- in:  www.lemonaidhealth.com    # type: url # max: critical
- in:  Secondary-Targets    # type: other # max: medium
- in:  Primary-Targets    # type: other # max: critical
- in:  Tier 1     # type: other # max: critical

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $18,618
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
