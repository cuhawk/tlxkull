---
title: event-stream / flatmap-stream (Copay bitcoin steal, Nov 2018)
slug: event-stream-flatmap-stream
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, registry/npm, technique/maintainer-handover, technique/targeted-payload, technique/dependency-injection]
inbound: []
---

# event-stream / flatmap-stream (Copay bitcoin steal, Nov 2018)

## What happened

The npm package `event-stream` was maintained by **Dominic Tarr** as
an unpaid hobby project; by 2018 it was downloaded ~2 million times a
week and was a transitive dep of much of the Node ecosystem. In
September 2018 a contributor named **right9ctrl** opened a PR adding
`flatmap` functionality and asked to take over publishing. Dominic
handed over both GitHub commit rights and npm publish rights.
Right9ctrl shipped `event-stream` 3.3.6 on 2018-09-09, adding a new
direct dependency: `flatmap-stream` 0.1.1, which they had published
under their own name three days earlier.

`flatmap-stream` 0.1.1 contained a benign payload at install. **A
second release, 0.1.2**, shipped with an encrypted stage-2 that
decrypted itself using a key derived from the consumer package's
`description` field. The only consumer whose description produced the
correct key was **Copay** (Bitpay's open-source bitcoin wallet),
specifically Copay's build-time bundling step. Inside that one
context the payload activated, hooked Copay's wallet-init code, and
exfiltrated private keys + seed phrases of any wallet holding >=100
BTC or >=1000 BCH to `copayapi.host` and `111.90.151.134`. The attack
ran undetected from 2018-09-09 to 2018-11-20 -- **2.5 months, ~8M
event-stream downloads in window** -- until **Ayrton Sparling**
filed a GitHub issue noticing the obfuscated `flatmap-stream` blob.

## Attack chain

1. **Maintainer-handover social engineering.** New contributor adds
   value (the flatmap PR was technically fine), then asks for keys.
   Dominic, unpaid and uninterested, said yes by email. No identity
   check, no co-maintainer model.
2. **Inject via new dep, not new code in event-stream itself.** The
   `flatmap-stream` package was the attacker's own. Code-review of
   `event-stream` 3.3.6 by a downstream consumer would see only "added
   `flatmap-stream` as a dep" -- which looks like normal feature work.
3. **Patch-version payload.** Stage-2 shipped in `flatmap-stream`
   0.1.2 as a republish, not in the initial 0.1.1. Lockfiles that
   pinned `flatmap-stream@~0.1` (caret/tilde semver) auto-upgraded
   to 0.1.2 on next `npm install`. Anyone who reviewed 0.1.1 at PR
   time wouldn't see the payload.
4. **Targeted unpack via consumer-package description.** The
   encrypted blob used AES-256-CBC with a key derived from
   `process.env.npm_package_description` of the *parent* package
   running install. Only Copay's exact description string produced a
   valid key. On every other npm install in the world, decryption
   yielded garbage and silently no-op'd.
5. **Wallet-private-key exfil.** Inside Copay's bundle the payload
   monkey-patched the BitcoinJS wallet-instantiation flow, captured
   the in-memory mnemonic, base64-encoded it with the user's address,
   and POSTed to the C2.
6. **Discovery.** The deobfuscation step was sloppy -- `flatmap-stream`
   shipped a minified `index.js` that didn't match its claimed source.
   Ayrton noticed during a routine dep audit.

## Lessons for bug hunters

- **Encrypted payload + env-based unpack is a real evasion.** Generic
  npm-scanning tooling that runs `npm install` in a sandbox sees only
  the dead-decryption path. The payload only lives in one specific
  consumer's build context. When auditing a target's deps, simulate
  the *target's* env (package name, description, working dir name)
  before concluding a dep is benign.
- **Maintainer-handover is recognisable.** New contributor with no
  prior history asks for publish rights within weeks of first PR.
  This is the canonical pattern; see also [[xz-utils-cve-2024-3094]].
  Programs that bake out the human-trust chain (Tidelift, SLSA L3+)
  are uniquely defended.
- **Sub-dep-of-sub-dep payloads.** The compromised package
  (`flatmap-stream`) was at depth-2 from any direct consumer. Audit
  tooling that only fingerprints direct deps misses everything below.
  When investigating a target's package-lock, the leaf packages
  (especially single-maintainer, low-download-count tools-of-tools)
  are the highest-risk nodes.
- **Caret/tilde semver auto-upgrades stage payloads.** Anyone who
  pinned `event-stream@^3.3.6` had `flatmap-stream` resolved
  separately and would get 0.1.2 even if they hadn't bumped
  event-stream. Lockfile churn alone won't catch this -- the *new*
  version's diff is the only signal.
- **Targeted attacks exist in the npm ecosystem.** Copay was the only
  successful detonation. Most "supply chain incidents" since are
  broad-spray. This case proves spear-attacks at scale-of-1 are
  feasible and were running silent for 2.5 months.

## Primary sources

- [npm Blog: Details about the event-stream incident](https://blog.npmjs.org/post/180565383195/details-about-the-event-stream-incident)
  -- npm's official post-mortem with timeline and IoCs.
- [Snyk: A post-mortem of the malicious event-stream backdoor](https://snyk.io/blog/a-post-mortem-of-the-malicious-event-stream-backdoor/)
  -- deep technical writeup of the AES-256-CBC unpack, the env-keyed
  decryption, and the Copay wallet hook.

## Related

- [[xz-utils-cve-2024-3094]]
- [[ua-parser-js]]
- [[maintainer-domain-takeover]]
- [[dependency-confusion]]
