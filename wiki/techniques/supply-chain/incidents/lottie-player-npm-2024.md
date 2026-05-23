---
title: @lottiefiles/lottie-player npm compromise (Oct 2024)
slug: lottie-player-npm-2024
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, language/javascript, registry/npm, technique/token-theft, technique/wallet-drainer, target/crypto]
inbound: []
---

# @lottiefiles/lottie-player npm compromise (Oct 2024)

## What happened

On 2024-10-30 between roughly 20:00 and 22:00 UTC, three sequential
versions of the `@lottiefiles/lottie-player` npm package -- **2.0.5,
2.0.6, 2.0.7** -- were published to npm within a one-hour window. The
package is the official LottieFiles web renderer for Lottie/Bodymovin
animations, embedded as a `<lottie-player>` Web Component on
millions of marketing pages and dApps; weekly download volume is in
the hundreds of thousands.

The malicious versions injected a **Web3 wallet-connection prompt**
into every page that loaded the component. Reports surfaced first from
users of **1inch's dApp** seeing an unexpected "Connect Wallet" modal;
Blockaid's frontend telemetry flagged the same pattern across multiple
crypto sites within minutes. The dialog was the third-party "Ace
Drainer" SDK, which signs a malicious approval transaction once the
victim connects. At least one victim reportedly lost approximately
**$723k of Bitcoin** to the drainer. LottieFiles' published
post-mortem confirmed the root cause was an **email phishing attack
that took over a developer's npm publishing account**. The malicious
versions were unpublished and a clean `2.0.8` (binary-identical to the
known-good `2.0.4`) was released the same evening UTC.

## Attack chain

1. **Phish the maintainer.** A LottieFiles developer with publish
   rights on the `@lottiefiles` npm scope was phished. The attacker
   obtained a valid publish token; npm 2FA was either not enforced on
   the automation token path or was bypassed via the OTP-replay
   variant common in 2024 npm ATOs.
2. **Rapid burner-version sequence.** Three patch-level publishes
   (2.0.5 → 2.0.7) inside one hour. The accelerated cadence is a
   characteristic ATO tell -- legitimate maintainers rarely cut three
   patches in 60 minutes. The GitHub repo had no matching tags or
   commits for any of the three.
3. **Wallet-drainer injection at render time.** The malicious bundle
   appended a Web3 prompt routine to the player's component
   lifecycle. When the custom element connected to the DOM on any
   embedding site, it invoked the Ace Drainer SDK to render a fake
   wallet-connect modal styled to match the host site.
4. **Approval-transaction theft.** Victims who connected and approved
   the Ace Drainer transaction signed an `approve()`/`setApprovalForAll`
   that handed token-spending authority to the attacker's contract.
   The actual drain happened off-page from the attacker's wallet later.
5. **Detection & rollback.** Sansec, Snyk, and Blockaid published
   advisories within hours. Affected versions were unpublished from
   npm; LottieFiles released `2.0.8` rebuilt from the clean
   `2.0.4` source. CDN-served copies of the malicious bundle continued
   to serve from caches for some period afterward.

## Lessons for bug hunters

- **UI components with a wide-iframe-style audience are
  drainer-magnets.** Any package whose runtime job is to inject HTML
  / Web Components into a host page is one bad patch away from a
  drainer attack on every embedder. Audit the install/start scripts
  AND the runtime DOM-mutation surface of UI deps.
- **Three patches in an hour = ATO until proven otherwise.** Compare
  npm publish times (`npm view <pkg> time`) against commit times on
  the GitHub repo. A version that exists on npm without a matching
  git tag or release is an immediate audit signal. See
  [[xrpl-js-npm-2025]] for the same pattern.
- **Web3 prompt injection from a CDN-hosted lib.** Bug-hunters working
  bug-bounty programs that pay for "supply-chain risk in vendor
  dependencies" can grep the target's HTML for
  `<lottie-player>`, `<spline-viewer>`, `<dotlottie-player>`, etc.,
  and pin the served version against the known-clean baseline. The
  bounty case is the same any time a third-party UI component can
  inject DOM into a high-trust page.
- **Token security on maintainer accounts is the actual attack
  surface.** Bug-bounty researchers reporting "your CDN-fetched
  component is from a phishable maintainer" can frame the finding as
  a hardening recommendation -- worth a low-severity payout on
  programs that scope third-party dep hygiene (Synack tier-1
  customers, many DeFi programs).
- **Ace Drainer / Inferno Drainer / Pink Drainer signatures.** Static
  scanning a JS bundle for known drainer-SDK fingerprints (eval'd
  base64 blobs, specific Web3 modal CSS class names, calls to
  `eth_sendTransaction` with `setApprovalForAll`) catches re-uses of
  the same drainer-as-a-service across incidents.

## Primary sources

- [Sansec: Supply chain attack compromises @lottiefiles/lottie-player npm package](https://sansec.io/research/lottiefiles-supply-chain) <<NEEDS VERIFICATION>>
- [Snyk: Lottie Player npm package compromised for crypto wallet theft](https://snyk.io/blog/lottie-player-npm-package-compromised-crypto-wallet-theft/)
  -- detailed technical writeup with version-level IOCs.

## Related

- [[xrpl-js-npm-2025]]
- [[ledger-connect-kit]]
- [[solana-web3js]]
- [[polyfill-io-cdn-2024]]
- [[shai-hulud-npm-worm-2025]]
