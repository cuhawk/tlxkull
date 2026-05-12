# X / xAI

> Platform: HackerOne — https://hackerone.com/x
> Type: BBP
> Bounty: Low $500 | Medium $2,000 | High $7,000 | Critical $20,000
> Avg bounty: $560–$560
> Response efficiency: 95% | Avg first response: N/A | Total paid: $1,806,255
> Last scope update: 2025-05-15

## Scope

- in:  *.twitter.com    # type: wildcard # max: critical
- in:  *.vine.co    # type: wildcard # max: critical
- in:  *.twimg.com    # type: wildcard # max: critical
- in:  *.x.ai    # type: wildcard # max: critical
- in:  *.x.com    # type: wildcard # max: critical
- in:  *.grok.com    # type: wildcard # max: critical
- in:  *.twitter.biz    # type: wildcard # max: critical
- in:  gnip.com    # type: url # max: critical
- in:  x.com    # type: url # max: critical
- in:  grok.com    # type: url # max: critical
- in:  chat.x.com    # type: url # max: critical
- in:  grokipedia.com    # type: url # max: critical
- in:  money.x.com    # type: url # max: critical
- in:  com.twitter.android    # type: android_app # max: critical
- in:  ai.x.grok    # type: android_app # max: critical
- in:  com.atebits.Tweetie2    # type: ios_app # max: critical
- in:  ai.x.GrokApp    # type: ios_app # max: critical
- in:  t.co    # type: url # max: medium # not eligible for bounty
- in:  xadsacademy.com    # type: url # max: medium # not eligible for bounty
- in:  api.x.ai    # type: url # max: critical
- in:  grok.x.ai    # type: url # max: critical
- in:  ide.x.ai    # type: url # max: critical
- in:  accounts.x.ai    # type: url # max: critical
- in:  console.x.ai    # type: url # max: critical
- in:  twitterflightschool.com    # type: url # max: medium # not eligible for bounty
- in:  snappytv.com    # type: url # max: critical # not eligible for bounty
- in:  niche.co    # type: url # max: critical # not eligible for bounty
- in:  mopub.com    # type: url # max: critical
- in:  vine.co    # type: url # max: critical
- out:  status.twitter.com    # type: url # max: none
- out:  *.getrevue.co    # type: wildcard # max: none
- out:  *.pscp.tv    # type: wildcard # max: none
- out:  *.periscope.tv    # type: wildcard # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $1,806,255
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
