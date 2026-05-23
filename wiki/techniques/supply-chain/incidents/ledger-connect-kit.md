---
title: Ledger Connect Kit drain (Angel Drainer, Dec 2023)
slug: ledger-connect-kit
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, registry/npm, ecosystem/web3, technique/phishing, technique/ex-employee, technique/cdn-style-loader, technique/wallet-drainer]
inbound: []
---

# Ledger Connect Kit drain (Angel Drainer, Dec 2023)

## What happened

On **2023-12-14**, a former Ledger employee was successfully
spear-phished. The phishing flow harvested their **active npmjs
session token** (not credentials -- session-cookie style), bypassing
the 2FA they did have configured. The attacker used the live session
to publish three malicious versions of **`@ledgerhq/connect-kit`**
(versions 1.1.5, 1.1.6, 1.1.7), the npm package that every Ledger-
integrated dApp uses to negotiate wallet connections in the browser.

Critically, the standard integration pattern was a thin loader
called `@ledgerhq/connect-kit-loader` that **dynamically fetched
the latest version of connect-kit from npm at page-load time**, via
unpkg.com / jsDelivr. So dApps did not need to re-deploy to be
infected -- the moment 1.1.5 went live on npm, every running dApp's
browser fetched the malicious bundle on the next user wallet
connect. The malicious payload was the **Angel Drainer** wallet-
drainer-as-a-service: it presented Ledger-branded transaction
prompts that, when signed, executed `approve`/`permit` operations
draining ERC-20 tokens, NFTs, and native ETH to the attacker.

Total window: **~5 hours from npm publish to genuine 1.1.8 push**,
with the active drain happening in a ~2-hour window. Reported loss
was **~$600,000** across SushiSwap, Zapper, Revoke.cash, Hey,
Balancer, Phantom, and dozens of other dApps. Root cause: ex-employee
npm access was not revoked on offboarding -- only internal corp
access was. Angel Drainer was a malware-as-a-service operator;
on-chain analytics show the 85/15 revenue split typical of drainer
SaaS.

## Attack chain

1. **Spear-phish targeting session, not password.** Phish email
   delivered to former employee's still-active inbox, linking to a
   fake login. Attacker captured the session cookie rather than
   creds + TOTP -- so the post-login MFA was already cleared.
2. **Off-boarding gap.** Ledger's internal corp SSO had been
   revoked at offboarding. The ex-employee's **separate npmjs
   account**, which still held publish rights to `@ledgerhq/*`,
   was never revoked. Lesson: registry / vendor / cloud accounts
   are a parallel access plane to corp SSO.
3. **Three quick publishes.** 1.1.5, 1.1.6, 1.1.7 in succession --
   same pattern as `ua-parser-js`. Maximises coverage of consumers
   pinning at different points.
4. **The loader-pattern multiplied blast radius.** `connect-kit-
   loader` was a tiny bootstrapper that, on each pageview, fetched
   the current latest from npm CDN
   (`https://cdn.jsdelivr.net/npm/@ledgerhq/connect-kit/...`). dApps
   did not bundle the kit at their own build time -- they hot-loaded
   from npm. Zero redeploys needed for the malicious code to reach
   end users.
5. **Angel Drainer payload.** The malicious bundle injected a
   Ledger-styled modal that, on "Connect", asked the user to sign
   what looked like a routine approval. The signature granted ERC-20
   approval / EIP-2612 permit / NFT setApprovalForAll to the
   attacker contract, or for native ETH, signed an outright transfer.
   The drainer infrastructure was the same Angel Drainer SaaS used
   on prior dApp phishing campaigns since Oct 2023.
6. **Detection + remediation.** SushiSwap CTO publicly warned at
   13:54 UTC. Ledger pushed 1.1.8 (clean) and revoked the npm
   credentials within 40 minutes of internal awareness. Total time-
   from-publish-to-cleanup ~5 hours; active-drain window ~1h45.

## Lessons for bug hunters

- **Ex-employee access in third-party registries is a recurring
  off-boarding miss.** When investigating a target's offboarding
  process, ask: was the ex-employee's npm / PyPI / Docker Hub /
  GitHub / HuggingFace / vercel / cloudflare account revoked?
  These are parallel to corp SSO and often missed. Findings here
  are common, especially in pre-IPO crypto/web3 companies.
- **CDN-loader patterns turn npm publish into a website XSS.** Any
  app that ships a bootstrapper hot-loading from jsDelivr / unpkg /
  esm.sh at runtime is effectively trusting the registry at user-
  visit time, not at build time. If a target's HTML pulls `<script
  src="https://cdn.jsdelivr.net/npm/...@latest">` -- or any unpinned
  CDN ref -- that's exploitable surface (and a hardening finding).
  Subresource Integrity (SRI) hashes are the defence.
- **Session-cookie theft beats TOTP.** Programs that scope a single
  long-lived web session to publish rights are accepting that any
  phish of an active maintainer session = publish. WebAuthn-bound
  publish tokens (npm's newer model, post-this-incident) is the
  defence; finding programs that lack equivalent on their own
  release pipelines is a hardening report.
- **Drainer-as-a-service exists.** The 85/15 on-chain split is a
  recognisable signature. When investigating a wallet-drain
  incident in a target's web3 product, on-chain attribution to a
  known drainer SaaS (Angel, Inferno, Pink, MS Drainer) is fast
  triage. Cross-link to the [[wallet-drainer-signatures]] page if
  one is added.
- **Phantom was named but unaffected** -- Phantom's wallet runs in
  a browser extension context that did not load the malicious
  connect-kit. Worth modelling: do dApp users get their drained
  approval via the dApp's own JS context, or via the wallet's? The
  former is exposed to every supply-chain risk of every dep the
  dApp ships.

## Primary sources

- [Ledger: Security Incident Report (Dec 2023)](https://www.ledger.com/blog/security-incident-report)
  -- Ledger's own post-mortem with timeline, root cause (ex-employee
  phish + npm session token), and remediation steps.
- [Phylum: Ledger npm Repo Breached in Spear Phishing Attack](https://blog.phylum.io/ledger-phishing-attack-connect-kit/)
  -- deep technical writeup of the malicious bundle, the Angel
  Drainer behaviour, and the connect-kit-loader CDN amplification.

## Related

- [[solana-web3js]]
- [[reviewdog-action-setup]]
- [[ua-parser-js]]
- [[maintainer-domain-takeover]]
