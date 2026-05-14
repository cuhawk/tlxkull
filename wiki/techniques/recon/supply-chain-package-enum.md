---
title: Supply-chain package enumeration for a target
slug: supply-chain-package-enum
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/recon, technique/supply-chain]
inbound: []
---

# Supply-chain package enumeration

## Pattern

Before any supply-chain attack (dependency confusion, npx confusion,
maintainer takeover) you need an accurate list of the target's private
+ internal package names. Multiple sources, in increasing order of
yield.

## Sources

### 1. Open-source repos
- `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`,
  `requirements.txt`, `Pipfile.lock`, `Gemfile.lock`, `go.mod`.
- Walk every commit in `git log` -- Tom Nom Nom's `git-dump` script
  iterates every blob ever referenced and dumps deleted-package
  references that the latest HEAD no longer shows. Often surfaces
  internal package names devs scrubbed from HEAD.

### 2. Web-root path fuzzing
- `/package.json`, `/package-lock.json` on every web app.
- `/composer.json`, `/composer.lock`.

### 3. Webpack-bundled `package.json`
- Some bundlers ship a string-serialised `package.json` inside the
  minified JS. Pulled via AST string-walk -- jsweasel has a detector;
  jsluice can be adapted.

### 4. Source-map source key
- Every `.js.map` JSON has a `sources` array listing
  `node_modules/<name>`, `webpack:///./src/utils/...`, etc.
- All private package names appear under `node_modules/`.
- Cheaper than full source-map reconstruction.

### 5. GitHub SBOM API (highest signal)
- Every public GitHub repo exposes
  `GET /repos/{owner}/{repo}/dependency-graph/sbom`.
- Returns full transitive dependency set including lockfile-resolved
  packages.
- No `npm install` required; works for repos too large to clone.
- Authenticated personal token needed; respects repo visibility.

### 6. Artifactory log / metadata leaks
- Some build CI logs leak `npm install --registry=<internal>` traffic
  containing internal package names.
- Search GitHub for `path:package-lock.json <artifactory-domain>` ->
  often surfaces internal devs' personal repos containing internal
  packages.

### 7. Microservice/host naming patterns
- Errors / response bodies sometimes leak internal microservice names
  that map 1:1 to internal npm package names (Justin's PayPal example
  in Ep 74).
- Take any unique-looking string ("svc-payments-orchestrator") to
  GitHub code search -> surfaces accidentally-pushed internal repos.

## Triggering

Combine all sources into a deduped list. For each name:

- Check `registry.npmjs.org/<name>` / PyPI / RubyGems for 404 ->
  claimable for dependency confusion.
- Check if a dashed/scoped split exists -> npx-confusion candidate.
- Look up published maintainers -> maintainer-takeover candidates.

## Seen in the wild

- {date: 2024-06, source: CT Ep 74} -- depi runs all of the above as
  separate research modules; first-run on most enterprise targets
  yields at least one claimable name.
- {date: 2021, source: PayPal / Alex Birsan} -- microservice-name ->
  GitHub -> leaked internal source code with secrets -> $50k+ in
  derivative bugs.

## References

- Critical Thinking Podcast Ep 74
- Critical Thinking Podcast Ep 26 -- `git-dump`, jsluice mentions
- Alex Birsan -- original dependency confusion writeup
- GitHub Docs -- SBOM API
- Related: [[../supply-chain/dependency-confusion]],
  [[../supply-chain/npx-binary-package-confusion]],
  [[../supply-chain/maintainer-domain-takeover]]
