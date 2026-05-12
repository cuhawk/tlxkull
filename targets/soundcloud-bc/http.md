# SoundCloud

> Platform: Bugcrowd — https://bugcrowd.com/engagements/soundcloud
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  https://play.google.com/store/apps/details?id=com.soundcloud.android&hl=en&gl=US   # type: android_app
- in:  https://soundcloud.com   # type: url
- in:  *.soundcloud.org   # type: wildcard
- in:  *.s-cloud.net   # type: wildcard
- in:  https://apps.apple.com/us/app/soundcloud-music-audio/id336353151   # type: ios_app
- in:  https://connect.soundcloud.com   # type: url
- in:  *.services.repostnetwork.com   # type: wildcard
- in:  api-*.soundcloud.com   # type: domain
- in:  http://artists.soundcloud.com/   # type: url
- in:  https://soundcloud.org   # type: url

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
