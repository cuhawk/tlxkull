# Chaturbate

> Platform: HackerOne — https://hackerone.com/chaturbate
> Type: BBP
> Bounty: Low $150 | Medium $400 | High $1,000 | Critical $3,000
> Avg bounty: $250–$400
> Response efficiency: 97% | Avg first response: N/A | Total paid: $244,899
> Last scope update: 2024-03-01

## Scope

- in:  *.highwebmedia.com    # type: wildcard # max: critical
- in:  *.securegatewayaccess.com    # type: wildcard # max: critical
- in:  *.mmcdn.com    # type: wildcard # max: critical
- in:  *.cb.dev    # type: wildcard # max: critical
- in:  *.mmwebc.dev    # type: wildcard # max: critical
- in:  chaturbate.com    # type: url # max: critical
- in:  m.chaturbate.com    # type: url # max: critical
- in:  billingsupport.chaturbate.com    # type: url # max: critical
- in:  secure.chaturbate.com    # type: url # max: critical
- in:  Blossm Media, LLC transfer scope    # type: other # max: none
- in:  Peach transfer scope    # type: other # max: none
- in:  cb.dev    # type: url # max: critical
- in:  blog.chaturbate.com    # type: url # max: critical
- out:  support.chaturbate.com    # type: url # max: none
- out:  status.chaturbate.com    # type: url # max: none
- out:  cbswag.com    # type: url # max: none
- out:  *.caturbate.com    # type: wildcard # max: none
- out:  archiveblog.chaturbate.com    # type: url # max: none
- out:  testbed.chaturbate.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $244,899
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
