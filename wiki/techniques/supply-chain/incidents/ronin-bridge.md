---
title: Ronin Network bridge -- $625M validator-key heist (Mar 2022)
slug: ronin-bridge
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/web3, technique/social-engineering, technique/spearphish-pdf, technique/unrevoked-delegation, actor/lazarus, target/cross-chain-bridge]
inbound: []
---

# Ronin Network bridge -- $625M validator-key heist (Mar 2022)

## What happened

On **23 March 2022** an attacker drained **173,600 ETH + 25.5M USDC**
(~$625M at the time) from the **Ronin** sidechain bridge that
underpins Axie Infinity. Sky Mavis didn't notice until **29 March**,
when a user reported a stuck withdrawal -- six days of silent loss.
The bridge used a 5-of-9 validator multisig; the attacker held private
keys for **five** validators (the 4 Sky Mavis-operated nodes plus the
single Axie DAO-operated node), enough to forge a withdrawal signature
quorum without any on-chain exploit.

The FBI and Treasury attributed the operation to **DPRK Lazarus
Group**. Initial entry was a fake-job-offer LinkedIn campaign: a Sky
Mavis senior engineer was approached by a non-existent recruiter,
went through several rounds of interviews, and was sent an "offer
letter" PDF. Opening the PDF on his work laptop yielded RCE; lateral
movement reached the four Sky Mavis validator nodes. The fifth
signature came from an old delegation: in **November 2021** the Axie
DAO had allow-listed Sky Mavis to co-sign transactions during a load
spike. The delegation was supposed to lapse in December 2021. Nobody
revoked it. Months later the attacker used Sky Mavis's existing
gas-free RPC pipe to obtain a valid Axie DAO signature, completing
the quorum.

## Attack chain

1. **Targeted spear-phish via LinkedIn.** Multi-week persona build:
   fake recruiter, fake company, fake interview rounds. Pattern matches
   Lazarus's broader **Operation Dream Job** campaign against crypto
   and defense personnel.
2. **Weaponised PDF / offer letter.** Opened on the engineer's macOS
   workstation; planted implant. (Specific CVE not publicly named in
   the postmortem, consistent with Lazarus's pattern of using a
   custom loader plus a current-quarter office/PDF n-day.)
3. **Lateral to validator infrastructure.** Sky Mavis validators ran
   in a shared internal environment; engineer's creds /
   bastion-host access enabled hops to all four Sky Mavis validator
   signing nodes. **Four** signatures harvested.
4. **Abuse the unrevoked Axie DAO delegation.** In Nov 2021 Axie DAO
   had whitelisted Sky Mavis to sign on its behalf via a **gas-free
   RPC**; the access was never revoked when the December load-spike
   season ended. The attacker re-used Sky Mavis's authority to request
   a signed transaction from the Axie DAO validator -- the **fifth**
   signature.
5. **Forge bridge withdrawals.** Two transactions:
   `0xc28f...` (173,600 ETH) and `0xed2c...` (25.5M USDC) drained
   directly to attacker-controlled addresses. No smart-contract exploit
   -- the signatures were cryptographically valid.

## Lessons for bug hunters

- **Multisig is only as strong as the operational separation between
  signers.** Four of five signers running on the same internal
  network with shared bastion access is a single failure domain. On
  any Web3 bounty: enumerate validator / signer node operators, map
  shared infrastructure, look for `*.skymavis.com`-style common-suffix
  hosting hints. Cross-link [[bybit-safewallet-ui]] -- the dApp-frontend
  analog of the same lesson.
- **Stale delegations are the canonical access-control bug.** Any
  "temporary allow-list" / "emergency role" / "co-signer override"
  added during a load spike or migration is rarely revoked. Audit
  smart-contract `onlyRole` / `whitelisted` mappings, AWS IAM
  trust policies, OAuth scope grants, and "service account"
  delegations for entries with no expiry and no recent use.
- **Gas-free RPC = privileged signing oracle.** Any RPC endpoint that
  signs transactions on behalf of users (meta-transactions, gasless
  approvals, paymasters in ERC-4337) is a high-value target. The
  abuse is "convince the RPC to sign something it shouldn't" -- find
  the access-control predicate.
- **LinkedIn / job-offer PDFs remain Lazarus's preferred entry on
  crypto and defense targets.** On engagements that include the
  client's employees as in-scope (red team, full-program H1 scope),
  passive recon on engineers' LinkedIn activity often reveals
  ongoing Lazarus contact campaigns. Report them as observed TTPs.
- **Six-day silent dwell.** The drain was on-chain but Sky Mavis ran
  no on-chain monitoring on their own bridge. For any Web3 bounty
  with a bridge / treasury / multisig surface, lack of independent
  monitoring is itself a reportable risk -- some programs pay for
  defense-gap findings.

## Primary sources

- [Sky Mavis / Ronin Chain: "Back to Building: Ronin Security Breach Postmortem"](https://roninchain.com/blog/posts/back-to-building-ronin-security-breach-6513cc78a5edc1001b03c364)
- [Elliptic: "North Korea's Lazarus Group identified as exploiters behind $540 million Ronin bridge heist"](https://www.elliptic.co/blog/540-million-stolen-from-the-ronin-defi-bridge)

## Related

- [[bybit-safewallet-ui]]
- [[xz-utils-cve-2024-3094]]
- [[operation-triangulation]]
