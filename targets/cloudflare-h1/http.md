# Cloudflare Public Bug Bounty

> Platform: HackerOne — https://hackerone.com/cloudflare
> Type: BBP
> Bounty: Low $500 | Medium $750 | High $3,000 | Critical $10,000
> Avg bounty: $250–$350
> Response efficiency: 81% | Avg first response: N/A | Total paid: $512,225
> Last scope update: 2024-10-04

## Scope

- in:  dash.cloudflare.com    # type: url # max: critical
- in:  cloudflareworkers.com    # type: url # max: critical
- in:  *.teams.cloudflare.com    # type: url # max: critical
- in:  api.cloudflare.com    # type: url # max: critical
- in:  *.cloudflare.com    # type: url # max: critical
- in:  http://github.com/cloudflare    # type: url # max: critical
- in:  one.dash.cloudflare.com    # type: url # max: critical
- in:  waf.cumulusfire.net    # type: url # max: medium
- in:  https://github.com/cloudflare/workerd    # type: repo # max: critical
- in:  https://github.com/cloudflare/vinext    # type: repo # max: critical
- in:  Cloudflare Pages    # type: other # max: critical
- in:  CDNJS    # type: other # max: critical
- in:  WARP Mobile Apps    # type: other # max: critical
- in:  Cloudflare Access    # type: other # max: critical
- in:  Stream    # type: other # max: critical
- in:  1.1.1.1 Resolver    # type: other # max: critical
- in:  Magic Transit    # type: other # max: critical
- in:  Spectrum    # type: other # max: critical
- in:  Load Balancing    # type: other # max: critical
- in:  Bot Management    # type: other # max: critical
- in:  Cloudflare Zero Trust/Cloudflare One    # type: other # max: critical
- in:  Open source tools from Cloudflare    # type: other # max: critical
- in:  Area 1    # type: other # max: critical
- in:  Cloudflare D1    # type: other # max: critical
- in:  Cloudflare R2    # type: other # max: critical
- in:  WARP desktop client    # type: other # max: critical
- in:  *.cloudflarepartners.com    # type: other # max: critical
- in:  Cloudflare DNS    # type: other # max: critical
- in:  Cloudflare CASB    # type: other # max: critical
- in:  Workers    # type: other # max: critical
- in:  Cloudflare Tunnel    # type: other # max: critical
- in:  AMP Real URL    # type: other # max: critical
- in:  Cloudflare Cache     # type: other # max: critical
- in:  Magic Firewall    # type: other # max: critical
- in:  Cloudflare Zaraz    # type: other # max: critical
- in:  China Network    # type: other # max: critical
- in:  API Shield    # type: other # max: critical
- in:  Gateway    # type: other # max: critical
- in:  Browser Isolation    # type: other # max: critical
- in:  AI Gateway    # type: other # max: critical
- in:  Vectorize    # type: other # max: critical
- in:  Hyperdrive    # type: other # max: critical
- in:  Workers KV    # type: other # max: critical
- in:  Cloudflare Analytics    # type: other # max: critical
- in:  Cloudflare Durable Objects    # type: other # max: critical
- in:  Turnstile    # type: other # max: critical
- in:  Waiting Room    # type: other # max: critical
- in:  Magic WAN    # type: other # max: critical
- in:  Data Loss Prevention (DLP)    # type: other # max: critical
- in:  SSL/TLS    # type: other # max: critical
- in:  Cloudflare Workers CI    # type: other # max: critical
- in:  Images    # type: other # max: none
- in:  Workers AI    # type: other # max: critical
- in:  Durable Objects    # type: other # max: none
- in:  Argo Tunnel    # type: other # max: critical
- in:  dash.teams.cloudflare.com    # type: url # max: critical
- in:  http://cloudflare.com/apps/    # type: url # max: critical
- out:  support.cloudflare.com    # type: url # max: none
- out:  community.cloudflare.com    # type: url # max: none
- out:  support.cloudflarewarp.com    # type: url # max: none
- out:  events.www.cloudflare.com    # type: url # max: none
- out:  https://github.com/cloudflare/vinext-private    # type: repo # max: none
- out:  172.65.0.0/16     # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $512,225
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
