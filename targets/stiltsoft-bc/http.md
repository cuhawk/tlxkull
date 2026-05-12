# Stiltsoft Bug Bounty — Bugcrowd BBP

**Program URL:** https://bugcrowd.com/engagements/stiltsoft  
**Category:** Computer Software / Safe harbor  
**Status:** ACTIVE  
**Started:** Jul 14, 2020  
**Part of:** Atlassian Marketplace Bounty Program  
**Nondisclosure:** YES (no public disclosure without written consent)

---

## Reward Tiers

### High-Priority Targets
| Priority | Reward |
|----------|--------|
| P1 | $3,000 |
| P2 | $1,800 |
| P3 | $600 |
| P4 | $200 |

### Other In-Scope Targets
| Priority | Reward |
|----------|--------|
| P1 | $1,500 |
| P2 | $900 |
| P3 | $300 |
| P4 | $100 |

---

## In-Scope Targets (Atlassian Marketplace Apps)

- in: https://marketplace.atlassian.com/apps/27447/table-filter-and-charts-for-confluence?hosting=cloud  # Table Filter and Charts for Confluence (Cloud)
- in: https://marketplace.atlassian.com/apps/27447/table-filter-and-charts-for-confluence?hosting=datacenter  # Table Filter and Charts for Confluence (Data Center)
- in: https://marketplace.atlassian.com/apps/1213965/courses-and-quizzes-lms-for-confluence?hosting=cloud  # Courses and Quizzes - LMS for Confluence (Cloud)
- in: https://marketplace.atlassian.com/apps/1210934/awesome-graphs-for-bitbucket?hosting=cloud  # Awesome Graphs for Bitbucket (Cloud)
- in: https://marketplace.atlassian.com/apps/1210934/awesome-graphs-for-bitbucket?hosting=datacenter  # Awesome Graphs for Bitbucket (Data Center)
- in: https://marketplace.atlassian.com/apps/1213500/teamcity-integration-for-jira?hosting=cloud  # TeamCity Integration for Jira (Cloud)
- in: https://marketplace.atlassian.com/apps/1214971/handy-macros-for-confluence?hosting=cloud  # Handy Macros for Confluence (Cloud)
- in: https://marketplace.atlassian.com/apps/1214971/handy-macros-for-confluence?hosting=datacenter  # Handy Macros for Confluence (Data Center)
- in: https://marketplace.atlassian.com/apps/1216031/spreadsheet-issue-field-editor  # Spreadsheet Issue Field Editor
- in: https://marketplace.atlassian.com/apps/1215249/smart-attachments-for-jira?hosting=cloud  # Smart Attachments for Jira (Cloud)
- in: https://marketplace.atlassian.com/apps/1216119/webhook-manager-for-confluence?hosting=cloud  # Webhook Manager for Confluence (Cloud)
- in: https://marketplace.atlassian.com/apps/1216278/latex-math-for-confluence?hosting=cloud  # LaTeX Math for Confluence (Cloud)
- in: https://marketplace.atlassian.com/apps/1215986/checklist-for-jira-cloud?hosting=cloud  # Checklist for Jira Cloud | Smart ToDo Lists (Cloud)
- in: https://marketplace.atlassian.com/apps/1216523/live-tables-from-csv-json-for-confluence  # Live Tables from CSV & JSON for Confluence

**Testing target:** Install apps in your own Atlassian instance (do NOT test marketplace.atlassian.com itself)

---

## Out-of-Scope

- out: marketplace.atlassian.com (do not test; only install apps from here)
- out: Any StiltSoft website not directly accessible from a target
- out: Customer cloud instances and data
- out: Any internal or development services
- out: Repositories you do not own

---

## Instance Setup

**Jira + Confluence Cloud namespace:** `bugbounty-test-<bugcrowd-name>.atlassian.net`

Steps:
1. Navigate to checkout page → Click "Next"
2. Use format: `bugbounty-test-<bugcrowd-name>` (replace with your Bugcrowd username)
3. Click "Start now"

**Confluence Data Center:** Download from atlassian.com, generate trial license, install app with `[username]@bugcrowdninja.com`

**Bitbucket Cloud:** https://bitbucket.org/ — sign up with @bugcrowdninja.com, install Awesome Graphs

**Bitbucket Data Center:** Download from atlassian.com, generate trial license, install app

---

## Rules & Constraints

- Use @bugcrowdninja.com email for all accounts
- Do NOT post reviews on marketplace.atlassian.com (disqualification + ban from Atlassian programs)
- Do NOT test marketplace.atlassian.com itself
- Only latest version of Server/DC app eligible for reward
- No cross-platform double-dipping (Cloud vuln != Server/DC vuln for same reward)
- No automated scanners (strictly prohibited)
- No pivoting/post-exploitation
- Reports in plain text only (no PDF/DOCX)

---

## Focus Areas

- Cross Instance Data Leakage/Access (unauthorized data between instances)
- Server-side RCE
- SSRF
- Stored/Reflected XSS
- CSRF
- SQLi
- XXE
- Access Control / IDOR
- Path/Directory Traversal

---

## Notes

- Awesome Graphs Bitbucket Cloud REST APIs use long-lived 1-year JWTs — verify token forgery, expiry enforcement, revocation
- Table from CSV macro: credential copy prevention setting — test access after permission revocation
- CVSS used for scoring where VRT and CVSS diverge
