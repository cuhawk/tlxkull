# Coolblue

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/coolblue/coolblue/detail
> Type: BBP | Public | Open
> Bounty: Low €250 | Medium €750 | High €1,337 | Critical €2,500 | Exceptional €2,500 (Tier 1); Low €125 | Medium €375 | High €669 | Critical €1,250 (Tier 2); min Tier 1 €50, Tier 2 €25
> Avg payout: N/A | Total paid: N/A
> Response: N/A
> Last scope update: unknown

## Scope

- in:  www.coolblue.nl   # type: url | tier: Tier 1 (webshop)
- in:  www.coolblue.be   # type: url | tier: Tier 1 (webshop)
- in:  www.coolblue.de   # type: url | tier: Tier 1 (webshop)
- in:  eu.coolblue.shop (Android)   # type: android_app | tier: Tier 2
- in:  1174047097 (iOS)   # type: ios_app | tier: Tier 2
- in:  mobile-api.coolblue-production.eu   # type: other | tier: Tier 2

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: self-register at https://www.coolblue.nl/registreren using @intigriti.me address; always communicate your testing IP

## Notes

- payout speed: N/A
- e-commerce; NL/BE/DE webshops share high % of source code — submit once per vuln
- rate limit: NL/BE/DE max 2 req/sec; other countries max 0.3 req/sec
- hosted on AWS — respect AWS pentest policy
- any products received without payment must be returned
- must include testing IP in all reports
- focus: infrastructure access, order process exploits (free/discounted products), customer password/data exposure
- out-of-scope specifics: appointments/UUID findings, no-captcha login, no password length req

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
