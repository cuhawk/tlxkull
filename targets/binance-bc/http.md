# Binance Bug Bounty

## Target
- program: binance (Bugcrowd)
- category: bbp
- started: Apr 12, 2018
- nondisclosure: true (no public disclosure)
- partial_safe_harbor: true

## Bounties
- Special: up to $100,000 (extraordinarily severe issues)
- P1: $5,000-10,000
- P2: $1,500-5,000
- P3: $600-1,500
- P4: $200-600
- Rewards paid in BNB (amounts fluctuate with crypto market)
- Bonus rewards possible for exceptional reports at Binance's discretion

### Secondary Targets (P1/P2 bounty; P3/P4 points only)
- academy.binance.com
- info.binance.com
- coinmarketcap.com, api.coinmarketcap.com, pro-api.coinmarketcap.com, pro.coinmarketcap.com, portal-api.coinmarketcap.com, 3rdparty-apis.coinmarketcap.com
- CoinMarketCap Android app
- CoinMarketCap iOS app

## Scope
### Primary Targets (P4+ bounty)
- in: *.binance.com (with exceptions, see secondary targets)
- in: api.binance.com
- in: binance.us
- in: Binance Mobile App for Android
- in: Binance Mobile App for iOS
- in: Binance Desktop Application
- in: Binance macOS Application
- in: Binance Connect
- in: binance.tr

### TrustWallet (separate scope rules)
- in: TrustWallet Android app
- in: TrustWallet iOS app
- in: TrustWallet walletcore
- in: TrustWallet Chrome Extension
- out: *.trustwallet.com, *.trustwalletapp.com

## Auth
- Self-register with @bugcrowdninja.com email
- Create a separate private Binance account for testing
- Or use a Binance Smart Chain wallet for receiving BNB rewards

## TrustWallet Focus Areas
- Loss of user funds/assets remotely
- Exposure of private keys or mnemonic seed phrase
- Chain-related implementation vulnerabilities
- Denial of service of wallet app
- RCE
- Insecure cryptographic implementation (wallet generation, tx signing)
- Lock screen bypass

## OOS Findings
- Theoretical vulns without PoC (closed as OOS)
- Email verification deficiencies, expired password reset links, password complexity
- Missing SPF/DKIM/DMARC
- Clickjacking with minimal security impact
- Email/mobile enumeration
- Info disclosure with minimal impact (stack traces, path disclosure)
- Known/duplicate/public issues
- Tab-nabbing
- Self-XSS
- Vuln in out-of-date browsers/platforms
- Vulnerabilities related to auto-fill web forms
- Known vulnerable libraries without PoC
- Lack of security flags in cookies
- Unsafe SSL/TLS cipher suites or protocol versions
- Content spoofing
- Cache-control issues
- Internal IP/domain exposure
- Missing security headers without direct exploitation
- CSRF with negligible impact
- Physical device access required
- Rooted/jailbroken device required
- Issues with no security impact
- Assets not belonging to Binance
- DoS/DDoS activities
- Installation path permissions
- Reports from automated tools or scans
- Social engineering
- Links to invalid/expired pages (only valid if actual official Binance social media takeover demonstrated)

## Notes
- Bug affecting multiple exchanges sharing same root cause = single report
- Bugs submitted must have working PoC; no monetary reward without PoC
- Reward eligibility and amount at Binance's discretion
