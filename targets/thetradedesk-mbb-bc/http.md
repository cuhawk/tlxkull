# The Trade Desk

> Platform: Bugcrowd — https://bugcrowd.com/engagements/thetradedesk-mbb
> Type: BBP
> Bounty: P1 $4000–$5000 | P2 $2000–$3000 | P3 $500–$750 | P4 $175–$225
> Status: In progress

## Scope

- in:  https://open.sincera.io   # type: url
- in:  https://desk.thetradedesk.com   # type: url
- in:  https://api.thetradedesk.com   # type: url
- in:  https://auth.thetradedesk.com   # type: url
- in:  https://partner.thetradedesk.com   # type: url
- in:  https://www.thetradedesk.com   # type: url
- in:  https://ops-sso.adsrvr.org/   # type: url
- in:  https://myopenpass.com   # type: url
- in:  https://auth.myopenpass.com   # type: url
- in:  https://partner.myopenpass.com   # type: url
- in:  https://atlantis-ext.myopenpass.com   # type: url
- in:  https://prod.uidapi.com   # type: url
- in:  https://prod.euid.eu   # type: url
- in:  https://core-prod.uidapi.com   # type: url
- in:  https://optout-prod.uidapi.com   # type: url
- in:  https://optout.prod.euid.eu   # type: url
- in:  https://transparentadvertising.com   # type: url
- in:  https://transparentadvertising.eu   # type: url
- in:  https://portal.unifiedid.com   # type: url
- in:  *.thetradedesk.com   # type: wildcard
- in:  *.adsrvr.org   # type: wildcard
- in:  https://www.thecurrent.com   # type: url
- in:  https://cdn.myopenpass.com   # type: url
- in:  https://cstg-integ.uidapi.com   # type: url
- in:  https://esp-jssdk-integ.uidapi.com   # type: url
- in:  https://esp-srvonly-integ.uidapi.com   # type: url
- in:  https://example-jssdk-integ.uidapi.com   # type: url
- in:  https://example-srvonly-integ.uidapi.com   # type: url
- in:  https://secure-signals-jssdk-integ.uidapi.com   # type: url
- in:  https://secure-signals-srvonly-integ.uidapi.com   # type: url
- in:  https://secure-signals-client-side-integ.uidapi.com/   # type: url
- in:  https://secure-signals-react-integ.uidapi.com   # type: url
- in:  https://www.adsrvr.org   # type: url
- in:  https://myopenpassdemo.com/   # type: url
- in:  https://careers.thetradedesk.com   # type: url
- in:  https://www.venturatvos.com   # type: url
- in:  https://www.opensincera.com   # type: url
- in:  https://edgeacademy.thetradedesk.com   # type: url
- out: https://investors.thetradedesk.com   # type: url
- out: https://ask.thetradedesk.com   # type: url
- out: https://www.thetradedeskedgeacademy.com   # type: url
- out: https://openpass.thetradedesk.com   # type: url
- out: https://unifiedid.com   # type: url
- out: https://euid.eu   # type: url
- out: argocd.*.uidapi.com   # type: domain
- out: https://stationery.thetradedesk.com   # type: url
- out: https://bynder.thetradedesk.com   # type: url

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
