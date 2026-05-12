# Argenta

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/argenta/argenta/detail
> Type: BBP | Public | Open
> Bounty: Low €200 | Medium €750 | High €1,500 | Critical €6,000 | Exceptional €7,500 (Tier 2); Low €100 | Medium €350 | High €800 | Critical €2,000 | Exceptional €3,000 (Tier 3)
> Avg payout: €673 | Total paid: €37,675
> Response: avg first response < 1 week | avg to decide +3 weeks
> Last scope update: unknown

## Scope

- in:  *.argenta.be/(lang)/lenen/hypothecairelening.html   # type: wildcard | tier: Tier 2
- in:  *.argenta.be/(lang)/beleggen.html   # type: wildcard | tier: Tier 2
- in:  *.argenta.be/(lang)/privacy/responsible-disclosure.html   # type: wildcard | tier: Tier 2
- in:  *.argenta.be/(lang)/klant-worden.html   # type: wildcard | tier: Tier 2
- in:  *.argenta.be/(lang)/zoeken.html   # type: wildcard | tier: Tier 2
- in:  *.argenta.be/(lang)/contacteer-ons/klachten.html   # type: wildcard | tier: Tier 2
- in:  194.78.107.77/32   # type: other | tier: Tier 2 (IP range)
- in:  argenta-bankieren/id893585833 (iOS)   # type: ios_app | tier: Tier 2
- in:  be.argenta.bankieren (Android)   # type: android_app | tier: Tier 2
- in:  homebank.argenta.be   # type: url | tier: Tier 2
- in:  mobile-api.argenta.be   # type: url | tier: Tier 2
- in:  *.argenta.be   # type: wildcard | tier: Tier 3
- in:  *.argenta.eu   # type: wildcard | tier: Tier 3
- in:  194.78.107.0/27   # type: other | tier: Tier 3
- in:  194.78.107.32/28   # type: other | tier: Tier 3
- in:  194.78.107.56/29   # type: other | tier: Tier 3
- in:  194.78.107.64/27   # type: other | tier: Tier 3
- in:  194.78.107.96/28   # type: other | tier: Tier 3
- in:  194.78.132.160/27   # type: other | tier: Tier 3
- in:  194.78.141.160/28   # type: other | tier: Tier 3
- in:  194.78.141.176/29   # type: other | tier: Tier 3
- in:  194.78.141.184/29   # type: other | tier: Tier 3
- in:  194.78.154.120/29   # type: other | tier: Tier 3
- in:  194.78.154.64/27   # type: other | tier: Tier 3
- in:  194.78.154.96/28   # type: other | tier: Tier 3
- in:  81.246.81.160/27   # type: other | tier: Tier 3
- out: sts.corporate.argenta.be   # type: url
- out: *.archibus.argenta.be   # type: wildcard
- out: *.argenta.lu   # type: wildcard
- out: *.crescendo.argenta.be   # type: wildcard
- out: *.digitalchannels.argenta.be   # type: wildcard
- out: *.dr-author.argenta.be   # type: wildcard
- out: *.email.argenta.be   # type: wildcard
- out: *.enterpriseenrollment.argenta.be   # type: wildcard
- out: *.enterpriseregistration.argenta.be   # type: wildcard
- out: *.feedback.argenta.be   # type: wildcard
- out: *.gezondheid.argenta.be   # type: wildcard
- out: *.guestwifi.argenta.be   # type: wildcard
- out: *.hospitalisation.argenta.be   # type: wildcard
- out: *.info.argenta.be   # type: wildcard
- out: *.kubeflow.cbs.argenta.be   # type: wildcard
- out: *.magazine.argenta.be   # type: wildcard
- out: *.margot.argenta.be   # type: wildcard
- out: *.metrics.argenta.be   # type: wildcard
- out: *.mijngedacht.argenta.be   # type: wildcard
- out: *.mijngedachtvoorkantoren.argenta.be   # type: wildcard
- out: *.nieuw.argenta.be   # type: wildcard
- out: *.payments.argenta.be   # type: wildcard
- out: *.plaza.argenta.be   # type: wildcard
- out: *.prd-author.argenta.be   # type: wildcard
- out: *.r43.info.argenta.be   # type: wildcard
- out: *.r46.email.argenta.be   # type: wildcard
- out: *.r47.email.argenta.be   # type: wildcard
- out: *.r48.email.argenta.be   # type: wildcard
- out: *.r49.email.argenta.be   # type: wildcard
- out: *.schadeargenta.be   # type: wildcard
- out: *.smetrics.argenta.be   # type: wildcard
- out: *.test-payments.argenta.be   # type: wildcard
- out: *.warm.argenta.be   # type: wildcard
- out: *.watson.argenta.be   # type: wildcard

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: no Argenta account needed for public scope; need to be Argenta customer to test online banking (homebank.argenta.be) — sign up via https://www.argenta.be/nl/klant-worden.html; X-Intigrity-Username: {Username} header required; @intigriti.me address mandatory

## Notes

- payout speed: avg to decide +3 weeks
- Belgian retail bank; broadly scoped
- X-Intigrity-Username request header required (note: typo in header name is intentional per program)
- video PoC required for authenticated scope submissions
- ID check required; T&C required
- CVSS v3 based severity assessment
- focus: mobile app, online banking (homebank), OWASP TOP 20

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
