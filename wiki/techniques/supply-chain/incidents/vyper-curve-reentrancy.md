---
title: Vyper compiler reentrancy-lock bug → Curve Finance hack (Jul 2023)
slug: vyper-curve-reentrancy
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, language/vyper, ecosystem/defi, technique/compiler-bug, technique/reentrancy]
inbound: []
---

# Vyper compiler reentrancy-lock bug → Curve Finance hack (Jul 2023)

## What happened

On **2023-07-30** several Curve Finance stable-swap pools whose pool
contracts had been compiled with **Vyper 0.2.15, 0.2.16, or 0.3.0** were
drained via cross-function reentrancy. Pools hit included **pETH/ETH,
msETH/ETH, alETH/ETH** (Alchemix), and the **CRV/ETH** pool itself. Total
losses were initially reported at ~$73M; on-chain accounting after
whitehat returns settled around **$52M net stolen** across Alchemix
(~$13.6M), JPEG'd (~$11.4M), MetronomeDAO (~$1.6M), and others.

The root cause was not in any pool's Vyper source -- every affected
contract correctly decorated state-mutating functions with
`@nonreentrant('lock')`. The bug was in the **compiler itself**: in the
affected versions the per-key reentrancy lock was given a fresh storage
slot for *each function that referenced it*, rather than a single
deduplicated slot. The functions therefore each held an independent lock
and could not block one another, so a callback during ETH transfer in
`remove_liquidity` could re-enter `add_liquidity` (or vice versa) with
the lock byte still zero.

## Attack chain

1. **Compiler bug seeded during refactor.** Vyper removed the
   `self._nonreentrant_keys` deduplication table that previously ensured
   every `@nonreentrant('<key>')` decoration mapped to the same storage
   slot. After the refactor each decorated function got its own slot.
2. **Decorator looks identical at the Vyper source level.** All affected
   pools used the canonical `@nonreentrant('lock')` pattern -- so source
   review, Slither, and static auditors all pass. The bug is only
   visible in the emitted EVM bytecode (different `SSTORE` slot per
   function).
3. **Exploit primitive: cross-function reentrancy via ETH callback.**
   Attacker calls `remove_liquidity` which transfers raw ETH (Curve
   stable-swap pools holding ETH use `raw_call` with `call(value)` to
   the receiver). Receiver's fallback re-enters `add_liquidity` (or
   `exchange`); the pool's `get_virtual_price()` and internal balance
   state are mid-update, so the reentry observes an inconsistent ratio
   and over-credits the attacker.
4. **Profit extraction.** Attacker withdraws the inflated LP balance
   through a second `remove_liquidity` from the now-poisoned pool, or
   re-routes via the metapool to convert to a freely-tradeable asset.
5. **Whitehat MEV race.** Several pools were re-exploited by MEV
   searchers running the same primitive within minutes of the original
   tx becoming public, in some cases returning funds to victim DAOs.

## Lessons for bug hunters

- **Compiler version is a sink, not just a setting.** When auditing any
  Vyper contract, capture the `vyper --version` used at compile time
  (often in `pragma` or build artifacts). Versions 0.2.15, 0.2.16, 0.3.0
  are the known-bad set; treat any pool whose deploy tx bytecode matches
  those compiler signatures as latent reentrancy. The same applies to
  Solidity -- compiler advisories in the `solc` repo's `docs/bugs.json`
  are a checklist most auditors skip. See [[xz-utils-cve-2024-3094]] for
  another "trust the toolchain" failure.
- **`@nonreentrant` and `nonReentrant` are not the same control.** In
  Solidity the OpenZeppelin guard maps to a single contract-wide
  storage slot; in Vyper pre-0.3.1 each decorated function may have had
  its own. Cross-function reentrancy is the natural exploit primitive
  whenever locks are not deduplicated. Probe by simulating
  `remove_liquidity` -> attacker fallback -> `exchange` in Foundry/Tenderly
  before assuming the lock is global.
- **Raw ETH pools are the dangerous subset.** ERC-20-only pools are
  hard to reenter because the token contract's `transfer` does not call
  user code. ETH-bearing pools (`raw_call` / `selfdestruct`-fed) are the
  primary cross-function-reentrancy victims. Flag any Curve fork or
  derivative pool holding native ETH.
- **Fork/derivative blast radius.** Curve's Vyper code was directly
  forked by JPEG'd, Conic, and many smaller protocols. When a
  language-level toolchain bug lands, sweep every fork on GitHub via
  bytecode-signature search, not just the upstream protocol. Pattern
  rhymes with [[codecov-bash-uploader]] where one upstream artifact
  poisoned downstreams.
- **Audit reports do not cover the compiler.** Every affected pool had
  passed multiple audits. Auditors disclaim toolchain bugs by default.
  Adding a compiler-version row to your audit checklist is free alpha.

## Primary sources

- [Vyper team: Nonreentrancy Lock Vulnerability Technical Post-Mortem](https://hackmd.io/@vyperlang/HJUgNMhs2)
  -- root-cause walk-through from the Vyper maintainers with the offending PR.
- [LlamaRisk: Curve Pool Reentrancy Exploit Postmortem July 30th, 2023](https://hackmd.io/@LlamaRisk/BJzSKHNjn)
  -- end-to-end attack reconstruction with tx-level traces for each pool.

## Related

- [[xz-utils-cve-2024-3094]]
- [[tj-actions-changed-files]]
