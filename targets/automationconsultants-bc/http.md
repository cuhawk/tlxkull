# AppFox (Automation Consultants) — Bugcrowd

**URL:** https://bugcrowd.com/engagements/automationconsultants
**Category:** BBP
**Safe harbor:** Yes
**Disclosure:** Coordinated (explicit permission required)
**Started:** 2020-07-07
**Note:** Part of Atlassian Marketplace Bounty Program

## Targets (P1=$1,500)

### Atlassian Cloud Apps
- in: Approvals for Confluence Cloud
- in: Votes for Confluence Cloud
- in: Compliance for Confluence Cloud
- in: Optimizer for Jira Cloud
- in: Workflows for Confluence Cloud
- in: Captionizer (AI Image Analyzer) — https://marketplace.atlassian.com/apps/1237517/captionizer-ai-image-analyzer (added Oct 2025)

## Rewards
| Priority | Amount |
|----------|--------|
| P1 | $1,500 |
| P2 | $900 |
| P3 | $300 |
| P4 | $100 |

CVSS used — where VRT and CVSS conflict, CVSS takes precedence.

## Auth / Instance Setup
- Navigate to checkout, use format `bugbounty-test-<bugcrowd-username>` for site name
- Use @bugcrowdninja.com email
- Do NOT create instances outside the `bugbounty-test-<bugcrowd-name>.atlassian.net` namespace

## Focus areas
- Cross Instance Data Leakage/Access (unauthorized data access between Atlassian instances)
- Server-side RCE
- SSRF
- Stored/Reflected XSS
- CSRF
- SQLi
- XXE
- IDOR / Access Control
- Path/Directory Traversal

## Out of scope
- Issues from Atlassian-provided APIs/apps (beyond AppFox control)
- Blind XSS returning data you don't own
- No pivoting/post-exploitation attacks
- Customer cloud instances and data
- Any Automation Consultants website not directly accessible from target
- Repositories you don't own
- Only latest product version eligible
- Internal/development services
- Rate limiting
- Automated scanners (strictly prohibited — will be removed from program)
- Stack traces / descriptive error messages
- Fingerprinting / banner disclosure
- Clickjacking
- Logout CSRF
- Content spoofing
- Autocomplete / save password
- Non-sensitive cookie flags
- Security speedbump
- CAPTCHA bypass
- Brute force / account lockout
- Username/email enumeration
- HTTP security headers (HSTS, X-Frame-Options, CSP, etc.)
- DNS/HTTP cache poisoning
- SSL/TLS issues (BEAST, BREACH, weak ciphers, forward secrecy)
- Self-XSS
- XSS requiring local access (unless off-path MiTM PoC shown)
- Old browser vulnerabilities
- Known vulnerable libraries without PoC
- Missing/incorrect SPF, DMARC
- Source code disclosure
- Non-confidential information disclosure (issue IDs, project IDs, commit hashes)
- Virus/malware upload
- Email bombing/flooding/rate limiting
- JWT in ajax ignoring path/HTTP method
- Admin-only arbitrary HTML template XSS

## Rules
- Reports in plain text only (no PDF/DOCX)
- Non-destructive testing on instances you own
- Do NOT access customer instances or data
- No automated tools
- Public disclosure requires written permission from Automation Consultants
- Bugs in Pulse for Jira Pro or Free: limited to 1 submission and reward
