# Nextup.ai

> Platform: Bugcrowd — https://bugcrowd.com/engagements/nextupai
> Type: BBP
> Bounty: P1=$1500, P2=$900, P3=$300, P4=$100
> Status: PAUSED (since Feb 5 2023 — pause all testing until further notice)
> Note: Part of Atlassian Marketplace Bounty Program.

## Scope

### In Scope — Slack/Jira/Confluence Apps (install on own Atlassian instance)

- in: https://marketplace.atlassian.com/apps/1219324/slack-integration-for-jira?hosting=cloud
  type: webapp
  note: Slack Integration+ for Jira. Use own test instance: bugbounty-test-<bugcrowd-name>.atlassian.net
- in: https://marketplace.atlassian.com/apps/1227628/microsoft-teams-integration-for-jira?hosting=cloud
  type: webapp
  note: Microsoft Teams Integration for Jira
- in: https://marketplace.atlassian.com/apps/1227656/docs-slack-for-confluence?hosting=cloud
  type: webapp
  note: Docs/Slack for Confluence

### Out of Scope

- out: The Atlassian Marketplace listing pages themselves (only the app is in scope)
- out: Customer cloud instances and data
- out: Any Nextup website not directly accessible from target
- out: Automated scanners (strictly prohibited)
- out: Lack of rate limiting

## Auth

- type: session
- creds: env:BUGCROWD_NINJA_EMAIL
- note: Create own Jira+Confluence instance at bugbounty-test-<bugcrowd-name>.atlassian.net, then install app from Marketplace

## Notes

- status: PAUSED (Feb 5 2023, indefinitely)
- atlassian_marketplace: true
- instance_namespace: bugbounty-test-<bugcrowd-name>.atlassian.net

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
