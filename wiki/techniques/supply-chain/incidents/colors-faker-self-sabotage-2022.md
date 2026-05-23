---
title: colors / faker self-sabotage (Marak Squires, Jan 2022)
slug: colors-faker-self-sabotage-2022
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, language/javascript, registry/npm, technique/protestware, technique/maintainer-self-sabotage]
inbound: []
---

# colors / faker self-sabotage (Marak Squires, Jan 2022)

## What happened

Between **2022-01-07 and 2022-01-09**, the sole maintainer of two
heavily-depended-on npm packages -- **`colors`** (terminal ANSI
coloring, ~20M weekly downloads) and **`faker`** (test-data
generation, ~2.8M weekly downloads) -- deliberately shipped breaking
releases as an act of protest. Marak Squires pushed
**`colors@1.4.44-liberty-2`** containing an infinite-loop "LIBERTY
LIBERTY LIBERTY" banner that printed non-ASCII garbage forever, and
published **`faker@6.6.6`** that emptied the package's `README` and
source to a single inflammatory paragraph.

The action immediately broke downstream tooling that resolved against
`^1.4.0` of `colors` or any non-pinned `faker`. Affected projects
included **AWS CDK**, **Storybook**, **Next.js**, **Sentry**, and
thousands of smaller consumers; CI pipelines around the world either
hung on the infinite loop or failed to find `faker` exports. GitHub
suspended Squires' account; npm reverted `colors` to `1.4.0` for new
installs. Squires framed the action publicly as protest at Fortune
500s extracting unpaid labour from open-source maintainers (he had
previously, in November 2020, told big corporate consumers to either
fork or pay six figures). The episode became the canonical reference
for **protestware** -- a maintainer turning their own package into
a denial-of-service against downstream users.

## Attack chain

1. **Sole-maintainer publish rights.** Both `colors` and `faker` had
   exactly one human with publish authority. No co-maintainer review
   step, no four-eyes gate. The structural weakness was the social
   organisation, not a credential compromise.
2. **`colors@1.4.44-liberty-2` -- infinite loop in module body.** The
   sabotaged release added a `while (true) { ... }` that ran on module
   load, printing a sequence of non-ASCII bytes and the phrase
   "LIBERTY LIBERTY LIBERTY" forever. Because the loop sits in the
   top-level module body, every consumer that did
   `require('colors')` (transitively or directly) hung at import time.
3. **Range-resolver auto-pickup.** Standard `package.json` patterns
   pin `colors` as `^1.4.0` or `~1.4.0`. The sabotaged version 1.4.44
   satisfies `^1.4.0`, so any fresh install or any CI run that
   resolved against the registry got the bad copy automatically. Only
   projects with a committed `package-lock.json` containing a known
   prior version's integrity hash survived.
4. **`faker@6.6.6` -- emptied package.** The faker release blanked
   most of the actual source and replaced the README with the protest
   text. Downstream tests that used `faker.name.firstName()` and the
   like crashed on undefined functions.
5. **Detection and rollback.** Within hours, downstream maintainers
   were filing bug reports against AWS CDK, Storybook, etc. GitHub
   suspended Squires' account on 2022-01-08; npm rolled `colors`
   back to the prior known-good version for new installs and pulled
   the malicious `faker`. The author later regained partial GitHub
   access; the packages have since been transferred to community
   maintainers and forks.

## Lessons for bug hunters

- **Sole-maintainer + ungated range-resolver = DoS magnet.** Any
  bug-bounty target whose runtime CI / production install resolves
  npm deps against the live registry with `^` or `~` ranges and no
  lockfile integrity check can be denial-of-serviced (and
  potentially worse) by a single maintainer publishing a bad version.
  This is a reportable hardening finding on programs that scope
  build-system resilience.
- **Pin or vendor critical paths.** Findings of the form "your build
  pipeline auto-pulls latest `^1.4.0` of `colors` / `chalk` / `debug`
  / `axios` / `lodash` without `--frozen-lockfile`" are paid out on
  large vendor programs that take supply-chain seriously.
- **Protestware is part of the threat model.** The actor here is not
  an external attacker; it is the legitimate maintainer. Defensive
  controls (code review, 2FA, publish-token rotation) do not apply.
  The only structural defence is downstream pinning + integrity
  hashes. The same primitive has since recurred in
  [[node-ipc-protestware]].
- **Top-level module-body side effects are a smell.** Any module that
  does work, prints output, or initialises a timer at `require()`
  time -- not behind an exported function -- is fragile and a
  high-leverage sabotage point. Audit critical dependency
  `index.js`/`main` entrypoints for top-level side effects.
- **Read the maintainer's public stance.** Maintainers who publicly
  threaten to "burn it down" or stop supporting a corporate-dominated
  ecosystem are not pure protestware risk -- their tokens are also
  more likely to be a phishing target (the volatility hides anomalous
  publishes). Maintainer-sentiment monitoring is a real
  supply-chain-risk discipline now.
- **Lockfile integrity verification is the structural answer.**
  `npm ci` with a committed `package-lock.json`, `pnpm install
  --frozen-lockfile`, and Yarn's `--immutable` reject any drift from
  the locked SHA. If a target ships without these on their build
  pipeline, that is the finding.

## Primary sources

- [Sonatype: Maintainer sabotages npm libraries 'colors' and 'faker' in protest](https://www.sonatype.com/blog/npm-libraries-colors-and-faker-sabotaged-in-protest-by-their-maintainer-what-to-do-now)
  -- the original disclosing vendor writeup with the version-level
  IOCs and corporate-impact list.
- [BleepingComputer: Dev corrupts npm libs 'colors' and 'faker' breaking thousands of apps](https://www.bleepingcomputer.com/news/security/dev-corrupts-npm-libs-colors-and-faker-breaking-thousands-of-apps/)
  -- corroborating reporting with the maintainer's public statements
  and GitHub-account suspension timeline.

## Related

- [[node-ipc-protestware]]
- [[event-stream-flatmap-stream]]
- [[left-pad]]
- [[ua-parser-js]]
- [[shai-hulud-npm-worm-2025]]
