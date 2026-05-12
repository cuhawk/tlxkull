# Aiven

> Platform: Bugcrowd — https://bugcrowd.com/engagements/aiven-mbb-og
> Type: VDP
> Bounty: P1 $16500–$23100 | P2 $5280–$13200 | P3 $1650–$4620 | P4 $660–$990
> Status: In progress

## Scope

- in:  https://aiven.io/clickhouse   # type: url
- in:  https://aiven.io/docs/products/metrics/concepts/metrics-overview   # type: url
- in:  https://regatta.aiven.io/   # type: url
- in:  https://aiven.io/   # type: url
- in:  https://console.aiven.io/login   # type: url
- in:  https://api.aiven.io/login   # type: url
- in:  https://github.com/Aiven-Open   # type: url
- in:  https://github.com/Aiven   # type: url
- in:  http://falcon-bug-bounty-flag-pgsql-dev-sandbox.aivencloud.com/   # type: url
- out: aquarium.aiven.io   # type: domain
- out: uptime.aiven.io   # type: domain
- out: video.aiven.io   # type: domain
- out: aiven.io/community   # type: domain
- out: aiven.io/contact   # type: domain
- out: *.aiven.fi   # type: wildcard
- out: github.com/Aiven-Labs   # type: domain
- out: *.avns.net   # type: wildcard
- out: events.aiven.io   # type: domain
- out: ideas.aiven.io   # type: domain
- out: aivenhelp.zendesk.com   # type: domain
- out: support.aiven.io   # type: domain

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
