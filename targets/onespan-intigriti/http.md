# OneSpan Transaction Cloud Platform

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/onespan/onespan/detail
> Type: BBP | Public | Open
> Bounty: Low €100-250 | Medium €400-750 | High €1,000-2,500 | Critical €2,500-5,000 | Exceptional €5,000-7,500 (Tier 2)
> Avg payout: €362 | Total paid: €19,894
> Response: avg first response < 1 week | avg to decide < 2 weeks
> Last scope update: unknown

## Scope

- in:  https://sandbox.esignlive.com/a/   # type: url | tier: Tier 2 (OneSpan Sign UI)
- in:  https://sandbox.esignlive.com/api/   # type: url | tier: Tier 2 (OneSpan Sign API)
- in:  https://tenant-id.sdb.tid.onespan.cloud/riskui/   # type: url | tier: Tier 2 (Risk Analytics)
- in:  https://tenant-id.sdb.tid.onespan.cloud/v1/   # type: url | tier: Tier 2 (IAA/OCA/RA API)
- out: all other onespan.com domains   # type: domain
- out: demo/sample applications   # type: other
- out: Community Portal   # type: url

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: OneSpan Sign — register at https://www.onespan.com/products/esignature/sandbox using @intigriti.me; IAA/OCA/RA — register at https://community.onespan.com/trusted-identity-platform-sandbox-registration; X-Intigriti-Username header required

## Notes

- payout speed: avg to decide < 2 weeks
- rate limit: max 10 requests/second; exceeding violates TOS
- X-Intigriti-Username request header required
- focus: cross-tenant information leaks
- ID check required; T&C required
- sandbox environments only; one account per researcher

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
