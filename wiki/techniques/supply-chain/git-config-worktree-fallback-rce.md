---
title: Git Config Work-Tree Fallback → Arbitrary RCE (Delete-`.git` Primitive)
slug: git-config-worktree-fallback-rce
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [technique/supply-chain, technique/rce, technique/race-condition, target/git]
inbound: []
---

# Git Config Work-Tree Fallback → RCE

## Core primitive

When you run a `git` command and **no `.git` directory exists in or
above the working directory**, git falls back to treating the **current
work-tree root** as if it were the `.git` directory. It then loads
files from that root *as git config* — including `config` (general
options), `hooks/`, and `fsmonitor` triggers.

Any attacker who can:

1. Place attacker-controlled `config` (and optional `hooks/`)
   files into the work-tree root, **and**
2. Cause `.git` to be missing when a git command runs

…gets **arbitrary command execution** as the user running git. The
attack surface is "any feature that lets a user trigger `git status`
(or any git command) inside a directory containing user-uploaded
files."

## Why this is not (necessarily) a git CVE

Git's design assumes the work-tree root is trusted because in normal
use the user only runs git inside their own repo. The git team has
historically treated "you control the work-tree, so don't expect
isolation" as a feature, not a bug. **But every sandbox / hosted-Git
/ CI / AI-coding-agent product that runs git on user content inherits
this primitive.**

## Primitives needed at the target

You need **one** of:

- **Delete-arbitrary-directory** in a user-controlled repo path that
  doesn't refuse `.git`. (Looker had a path-confusion in
  `validate_pathname` for the "delete directory" feature: explicit
  blocklist on `.git` was bypassable by deleting the **parent** repo
  dir, which recurses into `.git` first.)
- **Symlink-into-`.git`** (the classic "your CI clones submodules"
  variant — different writeups).
- **Race condition** during `rm -rf` of a repo where you can sneak in
  attacker config files between `.git` deletion and the rest of the
  tree being wiped.

## The race-condition lift (Looker)

The exploit chain used by Ryotak against Google Cloud Looker:

1. Upload a repo with:
   - attacker `config` file at repo root containing
     `[core]\nfsmonitor = sh -c '...payload...'` (or hooks/ etc.)
   - a **massive nested directory tree** ordered, by FS traversal
     order, *between* `.git` and the attacker config.
2. Trigger the "delete repository" endpoint. It calls Ruby
   `FileUtils.rm_rf` (or equivalent), which deletes `.git` first,
   then enters the massive nested tree.
3. While the recursive delete is grinding through the nested tree
   (seconds-to-minutes), hit a **second endpoint** that runs `git
   status` (or any git operation) inside that same partially-deleted
   repo. `.git` is gone; the attacker `config` at the root is still
   there → git loads it → `fsmonitor` hook fires → RCE.

The "ordered between `.git` and config" trick exploits the predictable
ordering of `readdir` on EXT4-family file systems used by the recursive
delete. The nested tree is the **slow-down primitive** that opens the
race window.

## Privilege escalation tail

In Looker's Kubernetes deployment, the RCE landed in a pod with a
service-account token mounted at:

```
/var/run/secrets/kubernetes.io/serviceaccount/token
```

The service account had `secrets:update` on other namespaces → cluster-wide
privilege escalation by injecting a malicious image-pull secret.

## Hunting checklist

Any product that fits these criteria is in scope:

- Users can upload a git repository (or files arranged as one).
- The product runs `git` commands on user content (clone, status,
  commit, fetch, log, diff — all of them load config).
- There is **any** primitive — explicit delete, archive extraction,
  path traversal, rename — that can remove or skip the `.git`
  directory.

Sandbox-style products with the highest hit-rate:

- AI coding-agent sandboxes (Sourcegraph Cody, Cursor cloud, Devin,
  Replit, Codespaces, e2b, Modal, Daytona, Codesandbox, gitpod, etc.)
- CI/CD task runners that clone user-controlled refs.
- Hosted developer Notebooks (Colab, Hex, Hugging Face Spaces).
- Self-hosted Looker / Tableau / Mode / Hex / Metabase analytics
  platforms when they integrate user-supplied git repos.

## Seen in the wild

- **2026-03 — Google Cloud Looker.** Ryotak. Path-confusion in
  `validate_pathname` → arbitrary repo dir delete → race condition
  with `FileUtils.rm_rf` → `core.fsmonitor` hook RCE → Kubernetes
  service-account → cluster-wide PrivEsc.
  Source: [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174).
  Original writeup: Ryotak's blog (Flatt Security).

## Related

- [[../race-conditions]]
- [[../server-side/SUMMARY]]
- [[npm-cache-poisoning-404]] (sibling supply-chain primitive)
