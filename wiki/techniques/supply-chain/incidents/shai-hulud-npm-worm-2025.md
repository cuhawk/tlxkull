---
title: shai-hulud npm worm (Sep 2025)
slug: shai-hulud-npm-worm-2025
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, language/javascript, registry/npm, technique/worm, technique/postinstall-hook, technique/credential-stealer, technique/self-propagation]
inbound: []
---

# shai-hulud npm worm (Sep 2025)

## What happened

Between **2025-09-14 and 2025-09-18**, Socket and Phylum disclosed the
first publicly documented self-propagating worm in the npm ecosystem.
The campaign was named **Shai-Hulud** after the artifact filename
embedded in the dropper (a reference to Frank Herbert's Dune sandworm).

The earliest confirmed entry point was a compromised version of
**`@ctrl/tinycolor`** (~2M weekly downloads). The malicious tarball
included a `bundle.js` invoked from a postinstall hook. On install,
the script harvested credentials from the developer's machine and then
**used the harvested `~/.npmrc` token to publish itself into every
other npm package the same maintainer had write rights to**. Each
fresh victim package then propagated the same payload to its own
maintainer's package set on the next install. The worm spread without
operator action between hops.

By the time CISA issued its widespread-compromise advisory on
**2025-09-23**, roughly **180 distinct npm packages** were known
infected, including `@ctrl/tinycolor`, `ngx-bootstrap`,
`gluestack-ui` family packages, and CrowdStrike-published npm
packages. A separate but contemporaneous wave injected
crypto-stealer code into 18 widely-used libraries including
**`chalk`** and **`debug`**. Subsequent variants extended the worm
into hundreds more packages through 2025-Q4 ("Shai-Hulud 2.0",
AntV-cluster, etc.).

## Attack chain

1. **Initial infection from a phished maintainer.** Entry point was an
   account takeover of a maintainer with publish rights to
   `@ctrl/tinycolor` (and related packages). The attacker pushed a
   patch version containing a `postinstall` script and a `bundle.js`
   dropper.
2. **Credential sweep on install.** The dropper used **TruffleHog**
   (downloaded at runtime or bundled) plus its own regexes to scrape
   `~/.npmrc`, `~/.gitconfig`, `~/.aws/`, `~/.config/gcloud/`, environment
   variables, and developer project trees for high-value tokens (AWS,
   GCP, Azure, npm, GitHub, OpenAI, Anthropic, etc.).
3. **Exfil via the victim's own GitHub account.** Base64-encoded
   credential dumps were committed to a brand-new public repository
   named **`Shai-Hulud`** on the victim's GitHub account using the
   harvested PAT. A malicious GitHub Actions workflow was also
   injected into accessible repositories to forward future secrets
   to an attacker-controlled webhook.
4. **Self-replication via stolen npm token.** Using the victim's
   `~/.npmrc` token, the worm authenticated to the npm registry,
   enumerated every package the token could publish to (`npm access
   ls-packages`), wrote the payload into each one as a patch-version
   bump, and published. Each new infected package became a hop in the
   spread tree.
5. **Crypto-stealer side payload.** A subset of infected packages
   (chalk, debug, supports-color, ansi-styles, etc.) carried an
   additional browser-side stealer that hooked `window.ethereum` /
   `window.solana` providers and rewrote outgoing wallet transactions
   to attacker addresses -- the same wallet-drainer primitive seen in
   [[ledger-connect-kit]] and [[lottie-player-npm-2024]].
6. **Detection and stalling.** Socket and Phylum static-diff feeds
   flagged the postinstall + bundle.js pattern; the `Shai-Hulud`
   GitHub repository name was a reliable IOC. CISA, GitHub, and npm
   coordinated to unpublish the malicious versions and disable victim
   accounts.

## Lessons for bug hunters

- **`postinstall` + bundled `bundle.js` / `webhook.js` is the
  signature.** Any npm package whose `package.json` declares a
  postinstall script that runs a file not present in the GitHub
  source tree is a red flag. The diff between
  `npm pack`'s files and `git ls-files` for the matching tag is the
  single highest-signal supply-chain audit.
- **TruffleHog at runtime is a tell.** A legitimate library has no
  business invoking `trufflehog` or any credential-scanner. If a
  package's install path spawns one, it is exfiltrating. Process-tree
  monitoring on dev workstations and CI runners catches this.
- **Search GitHub for the campaign IOC name.** GitHub code search /
  repo search for `Shai-Hulud` (and successor names: `s1ngularity-
  repository`, `SANDWORM`, etc.) maps directly onto victim
  organisations. Bug-bounty hunters can use this to surface a target
  organisation's actual infection footprint before approaching them.
- **Lockfile audit is the structural defence.** Pinned
  `package-lock.json` / `pnpm-lock.yaml` with hash verification
  prevents in-place version-swap attacks. Any target that uses
  `^x.y.z` ranges in production CI without lockfile verification is
  shippable as a hardening finding.
- **Maintainer-token blast radius.** Every npm publish token is a
  worm vector if the maintainer publishes more than one package. The
  finding "your shared maintainer account publishes N packages with a
  single classic token" is a real reportable risk for a
  vendor-security program.
- **Look for the cross-namespace propagation graph.** A useful
  retrospective tool is to map "package A was infected at time T;
  every other package its maintainer owns was infected at T+epsilon"
  -- if that pattern is in the public npm publish history of a
  target's deps, the target was exposed during the window.

## Primary sources

- [Socket: Shai-Hulud -- the novel self-replicating worm infecting hundreds of npm packages](https://socket.dev/blog/shai-hulud-the-novel-self-replicating-worm-infecting-hundreds-of-npm-packages) <<NEEDS VERIFICATION>>
- [StepSecurity: Shai-Hulud -- self-replicating worm compromises 500+ npm packages](https://www.stepsecurity.io/blog/ctrl-tinycolor-and-40-npm-packages-compromised)
  -- corroborating writeup with the @ctrl/tinycolor entry-point
  analysis and full IOC list.

## Related

- [[nx-s1ngularity-2025]]
- [[xrpl-js-npm-2025]]
- [[lottie-player-npm-2024]]
- [[ledger-connect-kit]]
- [[ua-parser-js]]
- [[event-stream-flatmap-stream]]
- [[colors-faker-self-sabotage-2022]]
