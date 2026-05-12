# codefortynine

> Platform: Bugcrowd — https://bugcrowd.com/engagements/codefortynine
> Type: BBP
> Bounty: P1 $1500 | P2 $900 | P3 $300 | P4 $100
> Status: In progress

## Scope

- in:  https://marketplace.atlassian.com/apps/1218652/deep-clone-for-jira?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1219514/merge-agent-for-jira?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1220136/quick-filters-for-jira-dashboards?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1219476/comment-custom-fields-for-jira?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1221733/external-data-for-confluence?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1219288/comment-history-log-for-jira?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1215055/slack-for-confluence?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1219807/version-sync-for-jira?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1220964/snipe-it-for-jira?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1218211/secure-google-calendar-for-confluence?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1219994/external-data-for-jira-fields?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1232630/external-data-for-jira-fields-extension?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1222978/dynamic-fields-for-jira?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1223455/advanced-bulk-edit-for-jira?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1226627/prime-custom-fields-for-jira?hosting=cloud   # type: url
- in:  https://marketplace.atlassian.com/apps/1230689/easy-confluence-gadget-for-jira-dashboards?hosting=cloud   # type: url
- out: codefortynine.atlassian.net   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Instance Setup

Create test Jira Cloud instance at: https://www.atlassian.com/try/cloud/signup?bundle=jira-software
Instance namespace: bugbounty-test-<bugcrowd-username>.atlassian.net
Install apps from Marketplace into your own instance — do NOT test on codefortynine.atlassian.net

## Notes

- Part of the Atlassian Marketplace Bounty Program
- Use @bugcrowdninja.com email
- Do NOT create support requests on codefortynine.atlassian.net (removal risk)
- Do NOT post reviews on marketplace.atlassian.com (removal risk)
- No automated scanners (prohibited, will be banned)
- CVSS score takes precedence over VRT when discrepancies exist
- Cross Instance Data Leakage/Access is top priority target
- Only latest version of apps eligible for reward
- Reports must be plain text (no PDF/DOCX)
- Coordinated disclosure required (permission needed before public disclosure)
- Nondisclosure
