# KU Leuven - Admissions for Students

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/kuleuven/admissions-for-students/detail
> Type: BBP | Public | Open
> Bounty: Low €100 | Medium €500 | High €1,250 | Critical €2,000 | Exceptional €2,500 (Tier 2)
> Avg payout: €234 | Total paid: €700
> Response: avg first response < 2 weeks | avg to decide +3 weeks
> Last scope update: unknown

## Scope

- in:  https://webwsp.aps.kuleuven.be/sap/bc/ui5_ui5/sap/zc_ad_appl/*   # type: wildcard | tier: Tier 2
- in:  https://webwsp.aps.kuleuven.be/sap/opu/odata/sap/ZC_AD_APPLICANT_SRV/*   # type: wildcard | tier: Tier 2
- in:  https://www.kuleuven.be/sapredir/admissions_50000050   # type: url | tier: No bounty (account creation entry point)
- out: https://secure.ogone.com   # type: url
- out: https://idp.kuleuven.be/idp/   # type: url
- out: https://account.kuleuven.be/   # type: url

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: create account at https://www.kuleuven.be/sapredir/admissions_50000050 — first name must be "Intigriti"; use @intigriti.me address; limited test credentials available via Credentials section (may be out); do NOT change passwords of provided accounts

## Notes

- payout speed: avg to decide +3 weeks
- SAP-based university admissions portal; two-phase application flow
- idp.kuleuven.be (login) is out of scope
- processing fee payment (ogone) is out of scope
- focus: privilege escalation, sensitive data access of other users, arbitrary file read/write, code execution, data modification
- severity table: Exceptional=RCE; Critical=full DB access/vertical privesc; High=random user data/stored XSS; Medium=reflected XSS; Low=reflected XSS no impact

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
