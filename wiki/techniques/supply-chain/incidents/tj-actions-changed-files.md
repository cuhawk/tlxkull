---
title: tj-actions/changed-files retag attack (CVE-2025-30066, Mar 2025)
slug: tj-actions-changed-files
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, registry/github-actions, technique/tag-mutation, technique/env-exfil, scope/ci-cd]
inbound: []
---

# tj-actions/changed-files retag attack (CVE-2025-30066, Mar 2025)

## What happened

On **2025-03-14** an attacker compromised a personal access token used
by the **`@tj-actions-bot`** account on the popular GitHub Action
**`tj-actions/changed-files`**. Using that token, the attacker
**rewrote every existing version tag** (`v1`, `v2`, ..., `v45`, plus
`v45.0.7` and friends) to point at a single malicious commit that
dumped the runner's process memory, scanned it for secrets, and
printed the **base64-double-encoded** payload to the workflow log.

Because the action is referenced by ~**23,000 repositories** -- many
of them pinning by *mutable* tag rather than commit SHA -- the next
workflow run on each repo fetched the malicious commit. On public
repos, the encoded secrets ended up in publicly-readable workflow
logs. CISA issued an advisory. GitHub removed the action, then
restored it after maintainers regained control. The malicious tags
existed from roughly **2025-03-14 → 2025-03-15** before being
re-pointed at clean commits and v46.0.1 published as the safe
baseline.

## Attack chain

1. **PAT compromise on a bot account.** Attacker obtained a GitHub
   Personal Access Token for `@tj-actions-bot`, the bot with write
   access to the `tj-actions/changed-files` repository. The exact
   vector was not publicly confirmed by the maintainers -- credential
   theft via prior compromise of a maintainer-adjacent system is the
   working hypothesis.
2. **Force-push to existing tag refs.** GitHub Actions resolves
   `uses: tj-actions/changed-files@v45` by looking up the *current*
   commit the tag points to at run time. Tags are mutable refs by
   design. Attacker `git tag -f`'d every release tag onto a single
   commit containing the payload, then pushed with `--force`. Repos
   pinning by `@v45.0.7` (a specific patch tag) were still vulnerable
   -- the attacker rewrote those too. Only `@<commit-sha>` pins were
   safe.
3. **In-action memory scrape.** The malicious commit's JS entrypoint
   ran a Node.js shim that exec'd a Python payload. The Python read
   `/proc/<runner-pid>/maps` and `/proc/<runner-pid>/mem` on Linux
   runners and grepped for secrets-shaped strings (AWS keys, GitHub
   tokens prefixed `ghp_`/`ghs_`, npm tokens, RSA private-key
   headers). Anything matched was double-base64-encoded and `echo`ed.
4. **Log exfil over a public read channel.** On public repos, the
   workflow log is world-readable -- no callback to attacker
   infrastructure needed. Anyone could `gh run list` + `gh run view
   --log` to harvest the encoded secrets from any affected public
   workflow. Private-repo victims still leaked to anyone with read
   access to Actions logs (often the entire engineering org).
5. **Detection and remediation.** Security researchers noticed
   anomalous output in public workflow logs (recognisable
   double-base64 envelope), reported within hours. GitHub disabled
   the action briefly, then restored it after maintainers rotated
   the bot token and retagged. CISA issued KEV-class advisory.
   `v46.0.1` was published as the clean baseline.

## Lessons for bug hunters

- **Mutable refs = supply chain hole.** Pin every third-party
  GitHub Action (and Docker image, Helm chart, Terraform module) to
  an immutable identifier -- commit SHA for Actions, image digest for
  Docker, exact chart hash for Helm. When auditing a target's
  `.github/workflows/`, grep for `uses: .+@v\d` -- any non-SHA pin is
  a reportable supply-chain finding. Same primitive lurked in
  [[codecov-bash-uploader]] (mutable script URL) and the
  `curl https://get.example.com | bash` pattern generally.
- **`pull_request_target` and `workflow_run` amplify impact.** If
  the victim repo runs the compromised action under
  `pull_request_target` (read/write GITHUB_TOKEN, secrets exposed),
  blast radius includes branch protection bypass and arbitrary push.
  On any in-scope target, list workflows using
  `pull_request_target` -- those are the high-value workflows to
  cross-reference against the compromised-action list.
- **Public workflow logs as exfil channel.** Attackers do not need
  outbound C2 if the target writes the secret to its own public log.
  Same as the [[circleci-2023-oauth]] env-var pattern but
  one degree removed -- secret printed by an action, not by an
  engineer's `echo`. Probe target workflows for `set -x`, `bash -x`,
  and actions that intentionally write env to log (`actions/github-script`
  with `console.log(JSON.stringify(process.env))` etc).
- **CVE-2025-30066 indicators are still in public logs.** GitHub did
  not retroactively scrub the leaked secrets from public workflow
  archives -- only the action itself. As a hunter, archived workflow
  logs from public repos running the affected action between
  2025-03-14 and 2025-03-15 may *still contain harvestable secrets*.
  This is reportable to the originating org under their bug-bounty
  program: "Secret previously leaked, still valid in production".
- **GitHub Apps > PATs for automation.** A bot account with a PAT
  has the same blast radius as a human with that PAT. Migrating
  release automation to a GitHub App with scoped, time-limited
  installation tokens (and short-lived OIDC tokens for cloud) is the
  reportable remediation pattern.

## Primary sources

- [Wiz Research: "GitHub Action tj-actions/changed-files supply chain attack (CVE-2025-30066)"](https://www.wiz.io/blog/github-action-tj-actions-changed-files-supply-chain-attack-cve-2025-30066)
  -- timeline, IOCs, payload decode, and impact analysis from the first responders.
- [CISA: "Supply Chain Compromise of Third-Party tj-actions/changed-files (CVE-2025-30066)"](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction)
  -- official US-CERT advisory with detection guidance.

## Related

- [[codecov-bash-uploader]]
- [[circleci-2023-oauth]]
- [[heroku-travis-oauth-2022]]
- [[xz-utils-cve-2024-3094]]
