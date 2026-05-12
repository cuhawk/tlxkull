# Slack

> Platform: HackerOne — https://hackerone.com/slack
> Type: BBP
> Bounty: Low $500 | Medium $8,000 | High $13,000 | Critical $17,000
> Avg bounty: $500–$500
> Response efficiency: 99% | Avg first response: N/A | Total paid: $2,697,370
> Last scope update: 2026-03-11

## Scope

- in:  slack.com    # type: url # max: critical
- in:  api.slack.com    # type: url # max: critical
- in:  slackb.com    # type: url # max: critical
- in:  app.slack.com    # type: url # max: critical
- in:  edgeapi.slack.com    # type: url # max: critical
- in:  slackatwork.com    # type: url # max: critical
- in:  slack-redir.net    # type: url # max: critical
- in:  slack-imgs.com    # type: url # max: critical
- in:  spaces.pm    # type: url # max: critical
- in:  www.quip.com    # type: url # max: critical
- in:  *.quip.com    # type: url # max: critical
- in:  slack-status.com    # type: url # max: critical
- in:  https://github.com/slackhq/nebula    # type: repo # max: critical
- in:  Slack Desktop Application    # type: other # max: critical
- in:  com.Slack    # type: android_app # max: critical
- in:  https://salesforce.quip.com/blog/desktop    # type: downloadable_executables # max: critical
- in:  com.tinyspeck.chatlyio    # type: ios_app # max: critical
- in:  com.slack.slackmdm    # type: ios_app # max: critical
- in:  https://apps.apple.com/us/app/quip-docs-chat-sheets/id647922896    # type: ios_app # max: critical
- in:  com.quip.quip    # type: android_app # max: critical
- in:  647922896    # type: ios_app # max: critical
- out:  status.slack.com    # type: url # max: none
- out:  *.glitchthegame.com    # type: url # max: none
- out:  slackhq.com    # type: url # max: none
- out:  3rd Party Quip Apps    # type: other # max: none
- out:  com.Slack.intune    # type: android_app # max: none
- out:  com.slack.slackintune    # type: ios_app # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $2,697,370
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
