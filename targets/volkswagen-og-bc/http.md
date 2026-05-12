# Volkswagen

> Platform: Bugcrowd — https://bugcrowd.com/engagements/volkswagen-og
> Type: BBP
> Bounty: P1 $2,100–$2,500 | P2 $1,000–$1,250 | P3 $450–$600 | P4 $150–$200
> Status: In progress (started Jun 15, 2021)

## Scope

- in:  *.volkswagen.de   # type: wildcard — primary German website
- out: erwin.volkswagen.de  # OOS unless chained to impact on volkswagen.de (RCE, SSRF, cookie steal)

## Auth

- type: signup
- creds: No credentials provided; use @bugcrowdninja.com for any account creation found in scope

## Notes

- safe harbor: yes (CFAA + DMCA)
- disclosure: coordinated (explicit request required on submission)
- status: ACTIVE; transitioned to public Aug 28, 2025
- Average payout $480; validation within 5 days
- QA/test/staging systems (with "qa", "q", "test", "staging", "dev", "pre" in name) are in-scope but lower reward; always verify on prod for max bounty
- Rate limit: max 6 req/sec for scripts/fuzzing; no automated scanners (Nessus etc.)

## OOS Vuln Types

- Self-XSS
- Email spoofing (SPF, DKIM, DMARC)
- CSRF without account integrity impact
- Rate limiting / DoS
- Old browser/OS-only exploits
- Recent unpatched third-party CVEs
- P5 (no reward without concrete impact): internal IP disclosure, missing headers/flags, clickjacking, HTTPS mixed content, expired certs
