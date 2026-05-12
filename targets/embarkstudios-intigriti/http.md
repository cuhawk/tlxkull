# Embark Studios

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/embarkstudios/embarkstudios/detail
> Type: BBP | Public | Suspended
> Bounty: Low €300 | Medium €1,000 | High €2,000 | Critical €3,000 | Exceptional €4,000 (Tier 1); Low €100 | Medium €500 | High €1,000 | Critical €1,500 | Exceptional €3,000 (Tier 2); Low €50 | Medium €500 | High €1,000 | Exceptional €1,500 (Tier 3)
> Avg payout: €567 | Total paid: €14,720
> Response: avg first response < 2 weeks | avg to decide +3 weeks
> Last scope update: unknown

## Scope

- in:  auth.embark.net   # type: url | tier: Tier 1
- in:  id.embark.games   # type: url | tier: Tier 1
- in:  *.observability.embark.net   # type: wildcard | tier: Tier 2
- in:  has.embark.net   # type: url | tier: Tier 2
- in:  p4-submit-service.embark.net   # type: url | tier: Tier 2
- in:  perforce.embark.net   # type: url | tier: Tier 2
- in:  swarm.embark.net   # type: url | tier: Tier 2
- in:  user-lookup-api.embark.net   # type: url | tier: Tier 2
- in:  arcraiders.com   # type: url | tier: Tier 3
- in:  embark-studios.com   # type: url | tier: Tier 3
- in:  reachthefinals.com   # type: url | tier: Tier 3
- out: careers page on embark-studios.com   # type: url
- out: any domain not listed in Assets section   # type: wildcard

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: @intigriti.me required; X-Intigriti: <username> request header required; own account usable for auth.embark.net (discord OAuth flow); client_id: intigriti, client_secret: uERsh8FGRspjTyVgS0fPdADQ06EoNQCgXgbK5qVrcM8=; auth URL: https://auth.embark.net; auth helpers binary at https://storage.googleapis.com/embark-x-intigriti

## Notes

- payout speed: avg to decide +3 weeks; CURRENTLY SUSPENDED
- games studio (Arc Raiders, The Finals); Media & Entertainment
- no automated tooling rate limit specified
- OOS: API key disclosure without proven impact, Self-XSS, CORS on non-sensitive endpoints, missing headers/cookies, CSRF low impact, clickjacking, CSV injection, tokens to third parties, SPF/DMARC/DKIM, username enumeration, HTTP smuggling without impact, subdomain takeover without actual takeover, blind SSRF without impact, host header injection without impact
- IAP-protected assets are intentionally inaccessible — report if bypass found
- GitHub public repos: use Private Vulnerability Reporting, then submit PR URL on Intigriti

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
