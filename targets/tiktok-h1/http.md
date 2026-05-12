# TikTok

> Platform: HackerOne — https://hackerone.com/tiktok
> Type: BBP
> Bounty: Low $500 | Medium $4,500 | High $10,000 | Critical $15,000
> Avg bounty: $679–$1,000
> Response efficiency: 96% | Avg first response: N/A | Total paid: $3,700,776
> Last scope update: 2026-03-13

## Scope

- in:  *.pipopay.com    # type: wildcard # max: critical
- in:  *.tiktokpublishers.com    # type: wildcard # max: critical
- in:  *.tiktokcdn.com    # type: wildcard # max: critical
- in:  *.tiktok.com    # type: url # max: critical
- in:  business.tiktok.com    # type: url # max: critical
- in:  ads.tiktok.com    # type: url # max: critical
- in:  tiktok.com    # type: url # max: critical
- in:  careers.tiktok.com    # type: url # max: critical
- in:  creatormarketplace.tiktok.com    # type: url # max: critical
- in:  *.tiktokv.com    # type: url # max: critical
- in:  developers.tiktok.com    # type: url # max: critical
- in:  effecthouse.tiktok.com    # type: url # max: critical
- in:  partner.tiktokshop.com    # type: url # max: critical
- in:  shop.tiktok.com    # type: url # max: critical
- in:  live-backstage.tiktok.com    # type: url # max: critical
- in:  academy-outbound-ads.tiktok.com    # type: url # max: critical
- in:  www.pangleglobal.com    # type: url # max: critical
- in:  fp-sg.tiktokv.com    # type: url # max: critical
- in:  affiliate-id.tokopedia.com    # type: url # max: critical
- in:  seller-id.tokopedia.com    # type: url # max: critical
- in:  shop-id.tokopedia.com    # type: url # max: critical
- in:  pay.tokopediax.com    # type: url # max: critical
- in:  lemon8-api.tiktokv.us    # type: url # max: critical
- in:  starling-ttp.lemon8-app.us    # type: url # max: critical
- in:  platform.tiktokpangle.us    # type: url # max: critical
- in:  pangle-mediation-ttp.tiktokpangle.us    # type: url # max: critical
- in:  www.soundonw.us    # type: url # max: critical
- in:  tiktokdata-us-open.tiktokw.us    # type: url # max: critical
- in:  Other Asset (Campaigns)    # type: other # max: critical
- in:  com.zhiliaoapp.musically    # type: android_app # max: critical
- in:  com.ss.android.ugc.trill    # type: android_app # max: critical
- in:  com.ss.android.ugc.now    # type: android_app # max: critical
- in:  com.tiktok.tv    # type: android_app # max: critical
- in:  com.zhiliao.musically.livewallpaper    # type: android_app # max: critical
- in:  com.tiktokshop.seller    # type: android_app # max: critical
- in:  835599320    # type: ios_app # max: critical
- in:  1235601864    # type: ios_app # max: critical
- in:  641062073    # type: ios_app # max: critical
- in:  1591003012    # type: ios_app # max: critical
- in:  feed.capcutapi.us    # type: url # max: critical
- in:  editor.capcutapi.us    # type: url # max: critical
- in:  *.trae.ai    # type: wildcard # max: critical
- in:  TRAE MacOS Desktop App    # type: downloadable_executables # max: critical
- in:  Trae Windows Desktop App    # type: downloadable_executables # max: critical
- in:  TRAE Windows Desktop App    # type: downloadable_executables # max: critical
- in:  tiktokcdn.com    # type: url # max: critical
- in:  seller-*.tiktok.com    # type: wildcard # max: critical
- in:  1641062073    # type: ios_app # max: critical
- in:  datahub.tiktok.com    # type: url # max: critical
- in:  ads.tiktok.com    # type: url # max: critical
- in:  com.ss.android.ugc.trill    # type: other_apk # max: critical
- out:  https://developers.tiktok.com/minis/    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $3,700,776
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
