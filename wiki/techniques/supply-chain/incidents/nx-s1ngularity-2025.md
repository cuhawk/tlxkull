---
title: nx "s1ngularity" credential-exfil attack (Aug 2025)
slug: nx-s1ngularity-2025
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, language/javascript, registry/npm, technique/postinstall-hook, technique/credential-stealer, technique/ai-cli-abuse, target/devtools]
inbound: []
---

# nx "s1ngularity" credential-exfil attack (Aug 2025)

## What happened

On **2025-08-26 at ~22:32 UTC**, attackers published malicious
versions of the **`nx`** build-system package and several of its
official plugins (`@nx/devkit`, `@nx/eslint`, `@nx/js`, `@nx/key`,
`@nx/node`, `@nx/workspace`, `@nx/enterprise-cloud`, and others) to
npm. The packages remained live for roughly five hours before Nrwl
unpublished them. Wiz, StepSecurity, and GitGuardian published
forensics writeups starting **2025-08-27**.

The root cause was a vulnerable GitHub Actions workflow in the
`nrwl/nx` repository, introduced on **2025-08-21**, that accepted PR
title text in an unsafe shell context. A specially crafted PR title
allowed code injection that exfiltrated an npm publish token, which
the attacker then used to publish backdoored versions. The malicious
versions shipped a **postinstall script** that, after `npm install`,
scanned the developer's machine for credentials and posted them to a
brand-new public GitHub repository named **`s1ngularity-repository`**
on the victim's own GitHub account. Wiz's follow-up identified a
**second wave** that used the leaked GitHub tokens to flip ~5500
previously-private repositories to public. Approximately **2349
distinct secrets** across **~190 organisations** and **~3000
repositories** were exfiltrated, including GitHub PATs, AWS keys,
Google AI and Anthropic API keys, OpenAI keys, Datadog tokens, and
Postgres credentials.

The standout technique was the **abuse of locally-installed AI CLI
tools** (Claude Code, Gemini CLI, Amazon Q) -- the postinstall script
spawned them with `--dangerously-skip-permissions`, `--yolo`, and
`--trust-all-tools` and prompted them to crawl the filesystem and
summarise sensitive files. This was the first publicly documented
weaponisation of developer AI assistants in a supply-chain attack.

## Attack chain

1. **PR-title shell injection in a maintainer workflow.** A GitHub
   Actions workflow added 2025-08-21 to `nrwl/nx` ran a step whose
   shell argument interpolated `${{ github.event.pull_request.title }}`
   without quoting. A PR title crafted to break out of the argument
   context executed attacker commands in the runner with access to
   the `NPM_TOKEN` secret. (Same primitive class as the
   `pull_request_target` workflow-injection family.)
2. **Steal the npm publish token, publish backdoored versions.** The
   attacker used the exfiltrated token to publish poisoned versions of
   `nx` plus the official plugins. Each tarball added a postinstall
   stage that runs unconditionally on `npm install`.
3. **Local recon postinstall script.** The script walked `~/`,
   `$HOME/.ssh`, `$HOME/.gitconfig`, `$HOME/.aws`, `$HOME/.gcloud`,
   `$HOME/.npmrc`, `$HOME/.config`, browser keystores, and developer
   project directories looking for files matching credential patterns.
4. **Weaponised AI CLI for deeper recon.** If `claude`, `gemini`, or
   `q` (Amazon Q) was present on PATH, the script invoked it with
   permission-bypass flags and a prompt instructing the assistant to
   read the filesystem and surface secrets. This used the developer's
   own paid-for LLM session as the recon agent.
5. **Exfil via the victim's own GitHub.** The collected secrets were
   base64-encoded and pushed to a new public repository called
   `s1ngularity-repository` on the victim's account using their
   stolen GitHub PAT. Roughly **6800 victim repos** were created
   before GitHub started bulk-removing them.
6. **Wave two: re-use the stolen tokens.** Two days later, attackers
   logged in with the stolen GitHub PATs and toggled large numbers of
   private repos to public, exposing additional internal code and
   secrets.

## Lessons for bug hunters

- **`pull_request_target` + untrusted PR text = workflow RCE.** Any
  GitHub Actions workflow that interpolates `${{ github.event.* }}` /
  PR title / branch name into a shell command without explicit
  quoting is a publish-token compromise waiting to happen. Hunters
  scanning a vendor's `.github/workflows/*.yml` should grep for
  `${{ github.event.pull_request.title }}`,
  `${{ github.head_ref }}`, and similar in `run:` blocks. The
  GitHub Security Lab catalog calls this "GitHub Actions script
  injection" -- bountied on multiple programs.
- **Postinstall scripts on dev-tool packages are the highest-leverage
  exfil surface in npm.** Build-tool dev-dependencies (`nx`, `rollup`,
  `vite`, `turbo`) install on every developer machine and every CI
  runner; the secrets they reach are huge. Audit `package.json`
  scripts on a target's transitive devDependencies.
- **Look for the `s1ngularity-repository` IOC in GitHub search.**
  GitHub code search for `s1ngularity-repository` reveals victim
  organisations that still have the exfil repo or its mirrors lying
  around -- a free recon vector that maps onto bug-bounty targets.
- **AI-CLI abuse is a generic primitive now.** Any developer machine
  with an authenticated `claude` / `gemini` / `q` CLI is one
  postinstall away from having that session weaponised against the
  user. Watch for **uninvoked** spawns of AI CLIs with `--yolo` /
  `--dangerously-skip-permissions` in the process tree of an
  `npm install`. See [[shai-hulud-npm-worm-2025]] for the worm
  evolution of the same pattern.
- **GitHub-as-exfil-channel reduces network IOCs.** The malware does
  not call out to a C2 -- it pushes to `api.github.com` using the
  victim's own credentials. Network-layer egress filters that
  whitelist GitHub will not catch this. Detection has to happen at
  the GitHub-events layer (audit log for new public repos named with
  a campaign string) and at the process-tree layer.

## Primary sources

- [Wiz: s1ngularity supply chain attack leaks secrets on GitHub](https://www.wiz.io/blog/s1ngularity-supply-chain-attack)
  -- primary forensics writeup with the second-wave analysis.
- [StepSecurity: s1ngularity -- popular Nx build system compromised with data-stealing malware](https://www.stepsecurity.io/blog/supply-chain-security-alert-popular-nx-build-system-package-compromised-with-data-stealing-malware)
  -- corroborating writeup with the postinstall script breakdown and
  AI-CLI-abuse detail.

## Related

- [[shai-hulud-npm-worm-2025]]
- [[ua-parser-js]]
- [[tj-actions-changed-files]]
- [[reviewdog-action-setup]]
- [[event-stream-flatmap-stream]]
