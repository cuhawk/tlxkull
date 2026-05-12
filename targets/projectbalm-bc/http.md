# projectbalm — ProjectBalm Bug Bounty (Atlassian Marketplace)

**Platform:** Bugcrowd BBP  
**Program URL:** https://bugcrowd.com/engagements/projectbalm  
**Started:** Jul 07, 2020  
**Disclosure:** Coordinated (explicit permission required before public disclosure)  
**Safe Harbor:** Partial  

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

- Create Jira Cloud instance: `bugbounty-test-<bugcrowd-name>.atlassian.net`
- Navigate to checkout, click Next, enter `bugbounty-test-<bugcrowd-name>` as instance name
- In Jira Settings > Apps, search "Risk Register" and install (Try it free)
- Do NOT access customer instances in any way

---

## In-Scope Target

- in: https://marketplace.atlassian.com/apps/1213146/risk-register?hosting=cloud (Website Testing)

---

## Product

ProjectBalm Risk Register — Jira Cloud app for recording risks, assessing magnitude, assigning to team members, collaborating on treatment.

---

## Focus Areas

Server Security Misconfiguration, Server-Side Injection, Broken Authentication/Session Management, Sensitive Data Exposure, XSS, Broken Access Control, CSRF, Application-Level DoS, Client-Side Injection, Unvalidated Redirects, Insecure Data Storage/Transport

---

## Out-of-Scope

- Any domain/property of ProjectBalm not listed in targets
- Using components with known vulnerabilities
- Customer instances/data
- Automated scanners (leads to removal from program)
- Non-plain-text reports (PDF/DOCX rejected)
- Social engineering, phishing, physical security tests

---

## Notes

- Part of the Atlassian Marketplace Bounty Program
- Grants at discretion of ProjectBalm
- Bounty withdrawn if publicly disclosed without written consent
