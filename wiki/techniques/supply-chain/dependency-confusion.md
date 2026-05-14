---
title: Dependency confusion (private package name on public registry)
slug: dependency-confusion
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/supply-chain, technique/rce, registry/npm, registry/pypi]
inbound: []
---

# Dependency confusion

## Pattern

Companies use a private Artifactory/JFrog/CodeArtifact proxy in front of
the public registry (npm/PyPI/RubyGems). The proxy's resolution rule is
"prefer highest version across both private + public mirror." Publish a
package on the **public** registry with the **same name** as one of the
company's private internal packages but a **higher version number** --
the proxy serves your package to internal CI/dev machines. Top-level
script in the package then runs (`preinstall`/`postinstall` for npm,
`setup.py` for PyPI) -> RCE inside the CI host.

Alex Birsan original research (2021). Still actively paying out across
HackerOne and direct programs as of 2024.

## Preconditions

- Target organization references at least one private package by a name
  that is **unclaimed on the public registry**.
- Their build resolver does not pin to the private mirror exclusively or
  does not honour a `.npmrc` / `pip.conf` scope rule.
- Public registry account that lets you publish the package (npm + PyPI
  do not currently allow you to delete-and-overwrite a published version
  past 24h).

## Detection

Find candidate private package names via:

- `package.json` / `package-lock.json` / `requirements.txt` /
  `yarn.lock` in public open-source repos belonging to the target org.
- Path-fuzz `/package.json` (and `/package-lock.json`) at the web root
  of every in-scope web app.
- **package.json embedded in webpack bundle.** Some bundlers ship a
  string-serialised `package.json` inside the front-end JS -- extract via
  AST string-walk over minified bundles (jsweasel and depi do this).
- **Source-map source key.** Every `.js.map` JSON has a `sources` array
  listing `node_modules/<name>` and webpack module names -- pull every
  dependency name from there.
- **GitHub SBOM API.** Every public GitHub repo exposes an SBOM endpoint
  (`/dependency-graph/sbom`) returning all detected packages -- no need
  to clone + `npm install`.

Then check each name on `registry.npmjs.org/<name>` / `pypi.org/project/<name>`.
404 = claimable.

## Triggering

- Publish a placeholder package with version `99.99.99` and a
  `preinstall` script that callbacks to your registry (DNS exfil
  preferred -- works through Artifactory egress that blocks direct HTTP
  from dev hosts).
- **Don't host a backdoor directly on the public registry.** Registry
  scanners now flag callbacks. Workaround (depi 2024): set one of your
  package's dependencies to point at **your own registry URL**; serve
  benign on scanner IPs, real payload on victim IPs. Or use the
  supplyshark "week-old swap" pattern (benign for first 7 days, then
  swap to malicious on GitHub).
- Ethical: ask the program for an IP allow-list before going live.

## Exfil channel

- HTTP from the Artifactory host (it has egress; dev hosts often don't).
- DNS recursive -- survives stricter egress because the artifactory is
  itself proxied.
- HTTPS with the same trick.

## Bypasses (of registry-side scanners)

- Hot-swap by IP/scanner-fingerprint at your own registry.
- "Week-old swap" -- supplyshark pattern.
- Allowlist target IP ranges (most legally / ethically defensible).

## Seen in the wild

- {date: 2021, source: Alex Birsan} -- original blog, 20k+ medium claps;
  Microsoft / Apple / PayPal / Tesla / Yelp / Uber paid out.
- {date: 2024, source: CT Ep 74} -- depi sub-module first-run finds new
  confusion on enterprise targets weekly; one client averages 200k-400k
  packages in their internal dep tree.

## References

- Critical Thinking Podcast Ep 74 (with 0xLupin / Ronnie)
- Alex Birsan -- original Medium post (2021)
- Snorlax / matthew bryant -- Travis CI supplemental research
- depi -- `lnh.tech/depi` (Lupin's commercial scanner)
- Related: [[maintainer-domain-takeover]], [[npx-binary-package-confusion]]
