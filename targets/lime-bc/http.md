# Lime

> Platform: Bugcrowd — https://bugcrowd.com/engagements/lime
> Type: BBP
> Bounty: P1 $5500–$7000 | P2 $2800–$3500 | P3 $800–$1500 | P4 $300–$450
> Status: In progress

## Scope

- in:  proxy-production.lime.bike   # type: domain
- in:  web-message.lime.bike   # type: domain
- in:  web-message-high.lime.bike   # type: domain
- in:  https://apps.apple.com/ca/app/lime-supply/id1620058457   # type: ios_app
- in:  web-production.lime.bike   # type: domain
- in:  external-api.lime.bike   # type: domain
- in:  Data.lime.bike   # type: domain
- in:  https://apps.apple.com/ca/app/lime-ridegreen/id1199780189   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.limebike   # type: android_app
- in:  https://play.google.com/store/apps/details?id=com.lime.supply&hl=en_US   # type: android_app
- in:  admintool.lime.bike   # type: domain
- in:  juicer.lime.bike   # type: domain
- in:  https://data.limeinternal.com   # type: url
- in:  help.lime.bike   # type: domain
- in:  https://admintool.lime.bike   # type: url
- in:  ops.lime.bike   # type: domain
- in:  https://lp.lime.bike/   # type: url
- in:  https://orchard.limeinternal.com   # type: url
- in:  https://www.li.me/   # type: url
- in:  https://gpt.lime.bike   # type: url
- out: https://help.li.me (Zendesk)   # type: url
- out: *.limeinternal.com   # type: wildcard
- out: *.lime.bike   # type: wildcard
- out: https://li.me (HubSpot)   # type: url

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
