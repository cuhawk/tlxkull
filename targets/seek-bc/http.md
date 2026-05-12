# SEEK

> Platform: Bugcrowd — https://bugcrowd.com/engagements/seek
> Type: VDP
> Bounty: P1 $5000–$10000 | P2 $700–$5000 | P3 $200–$700 | P4 $50–$200
> Status: In progress (started Nov 08, 2016)

## Scope

- in:  *.seek.com.au   # type: wildcard
- in:  https://seekcdn.com   # type: url
- in:  https://apps.apple.com/au/app/seek-jobs-job-search/id520400855   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=au.com.seek&hl=en_AU&gl=US   # type: android_app
- in:  *.skinfra.xyz   # type: wildcard
- in:  *.outfra.xyz   # type: wildcard
- in:  *.sol-data.com   # type: wildcard
- in:  *.jobapi.net   # type: wildcard
- in:  *.seekpass.co   # type: wildcard
- in:  *.seekpass-staging.com   # type: wildcard
- in:  Moment.js   # type: domain
- in:  *.aips-internal.com   # type: wildcard
- in:  *.certsy.com   # type: wildcard
- in:  *.certsynonprod.com   # type: wildcard
- in:  https://apps.apple.com/au/app/certsy/id1617796159   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.certsy.app   # type: android_app
- in:  https://graphql.seek.com   # type: url
- in:  https://auth.seek.com   # type: url

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
