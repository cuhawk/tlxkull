---
title: Bybit / Safe{Wallet} UI compromise -- $1.46B ETH heist (Feb 2025)
slug: bybit-safewallet-ui
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, technique/frontend-tampering, technique/aws-token-theft, target/web3, actor/lazarus, exfil/multisig-bypass]
inbound: []
---

# Bybit / Safe{Wallet} UI compromise -- $1.46B ETH heist (Feb 2025)

## What happened

On **21 February 2025** Bybit lost roughly **401,347 ETH (~$1.46B)** in
a single signed transaction -- the largest crypto theft on record. The
exchange's cold wallet was a 3-of-N Gnosis Safe multisig administered
via the official Safe{Wallet} web UI at `app.safe.global`. When Bybit's
signers approved what their UI showed as a routine transfer between
their own wallets, they actually signed a `delegateCall` that swapped
the Safe's implementation contract for an attacker-controlled one,
which then drained the cold wallet.

The compromise was upstream of Bybit. On **4 February 2025**
DPRK's **Lazarus Group** social-engineered a Safe{Wallet} developer's
macOS workstation. From that laptop they harvested **AWS session
tokens** for the Safe deployment account, bypassed MFA (which gates
console login, not active-token reuse), and operated inside Safe's
AWS environment from 5 to 17 February. On **19 February** they
replaced the production `app.safe.global` JS bundle directly in the
**S3 bucket** that fronts the SPA. The malicious bundle filtered for
the Bybit cold-wallet Safe address, swapped the `to` / `data` fields
shown to the user against the payload actually proposed via the EIP-712
typed-data signature, and self-deleted after the heist transaction was
mined. Investigations by Sygnia and Verichains agree on the chain.

## Attack chain

1. **Targeted social engineering on a Safe developer.** Lazarus
   typically uses fake job-offer PDFs / npm packages (the
   `Operation Dream Job` pattern from [[ronin-bridge]]). The result:
   RCE on the developer's macOS box.
2. **AWS session-token theft.** Most cloud-CLI workflows write
   short-lived credentials to `~/.aws/credentials` or to environment
   variables in shell sessions. Active tokens are bearer tokens; MFA
   only gates initial console login, not subsequent API calls until
   token TTL expiry. Steal them, reuse them from anywhere.
3. **S3 object-overwrite of the SPA bundle.** `app.safe.global` is a
   static SPA served from S3 behind CloudFront. The deploy IAM role has
   `s3:PutObject` on the prod bucket. Overwrite `main.<hash>.js`
   directly; CloudFront's TTL flushes within minutes.
4. **Targeted UI tampering.** The malicious JS detected
   `bybit-cold-wallet`-shaped Safe addresses, intercepted the
   "Send transaction" flow, displayed the original benign tx details in
   the UI, but produced a different EIP-712 hash for the Ledger to
   sign -- a `delegateCall` to attacker's contract.
5. **Self-cleanup post-mining.** The malicious bundle was reverted (or
   deleted) shortly after the heist tx confirmed, hindering forensic
   capture; defenders rebuilt the bundle from CloudFront edge caches
   and Wayback snapshots.

## Lessons for bug hunters

- **A Web3 dApp's frontend is the security boundary.** Hardware
  wallets sign whatever EIP-712 hash the page produces; the user reads
  what the page displays. If you can tamper with the bundle (XSS,
  cache poisoning, SRI gap, CDN takeover, S3 misconfig, dependency
  confusion in the build pipeline), you can produce a signature for
  any tx. Cross-link [[ronin-bridge]] (key-theft path) and
  [[ultralytics-pypi]] (build-pipeline path).
- **AWS session tokens are bearer tokens. MFA-gated console !=
  MFA-gated API.** A target whose threat model claims "all AWS access
  is MFA-protected" is almost always lying about the
  `sts:AssumeRole` / `sts:GetSessionToken` short-lived-creds flow.
  Recon: look for `aws_access_key_id` / `aws_session_token` shapes in
  any GitHub PR, error log, Sentry payload, or Slack export the target
  exposes.
- **S3 deploy buckets with no object-lock / no SRI on the served HTML
  are a single-write-gate to user-side code execution.** On any Web3
  bounty: inspect the production frontend's S3 origin, CloudFront
  config (signed-URL? OAI / OAC? versioning? object lock?), and the
  CI role's IAM policy. A wide `s3:*` on prod is a finding.
- **Subresource integrity (SRI) hashes pinned in the entry HTML would
  have caught this.** Targets that lack SRI on their main bundle are
  vulnerable to any CDN/bucket compromise. Easy passive recon.
- **EIP-712 display vs signed hash.** The user sees a structured-data
  preview rendered by the dApp; the wallet displays a domain-separator
  + struct-hash. Mismatch = compromise. Recommend to clients that
  hardware-wallet flows decode and display the full call data, not the
  hash, for `delegateCall` / proxy upgrade operations.
- **Lazarus moves slowly.** 17 days from initial laptop compromise to
  the heist tx. Long dwell time + targeted-trigger payload defeats
  most synthetic-traffic monitoring.

## Primary sources

- [Sygnia: "Sygnia's Investigation into the Bybit Hack: What We Know So Far" (post-mortem)](https://www.sygnia.co/blog/sygnia-investigation-bybit-hack/)
- [NCC Group: "Bybit Hack: In-Depth Technical Analysis"](https://www.nccgroup.com/research/in-depth-technical-analysis-of-the-bybit-hack/)

## Related

- [[ronin-bridge]]
- [[ultralytics-pypi]]
- [[xz-utils-cve-2024-3094]]
