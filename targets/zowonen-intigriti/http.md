# ZOwonen

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/zowonen/zowonen/detail
> Type: BBP | Public | Open
> Bounty: Low €150 | Medium €750 | High €1,500 | Critical €2,500 | Exceptional €3,000 (Tier 1); Low €250 | Medium €450 | High €600 | Critical €1,250 (Tier 2); min Tier 1 €150, Tier 2 €75
> Avg payout: €757 | Total paid: €20,425
> Response: avg first response < 5 days | avg to decide +3 weeks
> Last scope update: unknown

## Scope

- in:  https://portal.24rosa.nl/   # type: url | tier: Tier 1
- in:  www.zowonen.com   # type: url | tier: Tier 2
- in:  zowonen.ucsnet.nl   # type: url | tier: Tier 2
- out: Https://zowonen.mind2pay.com   # type: url
- out: klantportaal.zowonen.com   # type: url
- out: any domain not in scope section   # type: domain

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: no test credentials offered; 2FA required; @intigriti.me address not required (marked N/A)

## Notes

- payout speed: avg to decide +3 weeks
- Dutch social housing corporation; Microsoft Business Central ERP
- rate limit: max 3 requests/sec when using automation
- 2FA required; ID check required
- ERP interfaces: empire.zowonen.com (MS Business Central), klantportaal.zowonen.com (client portal), kovra.zowonen.com (KOVRA DICO standard)
- physical infra at primary location: MS Active Directory, MS Always On VPN
- mixed infrastructure shared with other businesses — respect scope strictly

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
