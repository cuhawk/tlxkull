# Auth0 by Okta

> Platform: Bugcrowd — https://bugcrowd.com/engagements/auth0-okta
> Type: VDP (Expedited triage)
> Bounty: P1 $10000–$50000 | P2 $4000–$10000 | P3 $1000–$4000 | P4 $100–$1000
> Status: In progress

## Scope

- in:  config.cic-bug-bounty.auth0app.com   # type: domain
- in:  https://manage.cic-bug-bounty.auth0app.com/   # type: url
- in:  *.cic-bug-bounty.auth0app.com   # type: wildcard
- in:  https://play.google.com/store/apps/details?id=com.auth0.guardian&hl=en_US&gl=US   # type: android_app
- in:  https://apps.apple.com/us/app/auth0-guardian/id1093447833   # type: ios_app
- in:  https://marketplace.auth0.com   # type: url
- in:  https://dashboard.fga.dev/   # type: url
- in:  https://api.us1.fga.dev/   # type: url
- in:  https://customers.us1.fga.dev/   # type: url
- in:  https://play.fga.dev/   # type: url
- in:  https://github.com/auth0/auth0.js   # type: url
- in:  https://github.com/auth0/lock   # type: url
- in:  https://github.com/auth0/auth0-spa-js   # type: url
- in:  https://github.com/auth0/Auth0.Net   # type: url
- in:  https://github.com/auth0/nextjs-auth0   # type: url
- in:  https://github.com/auth0/auth0-java   # type: url
- in:  https://github.com/auth0/react-native-auth0   # type: url
- in:  https://github.com/auth0/auth0-php   # type: url

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

## Tier 2 Targets (P1 $5000–$15000)
# NOTE: Tier 2 table was "Loading resources" — targets inferred from program description:
# Authentication API, Management API, Management Dashboard, MFA/Guardian, mobile apps
# Key documented targets per program brief:
- in:  https://auth0.com/docs/api/authentication   # type: url  # Authentication API docs
- in:  https://auth0.com/docs/api/management/v2   # type: url  # Management API docs

## Out of scope
- out:  auth0.auth0.com   # explicit OOS per program rules
- out:  manage.auth0.com   # explicit OOS per program rules

## Rules
- No automated scanning / DoS / scanners; max 5 req/sec for Burp Intruder
- Research environment: manage.cic-bug-bounty.auth0app.com (get creds via program page)
- No testing on production auth0.com systems other than researcher tenant
- Do NOT access customer instances
