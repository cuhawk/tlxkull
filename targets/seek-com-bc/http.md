# Seek.com

> Platform: Bugcrowd — https://bugcrowd.com/engagements/seek-com
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  *.employer.seek.com   # type: wildcard
- in:  *.jobsdb.com   # type: wildcard
- in:  *.jobstreet.com   # type: wildcard
- in:  *.jobstreet.com.sg   # type: wildcard
- in:  *.jobstreet.com.my   # type: wildcard
- in:  *.jobstreet.co.id   # type: wildcard
- in:  *.seekasia.com   # type: wildcard
- in:  id.employer.staging.seek.com   # type: domain
- in:  my.employer.staging.seek.com   # type: domain
- in:  ph.employer.staging.seek.com   # type: domain
- in:  hk.employer.staging.seek.com   # type: domain
- in:  th.employer.staging.seek.com   # type: domain
- in:  www.staging.jobstreet.com.ph   # type: domain
- in:  www.staging.jobstreet.co.id   # type: domain
- in:  www.staging.jobstreet.com.sg   # type: domain
- in:  www.staging.jobstreet.com.my   # type: domain
- in:  th.staging.jobsdb.com   # type: domain
- in:  hk.staging.jobsdb.com   # type: domain

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
