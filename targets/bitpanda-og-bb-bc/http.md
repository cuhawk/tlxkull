# Bitpanda Ongoing Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/bitpanda-og-bb
> Type: BBP
> Bounty: P1 $4000–$15000 | P2 $1200–$4000 | P3 $500–$1200 | P4 $200–$500
> Status: In progress

## Scope

- in:  https://web.bitpanda.com   # type: url
- in:  https://www.bitpanda.com   # type: url
- in:  https://www.bitpanda.com/   # type: url
- in:  https://api.bitpanda.com   # type: url
- in:  wss://socket.bitpanda.com   # type: domain
- in:  https://account.bitpanda.com   # type: url
- in:  https://play.google.com/store/apps/details?id=com.bitpanda.bitpanda   # type: android_app
- in:  https://apps.apple.com/app/bitpanda-buy-bitcoin-crypto/id1449018960   # type: ios_app
- in:  https://blog.bitpanda.com   # type: url
- in:  https://blog.bitpanda.com/en   # type: url
- in:  https://www.bitpanda.com/academy/   # type: url
- in:  https://www.bitpanda.com/academy/en/   # type: url
- out: https://support.bitpanda.com   # type: url
- out: https://maintenance.bitpanda.com   # type: url
- out: https://beta.bitpanda.com   # type: url
- out: https://developers.bitpanda.com   # type: url
- out: http://partners.whitelabel.bitpanda.com/   # type: url
- out: http://status.bitpanda.com   # type: url
- out: https://requests.bitpanda.com   # type: url
- out: https://*.exchange.bitpanda.com   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
