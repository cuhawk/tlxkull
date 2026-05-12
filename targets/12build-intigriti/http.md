# 12Build Bug Bounty Program

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/onetwobuild/12build/detail
> Type: BBP (Bug Bounty Program) | Application-gated | Open | Software
> Bounty: Tier 1 €100–€3,000 | Tier 2 €100–€2,300 (CVSS-based: Low/Med/High/Crit/Exceptional)
> Avg payout: €465 | Accepted: 74/187 submissions | Total paid: €34,375
> Response: <2w first response | <5d to decide | <3w+ triage
> Last scope update: May 8, 2026 (suspended briefly May 7–8, 2026)

## Scope

- in:  app.test.12build.com/*/statistieken                # type: wildcard
- in:  app.test.12build.com/*/ajax                        # type: wildcard
- in:  app.test.12build.com/*/forgot-password             # type: wildcard
- in:  app.test.12build.com/*/login                       # type: wildcard
- in:  app.test.12build.com/*/rest/1.1/api                # type: wildcard
- in:  app.test.12build.com/*/aannemers/                  # type: wildcard
- in:  app.test.12build.com/*/bill-of-quantities/*        # type: wildcard
- in:  app.test.12build.com/*/rest/bs_1.0/api             # type: wildcard
- in:  app.test.12build.com/*/bouwspecialisten/           # type: wildcard
- in:  app.test.12build.com                               # type: domain
- out: Production environment (app.12build.com)           # type: domain

## Auth

- type: session
- creds: env:TWELVEBUILD_CREDS_A      # intigriti-pentest+a@12build.com — claim from Intigriti credentials panel
- creds: env:TWELVEBUILD_CREDS_B      # second set for IDOR/BAC testing

## Notes

- payout speed: <5 days to decision
- target is TEST environment only: app.test.12build.com — NOT production
- SaaS quotation platform for construction industry (NL, DE, BE, AT), 800+ contractors, 4M+ requests
- focus areas: horiz/vert privilege escalation, credential theft, unauthorized data changes, unauthorized project document access
- NOT interested in Low/Medium issues with low impact currently
- test env: each cred set = 2 users (can switch between companies via user management)
- all intigriti-pentest+*@12build.com users are subadmins — do not change other researcher's user settings
- company structure: General Contractor (admin=subadmin same level) + Subcontractor (all approved users = admin)
  → viewing company data/settings of own company is known behavior, not a finding
  → GC admins can change all contact info of company users — intended
  → SC every approved user can change others' contact info — intended
- rate limit: max 5 req/sec (no automated scanners — manual only, scanner submissions rejected)
- ID check required on this program
- do NOT send offer requests to real companies/contacts — only provided test contacts or self-created
- do NOT discuss/post vulns without consent (incl. YouTube/Vimeo PoCs)
- attachments: Bug bounty setup PDF + GAEB helpfiles (claim from program page)
- payout tier: Tier 1 = main targets, Tier 2 = secondary
- recently active contributors: souravpaul, firebolt123456, soloboy, hx_op, theokeen, godiego

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts:
  - pdf: raw/12build-bugbounty-setup-19-03-2026.pdf    # download from Intigriti program page
  - zip: raw/GAEB-helpfiles-20250403.zip               # download from Intigriti program page
