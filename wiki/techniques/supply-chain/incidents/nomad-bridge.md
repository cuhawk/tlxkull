---
title: Nomad bridge frenzied loot (Aug 2022)
slug: nomad-bridge
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, chain/ethereum, surface/cross-chain-bridge, technique/zero-default, technique/copy-paste-exploit, technique/storage-init]
inbound: []
---

# Nomad bridge frenzied loot (Aug 2022)

## What happened

On 2022-08-01 the Nomad token bridge was drained of ~$190M in roughly
two hours across ~960 transactions from ~300 distinct addresses. It
was the first "crowd-looted" bridge hack in history -- once the first
attacker's transaction was on-chain, anyone with MetaMask could copy
the calldata, swap the recipient address, and pull funds out. Total
on-bridge value went from $190,740,000 to under $2,000 in the same
afternoon.

The root cause was a single-line initialization mistake in a routine
upgrade to `Replica.sol` merged on 2022-04-21 and on-chain in late
June. During initialization, `0x00` was written as a trusted
"committed root" into the `confirmAt` mapping. Because Solidity
mappings return the zero value for any missing key, the proof check
`acceptableRoot(messages[messageHash])` returned `true` for *any*
message whose hash was not in the `messages` mapping -- i.e. any
unproven message. The optimistic verifier accepted all of them.

## Attack chain

1. **Bad init: `_committedRoot = 0x00`.** The `initialize` call set
   `confirmAt[0x00] = 1`, marking the zero hash as a confirmed
   acceptable root.
2. **Mapping default == accepted.** `process(bytes _message)` computed
   `bytes32 _messageHash = keccak256(_message)`, looked it up in
   `messages[_messageHash]` (storage slot returns `0x00` if unset),
   then called `acceptableRoot(0x00)` which checked
   `confirmAt[0x00] > 0` -- true. Any never-proven message therefore
   passed `process()`.
3. **First attacker forged a withdraw message.** Crafted a `Home`-side
   message claiming a withdrawal of WBTC from the bridge to a chosen
   recipient. `process()` decoded the message body and called
   `_handle` -> `IBridgeRouter.handle` -> token unlock. No proof. No
   signature. No nonce check that prevented replay.
4. **Calldata copy-paste cascade.** Once the first transaction landed,
   the calldata was public on Etherscan. Any user could submit a new
   `process()` call with the exact same encoded message but the
   recipient address replaced with their own. Bots, kids, MEV
   searchers, white-hats, and a few protocol teams all piled in.
5. **No circuit breaker.** Nomad had no rate-limit, no withdrawal cap
   per epoch, no per-asset ceiling. The bridge emptied as fast as
   Ethereum could include blocks.

## Lessons for bug hunters

- **Storage-zero defaults are a Solidity foot-gun.** Any mapping read
  used as an authorization gate must explicitly reject the zero key.
  Grep targets for `mapping(... => bool)` / `mapping(... => uint)`
  used in `require(map[x])` -- a missing key reads `false`/`0`; a key
  set to `0` *for legitimate reasons* reads the same. See
  [[ethereum-storage-zero-default]].
- **Initializer / upgrade migrations are gold.** Compare every proxy
  upgrade's init params against the storage layout. A single argument
  flipped to `0x00` (zero hash, zero address, zero root) during an
  upgrade can flip an authorization gate. Check upgrade transaction
  history on Etherscan.
- **"Calldata copy" replay is its own threat model.** Even contracts
  that survive a sophisticated attacker can die when the calldata is
  one-edit reusable. Audit for any function whose calldata uniquely
  identifies the caller; if recipient/beneficiary is encoded in a
  field that's trivially swappable, the attack scales horizontally.
- **No circuit breaker == no second chance.** Bridges and lending
  markets that mint/release native value should ship per-epoch
  withdrawal caps. Programs without them are higher-tier targets.
- **Audits miss state-transition bugs.** Nomad had two audits. Neither
  caught the upgrade init. Pure-functional auditing of Solidity passes
  over migration scripts and proxy storage layout. Cross-link
  [[audit-fatigue-and-storage-layout]].

## Primary sources

- [Nomad incident analysis (Coinbase Cloud blog)](https://www.coinbase.com/blog/nomad-bridge-incident-analysis)
  -- step-by-step decode of the bad init and process() call.
- [Immunefi: Hack Analysis: Nomad Bridge, August 2022](https://medium.com/immunefi/hack-analysis-nomad-bridge-august-2022-5aa63d53814a)
  -- annotated Solidity walkthrough with the exact storage slot trace.

## Related

- [[wormhole-solana]]
- [[ethereum-storage-zero-default]]
- [[audit-fatigue-and-storage-layout]]
