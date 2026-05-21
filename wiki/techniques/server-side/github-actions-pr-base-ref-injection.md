---
title: GitHub Actions PR Base Ref Injection — Secret Theft via Forked PR
slug: github-actions-pr-base-ref-injection
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/supply-chain, technique/ci-cd, technique/github, technique/secrets-leak]
inbound: []
---

# GitHub Actions PR Base Ref Injection — Secret Theft via Forked PR

## Pattern

GitHub Actions has two pull request triggers: `pull_request` (runs attacker's
code from the fork, no secret access) and `pull_request_target` (runs base
branch code, has full secret access including `GITHUB_TOKEN` with write
permissions). The design assumption is that `pull_request_target` always runs
trusted code because the base branch is maintained by repository owners.

The vulnerability: when creating a pull request, `base_ref_name` must be a
branch name. However, after creating the PR, editing `base_ref_name` to a
commit hash was not validated. If the attacker can make GitHub treat a commit
in their fork as the "base" (trusted) commit, `pull_request_target` workflows
will execute the attacker's code with full secret access.

Attack chain:
1. Fork target repo; create a malicious commit with a `pull_request_target`
   workflow that exfiltrates `GITHUB_TOKEN`.
2. Create a PR from fork to target, specifying any valid branch as base.
3. Edit the PR to change `base_ref_name` to the hash of the malicious commit.
4. GitHub now treats the malicious commit as the base, triggering
   `pull_request_target` with the attacker's workflow and full secrets.

## Preconditions

- Target repository has a `pull_request_target` workflow.
- Attacker can create a fork and pull request.
- GitHub did not validate that the edited `base_ref_name` pointed to a real branch
  (fixed: commit hashes are now rejected).

## Detection

- Look for `pull_request_target` workflows that execute code or checkout from
  the PR head (`actions/checkout` with `ref: github.event.pull_request.head.sha`).
- Check the GitHub API endpoint `PATCH /repos/{owner}/{repo}/pulls/{id}` — was
  `base` parameter validated as a branch name?

## Triggering

```bash
# 1. Fork and add malicious .github/workflows/pwn.yml committed to fork
# 2. Create PR to main (valid branch as base):
gh pr create --base main --head attacker:feature-branch

# 3. Edit PR via API to set base to malicious commit hash:
curl -X PATCH -H "Authorization: token $GH_TOKEN" \
  https://api.github.com/repos/victim/repo/pulls/$PR_NUMBER \
  -d '{"base": "abc1234def5678..."}'

# 4. GitHub triggers pull_request_target using the malicious commit
```

## Seen in the wild

- 2021 — GitHub, $25,000. Found by Teddy Katz. GitHub fixed by requiring
  `base_ref_name` to be a valid branch name during PR edits, same as during
  PR creation.
  [BBRE](https://www.youtube.com/watch?v=xbSCRbfMOr4)

## References

- GitHub Security Advisory
- See also: [github-actions-pr-token-theft](github-actions-pr-token-theft.md)
  — expression injection variant
- Teddy Katz's blog post
