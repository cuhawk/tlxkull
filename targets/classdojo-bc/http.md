# ClassDojo

> Platform: Bugcrowd — https://bugcrowd.com/engagements/classdojo
> Type: VDP
> Bounty: P1 $1500–$2500 | P2 $500–$1500 | P3 $50–$500
> Status: In progress

## Scope

- in:  https://apps.apple.com/us/app/classdojo/id552602056   # type: ios_app
- in:  https://api.classdojo.com   # type: url
- in:  https://play.google.com/store/apps/details?id=com.classdojo.android   # type: android_app
- in:  https://teach.classdojo.com   # type: url
- in:  https://student.classdojo.com   # type: url
- in:  https://www.classdojo.com   # type: url
- in:  https://home.classdojo.com   # type: url
- in:  https://dev.tutoring.classdojo.com   # type: url
- in:  https://ws.multiplayer.classdojo.com/   # type: url
- in:  https://ticket.multiplayer.classdojo.com   # type: url
- in:  https://clients.multiplayer.classdojo.com/launcher/prod/latest   # type: url
- in:  https://monster-customizer.classdojo.com/cf6dfa68-1a81-4c6d-bc0b-38f3666b37d6/index.html   # type: url
- in:  *.classdojo.com   # type: wildcard
- in:  *.classdojo.co.uk   # type: wildcard
- in:  *.doj.io   # type: wildcard
- in:  *.dojo.me   # type: wildcard
- out: https://shop.classdojo.com   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
