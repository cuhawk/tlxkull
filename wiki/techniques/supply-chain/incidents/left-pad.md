---
title: left-pad npm unpublish (Mar 2016)
slug: left-pad
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, registry/npm, technique/availability, technique/unpublish, ecosystem/javascript]
inbound: []
---

# left-pad npm unpublish (Mar 2016)

## What happened

On 2016-03-22 npm maintainer **Azer Koçulu** unpublished **all 273**
of his npm packages, including the 11-line utility `left-pad`, in
protest of npm Inc.'s decision to transfer the `kik` package name to
**Kik Interactive** (the messenger company) over a trademark dispute.
The unpublish broke the install / CI step for thousands of downstream
projects -- **Babel**, **React** scaffolds, Webpack ecosystem
projects, and corporate build pipelines at Facebook, PayPal, Netflix,
and Spotify -- all of which had `left-pad` somewhere in their
transitive dependency tree. npm Inc. **manually republished
`left-pad`** within a few hours to restore the ecosystem, but the
breakage window was real and disruptive.

Not malicious. No data exfiltration, no code injection, no RCE. The
incident's importance is what it *established* as a supply-chain
threat class: **availability**, not confidentiality or integrity. A
single human decision (or coercion of that human) can take a
load-bearing package out of every downstream consumer's reach at
once. npm responded by introducing the **24-hour unpublish window**
(after which a package with dependents cannot be unpublished) and a
formal **package-name-dispute policy** that has since been copied by
PyPI, RubyGems, and Crates.io.

## Attack chain

(again, "incident chain" rather than malicious; same shape applies
to any future maintainer takeover/coercion.)

1. **Trademark dispute filed.** Kik Interactive emailed Koçulu on
   2016-03-11 asking him to rename or relinquish the `kik` package.
   Koçulu refused and demanded compensation; Kik escalated to npm
   Inc.
2. **Registry-side override.** npm Inc. CEO Isaac Schlueter
   manually transferred `kik` package ownership to Kik Interactive on
   2016-03-18 -- the registry has unilateral admin power to rename
   any package, by design.
3. **Maintainer retaliation: unpublish all.** Koçulu requested and
   received the unpublish command from npm support, which removed
   all 273 of his packages from the registry. `left-pad@0.0.3` was
   the highest-fanout victim.
4. **Cascade install failure.** Every `npm install` that resolved to
   `left-pad@^0.0.3` started failing within minutes. Because `npm
   install` re-resolves on every CI run (no lockfile enforcement on
   most repos in 2016), even projects with a previously-working build
   now broke -- the registry returned 404 on the tarball URL.
5. **Manual republish.** npm Inc. discovered the cascade, re-bound
   `left-pad` to a copy of the last published tarball (registered to
   a new owner), and issued a public statement on
   `blog.npmjs.org/post/141577284765/kik-left-pad-and-npm`.
6. **Policy fallout.** npm shipped the **24-hour unpublish block**
   for any package with downstream dependents; cache mirrors
   (`yarn.lock`, `package-lock.json`) became standard practice
   shortly after.

## Lessons for bug hunters

- **Availability is a supply-chain dimension, not just CIA's "A".**
  Any registry with a unilateral unpublish primitive (whether by the
  maintainer or by registry admins) carries availability risk for
  every downstream. Audit your target's lockfile hygiene -- a target
  that does `npm install` without `--frozen-lockfile` in CI is
  vulnerable to registry-side changes. See [[lockfile-hygiene]].
- **Tiny packages with massive transitive use are pivot points.**
  Single-file utility packages (`left-pad`, `is-promise`,
  `event-stream`) sit in deep dep trees and are minimally watched.
  When recon-ing a target's `package-lock.json`, sort by
  fanout-to-line-count ratio; the highest-ratio entries are the
  cheapest poisoning targets. Cross-link [[micro-package-attack-surface]].
- **Registry admin power is a single point of compromise.** npm
  Inc., PyPI admins, Crates.io admins all hold the same rename/
  takedown lever Schlueter pulled in 2016. A compromised registry
  admin account is a fleet-wide supply-chain event. Two-factor
  enforcement on registry maintainers is a control to look for when
  assessing third-party risk.
- **Cache-and-mirror is the cheapest defense.** Self-hosting a
  Verdaccio/Sonatype Nexus proxy that caches every successful
  resolve eliminates 90% of the unpublish/availability attack
  surface. When your target says "we just install from npmjs.com", it
  is a finding-adjacent observation.
- **Same pattern recurs.** `colors`/`faker` self-sabotage (Jan 2022),
  `node-ipc` protestware (Mar 2022), and PyPI typosquats with
  unpublish-and-republish cycles all rhyme with left-pad. The class
  is **"one maintainer == one decision == fleet-wide change"**.
  Cross-link [[maintainer-domain-takeover]] for the malicious
  variant.

## Primary sources

- [npm blog: kik, left-pad, and npm (2016-03-23)](https://blog.npmjs.org/post/141577284765/kik-left-pad-and-npm)
  -- npm Inc.'s official post-mortem with the policy change.
- [The Register: How one developer just broke Node, Babel and thousands of projects in 11 lines of JavaScript](https://www.theregister.com/2016/03/23/npm_left_pad_chaos/)
  -- contemporaneous deep dive with quoted maintainer email
  exchange and downstream impact list.

## Related

- [[xz-utils-cve-2024-3094]]
- [[maintainer-domain-takeover]]
- [[lockfile-hygiene]]
- [[micro-package-attack-surface]]
