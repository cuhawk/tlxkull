---
title: "@solana/web3.js backdoor (CVE-2024-54134, Dec 2024)"
slug: solana-web3js
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, registry/npm, ecosystem/web3, technique/phishing, technique/publish-token, technique/header-channel-exfil, technique/private-key-steal]
inbound: []
---

# @solana/web3.js backdoor (CVE-2024-54134, Dec 2024)

## What happened

On **2024-12-02** between 15:20 UTC and 20:25 UTC, attackers
published malicious versions **1.95.6 and 1.95.7** of
`@solana/web3.js` -- the official JavaScript SDK for the Solana
blockchain (~400-450K weekly downloads, dep of most Solana dApps and
bots). The publish was achieved via a phishing campaign that
targeted maintainers with **publish rights** to the package: the
phishing site cloned the npm login page, captured username +
password + a fresh 2FA code (live relay), and yielded a working
session.

The payload added a function `addToQueue` to the SDK. Wherever the
SDK touched a private key (signing transactions, instantiating
`Keypair`), `addToQueue` was called with the key material. The
function exfiltrated the key out-of-band via **HTTP headers** to
`sol-rpc[.]xyz`, masquerading the data as **CloudFlare-style
`CF-*` headers** so network monitors looking for unusual request
bodies saw clean JSON-RPC traffic. The C2 domain had been
registered 10 days earlier (2024-11-22) on NameSilo and was
proxied through CloudFlare for additional camouflage.

The window was **~5 hours**; the Solana team published 1.95.8
(clean) and yanked the malicious tags. CVE-2024-54134 (CVSS 8.3)
was assigned. On-chain attribution to wallet
`FnvLGtucz4E1ppJHRTev6Qv4X7g8Pw6WPStHCcbAKbfx` shows **~$160,000
drained**. The impact was limited to applications that **directly
handle private keys server-side** -- self-custody bots, automated
LP rebalancers, custodial backends -- and that pulled an `npm
install` during the window. Wallet apps that delegate signing to
extensions (Phantom, Solflare) were not exposed because the
malicious code lived inside the dApp's JS context, not the
wallet's.

## Attack chain

1. **Phishing campaign cloned npm login.** Targeted maintainers
   with publish access to `@solana/web3.js`. The phishing relay
   site captured user + password + a TOTP from the user's
   authenticator, then logged in to npm in real time. This yields
   a session token; 2FA on every-publish was not enabled.
2. **Two malicious patch releases.** 1.95.6 and 1.95.7 pushed in
   quick succession after 1.95.5 (clean). Both versions auto-
   resolved on `^1.95.0` carets within minutes of publish.
3. **In-code injection, not lifecycle script.** Unlike most npm
   incidents, there is no `postinstall` -- the malicious code is
   in the SDK's runtime path. `addToQueue` was added to the
   `Keypair`, `signTransaction`, and `sign` codepaths. Static-
   analysis tools that only flag lifecycle scripts missed this
   entirely.
4. **Header-channel exfil to look like CloudFlare.** The
   exfiltration HTTP request had body fields shaped like normal
   Solana JSON-RPC calls, but added headers like `CF-Ray`,
   `CF-Connecting-IP`, `CF-Worker`, etc. -- whose values were
   base64-encoded chunks of the private key. The receiving server
   parsed them off the request headers; network mirrors looking
   only at bodies saw clean traffic.
5. **C2 behind CloudFlare proxy.** `sol-rpc.xyz` was a NameSilo-
   registered domain CloudFlare-proxied to hide origin IP. Domain
   age: 10 days. Common operator pattern: register, warm up,
   detonate, abandon.
6. **Detection.** Solana team caught the malicious code via
   community report within hours, pulled the versions, pushed
   1.95.8. Socket.dev, ReversingLabs, and Phantom published
   technical writeups same-day.

## Lessons for bug hunters

- **In-code malice beats lifecycle scripts at evasion.** Hunters
  who only scan `pre/post-install` scripts on a target's deps are
  blind to this class. When auditing a target's `node_modules` for
  surprise outbound traffic, instrument the runtime path, not just
  install. Tools: `node --inspect`, eBPF on the runner, Falco.
- **Header-channel exfil is a stealth primitive.** Putting key
  material in **request headers** instead of bodies dodges most
  WAFs, DLP, and CASB rules -- header inspection is the rare
  configuration. When investigating a target's egress monitoring,
  ask whether they inspect outbound headers (not just bodies and
  TLS SNI). Most don't.
- **Newly-registered domain + CloudFlare proxy is a recognisable
  C2 pattern.** Domain age < 30 days + CloudFlare proxy + WHOIS
  privacy + NameSilo / Porkbun registrar bias = supply-chain C2
  signature. Threat-intel feeds (Spamhaus, abuse.ch) flag these;
  cross-reference against a target's egress allowlist.
- **Server-side private-key handlers are the high-value targets.**
  Wallet extensions are sandboxed; bots, custodial backends, and
  CI signers are not. If a target's product owns customer keys
  server-side, the threat model includes every JS dep in its
  signing path -- this is far less common than people think, but
  every crypto-bot, MEV searcher, and CEX has at least one such
  service.
- **Phishing-with-live-MFA-relay is the dominant 2024+ attack.**
  Static credential reuse is mostly mitigated; phish-on-live-MFA
  is not. Programs that haven't deployed phishing-resistant MFA
  (WebAuthn / passkeys) for publish access are accepting the
  Ledger / Solana attack model. See [[ledger-connect-kit]] for
  the prior precedent.

## Primary sources

- [Socket.dev: Supply Chain Attack Detected in Solana's web3.js Library](https://socket.dev/blog/supply-chain-attack-solana-web3-js-library)
  -- Socket's incident detection writeup with annotated
  `addToQueue` payload and the CloudFlare-header exfil channel.
- [The Hacker News: Researchers Uncover Backdoor in Solana's Popular Web3.js npm Library](https://thehackernews.com/2024/12/researchers-uncover-backdoor-in-solanas.html)
  -- consolidated technical reporting with CVE-2024-54134 details,
  C2 attribution, and on-chain loss accounting.

## Related

- [[ledger-connect-kit]]
- [[ua-parser-js]]
- [[reviewdog-action-setup]]
- [[event-stream-flatmap-stream]]
