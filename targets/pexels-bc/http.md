# Pexels (Canva)

> Platform: Bugcrowd — https://bugcrowd.com/engagements/pexels
> Type: BBP (partial safe harbor)
> Bounty: P1=$6000, P2=$2500, P3=$850, P4=$100
> Status: In progress (since Dec 2020)

## Scope

### In Scope
- in: pexels.com (target table didn't render — check program page for specific targets)
- NOTE: Program is operated by Canva team — any Canva domain property not listed is OOS

### Out of Scope
- out: Rate limiting bypass (except OTP control bypass)
- out: Generic third-party provider issues: pagely.com, zendesk.com, mandrillapp.com
- out: Noisy automated tools (rate limit: 1 request/second max)
- out: DoS, Phishing, Physical attacks, rubber hose
- out: Credential/cookie/API key dorking (report but do NOT validate)
- out: ID enumeration without further impact
- out: Non-sensitive info disclosure, version disclosure without PoC
- out: Methods to bypass review of uploaded content (anti-abuse, not security)
- out: P4 and below (only P3+ paid currently)

## Auth

- type: web_app
- creds: Sign up using @bugcrowdninja.com email (MANDATORY — other emails may result in removal)

## Notes

- status: ACTIVE (53 vulns rewarded)
- Operated by Canva team
- Nondisclosure: NO public disclosure allowed
- Only P3 and higher paid
- Focus on demonstrating REAL impact — not alert boxes but cookie/session theft
- AWS and Cloudflare configuration issues are welcome (within reason)
- Partial safe harbor

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
