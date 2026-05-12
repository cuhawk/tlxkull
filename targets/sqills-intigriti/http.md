# Sqills S3 Passenger

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/sqills/sqills/detail
> Type: BBP | Public | Suspended
> Bounty: Low €100 | Medium €750 | High €1,500 | Critical €3,000 | Exceptional €7,500 (Tier 2); Low €100 | Medium €500 | High €750 | Critical €2,000 | Exceptional €3,000 (Tier 3 - Saga AI)
> Avg payout: €473 | Total paid: N/A
> Response: avg first response < 2 weeks | avg to decide < 3 weeks
> Last scope update: unknown

## Scope

- in:  *.sqills-bugbounty-test.cloud.sqills.com   # type: wildcard | tier: Tier 2
- in:  admin.sqills-bugbounty-test.cloud.sqills.com   # type: url | tier: Tier 2
- in:  api.sqills-bugbounty-test.cloud.sqills.com   # type: url | tier: Tier 2
- in:  sqills-*.*.s3p.cloud   # type: wildcard | tier: Tier 2
- in:  https://api.sqills-bugbounty-test.cloud.sqills.com/api/v3/intelligence (Saga AI)   # type: url | tier: Tier 3
- in:  https://admin.sqills-bugbounty-test.cloud.sqills.com/api/v3/intelligence (Saga AI)   # type: url | tier: Tier 3
- in:  https://admin.sqills-bugbounty-test.cloud.sqills.com/en-GB/intelligence (Saga AI)   # type: url | tier: Tier 3
- out: confluence.sqills.com (docs only)   # type: url
- out: any subdomains not listed in scope   # type: wildcard

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: agent credentials claimable via program page; password format: !313Ab2dA462A09790Ae3351AdF366BbB82eD06b6@YYYYMMDD (current UTC date); reset daily at 00:00 UTC; Confluence docs: username=intigriti / password=bpM8fYo19Dm9 (read-only, out of scope to test)

## Notes

- payout speed: avg to decide < 3 weeks; CURRENTLY SUSPENDED
- rail/bus booking system (S3 Passenger); single-tenant per operator environment
- test environment only — no production access
- automated tooling allowed with rate limiting consideration
- grant types: public, agent, booking, CRM, system, refresh
- Portal UI: https://admin.sqills-bugbounty-test.cloud.sqills.com/en-GB/portal
- cash payment method available for testing (no real payments)
- focus: personal data leak, transactional data modification, configuration data modification
- Saga = S3 Passenger AI agent (Tier 3)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
