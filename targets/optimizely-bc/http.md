# Optimizely

> Platform: Bugcrowd — https://bugcrowd.com/engagements/optimizely
> Type: VDP
> Bounty: P1 $3000–$3500 | P2 $2000–$2250
> Status: In progress (started Feb 21, 2018)

## Scope

- in:  https://app.optimizely.com/   # type: url
- in:  https://cdn.optimizely.com/   # type: url
- in:  https://cdn-pci.optimizely.com/   # type: url
- in:  https://optimizely-edge.com   # type: url
- in:  https://api.optimizely.com/   # type: url
- in:  https://dxc.episerver.net/   # type: url
- in:  https://paasportal.episerver.net/   # type: url
- in:  https://paasportal.episerver.net/api/v1.0/   # type: url
- in:  https://app.welcomesoftware.com/   # type: url
- in:  https://accounts.welcomesoftware.com/   # type: url
- in:  https://api.welcomesoftware.com/   # type: url
- in:  https://cdn-app.welcomesoftware.com/   # type: url
- in:  https://analytics.welcomesoftware.com/   # type: url
- in:  https://flags.expeng.optimizely.com   # type: url
- in:  https://accounts.cmp.optimizely.com/   # type: url
- out: https://www.optimizely.com/   # type: url

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
