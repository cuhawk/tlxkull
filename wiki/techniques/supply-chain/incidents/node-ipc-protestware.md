---
title: node-ipc protestware (CVE-2022-23812, Mar 2022)
slug: node-ipc-protestware
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, registry/npm, technique/protestware, technique/maintainer-ideology, technique/geofenced-payload, technique/destructive]
inbound: []
---

# node-ipc protestware (CVE-2022-23812, Mar 2022)

## What happened

Between **2022-03-07 and 2022-03-15** maintainer **Brandon Nozaki
Miller (RIAEvangelist)** -- the legitimate, long-standing author of
the npm package `node-ipc` (~1M downloads/week) -- shipped two waves
of intentionally destructive code in his own package, motivated by
Russia's invasion of Ukraine. **Version 10.1.1 (2022-03-07)**
contained a payload that read the host's outbound IP via
`https://api.ipgeolocation.io/`, checked whether the country was
Russia or Belarus, and if so recursively overwrote every file the
process could write with a Unicode "heart" character (U+2764). The
payload was obfuscated as base64 with a layer of string-reversal.
**Version 9.2.2 and 11.x (2022-03-15)** added `peacenotwar` as a
dependency -- a non-destructive package that dropped a
`WITH-LOVE-FROM-AMERICA.txt` anti-war message file on the user's
desktop and any `node_modules` directory it found.

The blast radius was significant because `node-ipc` was an indirect
dep of **@vue/cli** (the Vue.js scaffolding tool) and thousands of
other build chains. Vue CLI pulled the destructive 10.1.1 within
hours via `^9.x` semver ranges that resolved up to the new major.
Reports of wiped filesystems came in from Russian developer
machines. GitHub assigned **CVE-2022-23812** to the destructive
variant -- one of the first CVEs ever issued against intentional,
ideologically-motivated open-source sabotage by the legitimate
maintainer. The incident established that "the maintainer is honest"
is no longer a defensible assumption.

## Attack chain

1. **No account compromise -- the legitimate maintainer is the
   threat.** RIAEvangelist published the malicious code himself,
   under his own credentials, with his real identity attached. There
   is no IoC at the credentials layer.
2. **Semver-range auto-upgrade.** Most `node-ipc` consumers pinned
   via `^9.x` or `^10.x` caret ranges. On any `npm install` after
   2022-03-07 those consumers pulled the new version.
3. **Geofencing via IP geo-lookup.** The payload made an outbound
   request to `api.ipgeolocation.io` (free public API; no key for
   small volumes). If the response JSON contained `country_code` of
   `RU` or `BY`, the destructive branch ran.
4. **Recursive file-wipe.** Using `fs.readdir` + `fs.writeFile`,
   the payload walked the current process's working directory tree
   and overwrote every readable file with a single heart emoji.
   No deletion, no rename -- pure overwrite, so the wipe survived
   undelete tooling but did not consume new disk inodes.
5. **Stage-two: peacenotwar dep + license flip.** A week later,
   9.2.2 (back-published to the legacy line) and 11.x added
   `peacenotwar` as a runtime dep and changed the package license
   from MIT to **DBAD** ("Don't Be a Dick"). Both moves made
   downstream re-licensing impossible without rebuilding from a
   pre-2022-03 lockfile.
6. **Detection.** A GitHub issue on `node-ipc` from a community
   user pointed out the obfuscated payload within ~30 hours of the
   first push. Snyk filed CVE-2022-23812 the following week. npm
   did not unpublish; the code stayed up because it was the
   maintainer's own.

## Lessons for bug hunters

- **Maintainer-ideology is a supply-chain threat vector.** Pre-2022
  threat models assumed "compromised account = malicious code".
  Post-node-ipc, "maintainer turns hostile" is in scope -- any
  political flashpoint (war, election, religious crisis) is a
  trigger window. Audit dep histories for commit-message and
  README-tone shifts during such windows.
- **Geofenced payloads dodge most CI scanners.** A scanner running
  `npm install` in a US-hosted CI sees only the benign branch -- the
  destructive branch only fires from RU/BY IPs. When auditing a
  suspect package, run the install behind VPN exits in multiple
  geographies, or mock the IP-geo response.
- **Caret-range semver auto-upgrade still rules.** `node-ipc` jumped
  from `9.2.1` benign to `10.1.1` destructive on the same caret
  range because the caret was `^9` (next minor only) for some users,
  but many had no upper-bound at all. Programs that ship pinned
  lockfiles AND auto-rebuild lockfiles weekly are accepting the
  caret-range risk in slow motion.
- **License changes are an IoC.** Any maintainer flipping from MIT
  / Apache / BSD to a custom or joke license is signalling intent
  to assert non-software-license terms. DBAD, JSON, WTFPL flips on
  high-impact packages are worth flagging in a supply-chain audit.
- **Vue CLI was the canonical victim.** A high-popularity meta-tool
  pulls dozens of utility packages with loose pinning -- the
  meta-tool's risk surface is the union of its deps' maintainer
  threat models. When auditing a target that pulls a CLI generator
  (Vue, Create-React-App, Angular CLI, Nest CLI), the generator's
  dep tree is the threat tree.

## Primary sources

- [Snyk: peacenotwar malicious npm node-ipc package vulnerability](https://snyk.io/blog/peacenotwar-malicious-npm-node-ipc-package-vulnerability/)
  -- Snyk's incident analysis with CVE-2022-23812 details, the
  obfuscated payload reverse-engineering, and the IP-geo logic.
- [BleepingComputer: BIG sabotage -- famous npm package deletes files to protest Ukraine war](https://www.bleepingcomputer.com/news/security/big-sabotage-famous-npm-package-deletes-files-to-protest-ukraine-war/)
  -- detailed technical writeup with annotated payload source and
  the Vue.js CLI downstream impact.

## Related

- [[event-stream-flatmap-stream]]
- [[xz-utils-cve-2024-3094]]
- [[ua-parser-js]]
- [[maintainer-domain-takeover]]
