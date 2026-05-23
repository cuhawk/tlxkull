---
title: eslint-scope 3.7.2 (npm-token exfil, Jul 2018)
slug: eslint-scope
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, registry/npm, technique/account-takeover, technique/postinstall-script, technique/token-exfil, technique/credential-cascade]
inbound: []
---

# eslint-scope 3.7.2 (npm-token exfil, Jul 2018)

## What happened

On **2018-07-12 at 17:49 UTC** an attacker who had compromised the
npm account of an ESLint maintainer published two malicious versions:
**`eslint-scope@3.7.2`** and **`eslint-config-eslint@5.0.2`**. Each
shipped a `postinstall` hook that downloaded code from a Pastebin
URL and executed it, with the goal of exfiltrating the local
machine's `~/.npmrc` to `npm.getmanifest.com`. `~/.npmrc` typically
contains a long-lived bearer token granting publish rights to every
package the user controls -- meaning a single successful infection
could be parlayed into widespread further package compromise.

The window was small (~2.5 hours) and npm unpublished both versions
by 20:30 UTC, but the ESLint post-mortem estimated **~4,500 npm
authentication tokens** were exfiltrated before detection. To
mitigate the worst-case downstream cascade, **npm revoked every
authentication token issued before 2018-07-12 12:30 UTC** -- a
nuclear measure that logged out every npm maintainer in the world.
No follow-on malicious publishes have been linked to this incident,
but the credential-cascade primitive (compromise -> steal-tokens ->
compromise-more) is now textbook.

## Attack chain

1. **Password reuse + no 2FA.** The maintainer's npm password was
   reused on a previously breached site (per ESLint's own
   post-mortem). 2FA was not enabled. Credential-stuffing trivially
   yielded a session.
2. **Two-package push.** Attacker published `eslint-config-eslint@5.0.2`
   first (a less-watched package -- shipped configurations are rarely
   audited), used the install-target token harvest to fish for the
   ESLint-scope publish token, then published `eslint-scope@3.7.2`
   (the high-value target -- 50M+ downloads/week, used by Webpack
   and most front-end build chains).
3. **`postinstall` -> Pastebin -> .npmrc steal.** The malicious
   `package.json` added a `postinstall` script that fetched a remote
   JS payload from Pastebin (URL was a short alphanumeric pastebin
   ID, no protocol obfuscation). The payload `fs.readFileSync`d
   `~/.npmrc`, HTTP-POSTed it to `https://npm.getmanifest.com/...`,
   and exited. No further on-disk persistence.
4. **`~/.npmrc` = long-lived publish bearer.** At the time, every
   `npm login` wrote an `_authToken` to `~/.npmrc` that did not
   expire and was scoped to all of the user's packages. Stealing it
   was equivalent to stealing publish rights forever (or until the
   user noticed and ran `npm token revoke`).
5. **Nuclear remediation.** npm staff revoked **every token issued
   before 2018-07-12 12:30 UTC**, globally. This was the only viable
   containment -- there was no way to know which of the 4,500
   harvested tokens the attacker had already used.

## Lessons for bug hunters

- **`~/.npmrc` and equivalents are crown jewels.** Any
  install-time script primitive on a target's CI box gives access
  to `~/.npmrc`, `~/.gitconfig`, `~/.aws/credentials`, `~/.ssh/`,
  `$HOME/.docker/config.json`, GitHub Actions
  `RUNNER_TEMP/_github_workflow/`. When auditing a target's
  third-party action / npm package, treat `postinstall` / `preinstall`
  / GHA `run:` blocks as the analytic interface to that filesystem.
- **Pastebin / gist as stage-2 host is still working.** Pastebin
  hosting of malicious JS payloads has been in use continuously
  from 2014 to date. Programs that have public-readable Pastebin
  / gist IDs in their CI configs (rare but happens) are leaking
  attacker-controllable injection points.
- **Token-rotation tooling for the target is a finding.** If your
  target's bug-bounty scope includes their internal "publish a new
  release" pipeline and that pipeline stores a long-lived npm
  token in CI without rotation, that's a hardening finding worth
  filing -- the eslint-scope precedent shows the realistic blast
  radius.
- **One-time-broad-revoke is a defender muscle.** The 2018 npm
  global token revoke worked. Programs that lack the equivalent
  capability (revoke all customer API keys at once) are accepting
  a longer-tail-of-compromise SLA. Worth quoting this incident in
  reports recommending revoke-all tooling.
- **Two-package push pattern.** Attacker hit the LOW-watched
  `eslint-config-eslint` first, then the HIGH-impact `eslint-scope`.
  When auditing the timeline of a maintainer's activity, look for
  small-package publishes immediately preceding big ones -- it can
  signal a reconnaissance phase inside the same compromised
  account.

## Primary sources

- [ESLint: Postmortem for Malicious Packages Published on July 12th, 2018](https://eslint.org/blog/2018/07/postmortem-for-malicious-package-publishes/)
  -- the ESLint team's own incident report with timeline, root
  cause (password reuse), and remediation.
- [npm: postmortem on the eslint-scope compromise (npm/npm issue 21202)](https://github.com/npm/npm/issues/21202)
  -- npm-side disclosure thread with IoCs, the Pastebin payload, and
  npm's global-token-revoke decision.

## Related

- [[ua-parser-js]]
- [[event-stream-flatmap-stream]]
- [[reviewdog-action-setup]]
- [[maintainer-domain-takeover]]
