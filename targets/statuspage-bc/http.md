# Statuspage

> Platform: Bugcrowd — https://bugcrowd.com/engagements/statuspage
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  https://manage.statuspage.io Fastly Ruby-on-Rails Moment.js website   # type: url
- in:  *.statuspage.io Recon Website-Testing DNS   # type: wildcard
- out: https://www.statuspage.io website   # type: url
- out: https://blog.statuspage.io website   # type: url
- out: https://metastatuspage.com website   # type: url

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

- status: ACTIVE (since Mar 2014, Atlassian property)
- Free researcher account: https://manage.statuspage.io/security-researcher (valid 1 month)
- Third parties also in scope IF attack exploits customers directly: help.statuspage.io, doers.statuspage.io, filepicker.io, segment.io
- HTML injection is a FEATURE (by design) — only in scope if it leads to XSS (non-self-XSS)
- Stored XSS must be viewable on publicly hosted *.statuspage.io subdomain
- Stored XSS requiring team member signup or appearing on CNAME domain is NOT eligible
- Custom header/footer HTML XSS: private pages allow it by design; see live status page for difference
- Similar access control issues should be grouped in ONE report (same bypass method, multiple endpoints)
- No automated scanners
