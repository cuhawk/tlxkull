---
title: reviewdog/action-setup compromise (CVE-2025-30154, Mar 2025)
slug: reviewdog-action-setup
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, registry/github-actions, technique/ci-secret-theft, technique/log-exfil, technique/transitive-compromise]
inbound: []
---

# reviewdog/action-setup compromise (CVE-2025-30154, Mar 2025)

## What happened

On **2025-03-11 between 18:42 and 20:31 UTC** an attacker pushed a
malicious commit to the `v1` tag of `reviewdog/action-setup` -- a
GitHub Action that bootstraps the `reviewdog` linter wrapper. The
tampered action dumped the GitHub Actions runner worker process memory
to extract repository secrets (`GITHUB_TOKEN`, `NPM_TOKEN`, deploy
keys, anything `secrets.*` resolved to during the job) and printed them
double-base64-encoded into the workflow log. Public-repo workflows
exposed those secrets to anyone with read access; private-repo
workflows leaked them only to insiders who could read the log, but the
secrets themselves were still recoverable.

Approximately **1,500 repositories** ran the malicious tag during the
~2-hour window. The bigger downstream impact was that the secrets
stolen from one of those repos -- `tj-actions` org -- enabled the
attacker to pivot and push a malicious commit into
`tj-actions/changed-files` (CVE-2025-30066) on 2025-03-14, which then
ran inside ~14,000 repositories over ~22 hours. Wiz attributes the
original Coinbase-targeted attacker as having walked from reviewdog ->
tj-actions and then expanded broadly when the targeted path didn't
yield. Root cause for reviewdog itself: contributors were
auto-added to a maintainer team with write access -- 118 members,
any one of whom was a credential-stuffing target.

## Attack chain

1. **Lateral team write access.** `reviewdog/action-*` repositories
   auto-invited any past contributor to a maintainer team holding
   write access. One of the 118 members' GitHub credentials/PAT was
   compromised (suspected credential reuse / phish).
2. **Tag-mutation, not new release.** Attacker force-pushed the `v1`
   floating tag to a malicious commit. Every consumer using
   `reviewdog/action-setup@v1` (the documented "latest" pin) pulled
   it on next workflow run.
3. **install.sh injection.** A base64 blob was appended to
   `install.sh`, decoded at run-time to a Python script (`memdump.py`)
   that walked `/proc/<Runner.Worker pid>/maps`, identified
   anonymous-heap regions, and grepped for the GitHub-secrets struct
   layout the Actions runner uses in-memory.
4. **Log-only exfil.** Recovered secrets were double-base64-encoded
   and `echo`d into the workflow log -- evading GitHub's
   `***`-masking which only matches single-base64 of the registered
   secret. No outbound C2; the attacker scraped the public logs
   afterwards.
5. **Pivot.** Secrets from one tj-actions-related workflow were used
   to publish a malicious commit on `tj-actions/changed-files`, which
   in turn re-used the same memdump-log-exfil primitive against every
   downstream consumer (see [[tj-actions-changed-files]] if added).

## Lessons for bug hunters

- **Floating `@v1` / `@main` references in `uses:` are mutable
  trust.** If you can sniff a target's CI for an unpinned third-party
  action, the action repo's threat model becomes the target's threat
  model. Pinning to a commit SHA is the only defence; absence of
  pinning is a finding in many programs' CI/SSDLC scope.
- **Runner-worker memory is harvestable from any action.** GitHub's
  secret-masking is string-based on the registered secret value. Any
  re-encoding (base64 of base64, hex, gzip, XOR with constant) bypasses
  the mask. Encoding-laundering of leaked secrets in CI logs is a
  recurring primitive -- see Trufflehog/Splunk research.
- **Auto-invite contributor teams = horizontal blast radius.** If a
  target's open-source org grants commit-on-merge, every past
  contributor's account is a credential. Look for orgs where the
  README brags about welcoming first-time contributors AND the actions
  it ships are widely consumed.
- **Compromise cascades through GitHub Actions.** The reviewdog ->
  tj-actions hop shows that one action's secrets bootstrap the next
  attack. Map the action-call DAG of your target; a low-popularity
  action that holds high-privilege secrets is the highest-value node.
- **CVE-2025-30154 reporting precedent.** Memory-dumping a runner
  is now a known technique; if your target's self-hosted runners run
  third-party actions without a `permissions:` block, that is exploit
  ground. See [[dependency-confusion]] for the registry-level analogue.

## Primary sources

- [StepSecurity: reviewdog GitHub Actions are compromised](https://www.stepsecurity.io/blog/reviewdog-github-actions-are-compromised)
  -- original incident disclosure with IoCs and timeline.
- [Wiz: GitHub Action supply chain attack: reviewdog/action-setup](https://www.wiz.io/blog/new-github-action-supply-chain-attack-reviewdog-action-setup)
  -- deep technical writeup of memdump.py, base64-laundering, and the
  pivot to tj-actions.

## Related

- [[dependency-confusion]]
- [[maintainer-domain-takeover]]
- [[ledger-connect-kit]]
- [[eslint-scope]]
