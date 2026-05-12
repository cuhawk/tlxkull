# Atlassian-Built Apps

> Platform: Bugcrowd — https://bugcrowd.com/engagements/atlassianapps
> Type: BBP
> Bounty: See tiers below
> Status: In progress (since Jun 2020)
> Part of Atlassian Marketplace Bounty Program

## Scope

### In Scope — Atlassian Marketplace Apps (installed on your test instance)
NOTE: Targets are Atlassian-developed marketplace apps. Target tables didn't render — check the program page for the full list (200+ targets).
Known recent activity targets:
- in: marketplace.atlassian.com/apps/1234673/jsm-incident-timeline?hosting=cloud (JSM Incident Timeline)
- in: marketplace.atlassian.com/apps/1235122/event-sign-up-for-confluence?hosting=cloud (Event Sign-up for Confluence)
- in: marketplace.atlassian.com/apps/1235496/jira-board-buddy?hosting=cloud (Jira Board Buddy)

### Reward Tiers
Preinstalled Apps in Jira/Confluence (System apps, admin-restricted):
- P1=$4000, P2=$1500, P3=$250, P4=$175

Atlassian Apps (standard):
- P1=$1800, P2=$1000, P3=$175, P4=$100

Trello Power-Ups (made by Trello):
- P1=$1800, P2=$1000, P3=$175, P4=$100

Third Party Apps: case-by-case, no guaranteed reward (only P1 critical may be considered)

### Special Scoring Notes
- Open Redirect bugs: scored as P4 (not P3 despite CVSS)
- Admin-to-SysAdmin privilege escalation: scored as P4
- XSS on Server instances requiring admin privileges: P5/informational/points only
- CVSS overrides VRT where discrepancies exist (Atlassian uses CVSS)

### Focus Areas (specific to Atlassian apps)
- Cross Instance Data Leakage/Access (unauthorized data access between instances)
- Server-side RCE, SSRF, Stored/Reflected XSS, CSRF, SQLi, XXE
- IDOR/Access Control Vulnerabilities, Path/Directory Traversal
- Connect App Authorization Bypass
- Shared Secret Leakage

### Out of Scope
- out: Atlassian products/services (report to main Atlassian program)
- out: Customer cloud instances and data
- out: Atlassian billing system (unless endpoint called from target app)
- out: Enumeration/information gathering (it's a collaboration tool feature)
- out: JWT in URL (known/accepted platform issue)
- out: App identification (part of Atlassian Connect threat model)
- out: Automated scanners (will result in removal)
- out: Rate limiting, DoS, Self-XSS, Clickjacking, Logout CSRF, Missing headers

## Auth

- type: atlassian_cloud_instance
- creds: Use @bugcrowdninja.com email, namespace bugbounty-test-<bugcrowd-name>.atlassian.net
- creds: Do NOT create instances outside this namespace

## Notes

- status: ACTIVE (231+ vulnerabilities rewarded, avg payout $882)
- Same vulnerability across hosting types: may pay only once if same codebase/fix
- Apps with distinct listings but same codebase: pay once (e.g., Opsgenie Incident Timeline and EU variant)
- Any OOS finding can still be reported — rewarded at Atlassian Security Team discretion
- Third party app finds: forwarded to vendor's BBP if one exists
- Atlassian's Bugcrowd Landing Page lists accessible vendor BBP programs

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
