# Mattermost Public Bug Bounty Engagement

> Platform: Bugcrowd — https://bugcrowd.com/engagements/mattermost-mbb-public
> Type: BBP
> Bounty: P1 $2000 | P2 $750 | P3 $300 | P4 $150
> Status: In progress (started Nov 06, 2024)

## Scope

- in:  https://play.google.com/store/search?q=mattermost&c=apps   # type: android_app
- in:  https://apps.apple.com/us/app/mattermost/id1257222717   # type: ios_app
- in:  https://mattermost.com/apps/   # type: url
- in:  https://bugcrowd-*your-own-instance*.cloud.mattermost.com/   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-jira   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-zoom   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-github   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-gitlab   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-calls   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-playbooks   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-boards   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-ai   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-mscalendar   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-msteams-meetings   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-confluence   # type: url
- in:  https://github.com/mattermost/mattermost-plugin-msteams   # type: url
- out: about.mattermost.com   # type: domain
- out: integrations.mattermost.com   # type: domain
- out: docs.mattermost.com   # type: domain
- out: academy.mattermost.com   # type: domain
- out: developers.mattermost.com   # type: domain
- out: forum.mattermost.com   # type: domain

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
