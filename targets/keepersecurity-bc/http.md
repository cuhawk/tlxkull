# Keeper Security Public Bounty Program

- platform: bugcrowd
- program_url: https://bugcrowd.com/engagements/keepersecurity
- category: Computer Software
- safe_harbor: partial
- nondisclosure: true
- scope_rating: 4/4
- started: 2018-04-10

## Rewards

| Priority | Range |
|---|---|
| P1 | $11000-$20000 (bonus up to $25000) |
| P2 | $3500-$7500 |
| P3 | $1000-$2500 |
| P4 | $300-$600 |

## Targets

### Web Vaults
- in: https://keepersecurity.com/vault/  # type: url  # Web Vault (US)
- in: https://keepersecurity.eu/vault/  # type: url  # Web Vault (EU)
- in: https://keepersecurity.com.au/vault/  # type: url  # Web Vault (AU)
- in: https://keepersecurity.jp/vault/  # type: url  # Web Vault (JP)
- in: https://keepersecurity.ca/vault/  # type: url  # Web Vault (CA)
- in: https://govcloud.keepersecurity.us/vault/  # type: url  # Web Vault (US GovCloud)

### Admin Console
- in: Keeper Admin Console (US, EU, AU, CA, JP, GovCloud)  # type: feature

### Applications
- in: KeeperFill Browser Extension  # type: feature
- in: Keeper Desktop Application  # type: software
- in: Keeper Secrets Manager  # type: feature
- in: Keeper Commander  # type: feature
- in: Keeper Connection Manager  # type: feature
- in: Keeper SSO Connect Cloud  # type: feature
- in: Keeper SSO Connect On-Prem  # type: feature
- in: Keeper AD Bridge  # type: feature
- in: Keeper Endpoint Privilege Manager  # type: feature

### Mobile
- in: Keeper for iOS  # type: ios_app
- in: Keeper for Android  # type: android_app
- in: KeeperChat for iOS  # type: ios_app
- in: KeeperChat for Android  # type: android_app
- in: KeeperChat for Mac  # type: software
- in: KeeperChat for Windows  # type: software

### Website
- in: https://www.keepersecurity.com/  # type: url  # Keeper Website
- in: https://checkout.keepersecurity.com/  # type: url  # Keeper Checkout Pages

## Out of Scope
- out: kepr.co  # type: domain
- out: kepr.io  # type: domain

## Auth / Testing Notes

- Sign up with @bugcrowdninja.com email
- Enterprise trial: 14-day; Personal trial: 30-day at Web Vault
- Debug: enableNetworkLog(true) in Web Vault devtools; api.shouldLog=true in Admin Console
- No automated tools (especially against contact forms)
- No rate limit / spam testing (rated P4 at best)
- Self-XSS OOS — must demonstrate attack against another user
- Throttling/spam testing rated P4
