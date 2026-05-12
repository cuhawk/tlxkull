# colined — Colined Bug Bounty (Bugcrowd)

platform: bugcrowd
program_url: https://bugcrowd.com/engagements/colined
category: bbp
safe_harbor: partial
disclosure: coordinated (explicit permission required before disclosure)
part_of: Atlassian Marketplace Bounty Program

## Rewards

| P1 | P2 | P3 | P4 |
|----|----|----|----|
| $1,500 | $900 | $300 | $100 |

## Scope

### In-scope targets (Atlassian Marketplace apps — install into your own Jira instance)

- in: Pivot Report Cloud (https://marketplace.atlassian.com/search?query=pivot+report+colined) — type: atlassian_app
- in: Pivot Report Server/DC — type: atlassian_app
- in: Worklogs Report Cloud — type: atlassian_app
- in: Worklogs Report Server/DC — type: atlassian_app

## Instance Setup

Create test Jira Cloud instance at: https://www.atlassian.com/try/cloud/signup?bundle=jira-software
Instance namespace: bugbounty-test-<bugcrowd-username>.atlassian.net
Install apps from Marketplace into your own instance.

## Testing Notes

- Part of Atlassian Marketplace Bounty Program
- Two independent developers; 30+ years combined experience
- Use @bugcrowdninja.com email address
- No automated scanners (prohibited, will be banned)
- Do NOT create support requests at colined platform or post Atlassian Marketplace reviews
- Reports must be plain text (no PDF/DOCX)
- Only latest version of products eligible for reward
- Cross Instance Data Leakage/Access is top focus area
- ACV (Access Control Vulnerabilities) reports reviewed with caution — Atlassian is changing permissions API
- Coordinated disclosure required (written consent before public disclosure)
- Transitioned to public from private: Apr 16, 2026

## OOS

- Atlassian platform itself (test only apps within your own instance)
- Customer cloud instances and data
- Atlassian Connect Express application code and its dependencies
- Admin-defined arbitrary HTML templates (admin-only = OOS for XSS)
- Rate limiting, automated scanner findings
- Logout CSRF, self-XSS, clickjacking, content spoofing
- Missing headers, SSL/TLS issues, SPF/DKIM/DMARC
- Source code disclosure, non-confidential info disclosure
- Legacy browser-only vulns
- Pivoting/post-exploitation
