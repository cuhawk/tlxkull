# plugin-people — The Plugin People (Bugcrowd BBP)

> **TYPE: Atlassian Marketplace Add-on** — Enterprise Mail Handler for Jira (JEMH) — Cloud and DataCenter editions.
> Scope is the add-on ONLY, NOT Atlassian platform/services.
> Must install add-on in your own Atlassian Jira Cloud/DataCenter test instance.
> Test instance namespace: `bugbounty-test-<bugcrowd-name>.atlassian.net`

## Program info
- URL: https://bugcrowd.com/engagements/plugin-people
- Type: bug_bounty (Atlassian Marketplace add-on)
- Scope rating: 1/4
- Started: Aug 18, 2020

## Rewards
### Cloud hosted Enterprise Mail Handler (JEMHC)
- P1: $1,500
- P2: $900
- P3: $300
- P4: $100

### Self hosted Enterprise Mail Handler (DataCenter)
- P1: $1,500 – $1,800
- P2: $900 – $1,200
- P3: $300 – $600
- P4: $100 – $200

## In scope
- type: web
  url: https://marketplace.atlassian.com/apps/4832/enterprise-mail-handler-for-jira-jemh?hosting=cloud
  notes: JEMHC app deployed in your Atlassian Jira Cloud test instance
- type: web
  url: Enterprise Mail Handler for Jira DataCenter (self-hosted)
  notes: JEMH installed in self-hosted Jira DataCenter instance

## Out of scope
- Atlassian platform services (marketplace.atlassian.com, id.atlassian.com, team.atlassian.com, admin.atlassian.com, my.atlassian.com)
- thepluginpeople.atlassian.net/wiki (documentation)
- Customer cloud instances and data
- Any Atlassian supporting systems

## Notes
- Automated scanners strictly prohibited
- Plain text reports only
- DataCenter: Use Timebomb/eval licenses; test instance via Jira > System > Find Apps
- Cloud: Create test instance at bugbounty-test-<username>.atlassian.net, install JEMHC from marketplace
- JEMHC outbound notification templates are not considered RCE even if user-editable
