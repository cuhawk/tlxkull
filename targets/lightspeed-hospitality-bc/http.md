# Lightspeed Hospitality

> Platform: Bugcrowd — https://bugcrowd.com/engagements/lightspeed-hospitality
> Type: BBP
> Bounty: P1 $1000–$2000 | P2 $500–$1000 | P3 $200–$500 | P4 $20–$150
> Status: In progress

## Scope

- in:  https://k-series.lightspeedhq.com   # type: url
- in:  https://hq.breadcrumb.com/hq/restaurants/bounty-cafe-2/   # type: url
- out: https://lightspeedhq.com/trial   # type: url
- out: https://pos-admin.trial.lsk.lightspeed.app   # type: url

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

## Notes (appended)

- status: ACTIVE (resumed Dec 5 2025 after brief pause)
- oos_sitewide: XSS Reflected/Self/Stored (sitewide OOS since Feb 2023)
- oos_sitewide: CSRF (sitewide OOS since Feb 2023)
- known_oos_xss: /customers, /Receipt, /Stock paths (known issue)
- creds: pre-provisioned credentials available at bottom of brief (Credentials tab)
- no_new_users: Do not create or add any new users
- no_password_reset: Do not test forgot password functionality; do not change/reset account passwords (will be removed from program)
