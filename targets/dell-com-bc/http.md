# Dell Technologies Application Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/dell-com
> Type: BBP
> Bounty: See program page
> Status: In progress (started Jul 16, 2019)

## Scope

- in:  *.dell.com/* Bootstrap Modernizr ASP.NET   # type: wildcard
- in:  https://console.delltechnologies.com/nav/administration Website Testing   # type: url
- in:  https://console.delltechnologies.com/nav/invoice Website Testing   # type: url
- in:  https://console.delltechnologies.com/nav/billing Website Testing   # type: url
- out: https://console.delltechnologies.com/ Akamai CDN nginx ReactJS   # type: url
- out: https://console.delltechnologies.com/nav/catalog Website Testing   # type: url
- out: https://console.delltechnologies.com/nav/support Website Testing   # type: url
- out: https://console.delltechnologies.com/nav/subscriptions Website Testing   # type: url
- out: educate.dell.com   # type: domain
- out: console.dell.com   # type: domain
- out: console-test.dell.com   # type: domain
- out: salesproductivity.dell.com   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Notes
- DIFFERENT from dell-product (product hardware BBP) — this is web apps only
- Nondisclosure — public disclosure makes researcher ineligible for future programs
- No safe harbor mentioned — subject to Dell T&C
- Custom HTTP header required: `X-Bug-Bounty: Bugcrowd-<username>` in ALL traffic
- Do not submit checkout forms; stop at Review page — do NOT click Submit Order
- GitHub credentials initially rated P5; upgraded if real impact shown
- Unlisted Dell websites/services = P5 informational

## OOS submission types
- SSO session invalidation failure, DMARC, missing SPF
- No rate limiting / CAPTCHA
- 3rd party sites Dell doesn't own
- Out-of-date software without impact
- robots.txt/known public file disclosure
- Clickjacking
- API keys with no security impact / quota exhaustion only
- Internal IP disclosure
- Stack traces / tech stack disclosure
- Username/email enumeration
- Login/forgot-password brute force / account lockout / weak password
- Malicious file uploads not affecting server
- Cookies without HTTPOnly/Secure
- CSV formula injection
- CVEs published < 5 business days (unless Dell acts on report)
- Credential/token leaks from 3rd party sites without strong evidence of validity
- DoS/DDoS
- Automated scanner findings without analysis
- Open ports without PoC
- Old browser vulnerabilities
- Spam, phishing, social engineering
- Open redirect on SonicWall/similar
- Broken social media link hijacking

## XSS exceptions (OOS)
- https://www.dell.com/Identity/global/*
- https://www-poc.dell.com/Identity/*
- https://pilot.search.dell.com/Identity/global/*
- https://www.dell.com/sso/sm/*
