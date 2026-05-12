# Electroneum Smart Chain (ETN-SC)

> Platform: Bugcrowd — https://bugcrowd.com/engagements/smartchain-mbb-og
> Type: BBP
> Bounty: See program page
> Status: In progress (started Jul 08, 2025)

## Scope

- # TODO: scope not loaded — re-scrape with scroll

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Targets

### In Scope (P1=$5,000–12,000)
- in: https://github.com/electroneum/electroneum-sc/ (Smart Chain Blockchain — code review)
- in: https://blockexplorer.electroneum.com (Block Explorer)
- in: https://testnet-blockexplorer.electroneum.com (Staging Block Explorer)

## Rewards
| Priority | Range |
|----------|-------|
| P1 | $5,000–12,000 |
| P2 | $4,000–6,000 |
| P3 | $600–850 |
| P4 | $200–250 |

## Eligible submission types (REQUIRED — report must show one of these outcomes)
A) Minting or burning of tokens via unknown mechanism
B) Gaming consensus to gain monetary advantage or shut down network / disrupt block regularity
C) Stealing tokens or revealing wallet private keys
D) Changing historical blockchain data and having network accept it
E) Tricking exchanges/3rd parties about transaction/block reality via wallet or block explorer

Extraordinary findings outside these categories may still be rewarded at discretion.

## Rules
- Do NOT enact discovered exploits as PoC (no minting new tokens, moving balances, etc.)
- Do NOT target other users' data, DoS, or compromise availability for other users
- Stop testing immediately if you find a stability/integrity-compromising vulnerability and report it
- Read the codebase relevant to your submission; verify PoC yourself before submission
- No AI-generated PoCs without personal review
- N-day policy: N-days in scope 14 days after public disclosure

## OOS
- Theoretical vulns without working PoC
- Attacks requiring unrealistic validator collusion
- Dev/debug build crashes not affecting production
- Compiler crashes (Solidity/Vyper) from malformed input
- 3rd party unaudited/not-Electroneum smart contracts
- Attacks requiring full network control or unrealistic conditions (eclipse without feasible setup)
- Consensus splits from non-standard forks or unsupported clients
- Known issues documented in GitHub or public roadmap
- Bug reports based on already-committed Ethereum/EVM fixes
- 3rd party services/dependencies
- DoS not impacting consensus, validator liveness, or user funds
- Social engineering, phishing, physical attacks
- Publicly well-known issues discussed upstream in Ethereum community (even if unfixed)

## Related programs
- Electroneum Legacy Blockchain: EOL (separate program: legacy-blockchain-mbb-og)
- Electroneum Wallet: Gateway to the ETN Cryptocurrency (separate program)
- AnyTask: Freelancer Platform (separate program)
