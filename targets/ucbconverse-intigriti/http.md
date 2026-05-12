# UCB - External Perimeter

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/ucb/ucbconverse/detail
> Type: BBP | Public | Open
> Bounty: Low €250 | Medium €1,000 | High €2,000 | Critical €5,000 | Exceptional N/A (Tier 2); min €50
> Avg payout: N/A | Total paid: N/A
> Response: N/A
> Last scope update: 15/04 (launched)

## Scope

- in:  https://www.kygevvi.com/   # type: url | tier: Tier 2
- in:  https://www.hoitajareppu.fi/   # type: url | tier: Tier 2
- in:  https://www.lightupepilepsy.com/   # type: url | tier: Tier 2
- in:  https://www.ucb-hk.com/   # type: url | tier: Tier 2
- in:  https://youmissedaspothcp.com/   # type: url | tier: Tier 2
- in:  https://ucbventures.com/   # type: url | tier: Tier 2
- in:  https://reports.ucb.com/   # type: url | tier: Tier 2
- in:  https://ucb-media-hub.de/   # type: url | tier: Tier 2
- in:  https://www.ucbdirect.com/   # type: url | tier: Tier 2
- out: career section   # type: other
- out: contact forms, adverse event forms, application forms (production forms)   # type: other

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: do NOT self-register; request test accounts from UCB if sign-in available; User-Agent: Intigriti - <username>; X-Intigriti-username: <username>

## Notes

- payout speed: N/A (new program, launched 15 Apr)
- biopharma; avoid any patient/service impact; do not auto-submit forms
- 2FA required; ID check required
- custom User-Agent AND request header required for all testing
- UCB scans own assets with Invicti, Snyk, Qualys — scanner results out of scope
- €25 bonus if validation delayed; €100 bonus for re-testing fixed issues
- focus: IT system compromise, confidential data access

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
