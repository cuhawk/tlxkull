# The Hut Group

> Platform: Bugcrowd — https://bugcrowd.com/engagements/hutgroup-public
> Type: BBP
> Bounty: P1 $2000–$2500 | P2 $1000–$1500 | P3 $250–$750 | P4 $100–$200
> Status: In progress

## Scope

- in:  https://*.myprotein.com/   # type: url
- in:  https://www.matalan.co.uk   # type: url
- in:  https://*.myvitamins.com/   # type: url
- in:  https://*.lookfantastic.com/   # type: url
- in:  https://*.thehutgroup.com/   # type: url
- out: *.ringcentral.com   # type: wildcard
- out: *.uk2.net   # type: wildcard
- out: *.westhost.com   # type: wildcard
- out: *.vps.net   # type: wildcard
- out: *.midphase.com   # type: wildcard
- out: *.us2.net   # type: wildcard

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

- required_header: X-Request-ID: Bugcrowd (must include in all server requests)
- xss_bonus: 1.5x payout multiplier on XSS reports May 8-14 2026
- shared_platform: Ingenuity E-Commerce — submissions valid across all targets on same platform, duplicated against first submission
- out_of_scope: OAuth pre account takeover (known issue)
- out_of_scope: Subdomain Takeover
