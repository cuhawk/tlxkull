# KuCoin Bug Bounty

## Target
- program: kucoin (Bugcrowd)
- category: bbp
- started: Jun 19, 2024
- partial_safe_harbor: true

## Scope
- in: kucoin.com (main website)
- in: KuCoin iOS app (App Store)
- in: KuCoin Android app (Google Play)
- note: Other targets exist but target tables didn't render — check scope page

## Bounties
### Business-related assets (web)
- Special: $15,000
- P1: $5,000-15,000
- P2: $2,000-5,000
- P3: $200-400
- P4: $50-100

### None-Business-related assets
- Special: $5,000
- P1: $2,000-5,000
- P2: $1,000-2,000
- P3: $200-400
- P4: $50-100

### Mobile App Targets
- Special: $10,000
- P1: $5,000-10,000
- P2: $2,000-5,000
- P3: $200-400
- P4: $50-100

## Auth
- Self-register with @bugcrowdninja.com email
- KYC needed to access all features (full KYC required for certain testing)

## Focus Areas
### Critical (Web)
- RCE on KuCoin servers
- SQL Injection (Core DB) — large-scale data access
- Admin backend takeover (critical admin privileges)
- Mass account takeover affecting >50% of users
- System command execution on critical servers

### High (Web)
- Stored XSS worms (self-replicating)
- CSRF leading to account compromise or unauthorized asset actions
- Account access at scale (multiple user accounts)
- SQL Injection (limited data extraction)
- Source code leakage
- SSRF to internal services (severity depends on impact achieved)

### Medium (Web)
- Stored XSS requiring interaction
- CSRF on core business actions
- Auth bypass (limited, no financial impact)
- Subdomain takeover
- Verification code flaws (login/password reset)
- Sensitive data exposure
- Cleartext credentials in source/config
- Bypass of KYC/authenticity verification

### Low (Web)
- Reflected XSS
- DOM XSS
- Open redirects
- General info leaks
- Common CSRF (non-sensitive)

### Mobile Critical
- Contactless remote code execution
- Contactless remote sandbox file access
- Local TEE key/auth info theft

### Web3/Blockchain
- Critical: Affects >50% users, >15min downtime, or >$100K potential loss
- High: Affects >30% users, >10min downtime, or >$50K potential loss

## OOS (Web)
- Reports from automated tools/scans
- False positive SQL injection (must have working PoC)
- Self-XSS, spam, mail spoofing, mail bombs
- Known vulnerable libraries without PoC
- Clickjacking on non-sensitive pages
- CSRF on unauthenticated or non-sensitive forms
- Physical access or MITM required attacks
- CSV injection without exploitation PoC
- SSL/TLS config issues
- DoS activities
- Content spoofing without modifying HTML/CSS
- Rate limiting on non-auth endpoints
- Missing CSP, HttpOnly/Secure flags
- Missing SPF/DKIM/DMARC
- Outdated browser bugs (older than 2 stable versions behind)
- Software version disclosure / banner identification
- Tabnabbing
- Unlikely user interaction required
- Known vulnerabilities
- WordPress vulnerabilities
- Address bar spoofing in dApp browser
- Proof of reserves as "sensitive document" leak
- Broken link / social media account takeovers

## OOS (Mobile)
- Physical device access required
- Rooted/jailbroken device required
- Extensive user interaction required
- Non-sensitive data exposure
- Static analysis without business logic PoC
- Lack of obfuscation/binary protections
- Certificate pinning bypass on rooted devices
- OAuth/app secrets hardcoded in IPA/APK
- Frida/AppMon exploits (jailbroken environment)

## N-Day Policy
- N-day bugs in scope 14 days after public release

## Notes
- Coordinated disclosure; requires explicit permission
