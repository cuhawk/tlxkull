# Port of Antwerp-Bruges VIP

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/portofantwerp/portofantwerpvip/detail
> Type: BBP | Public | Open
> Bounty: Low €100 | Medium €400 | High €1,500 | Critical €4,000 | Exceptional €5,000 (Tier 1); Low €300 | Medium €1,000 | High €2,500 | Critical €4,000 (Tier 2)
> Avg payout: €350 | Total paid: €11,525
> Response: avg first response < 6 days | avg to decide < 3 days
> Last scope update: 18/12/2024

## Scope

- in:  login-test.portofantwerpbruges.com   # type: url | tier: Tier 1
- in:  apps-accpt.portofantwerpbruges.com/apics-loket   # type: url | tier: Tier 1
- in:  login-accpt.portofantwerpbruges.com   # type: url | tier: Tier 1
- in:  my-accpt.portofantwerpbruges.com   # type: url | tier: Tier 1
- in:  register-accpt.portofantwerpbruges.com   # type: url | tier: Tier 1
- in:  apps-accpt.portofantwerpbruges.com/bts   # type: url | tier: Tier 2
- in:  apps-accpt.portofantwerpbruges.com/portdues   # type: url | tier: Tier 2
- out: apps-test.portofantwerp.com   # type: url
- out: apps.portofantwerp.com   # type: url

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: intigriti.me address mandatory; registration via APICS wizard; Portdues Portal needs separate account — email poa_amaris_portdues_devteam@portofantwerpbruges.com

## Notes

- payout speed: avg to decide < 3 days
- acceptance environment only (accpt subdomain); do not use production portofantwerp.com assets
- report in Dutch or English
- no automated scanners; quality over quantity
- ID check required for program participation
- focus areas: privilege escalation, auth bypass, credential theft, data breach

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
