# Chime Managed Bug Bounty Engagement

> Platform: Bugcrowd — https://bugcrowd.com/engagements/chime
> Type: BBP
> Bounty: Primary: P1 $10,000–$20,000 | P2 $4,500–$5,000 | P3 $250–$500 | P4 $50–$100 | Secondary (Saltlabs): P1 $4,500–$7,000 | P2 $2,500–$4,000 | P3 $200–$400 | P4 $50–$100
> Status: In Progress | Started: May 06 2025
> Last scope update: 20 Jan 2026

## Scope

- in:  *.chime.com                                    # type: wildcard  (primary; confirmed via CrowdStream)
- in:  Chime iOS app                                  # type: ios_app   (App Store + TestFlight IPA provided)
- in:  Chime Android app                              # type: android_app  (APK provided + Play Store)
- in:  app.saltlabs.com (Saltlabs production)        # type: domain    (secondary target)
- in:  app-qa.chime.com (QA/staging web)             # type: domain    (for non-US researchers)
- in:  member-qa.chime.com/enroll/ (QA enrollment)  # type: domain    (staging)
- out: (long list of specific out-of-scope subdomains — see below)
- out: careers.chime.com, help.chime.com, developer.chime.com, status.chime.com  # type: domain
- out: bounce.*/em.*/email.*/links.*  chime subdomains (email infra)   # type: domain
- out: _acme-challenge.* subdomains                  # type: domain
- out: www.saltlabs.com, help.saltlabs.com, status.saltlabs.com  # type: domain
- out: any non-Chime-owned asset                     # type: other

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: sign up at chime.com/get-started using @bugcrowdninja.com
- note: US researchers need real SSN for KYC; non-US use QA env at member-qa.chime.com/enroll/
- note: for 2nd account (peer testing), email bugbounty@chime.com with Bugcrowd username
- note: Saltlabs account at https://app.saltlabs.com/session/new (US phone required)

## Notes

- payout speed: validation within 4 days
- status: ACTIVE
- Finance / fintech banking; production environment; KYC required for primary targets
- Safe harbor: yes (CFAA + DMCA exemptions)
- scope rating: 4/4
- focus (P1): unauthorized PII access, unauthorized fund transfers, race conditions (double-spend), RCE on prod, SSN/document leaks, wormable XSS, SQLi with DB access, SSRF→AWS
- focus (P2): single-account XSS/ATO, mobile bugs on non-rooted devices, access control (single-user), staging RCE, internal tool compromise
- focus (P3): non-sensitive data leak, limited info disclosure
- mobile: mobile app APK/IPA builds provided for testing; no jailbreak/root detection enforcement (not a bug)
- testing tip: use ≤$50 test transfers; contact bugbounty@chime.com if account locked
- out-of-scope: debug info disclosure, IP disclosure, Google Maps API keys, editable GitHub wikis (github.com/1debit), clickjacking no-action pages, CSRF no-action forms, MiTM/physical access, old libs without PoC, CSV injection, SSL/TLS best practices, DoS/stress-test, user enumeration low-risk, text injection, rate-limit non-auth endpoints, missing CSP/HttpOnly/cookie flags, missing SPF/DKIM/DMARC, outdated browsers, version disclosure, tabnabbing, open redirect (without extra impact), social engineering, scanner reports not validated, third-party services, dark web leaked creds, broken link hijacking, LLM hallucinations, code obfuscation, no cert pinning, no jailbreak detection, public analytics API keys
- do NOT target other members; stop immediately if you access someone else's sensitive data

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
