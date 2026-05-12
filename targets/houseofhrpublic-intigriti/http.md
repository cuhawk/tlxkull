# House of HR

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/houseofhr/houseofhrpublic/detail
> Type: BBP | Public | Suspended
> Bounty: Low €25 | Medium €100 | High €500 | Critical €1,000 | Exceptional €2,000 (Tier 2)
> Avg payout: €297 | Total paid: €14,850
> Response: avg first response < 2 weeks | avg to decide +3 weeks
> Last scope update: unknown

## Scope

- in:  mijncontinu.continu.nl   # type: url | tier: Tier 2
- in:  abylsen.com   # type: url | tier: Tier 2
- in:  accentjobs.be   # type: url | tier: Tier 2
- in:  connect-continu-uat.houseofhr.com   # type: url | tier: Tier 2
- in:  continu.nl   # type: url | tier: Tier 2
- in:  e-connect.accentjobs.be   # type: url | tier: Tier 2
- in:  foreign.accentjobs.be   # type: url | tier: Tier 2
- in:  testjobs.abylsen.com   # type: url | tier: Tier 2
- out: *.swop.com/*   # type: wildcard
- out: backoffice.uat.nowjobs.dev   # type: url
- out: be.gighouse.app (Android)   # type: android_app
- out: 1446739362 (iOS)   # type: ios_app
- out: any related domain not listed   # type: wildcard

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: @intigriti.me required; self-register on application; use "TestIntigriti" as first and last name when registering; ID check required; no request header required

## Notes

- payout speed: avg to decide +3 weeks; CURRENTLY SUSPENDED
- HR services company; Business & Professional Services; production sites in scope
- no automated tooling / no brute force — prohibited
- subdomains in scope if referenced on an in-scope domain AND functional to it (e.g. connect.continu.nl is in scope; swop.com referenced via houseofhr.com is NOT)
- do NOT apply for jobs on these production sites
- focus: PII leakage is highest priority (core business)
- known issues (do not report): Google Maps API key vulns across all scope; KvK number blocking new company signups on continu.nl
- OOS: API key disclosure without business impact, Self-XSS, CORS non-sensitive, missing headers/cookies, low-impact CSRF, clickjacking, CSV injection, SPF/DMARC/DKIM, username enumeration, HTTP smuggling without impact, Google Maps API keys

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
