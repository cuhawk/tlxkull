# Sky Italy Vulnerability Disclosure Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/sky-plc-mbb-og1
> Type: BBP
> Bounty: P1 $500–$1000
> Status: In progress

## Scope

- # TODO: scope not loaded — re-scrape with scroll

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- disclosure: standard Bugcrowd terms
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## In-Scope Targets

- in: All internet facing Sky Italy assets (GraphQL, Website Testing)

## Out-of-Scope Explicit Domains/Subsidiaries

- out: *skybroadband.com (subscriber-hosted, OOS)
- out: *skybet.com
- out: *skynewsarabia.com
- out: *skynews.com.au
- out: *safetytraining.sky.it
- out: All internet facing Sky UK/ROI assets (separate program)
- out: All internet facing Sky DACH assets (separate program)
- out: NBCUniversal (report to cyber@nbcuni.com)
- out: Comcast
- out: Sky Excluded IPs.xlsx (downloadable IP exclusion list)

## Program Details

**Started:** Jan 01, 2026  
**Disclosure:** Coordinated (explicit permission required)  
**Safe Harbor:** Yes (CFAA + DMCA exempt)  
**Validation:** ~4 days (fast turnaround)  
**Average payout:** $250 (last 3 months)  

## Custom Header Required

Add to all HTTP traffic: `X-Bug-Bounty: <bugcrowdusername>`  
Provide IP address in P1/P2 report submissions.

## N-Day Policy

N-day bugs in scope 30 days after public release.

## Key OOS Submission Types

- 3rd party endpoints / brand licensing / marketing analytics
- CSRF on unauthenticated forms
- Open redirect without additional impact
- Self-XSS, Flash XSS
- CORS without exploitation
- Swagger-UI XSS (accepted as P5/informational, not eligible for bounty)
- SSL/TLS scan reports
- Email spoofing (SPF/DKIM/DMARC)
- No PoC automated scan reports
- Dark web/OSINT credential leaks (points only, not cash)
- Load testing / DoS / DDoS
