---
title: npx binary-name vs package-name confusion
slug: npx-binary-package-confusion
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/supply-chain, technique/rce, registry/npm, tool/npx]
inbound: []
---

# npx binary-name vs package-name confusion

## Pattern

`npx <thing>` resolves `<thing>` as a **binary name** if installed
locally; if not, it pulls **a package of that name** from the public
registry and runs the binary. The bug: npx accepts dashed binary names
(`grafana-toolkit`) but the matching package is published under a
**scoped** name (`@grafana/toolkit`). If `grafana-toolkit` is unclaimed
on the public registry, an attacker can claim it. Any developer / CI
running `npx grafana-toolkit` without first `npm install`ing the
scoped package downloads and executes attacker code.

Ronnie / 0xLupin found this on Grafana's documentation, claimed
`grafana-toolkit` on npm. Real impact: open-source users running
documented commands; Grafana's internal CI was archived so internally
safe, but the docs sent everyone else to the attacker's binary.

Important shift: the attack target is the **package manager** (npx), not
the artifactory. Vulnerable to bug-bounty-grade attacks on every other
package manager -- yarn, pnpm, pip's `uv` / pipx, gem, cargo install.

## Preconditions

- Target's docs / Dockerfile / CI uses `npx <some-binary>` where the
  binary name differs from the scoped package name.
- The dashed/un-scoped variant is unclaimed on the public registry.
- User does not pre-install the scoped package (the typical
  "documented quickstart" path).

## Detection

- Grep target's open-source repos, docs site, README for `npx ` and
  `pipx run ` invocations.
- Check each invoked name on `npmjs.org/package/<name>` -- 404 =
  claimable.
- Cross-check scoped variants (`@<org>/<bin-name>`) -- if the org owns
  the scope but not the dashed name, you have a candidate.

## Triggering

1. Claim `<binary-name>` on npm.
2. Add a `bin` field in `package.json` mapping `binary-name` -> entry
   script.
3. Entry script runs your callback / DNS exfil, then optionally invokes
   the real scoped binary so the developer's workflow doesn't break (no
   ticket filed).

## Bypasses

(None known on the attacker side -- the bug is in npx resolution. Fix is
package-manager side or developer-side discipline: always
`npm install @org/pkg` before `npx pkg`.)

## Seen in the wild

- {date: 2024-06, source: CT Ep 74} -- Grafana docs invoked
  `npx grafana-toolkit`; Lupin claimed it. Grafana security team rated
  it appropriately (Grafana team praised for handling).

## Related

- [[dependency-confusion]] -- same shape, different resolver.
- [[maintainer-domain-takeover]]

## References

- Critical Thinking Podcast Ep 74
- 0xLupin / Ronnie -- npx confusion blog (2024-06)
