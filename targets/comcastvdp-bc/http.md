# comcastvdp — Comcast Xfinity Vulnerability Disclosure Program (Bugcrowd BBP)

> P1 rewards only. All Comcast Xfinity and Comcast Business services/products in scope.
> Must add header X-Bug-Bounty:<bugcrowdusername> to all HTTP traffic.
> Provide your IP address in report for P1/P2 findings.

## Program info
- URL: https://bugcrowd.com/engagements/comcastvdp
- Type: bug_bounty (VDP with P1-only rewards)
- Scope rating: 2/4
- Started: May 04, 2018
- Expedited triage

## Rewards
- P1: $1,250 – $3,500 (only valid P1 submissions rewarded)
- P2-P4: not eligible for rewards

## In scope
- type: web
  url: *.xfinity.com
  notes: All technologies, products, and services that Comcast Xfinity provides
- type: web
  url: *.comcast.com
  notes: All Comcast Business services
- type: web
  url: *.comcastbusiness.net
  notes: (excluding customer-hosted IPs - *.hfc.comcastbusiness.net)
- notes: All endpoints called by Comcast/Xfinity services are in-scope (confirm if unsure)

## Out of scope
- NBCUniversal (report to cyber@nbcuni.com)
- Sky
- 3rd party endpoints / marketing/analytics endpoints
- Residential/business customer IP ranges: 10.0.0.0/8, 50.128.0.0/12, 50.152.0.0/13, etc.
- Customer-hosted: *.hsd1.*.comcast.net, *.hfc.comcastbusiness.net
- CSRF on unauthenticated forms, open redirects (without additional impact)
- Self-XSS, XSS requiring Flash
- CORS without exploitation
- Swagger-UI XSS (P5 informational, no bounty)
- SPF/DKIM/DMARC email spoofing
- DoS/DDoS/load testing
- Subdomain takeover: downgraded P2->P3

## Notes
- Required HTTP header: X-Bug-Bounty:<bugcrowdusername>
- N-day policy: in scope 30 days after public release
- No test accounts provided; do not access customer data
- Contact: SecurityDefectReporting@comcast.com for clarifications
