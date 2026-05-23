---
title: xrpl.js npm compromise (CVE-2025-32965)
slug: xrpl-js-npm-2025
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, language/javascript, registry/npm, technique/token-theft, technique/credential-stealer, target/crypto]
inbound: []
---

# xrpl.js npm compromise (CVE-2025-32965)

## What happened

On 2025-04-22 at 08:14 UTC, Aikido Security's malware research feed
flagged five newly published versions of the `xrpl` npm package -- the
official Ripple-maintained JavaScript SDK for the XRP Ledger -- as
containing a credential-stealing payload. The compromised versions were
**4.2.1, 4.2.2, 4.2.3, 4.2.4** (pushed within hours of each other on
2025-04-21) and **2.14.2** (a backport on the older 2.x line). The
package ships at ~140k weekly downloads and is the dependency every
XRPL dApp, custodial integration, and exchange-side signer imports.

Ripple's post-mortem attributed the breach to **phishing of a single
Ripple employee's npm publish credentials**. The attacker used the
stolen token to publish the malicious versions directly to the npm
registry -- the GitHub source tree was never modified, so anyone who
built from `main` was not affected. Ripple deprecated the malicious
versions and shipped clean `4.2.5` / `2.14.3` by mid-afternoon UTC the
same day. CVE-2025-32965 was assigned with CVSS 9.3. Any wallet
created or used in a process that loaded one of the compromised
versions must be considered compromised; affected users were instructed
to rotate keys.

## Attack chain

1. **Phish the publisher.** Spear-phish targeting a Ripple developer
   with npm publish rights yielded a valid `npm` access token. No 2FA
   prompt was required because the token was a long-lived publish token,
   not an interactive session.
2. **Publish-only divergence.** The attacker bumped four
   patch-level versions on the `4.x` line (4.2.1 → 4.2.4) plus one on
   `2.x` (2.14.2), all carrying the modified tarball. The corresponding
   GitHub tags were never pushed -- a classic "registry tarball ≠ git
   tag" mismatch that a casual reviewer comparing `npm view xrpl` to
   the GitHub releases page would have caught.
3. **Drop-in seed exfil function.** The malicious tarball added a
   helper named `checkValidityOfSeed` inside the wallet/keypair module.
   It was wired into the normal seed-decode code path so that every
   call to `Wallet.fromSeed(...)`, `Wallet.fromSecret(...)`, or any
   constructor that internally validates a seed silently POSTed the
   seed string to an attacker-controlled domain (`0x9c[.]xyz`) before
   returning the parsed wallet.
4. **No persistence, no second-stage.** The payload was a pure
   exfiltration primitive -- no post-install hook, no obfuscated
   bootstrapper, no on-disk dropper. It depended entirely on the
   victim's app loading the SDK and invoking a seed-handling function
   in production. This kept the diff small and the malicious-code
   footprint a single function plus one `fetch()` call.
5. **Detection.** Aikido's automated diffing of newly published
   versions against prior releases flagged the unexpected outbound
   network call inserted into a cryptography hot-path. Manual triage
   confirmed the seed reached `0x9c[.]xyz`.

## Lessons for bug hunters

- **Registry-vs-VCS divergence is a first-class signal.** When the npm
  tarball contains files that do not appear in the `git` tag for the
  same version, treat that as a P1 indicator. `npm pack` against the
  source tree and diff against `npm view <pkg>@<ver> --json` plus the
  unpacked tarball.
- **Crypto-wallet SDKs are the highest-value supply-chain targets.**
  Any SDK whose normal API surface accepts secret material (seeds,
  keys, mnemonics) provides a one-line exfil primitive. Look for
  surprise `fetch`/`XMLHttpRequest`/`navigator.sendBeacon` calls in
  keypair or signer modules. See [[ledger-connect-kit]] and
  [[solana-web3js]] for sibling incidents.
- **Long-lived publish tokens are a phishing magnet.** Bug-bounty
  hunters reviewing a vendor's npm hygiene should check for
  `2FA: auto` on the maintainer set (`npm access list collaborators`)
  and for the presence of automation tokens with no scope restriction.
- **Function-name pattern signal.** A new helper named
  `checkValidityOfSeed`, `validateMnemonic`, `verifyWallet`, etc., that
  ships in a patch release without a corresponding test or PR is worth
  five minutes of grep. Phishing-driven supply-chain attacks reuse this
  "benign wrapper around exfil" pattern across incidents.
- **Hour-zero diff window matters.** The malicious versions lived for
  roughly eight hours before deprecation. CDN caches, lockfile-pinning
  CI runs, and offline mirrors that resolved within that window still
  carry the bad tarball. Hunters auditing a target's `package-lock.json`
  for known-bad SHAs can find lingering exposure long after the
  registry was cleaned.

## Primary sources

- [Aikido: XRP supply chain attack -- official npm package infected with crypto-stealing backdoor](https://www.aikido.dev/blog/xrp-supplychain-attack-official-npm-package-infected-with-crypto-stealing-backdoor)
  -- the original disclosing writeup with the IOC list.
- [XRPL Foundation: Vulnerability disclosure report, April 2025](https://xrpl.org/blog/2025/vulnerabilitydisclosurereport-bug-apr2025)
  -- Ripple's official post-mortem with the timeline and CVE
  reference.

## Related

- [[ledger-connect-kit]]
- [[solana-web3js]]
- [[ua-parser-js]]
- [[lottie-player-npm-2024]]
- [[shai-hulud-npm-worm-2025]]
