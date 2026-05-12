# Treasury Board of Canada Secretariat/Secrétariat du Conseil du Trésor du Canada

> Platform: HackerOne — https://hackerone.com/tbs-sct
> Type: VDP | Self-managed | Standard safe harbor
> Bounty: VDP (no bounties) | Response efficiency: 92%
> Last scope update: April 30, 2026

## Scope

- in:  talent.canada.ca   # type: domain
- in:  issue-verify.alpha.canada.ca   # type: domain
- in:  gciv-dvgc.alpha.canada.ca   # type: domain
- in:  forms-formulaires.alpha.canada.ca   # type: domain
- in:  design-system.alpha.canada.ca   # type: domain
- in:  delivrance-verification.alpha.canada.ca   # type: domain
- in:  auth.signin-connexion.canada.ca   # type: domain
- in:  articles.alpha.canada.ca   # type: domain
- in:  app.signin-connexion.canada.ca   # type: domain
- in:  api.signin-connexion.canada.ca   # type: domain
- in:  *.numerique.canada.ca   # type: wildcard
- in:  *.notification.canada.ca   # type: wildcard
- in:  *.digital.canada.ca   # type: wildcard
- in:  *.cdssandbox.xyz   # type: wildcard
- in:  *.cds-snc.ca   # type: wildcard
- out: strapi.cdssandbox.xyz   # type: domain
- out: reponses-ia.cdssandbox.xyz   # type: domain
- out: reponses-ia.alpha.canada.ca   # type: domain
- out: blawx.cdssandbox.xyz   # type: domain
- out: All other assets   # type: other
- out: ai-answers.cdssandbox.xyz   # type: domain
- out: ai-answers.alpha.canada.ca   # type: domain

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- payout speed: unknown
- Launched: Mar 2026

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
