# GitLab

> Platform: HackerOne — https://hackerone.com/gitlab
> Type: BBP
> Bounty: Low $750 | Medium $2,500 | High $15,000 | Critical $35,000
> Avg bounty: $1,000–$1,320
> Response efficiency: 93% | Avg first response: N/A | Total paid: $6,595,697
> Last scope update: 2023-06-13

## Scope

- in:  *.gitlab.net    # type: wildcard # max: medium
- in:  *.gitlab.org    # type: wildcard # max: medium
- in:  *.gitlap.com    # type: wildcard # max: medium
- in:  customers.gitlab.com    # type: url # max: critical
- in:  registry.gitlab.com    # type: url # max: critical
- in:  gitlab.com    # type: url # max: critical
- in:  about.gitlab.com    # type: url # max: medium
- in:  docs.gitlab.com    # type: url # max: medium
- in:  design.gitlab.com    # type: url # max: medium
- in:  advisories.gitlab.com    # type: url # max: medium
- in:  https://gitlab.com/gitlab-org/gitlab    # type: repo # max: critical
- in:  https://gitlab.com/gitlab-org/gitlab-runner    # type: repo # max: critical
- in:  https://gitlab.com/gitlab-org/gitaly    # type: repo # max: critical
- in:  https://gitlab.com/gitlab-org/gitlab-pages    # type: repo # max: critical
- in:  https://gitlab.com/gitlab-org/gitlab-shell    # type: repo # max: critical
- in:  https://gitlab.com/gitlab-org/gitlab-vscode-extension    # type: repo # max: critical
- in:  https://gitlab.com/gitlab-org/opstrace/opstrace    # type: repo # max: critical
- in:  Your Own GitLab Instance    # type: other # max: critical
- in:  Other non-production infrastructure    # type: other # max: medium
- in:  GitLab for Jira Cloud    # type: other # max: medium
- in:  GitLab for Jira Cloud Plugin    # type: other # max: critical
- in:  https://gitlab.com/gitlab-org/opstrace/    # type: repo # max: critical
- in:  Static websites    # type: other # max: medium
- in:  license.gitlab.com    # type: url # max: critical
- in:  https://gitlab.com/gitlab-org/gitlab-workhorse    # type: repo # max: critical
- out:  *.gitlab.cn    # type: wildcard # max: none
- out:  *.runway.gitlab.net    # type: wildcard # max: none
- out:  *.gitlab-private.org    # type: wildcard # max: none
- out:  *.service-now.com    # type: wildcard # max: none
- out:  dashboards.gitlab.com    # type: url # max: none
- out:  alerts.gitlab.com    # type: url # max: none
- out:  support.gitlab.com    # type: url # max: none
- out:  shop.gitlab.com    # type: url # max: none
- out:  forum.gitlab.com    # type: url # max: none
- out:  status.gitlab.com    # type: url # max: none
- out:  partners.gitlab.com    # type: url # max: none
- out:  aptly.gitlab.com    # type: url # max: none
- out:  translate.gitlab.com    # type: url # max: none
- out:  federal-support.gitlab.com    # type: url # max: none
- out:  us-federal-gitlab.com    # type: url # max: none
- out:  ir.gitlab.com    # type: url # max: none
- out:  levelup.gitlab.com    # type: url # max: none
- out:  gitlab.biterg.io    # type: url # max: none
- out:  gitlabsandbox.net    # type: url # max: none
- out:  gitlabdemo.cloud    # type: url # max: none
- out:  gitlabtraining.cloud    # type: url # max: none
- out:  packages.gitlab.com    # type: url # max: none
- out:  https://gitlab.com/gitlab-org/cli/    # type: repo # max: none
- out:  https://gitlab.com/gitlab-org/opstrace/opstrace-ui    # type: repo # max: none
- out:  docs.gitlab.com    # type: url # max: none
- out:  about.gitlab.com    # type: url # max: none
- out:  *.gitlab.net    # type: url # max: none
- out:  *.gitlap.com    # type: url # max: none
- out:  *.gitter.im    # type: wildcard # max: none
- out:  blog.gitter.im    # type: url # max: none
- out:  update.gitter.im    # type: url # max: none
- out:  files.gitter.im    # type: url # max: none
- out:  next.gitter.im    # type: url # max: none
- out:  beta.gitter.im    # type: url # max: none
- out:  ws*.gitter.im    # type: wildcard # max: none
- out:  api.gitter.im    # type: url # max: none
- out:  gitlab.net    # type: url # max: none
- out:  gitlap.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $6,595,697
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
