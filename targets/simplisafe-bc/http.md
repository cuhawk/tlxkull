# SimpliSafe Managed Bug Bounty Engagement

> Platform: Bugcrowd — https://bugcrowd.com/engagements/simplisafe
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  bb1.simplisafe.com   # type: domain
- in:  bb2.simplisafe.com   # type: domain
- in:  cb.simplisafe.com   # type: domain
- in:  *.prd.cam.simplisafe.com (HSP Endpoints)   # type: wildcard
- in:  *.prd.platform.simplisafe.com (HSP Endpoints)   # type: wildcard
- in:  *.prd.services.simplisafe.com (HSP Endpoints)   # type: wildcard
- in:  https://webapp.simplisafe.com   # type: url
- in:  https://webapp.simplisafe.co.uk   # type: url
- in:  mfa.simplisafe.com   # type: domain
- in:  *.prd.aser.simplisafe.com   # type: wildcard
- in:  *.prd.webapps.simplisafe.com   # type: wildcard
- in:  *.prd.services.simplisafe.com (App Endpoints)   # type: wildcard
- in:  *.prd.platform.simplisafe.com (App Endpoints)   # type: wildcard
- in:  media.simplisafe.com   # type: domain
- in:  *.prd.cam.simplisafe.com (App Endpoints)   # type: wildcard
- in:  https://simplisafe.com   # type: url
- in:  https://simplisafe.co.uk   # type: url
- in:  api.prd.commerce.simplisafe.com   # type: domain
- out: careers.simplisafe.com   # type: domain
- out: clicks.simplisafe.com   # type: domain
- out: library.simplisafe.com   # type: domain
- out: livechat.simplisafe.com   # type: domain
- out: press.simplisafe.com   # type: domain
- out: support.simplisafe.com   # type: domain

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
