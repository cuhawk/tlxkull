# Atlassian Bug Bounty

- platform: bugcrowd
- program_url: https://bugcrowd.com/engagements/atlassian
- category: Computer Software
- safe_harbor: full
- nondisclosure: false
- scope_rating: 4/4
- started: 2023-11-06

## Rewards

| Priority | Tier 1 | Rovo/AI | Tier 2/Loom/Forge | Tier 3 |
|---|---|---|---|---|
| P1 | $12000 | $12000 | $7000 | $4000 |
| P2 | $4000 | $6000 | $2500 | $1500 |
| P3 | $325 | $325 | $250 | $175 |
| P4 | $250 | $250 | $175 | $100 |

## Targets

### Tier 1 - Cloud Products (bugbounty-test-<bugcrowd-name>.atlassian.net)
- in: bugbounty-test-<bugcrowd-name>.atlassian.net  # type: wildcard  # Jira + Confluence Cloud instance
- in: https://bitbucket.org/  # type: url  # Bitbucket Cloud

### Tier 1 - Data Center Products (local install, latest version)
- in: Jira Software Data Center  # type: software  # https://www.atlassian.com/software/jira/download
- in: Confluence Data Center  # type: software
- in: Bitbucket Data Center  # type: software
- in: Crowd Data Center  # type: software
- in: Bamboo Data Center  # type: software

### Rovo & AI Features
- in: Rovo Chat  # type: feature
- in: Rovo Search / Rovo Connectors  # type: feature
- in: Rovo Studio / Rovo Agents / Rovo Forge Agents  # type: feature
- in: Rovo Browser Extension  # type: feature
- in: Rovo Slack App  # type: feature
- in: Atlassian MCP Server  # type: feature
- in: Rovo Dev Code Reviews  # type: feature
- in: Rovo Dev CLI  # type: feature
- in: Atlassian Extension for VSCode  # type: feature

### Tier 2 - Loom
- in: https://www.loom.com/  # type: url
- in: *.loom.com  # type: wildcard

### Atlassian Forge
- in: Forge Platform  # type: feature  # https://developer.atlassian.com/platform/forge/
- in: Forge CLI  # type: feature  # https://www.npmjs.com/package/@forge/cli

### Tier 3 - Other Products
- in: Crucible  # type: software
- in: Fisheye  # type: software
- in: Sourcetree  # type: software

### Mobile
- in: https://apps.apple.com/app/jira-cloud-by-atlassian/id1006972087  # type: ios_app  # Jira Cloud iOS
- in: https://play.google.com/store/apps/details?id=com.atlassian.android.jira.core  # type: android_app  # Jira Cloud Android
- in: https://apps.apple.com/app/confluence-for-jira-cloud/id1288365159  # type: ios_app  # Confluence Cloud iOS
- in: https://play.google.com/store/apps/details?id=com.atlassian.confluence.server  # type: android_app  # Confluence Cloud Android

## Out of Scope
- out: *.atlassian.net  # type: wildcard  # customer instances — only your own bugbounty-test namespace
- out: *.jira.com  # type: wildcard  # customer instances
- out: Atlassian billing system  # type: note

## Auth / Testing Notes

- Cloud instance naming: bugbounty-test-<bugcrowd-name>.atlassian.net
- Use @bugcrowdninja.com email for registration
- Data Center: download latest version, generate trial license at my.atlassian.com
- No automated scanners (will result in removal from program)
- No pivoting/post-exploitation attacks
- Customer instances explicitly out of scope
- XSS blocked by CSP → P4; XSS on DC requiring admin → P5 (points only)
- Open redirects → P4
- Focus: Cross Instance Data Leakage, RCE, SSRF, XSS, CSRF, SQLi, XXE, IDOR
