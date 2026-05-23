---
title: Wormhole Solana bridge exploit (Feb 2022)
slug: wormhole-solana
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, chain/solana, chain/ethereum, technique/account-confusion, technique/signature-bypass, surface/cross-chain-bridge]
inbound: []
---

# Wormhole Solana bridge exploit (Feb 2022)

## What happened

On 2022-02-02 an attacker drained the Solana side of the Wormhole
token bridge by forging guardian signatures and minting 120,000 wETH
(~$326M at the time) to themselves. Roughly 93,750 of those wETH were
bridged back to Ethereum mainnet before the team paused contracts. The
exploit went through in a single transaction. Jump Crypto, parent of
Wormhole, backstopped the loss within 24 hours by refilling the bridge
from its own treasury, preventing a wETH<->ETH depeg across the
ecosystem.

The root cause was an **account-confusion** bug in the Solana
program's signature-verification path. Wormhole used the deprecated
`solana_program::sysvar::instructions::load_current_index` (and
`load_instruction_at`), which read instruction data from a provided
account *without verifying that account was actually the instructions
sysvar*. A fix that swapped to the `*_checked` variants was already
merged on GitHub but had not yet been deployed -- the attacker observed
the public commit and built their exploit against the live program.

## Attack chain

1. **Spoofed instructions sysvar.** The attacker created a regular
   account whose data layout matched the `Instructions` sysvar
   serialization, and passed it in place of the real sysvar to
   Wormhole's `verify_signatures` instruction.
2. **Forged `Secp256k1` precompile evidence.** The spoofed account
   contained a serialized "previous instruction" pointing at the Solana
   `Secp256k1` precompile with attacker-chosen public keys and
   signatures. Wormhole's guardian-set check trusted the embedded data
   without re-running the precompile against the real transaction.
3. **`SignatureSet` minted.** With signature verification short-
   circuited, Wormhole wrote a `SignatureSet` PDA marking 19 of 19
   guardian signatures as valid for an attacker-controlled VAA payload.
4. **VAA -> mint 120k wETH on Solana.** The VAA authorised a
   `complete_wrapped` mint of 120,000 wETH on Solana to the attacker's
   token account; no actual ETH was ever locked on the L1 side.
5. **Bridge back.** Attacker bridged ~93,750 wETH to Ethereum via the
   normal redeem path, draining the L1 lockbox.

## Lessons for bug hunters

- **Sysvar / well-known-account confusion is a class.** Any Solana
  (or Anchor) program that reads from a sysvar via a deprecated/`*_unchecked`
  accessor is a candidate -- grep for `load_instruction_at`,
  `load_current_index`, `Sysvar::from_account_info` without an address
  equality check. Cross-link [[deprecated-api-cleanup-lag]].
- **Public-commit windows.** When a target merges a security fix to a
  public repo before deploying it, the merge SHA is a starting gun.
  Watch GitHub for the target's bridge/contract repos with a "deploy
  lag" radar. See also [[fix-disclosure-race]].
- **Bridges trust precompile *output*, not precompile *input*.**
  Verifying that signatures were checked is not the same as checking
  signatures. The same gap appears in EVM contracts that read
  `tx.origin`-style hints instead of re-running ECDSA themselves.
- **Cross-chain accounting asymmetry.** A mint on chain A backed by a
  lock on chain B is only as honest as the proof transport. Any
  signature/Merkle-proof verifier on the mint side is a high-value
  audit target -- compare to [[nomad-bridge]].
- **Solana program account validation is its own taxonomy.** Build a
  per-target check list: (a) is every passed account checked for owner,
  (b) is every well-known account address-asserted, (c) is every PDA
  re-derived. Sec3's Soteria-class tools encode many of these.

## Primary sources

- [Wormhole incident report and timeline (Wormhole / Jump Crypto)](https://wormholecrypto.medium.com/wormhole-incident-report-02-02-22-ad9b8f21eec6)
  -- official post-mortem with the patch diff.
- [samczsun: Wormhole exploit thread](https://twitter.com/samczsun/status/1489044939732406275)
  -- technical breakdown of the account-confusion primitive with the
  `verify_signature.rs` code path. See also Kudelski Security's
  research write-up: <https://kudelskisecurity.com/research/quick-analysis-of-the-wormhole-attack>.

## Related

- [[nomad-bridge]]
- [[deprecated-api-cleanup-lag]]
- [[fix-disclosure-race]]
