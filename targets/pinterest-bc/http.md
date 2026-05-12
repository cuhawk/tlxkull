# Pinterest

> Platform: Bugcrowd — https://bugcrowd.com/engagements/pinterest
> Type: BBP
> Bounty: P1 $10000–$25000 | P2 $5000–$8000 | P3 $1000–$3000 | P4 $200–$500
> Status: In progress

## Scope

- in:  https://api.pinterest.com   # type: url
- in:  *.pinterest.com Web Apps   # type: wildcard
- in:  https://apps.apple.com/us/app/pinterest/id429047995   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.pinterest&hl=en_US&gl=US   # type: android_app
- in:  https://play.google.com/store/apps/details?id=com.pinterest.twa&hl=en_US&gl=US   # type: android_app
- in:  https://chrome.google.com/webstore/detail/pinterest-save-button/gpdjojdkbbmdfjfahjcgigfpmkopogic   # type: url
- in:  https://microsoftedge.microsoft.com/addons/detail/pinterest-save-button/bkgoflemacdadndiohhdnphcmdhacabg   # type: url
- in:  https://addons.mozilla.org/en-US/firefox/addon/pinterest/   # type: url
- in:  https://apps.apple.com/us/app/save-to-pinterest/id6473649042   # type: ios_app
- in:  https://github.com/pinterest/   # type: url
- in:  https://www.shffls.com   # type: url
- in:  https://play.google.com/store/apps/details?id=com.pinterest.shuffles   # type: android_app
- in:  https://apps.apple.com/us/app/shuffles-by-pinterest/id1573869498   # type: ios_app

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
