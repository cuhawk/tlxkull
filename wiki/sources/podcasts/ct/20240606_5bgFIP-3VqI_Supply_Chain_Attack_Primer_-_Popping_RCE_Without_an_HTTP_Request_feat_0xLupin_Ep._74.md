---
title: Ep 74 -- Supply Chain Attack Primer (0xLupin / Ronnie)
slug: ct-ep-74-supply-chain-attack-primer
url: https://www.youtube.com/watch?v=5bgFIP-3VqI
fetched_utc: 2026-05-14T00:00:00Z
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, supply-chain, dependency-confusion, npm, npx, maintainer-takeover, cache-poisoning, recon]
inbound: []
---

# Ep 74 -- Supply Chain Attack Primer -- Popping RCE Without an HTTP Request (feat. 0xLupin)

- Date: 2024-06-06
- video_id: 5bgFIP-3VqI
- Speakers: Justin Gardner (JG), guest 0xLupin / Ronnie

## Summary

Deep tour of the modern software-supply-chain attack surface led by
Ronnie (founder of depi, lnh.tech). Re-covers Alex Birsan's 2021
dependency-confusion shape and walks through how registry-side scanners
made it harder: depi runs its own registry and hot-swaps malicious vs
benign packages by IP allow-list to stay legally clean. Demos package
enumeration via package.json embedded in webpack bundles, source-map
`sources` keys, and the GitHub SBOM API (every public repo exposes a
free dependency graph). Discusses maintainer-domain-takeover at scale
(weak-links paper, npm 2FA mandatory only above 1M weekly downloads).
Covers npm cache-poisoning via a specific malformed request header that
poisons the CDN edge with a 404 -- DoS of `express` etc., disclosed
to GitHub but downgraded to abuse/$500 over a year of back-and-forth.
New attack class: npx binary-vs-package confusion -- `npx grafana-toolkit`
resolves to the unscoped public name, attacker claims it. Touches CI
attacks (Ed Overflow + Justin's Travis CI work), git-history scanning
via Tom Nom Nom's `git-dump`, and microservice-name to internal source-code
pivoting (Justin's PayPal $50k chain origin). Closes with European
SBOM-mandatory regulation and how that shifts liability onto the
package consumer, not the upstream maintainer.

## Techniques extracted

- [[../../techniques/supply-chain/dependency-confusion]] -- publish higher-version public package with private name; Birsan original, depi-era ethical-hosting workarounds.
- [[../../techniques/supply-chain/maintainer-domain-takeover]] -- lapsed maintainer email-domain -> registry password-reset -> backdoor publish.
- [[../../techniques/supply-chain/npm-cache-poisoning-404]] -- specific malformed header poisons CDN edge with a cached 404 -> npm install DoS.
- [[../../techniques/supply-chain/npx-binary-package-confusion]] -- `npx <dashed-name>` resolves to public registry when scoped name was intended.
- [[../../techniques/recon/supply-chain-package-enum]] -- full enumeration pipeline: package.json sources, webpack bundles, .js.map source keys, GitHub SBOM API, git-dump, microservice-name -> GitHub.

## Tools mentioned

- depi -- `lnh.tech/depi`, Ronnie's commercial Rust-built supply-chain scanner.
- jsweasel -- JS-bundle string walker; detects embedded package.json.
- jsluice (Tom Nom Nom) -- go-tree-sitter JS URL/secret extractor.
- git-dump (Tom Nom Nom dot-files) -- dumps every file ever referenced in git history, including deleted blobs.

## Quotes

> "What's interesting about npx is that if you do `npx <package>` and you
> do not have the binary name inside your computer it will pull from the
> public registry and install the package and run it ... but the public
> registry takes packages name and npx takes a binary name, so there is a
> confusion."
> -- Ronnie, on the npx attack class.

> "We managed to make a 404 ... cached on the prod registry. Like it's
> not even an artifactory, it's the registry."
> -- Ronnie, on the npm cache poisoning bug.

> "Once you step back and you don't see it as a web app scope but more as
> a supply chain hub, you'll find many more vulnerabilities."
> -- Ronnie, on attacking artifactories themselves.

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
