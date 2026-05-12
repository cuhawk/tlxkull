# codeclou GmbH

> Platform: Bugcrowd — https://bugcrowd.com/engagements/codeclou
> Type: BBP
> Bounty: P1=$1500, P2=$900, P3=$300, P4=$100
> Status: In progress (since Sep 2020, went public Feb 2026)
> Part of Atlassian Marketplace Bounty Program

## Scope

### In Scope — Atlassian Marketplace Apps
- in: marketplace.atlassian.com/apps/1212096/customfield-editor-for-jira (Customfield Editor for Jira - Data Center)
- in: marketplace.atlassian.com/apps/1212096/customfield-editor-for-jira?hosting=cloud (Customfield Editor for Jira - Cloud)
- in: marketplace.atlassian.com/apps/1211159/advanced-codeblocks-for-confluence?hosting=cloud (Advanced Codeblocks for Confluence - Cloud)
- in: marketplace.atlassian.com/apps/1211159/advanced-codeblocks-for-confluence?hosting=datacenter (Advanced Codeblocks for Confluence - Data Center)
- NOTE: The marketplace URLs themselves are NOT in scope — the installed app functionality is in scope

### Focus Areas
- Cross Instance Data Leakage/Access (unauthorized data access between instances)
- Server-side RCE, SSRF, Stored/Reflected XSS, CSRF, SQLi, XXE
- IDOR / Access Control Vulnerabilities, Path/Directory Traversal

### Out of Scope
- out: Customer instances and data (never access customer data)
- out: marketplace.atlassian.com URLs themselves (reporting URLs only)
- out: Automated scanner use (strictly prohibited, will result in removal)
- out: Self-XSS, Clickjacking, Logout CSRF, Content Spoofing, Rate limiting
- out: Missing security headers, Outdated libraries without proven exploitability
- out: Old app versions (only latest version eligible)

## Auth

- type: atlassian_cloud_instance
- creds: Use your own Atlassian instance at bugbounty-test-<bugcrowd-name>.atlassian.net
- creds: Data Center — download from atlassian.com, get evaluation license from my.atlassian.com, install app

## Notes

- status: ACTIVE (public since Feb 2026)
- Namespace: bugbounty-test-<bugcrowd-name>.atlassian.net (do NOT create instances outside this)
- No automated scanning, no pivoting/post-exploitation
- Reports must be plain text only

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
