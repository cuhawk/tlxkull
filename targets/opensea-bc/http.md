# OpenSea Managed Bug Bounty Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/opensea
> Type: BBP
> Bounty: See program page
> Status: In progress (started Sep 18, 2023)

## Scope

- in:  http://wallet.opensea.io/ http://wallet.opensea.io/   # type: url
- in:  https://github.com/ProjectOpenSea/seaport#deployments   # type: url
- in:  https://etherscan.io/address/0x0000a26b00c1F0DF003000390027140000fAa719   # type: url
- in:  https://etherscan.io/address/0x00005EA00Ac477B1030CE78506496e8C2dE24bf5   # type: url

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

## Additional targets (not captured by parser)

### Mobile Apps (P1=$15,000)
- in: io.opensea Android App (Play Store)
- in: io.opensea iOS App (App Store)

### OpenSea MCP (P1=$15,000)
- in: https://mcp.opensea.io

### Seaport Smart Contract Deployment (P1=$3,000,000 — highest reward)
- in: https://github.com/ProjectOpenSea/seaport#deployments
- Seaport 1.6: 0x0000000000000068F116a894984e2DB1123eB395
- ConduitController: 0x00000000F9490004C11Cef243f5400493c00Ad63
- OOS: Seaport 1.1–1.5, SeaportValidator, SeaportNavigator (old versions)
- Only on-chain execution against in-scope contracts

### Fee Collector Smart Contract (P1=$50,000)
- in: 0x0000a26b00c1F0DF003000390027140000fAa719

### Seadrop Smart Contract (P1=$50,000)
- in: 0x00005EA00Ac477B1030CE78506496e8C2dE24bf5

### Broken Links (P4=$50)
- in: OpenSea curated content (blog, Learning Center) with takeover potential; PoC required

## Reward tiers summary
| Asset | P1 | P2 | P3 | P4 |
|-------|-----|-----|-----|-----|
| opensea.io + Wallet | $50,000 | $10,000 | $3,000 | $250 |
| Mobile + MCP | $15,000 | $3,000 | $500 | $125 |
| Fee Collector / Seadrop SC | $50,000 | $10,000 | $500 | $250 |
| Seaport 1.6 | $3,000,000 | $100,000 | $25,000 | $500 |

## Auth
- Register with @bugcrowdninja.com email; self-provision on all publicly-facing targets
- All smart contract testing must use forked local copy of mainnet (no production interaction)
- Nondisclosure — no public disclosure allowed

## OOS
- Gas optimizations in smart contracts
- MITM / physical access (client-side JS manipulation OOS unless remote exploit demonstrated)
- Old vulnerable libraries without PoC
- Rate limiting on non-auth endpoints
- DoS/DDoS
- Software version/stack disclosure
- Clickjacking on non-sensitive pages
- CSRF on unauthenticated/non-sensitive forms
- Missing HttpOnly/Secure cookie flags
- Old browser vulnerabilities (< 2 stable versions behind)
- 0-days with official patch < 1 month (may still be reviewed at OpenSea's discretion)
- Issues publicly disclosed before OpenSea received the report
- Open redirect (only in scope as part of a chain)
- Clickjacking within NFT content displayed on OpenSea
- JS execution on openseauserdata.com or raw.seadn.io (unless harm to in-scope assets shown)
- Wallet vulnerabilities (report to respective wallet companies)
- Copycat/copymint bypass (reportable but no reward)
- User wallet content (NFTs, transactions, balances) = not confidential
- Wallet requirement: only MetaMask, Coinbase Wallet, Ledger, Phantom, Bitkeep, Kaikas, Glow, Solflare, Venly, OperaTouch, Trust, WalletConnect
- Social engineering, phishing
- Smart contract issues on testnets.opensea.io
- Employee personal blogs
- All user-generated content
