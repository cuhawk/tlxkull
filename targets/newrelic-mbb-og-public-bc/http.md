# New Relic Public Bug Bounty Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/newrelic-mbb-og-public
> Type: BBP
> Bounty: P1 $6000 | P2 $2500 | P3 $500 | P4 $250
> Status: In progress

## Scope

- in:  https://one.newrelic.com/all-capabilities   # type: url
- in:  https://github.com/newrelic   # type: url
- in:  https://play.google.com/store/apps/details?id=com.newrelic.rpm   # type: android_app
- in:  https://apps.apple.com/ie/app/new-relic/id594038638   # type: ios_app
- in:  https://docs.newrelic.com/docs/infrastructure/infrastructure-monitoring/get-started/get-started-infrastructure-monitoring/   # type: url
- in:  https://www.newrelic.com/   # type: url
- in:  https://support.newrelic.com/   # type: url
- in:  forum.newrelic.com   # type: domain
- in:  knowledge.newrelic.com   # type: domain
- out: frame-rpm.newrelic.com   # type: domain
- out: feedback.service.newrelic.com   # type: domain

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
