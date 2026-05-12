# programmer-hat-market — Programmer Hat Marketplace Bug Bounty Program (Atlassian Marketplace)

**Platform:** Bugcrowd BBP  
**Program URL:** https://bugcrowd.com/engagements/programmer-hat-market  
**Started:** Jun 04, 2024  
**Disclosure:** Coordinated (explicit permission required before public disclosure)  
**Safe Harbor:** Yes (CFAA + DMCA exempt)  

---

## Rewards

| Priority | Reward |
|----------|--------|
| P1 | $1,500 |
| P2 | $900 |
| P3 | $300 |
| P4 | $100 |

---

## Authentication

- Create Atlassian Cloud instance: `bugbounty-test-<bugcrowd-name>.atlassian.net`
- Do NOT create additional instances outside of this namespace
- Use @bugcrowdninja.com email
- Navigate to checkout, use format `bugbounty-test-<bugcrowd-name>` as instance name

**CRITICAL:** Customer instances and customer data are explicitly out of scope — do not access them in any way.

---

## In-Scope Targets (Atlassian Marketplace Jira Plugins — Cloud)

- in: Create Ticket Template, Issue Template, Easy Templates — https://marketplace.atlassian.com/apps/1233451/ (Atlassian Forge, ReactJS, NodeJS)
- in: Export Backlog to CSV, Excel — https://marketplace.atlassian.com/apps/1233695/ (Atlassian Forge, ReactJS, NodeJS)
- in: Rich Text Editor for Jira — https://marketplace.atlassian.com/apps/1233647/ (Atlassian Forge, ReactJS, NodeJS)
- in: Email This Issue for Jira — https://marketplace.atlassian.com/apps/1233583/ (Laravel, Jira, Atlassian Forge)
- in: Mail Handler for Jira, Service Desk, Service Management — https://marketplace.atlassian.com/apps/1233836/ (Atlassian Forge, ReactJS, NodeJS)
- in: Basecamp Integration for Jira — https://marketplace.atlassian.com/apps/1234316/ (Laravel, Atlassian Forge, ReactJS)

Only latest versions of products are eligible for reward.

---

## Focus Areas

- Cross Instance Data Leakage/Access (unauthorized data access between instances)
- Server-side Remote Code Execution (RCE)
- Server-Side Request Forgery (SSRF)
- Stored/Reflected XSS
- CSRF
- SQL Injection (SQLi)
- XXE
- Access Control / IDOR
- Path/Directory Traversal

---

## Out-of-Scope Highlights

- Automated scanners strictly prohibited (will be removed from program)
- Any Programmer Hat website (e.g. programmerhat.com) unless directly accessible from a target
- Customer cloud instances and data
- No pivoting/post-exploitation
- Self-XSS, User-Agent injection XSS
- Blind XSS must not capture data not owned by tester
- DoS/DDoS/load testing
- Missing HTTP security headers, SSL/TLS issues
- Username/email enumeration
- Logout CSRF
- Clickjacking
- CSRF on anonymous-accessible forms
- Generic 3rd-party library versions without PoC
- Non-plain text reports (PDF/DOCX rejected)

---

## Notes

- Part of the Atlassian Marketplace Bounty Program — Jira plugins
- Grants at discretion of Programmer Hat; tax implications on reporter
- Do not conduct social engineering, phishing, physical security tests
