# Quizlet

> Platform: Bugcrowd — https://bugcrowd.com/engagements/quizlet
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  https://*.quizlet.com   # type: url
- in:  https://itunes.apple.com/us/app/quizlet-flashcards/id546473125   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.quizlet.quizletandroid   # type: android_app
- out: api.quizlet.com/2.0   # type: domain
- out: get.quizlet.com   # type: domain
- out: slader.com   # type: domain

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
