# Early Warning

> Platform: HackerOne — https://hackerone.com/early_warning
> Type: BBP
> Bounty: Low $500 | Medium $2,000 | High $6,000 | Critical $12,000
> Avg bounty: $300–$300
> Response efficiency: 99% | Avg first response: N/A | Total paid: $111,104
> Last scope update: 2026-03-05

## Scope

- in:  *.zellepay.com    # type: wildcard # max: critical
- in:  *.earlywarning.com    # type: wildcard # max: critical
- in:  developer*.earlywarning.com    # type: wildcard # max: critical
- in:  support*.earlywarning.com    # type: wildcard # max: critical
- in:  *.zelle.com    # type: wildcard # max: critical
- in:  zelleservice.my.site.com    # type: url # max: critical
- in:  ews-fusion.my.site.com    # type: url # max: critical
- in:  zelleservice.my.salesforce.com    # type: url # max: critical
- in:  www.certos.com    # type: url # max: critical
- in:  com.zellepay.zelle    # type: android_app # max: critical
- in:  com.zellepay.zelle    # type: ios_app # max: critical
- in:  api.zellepay.com    # type: url # max: critical
- in:  api.zmsp.earlywarning.com    # type: url # max: critical
- in:  earlywarningapi.force.com    # type: url # max: critical
- in:  https://mywallet-management-west.wallet.cat.earlywarning.io/    # type: url # max: critical
- in:  https://mywallet-management-east.wallet.cat.earlywarning.io/    # type: url # max: critical
- in:  https://sandbox.digitalwallet.earlywarning.com    # type: url # max: critical
- in:  *.paze.com    # type: wildcard # max: critical
- in:  stage.paze.com    # type: url # max: critical
- in:  dev.paze.com    # type: url # max: critical
- in:  qa.paze.com    # type: url # max: critical
- in:  edit-stage.paze.com    # type: url # max: critical
- in:  edit-qa.paze.com    # type: url # max: critical
- in:  edit-dev.paze.com    # type: url # max: critical
- in:  partners.zellepay.com    # type: url # max: critical
- in:  register.zellepay.com    # type: url # max: critical
- in:  accountinfo.earlywarning.com    # type: url # max: critical
- in:  identitychek.earlywarning.com    # type: url # max: critical
- in:  identitychekxml.earlywarning.com    # type: url # max: critical
- in:  aoa-ws.earlywarning.com    # type: url # max: critical
- in:  sa*.earlywarning.com    # type: wildcard # max: critical
- in:  www.zellepay.com    # type: url # max: critical
- in:  *.authentify.net    # type: wildcard # max: critical
- in:  authtrans.zellepay.com    # type: url # max: critical
- out:  *.clearxchange.com    # type: wildcard # max: none
- out:  api.zmsp.*.earlywarning.io    # type: wildcard # max: none
- out:  *bc.earlywarning.com    # type: wildcard # max: none
- out:  ccpa*.zellepay.com    # type: wildcard # max: none
- out:  toolkit.zellepay.com    # type: url # max: none
- out:  ccpa.zellepay.com    # type: url # max: none
- out:  zellepay.earlywarning.com    # type: url # max: none
- out:  platformtest.cat.earlywarning.io    # type: url # max: none
- out:  zellepay.force.com    # type: url # max: none
- out:  http://api.zellepay.com    # type: url # max: none
- out:  http://api.zmsp.earlywarning.com    # type: url # max: none
- out:  http://earlywarningapi.force.com    # type: url # max: none
- out:  platform.cat.earlywarning.io    # type: url # max: none
- out:  docs.earlywarning.com    # type: url # max: none
- out:  demo.earlywarning.com    # type: url # max: none
- out:  flip0717.earlywarning.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $111,104
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
