# Sophos

> Platform: Bugcrowd — https://bugcrowd.com/engagements/sophos
> Type: BBP
> Bounty: P1 $3000–$8000 | P2 $1000–$3000 | P3 $300–$1000 | P4 $100–$200
> Status: In progress

## Scope

- in:  https://www.sophos.com/en-us/products/endpoint-antivirus/free-trial   # type: url
- in:  https://central.sophos.com/   # type: url
- in:  https://central.sophos.com   # type: url
- in:  https://www.sophos.com/en-us/products/next-gen-firewall   # type: url
- in:  https://www.sophos.com/en-us/products/mobile-control/free-trial   # type: url
- in:  https://docs.sophos.com/central/customer/help/en-us/ManageYourProducts/ThreatAnalysisCenter/Integrations/Sophos/NDR/index.html   # type: url
- in:  https://www.sophos.com/en-us/products   # type: url
- in:  https://www.sophos.com/   # type: url
- out: community.sophos.com   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Special targets (separate bounty tiers)

- Intercept X Endpoint (Windows) Zero-click RCE → P1 $80,000 max
  - Requires: pre-auth remote RCE via Endpoint Protection, Admin privilege, no user interaction
- Sophos Central → P1 $50,000 max
  - Requires: large-scale data breach OR zero-touch super-admin account takeover OR AWS IAM escalation
- Sophos Firewall (XG/XGS SFOS) Pre-auth RCE → P1 $50,000 max
  - Requires: Network AV=N, AC=L, PR=None, UI=None, root code execution
- SOPHOS/Secureworks: Taegis and Redcloak also in Premium Bounty tier
