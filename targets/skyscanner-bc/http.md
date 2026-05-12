# Skyscanner

> Platform: Bugcrowd — https://bugcrowd.com/engagements/skyscanner
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  gateway.skyscanner.net/*   # type: domain
- in:  skyscanner.net/hotels/book/*   # type: domain
- in:  skyscanner.net/*   # type: domain
- in:  partnerportal.skyscanner.net/*   # type: domain
- in:  *.skyscanner.net   # type: wildcard

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
