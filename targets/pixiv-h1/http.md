# pixiv

> Platform: HackerOne — https://hackerone.com/pixiv
> Type: BBP
> Bounty: Low $200 | Medium $500 | High $3,000 | Critical $7,500
> Avg bounty: $200–$500
> Response efficiency: 79% | Avg first response: N/A | Total paid: $146,521
> Last scope update: 2026-03-08

## Scope

- in:  *.fanbox.cc    # type: wildcard # max: critical
- in:  booth.pm    # type: url # max: critical
- in:  comic.pixiv.net    # type: url # max: critical
- in:  sketch.pixiv.net    # type: url # max: critical
- in:  sensei.pixiv.net    # type: url # max: critical
- in:  accounts.pixiv.net    # type: url # max: critical
- in:  www.pixiv.net    # type: url # max: critical
- in:  hub.vroid.com    # type: url # max: critical
- in:  dic.pixiv.net    # type: url # max: critical
- in:  vroid.com    # type: url # max: critical
- in:  payment.pixiv.net    # type: url # max: critical
- in:  neoket.net    # type: url # max: critical
- in:  novel.pixiv.net    # type: url # max: critical
- in:  https://vroid.com/studio    # type: url # max: critical
- in:  coban.pixiv.net    # type: url # max: critical
- in:  pastela.app    # type: url # max: critical
- in:  comic-indies.pixiv.net    # type: url # max: critical
- in:  premium.pixiv.net    # type: url # max: critical
- in:  https://github.com/pixiv/charcoal    # type: repo # max: critical
- in:  net.pixiv.serval    # type: ios_app # max: critical
- in:  jp.pxv.pay    # type: android_app # max: critical
- in:  chatstory.pixiv.net    # type: url # max: high
- in:  1261274472    # type: ios_app # max: critical
- in:  *.pixiv.net    # type: wildcard # max: critical
- in:  pixiv.me    # type: url # max: critical
- in:  pay.pixiv.net    # type: url # max: critical
- in:  chatstory.pixiv.net    # type: url # max: critical
- in:  factory.pixiv.net    # type: url # max: critical
- in:  www.pixiv.net    # type: url # max: critical
- out:  *.pixiv.co.jp    # type: wildcard # max: none
- out:  factory.pixiv.net    # type: url # max: none
- out:  ads.pixiv.net    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $146,521
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
