# GoCardless Bug Bounty Program

> Platform: HackerOne — https://hackerone.com/gocardless_bbp
> Type: BBP
> Bounty: Low $50–$150 | Medium $300–$500 | High $1,000 | Critical $2,500
> Avg bounty: $150–$300
> Response efficiency: 93% | Avg first response: N/A | Total paid: $39,255
> Last scope update: 2026-05-06

## Scope

- in:  *.gocardless.io,*.gocardless-banking.io    # type: wildcard # max: high
- in:  *.gocardless-cicd.io    # type: wildcard # max: medium
- in:  *.gocardless.com    # type: wildcard # max: medium
- in:  manage-sandbox.gocardless.com    # type: url # max: critical
- in:  pay-sandbox.gocardless.com    # type: url # max: critical
- in:  api-sandbox.gocardless.com    # type: url # max: critical
- in:  connect-sandbox.gocardless.com    # type: url # max: high
- in:  oauth-sandbox.gocardless.com    # type: url # max: high
- in:  payer-details-sandbox.gocardless.com    # type: url # max: high
- in:  www.gocardless.com    # type: url # max: medium
- in:  ob.gocardless.com    # type: url # max: medium
- in:  auth0.gocardless.com    # type: url # max: medium
- in:  bankaccountdata.gocardless.com    # type: other # max: high
- in:  https://ob-sandbox.gocardless.io    # type: api # max: medium
- in:  *.gocardless-staging.io    # type: wildcard # max: medium # not eligible for bounty
- in:  *.gocardless-lab.io    # type: wildcard # max: low # not eligible for bounty
- in:  *.gocardless.dev    # type: wildcard # max: none # not eligible for bounty
- in:  http://sso-demo.gocardless-staging.io    # type: url # max: low # not eligible for bounty
- in:  bankaccountdata.gocardless.com    # type: url # max: medium
- in:  *.gocardless-staging.io,*.gocardless-lab.io    # type: wildcard # max: low
- in:  http://*.gocardless.com    # type: wildcard # max: medium # not eligible for bounty
- in:  http://xero-sandbox.gocardless.com    # type: url # max: critical
- in:  http://oauth-sandbox.gocardless.com    # type: url # max: critical
- out:  xero-staging.gocardless.com    # type: url # max: none
- out:  api.gocardless.com    # type: url # max: none
- out:  manage.gocardless.com    # type: url # max: none
- out:  connect.gocardless.com    # type: url # max: none
- out:  pay.gocardless.com    # type: url # max: none
- out:  xero.gocardless.com    # type: url # max: none
- out:  learn.gocardless.com    # type: url # max: none
- out:  outgrow.gocardless.com    # type: url # max: none
- out:  privacy.gocardless.com    # type: url # max: none
- out:  brand.gocardless.com    # type: url # max: none
- out:  storybook.gocardless.io    # type: url # max: none
- out:  qbo-api.gocardless.com    # type: url # max: none
- out:  xero-sandbox.gocardless.com    # type: url # max: none
- out:  oauth.gocardless.com    # type: url # max: none
- out:  gc4x-api-sandbox.gocardless.com    # type: url # max: none
- out:  manage.gocardless-staging.io    # type: url # max: none
- out:  api-staging.gocardless.com    # type: url # max: none
- out:  oauth-staging.gocardless.com    # type: url # max: none
- out:  support.gocardless.com    # type: url # max: none
- out:  payer-details.gocardless.com    # type: url # max: none
- out:  gocardless.atlassian.net    # type: url # max: none
- out:  partnerportal.gocardless.com, gocardless.my.site.com    # type: other # max: none
- out:  gocardless-status.com, status.gocardless.com    # type: other # max: none
- out:  qbo.gocardless.com    # type: url # max: none
- out:  nordigen.zendesk.com    # type: url # max: none
- out:  dash.bankaccountdata.gocardless.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $39,255
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
