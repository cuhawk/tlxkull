---
title: PHP git.php.net backdoor (Mar 2021)
slug: php-git-backdoor
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, language/php, registry/git, technique/source-tampering, technique/magic-header-backdoor]
inbound: []
---

# PHP git.php.net backdoor (Mar 2021)

## What happened

On **2021-03-28**, two malicious commits were pushed to the `php-src`
repository on `git.php.net` impersonating **Rasmus Lerdorf** and
**Nikita Popov**. The commits were dressed up as a "Fix Typo" change to
`ext/zend/zend.c` but added a hidden backdoor that called
`zend_eval_string()` on any HTTP `User-Agentt:` header (note the doubled
`t`) whose value began with `zerodium`. Any web server running the
backdoored build of PHP would execute attacker-supplied PHP code in
every request that carried the magic header.

The commits were caught within **hours** during routine post-commit
review. The exact intrusion vector was never published in detail, but
the PHP team concluded that the attacker compromised the bespoke
`git.php.net` Gitolite-style infrastructure rather than the individual
maintainer accounts. **PHP migrated its canonical repository to
GitHub** the same week and shut down direct pushes to `git.php.net`.
The commits never reached a tagged release.

## Attack chain

1. **Server compromise, not account compromise.** Attacker gained the
   ability to push commits to `git.php.net` as arbitrary authors -- so
   the commits carried Lerdorf / Popov signatures despite originating
   elsewhere. The maintainers' SSH keys and accounts were not breached.
2. **Plausible commit framing.** Commit messages read `Fix Typo` and
   `Revert "Fix Typo"`, and the diff touched a single line in a deep
   internals file (`ext/zend/zend.c`) -- low scrutiny on a one-character
   change in the Zend engine.
3. **Magic-header backdoor.** The added code took
   `SG(request_info).useragent` (Server Globals), checked
   `strncmp(useragent, "zerodium", 8)`, and on match passed the rest of
   the header straight to `zend_eval_string()` -- the same primitive
   used by `eval()`. The header name was `User-Agentt` (double `t`) so
   it would not be sanitised by WAFs filtering for `User-Agent`. The
   commit also embedded the literal string `REMOVETHIS: sold to
   zerodium, mid 2017` -- false-flag bait, intent disputed.
4. **Pre-release detection.** Standing post-commit review by Popov
   spotted the diff hours after it landed. No tarballs or distros ever
   shipped the backdoored code.
5. **Move-to-GitHub remediation.** PHP retired write access on
   `git.php.net` and made GitHub the canonical source-of-truth; pushes
   now go through GitHub-side authn (2FA, signed commits) plus PRs.

## Lessons for bug hunters

- **Custom git hosting is a recurring single point of failure.** Any
  vendor self-hosting a git server (`gitea`, `gitolite`, in-house GitLab)
  for the project's *canonical* code adds attack surface that the
  GitHub/GitLab cloud removes. Probe the host directly: stale Gitolite
  versions, dangling LDAP integrations, debug interfaces left exposed.
  Related primitive in [[heroku-travis-oauth-2022]] where third-party
  integrators became the weak link.
- **Magic-header / magic-cookie backdoors live in shipped binaries
  too.** Search target webapps for `strncmp`/`startsWith` against a
  fixed token in `User-Agent`, `Cookie`, `Referer`, or custom
  `X-*` headers in the request-handling path. Bonus points for
  doubled-letter variants (`User-Agentt`, `Authorizationn`) designed
  to evade WAF rules.
- **Author-line trust is cheap to forge.** A commit signed `Rasmus
  Lerdorf <rasmus@lerdorf.com>` proves nothing without a verified GPG /
  SSH signature. When auditing a supply-chain finding, always check
  whether the project requires signed commits and whether the signature
  on the malicious commit verifies.
- **Single-line diffs in language internals are high-value.** The
  diff was one line in a 30k-line file. Reviewing for new calls to
  `eval`/`system`/`zend_eval_string`/`exec` in `git log -p` between
  any two release tags catches the same class of attack. Pattern echoes
  [[xz-utils-cve-2024-3094]] (single m4 line) and [[linux-umn-hypocrite-commits]]
  (single semantic-only buggy line).

## Primary sources

- [PHP internals announcement: "Changes to Git commit workflow"](https://news-web.php.net/php.internals/113838)
  -- Nikita Popov's original mail with the disclosure and the move-to-GitHub plan.
- [PHP.Watch: "git.php.net server compromised, move to GitHub, and delayed updates"](https://php.watch/news/2021/03/git-php-net-hack)
  -- technical write-up of the commits with the diff and header analysis.

## Related

- [[xz-utils-cve-2024-3094]]
- [[linux-umn-hypocrite-commits]]
- [[heroku-travis-oauth-2022]]
