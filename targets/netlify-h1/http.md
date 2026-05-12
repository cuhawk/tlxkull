# Netlify

> Platform: HackerOne — https://hackerone.com/netlify
> Type: BBP
> Bounty: Low $200 | Medium $500 | High $2,500 | Critical $6,000
> Avg bounty: $200–$250
> Response efficiency: 66% | Avg first response: N/A | Total paid: $198,879
> Last scope update: 2023-03-22

## Scope

- in:  *.services.netlify.com    # type: wildcard # max: critical
- in:  *.services-prod.nsvcs.net    # type: wildcard # max: critical
- in:  *.infra-prod.nsvcs.net    # type: wildcard # max: critical
- in:  *.ops.netlify.com    # type: wildcard # max: critical
- in:  *.onegraph.com    # type: wildcard # max: high
- in:  app.netlify.com    # type: url # max: critical
- in:  api.netlify.com    # type: url # max: critical
- in:  internal.netlify.com    # type: url # max: critical
- in:  netlify-cdp-loader.netlify.app    # type: url # max: critical
- in:  screenshot-proxy.netlify.app    # type: url # max: medium
- in:  netlify-rum.netlify.app    # type: url # max: medium
- in:  list-v2--netlify-plugins.netlify.app    # type: url # max: medium
- in:  internal-docs.netlify.com    # type: url # max: medium
- in:  supportal.netlify.app    # type: url # max: medium
- in:  www.netlifycms.org    # type: url # max: low # not eligible for bounty
- out:  *.netlify.app    # type: wildcard # max: none
- out:  *.netlify.com    # type: wildcard # max: none
- out:  *.netlifycms.org    # type: wildcard # max: none
- out:  www.netlify.com    # type: url # max: none
- out:  webpop.com    # type: url # max: none
- out:  docs.netlify.com    # type: url # max: none
- out:  answers.netlify.com    # type: url # max: none
- out:  https://github.com/netlify/    # type: url # max: none
- out:  Netlify customers     # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $198,879
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
