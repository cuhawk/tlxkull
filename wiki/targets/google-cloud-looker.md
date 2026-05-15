---
title: Google Cloud Looker
slug: target-google-cloud-looker
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [target/google, target/looker, target/bi]
inbound: []
---

# Google Cloud Looker

## What it is

Google-owned business-intelligence platform. Self-hostable for
reverse-engineering; the hosted version runs in Google Cloud (GKE).
**Ruby**-based. Users upload **git repositories** to define LookML
models — this makes git the primary on-target attack surface.

## Attack-surface highlights

- **User-uploaded git repos** — every git operation Looker runs on
  user content is exploitable if the `.git` directory can be
  removed or skipped. See
  [[../techniques/supply-chain/git-config-worktree-fallback-rce]].
- **`FileUtils.rm_rf` recursive deletes** are race-condition-friendly
  on EXT4 — predictable readdir order lets you sequence what gets
  deleted when.
- **Path-validation routines** like `validate_pathname` historically
  allow deleting parent directories that contain `.git` even when
  direct `.git` deletion is blocked.
- **GKE service-account token** mounted at
  `/var/run/secrets/kubernetes.io/serviceaccount/` — once you have
  RCE, the next pivot is whatever cluster permissions that SA holds.
  Historically: `secrets:update` cluster-wide, enabling lateral
  movement via tampered image-pull secrets.

## Prior findings

- **2026-03 — Ryotak (Flatt Security).** Arbitrary repo dir delete +
  race-condition window via massive nested directory + git config
  work-tree fallback → `fsmonitor` hook RCE → GKE service account →
  cluster-wide PrivEsc.
  Source: [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174).

## Triage signal

- Self-host Looker to reverse-engineer the Ruby. The hosted version
  doesn't give you source; the self-hosted does.
- Map every endpoint that runs a `git ...` command server-side.
- For each: can you cause `.git` to be missing in the work-tree
  before that endpoint runs? If yes, you have the chain.
- Other Looker bugs have shipped historically — it's a productive
  scope, not a one-off.

## Related

- [[../techniques/supply-chain/git-config-worktree-fallback-rce]]
- [[../techniques/race-conditions]]
