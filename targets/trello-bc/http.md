# Trello Bug Bounty (Atlassian)

## Target
- program: trello (Bugcrowd)
- category: bbp
- started: Aug 16, 2018

## Bounties
- P1: $12,000
- P2: $4,000
- P3: $325
- P4: $250

## Scope
- in: trello.com (main web app)
- in: Trello Mobile App for iOS
- in: Trello Mobile App for Android
- in: Trello Desktop Client
- in: butlerfortrello.com
- in: Trello Third Party Powerups (case-by-case, no guaranteed reward — must affect Trello customers outside the powerup)
- out: customer instances and customer data
- out: blog.trello.com (unless PoC shows compromise of user data on trello.com)
- out: trello-attachments.s3.amazonaws.com, e.trello.com, help.trello.com, other unlisted subdomains
- out: Trello billing system (only specific endpoints called from in-scope targets)
- out: internal/development services

## Auth
- Create unlimited accounts on trello.com using @bugcrowdninja.com email
- Only test against your own accounts and data

## Scoring Notes
- Atlassian uses CVSS to determine priority (CVSS overrides VRT on discrepancies)
- These are scored as P4 regardless of CVSS:
  - XSS blocked by CSP (unless bypass documented)
  - Open Redirect bugs
  - Broken Access Control where Admin → System Admin escalation

## OOS Findings
- Automated scanners (strictly prohibited, will be removed from program)
- Descriptive error messages / stack traces
- HTTP 404 / non-200 pages
- Fingerprinting/banner disclosure
- robots.txt / public file disclosure
- Clickjacking (including clickjacking-only exploits)
- CSRF on anonymous forms or requiring CSRF token knowledge
- Logout CSRF
- Content Spoofing
- Autocomplete/save password
- Missing secure/HttpOnly cookies
- Missing security headers (HSTS, X-Frame-Options, CSP, etc.)
- HTTP/DNS cache poisoning
- SSL/TLS issues (BEAST, BREACH, weak ciphers, etc.)
- DoS/DDoS/load testing
- Self-XSS
- XSS requiring local access (User-Agent injection, etc.)
- Bugs in unsupported browsers
- Known vulnerable libraries without proof of exploitability
- Missing/incorrect SPF records
- Source code disclosure
- Non-confidential info disclosure (issue IDs, project IDs, commit hashes)
- Upload/download of malicious files
- Email bombing, flooding, rate limiting, CSV injection

## Rules
- Non-destructive testing only — do not affect customer data
- Do not access customer instances
- If you find credentials/API keys in the wild, report but do not validate
- Reports in plain text only (no PDF/DOCX)
- Group sufficiently similar access control issues in one report

## Disclosure
- Coordinated; disclosure on request after fix released in production
- Must not involve customer instance/data

## Notes
- Trello Third Party Powerups: payout determined partly by number of board installs (updated Oct 2025)
- Full safe harbor
