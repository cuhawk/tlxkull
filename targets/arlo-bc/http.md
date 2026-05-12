# Arlo Cash Rewards

> Platform: Bugcrowd — https://bugcrowd.com/engagements/arlo
> Type: BBP (partial safe harbor)
> Bounty: See tiers below; special $15,000 high-impact rewards
> Status: In progress (since May 2018)

## Scope

### Tier 1 — Arlo Devices (device ownership unlocks more attack surface)
- in: *.arlo.com (Arlo cloud infrastructure supporting devices)
- in: https://my.arlo.com (main user interface)
- NOTE: Most attack surface requires owning an Arlo device. Devices available under $40.
- Bounty: P1=$5000-$7000, P2=$2000-$3000, P3=$500-$1000, P4=$100-$500
- Special max: $15000 (see High Impact Rewards below)

### Tier 2 — All Other Arlo Targets
- in: *.arlo.com (subdomains impacting customer-facing services)
- Bounty: P1=$2000-$3000, P2=$500-$1000, P3=$150-$400, P4=$100
- NOTE: Subdomain takeovers only eligible if high impact (low impact = $150; high impact may reach P2-P1)
- arlostreaming and cvrstreaming subdomain reports NO LONGER accepted

### High Impact Rewards
- $15,000: Unauthorized access to ALL Arlo cloud storage video files OR all live video feeds
- $10,000: Remote unauthorized access to single account's live feed or cloud video; remote access to full Arlo customer database

### Out of Scope
- out: community.arlo.com (OOS since Oct 2025)
- out: survey.arlo.com (OOS since Oct 2025)
- out: research.arlo.com (OOS since Oct 2025)
- out: investor.arlo.com (OOS since Oct 2025)
- out: Any session management vulns on www.arlo.com
- out: Leaked credentials for community.arlo.com, my.arlo.com, www.arlo.com
- out: NETGEAR products (separate BBP)
- out: End-of-Life products
- out: DoS/DDoS, automated scanning, physical attacks, social engineering
- out: IP-only reports without video proving Arlo certificate ownership
- out: arlostreaming/cvrstreaming subdomain reports

## Auth

- type: web_app
- creds: Create account using your own email (no @bugcrowdninja.com requirement mentioned)
- creds: Can only test against your own accounts/devices

## Notes

- status: ACTIVE (574 vulns rewarded, avg payout $1502)
- Nondisclosure: NO public disclosure allowed
- Must own device for full access to attack surface
- Reports on specific IPs (no Arlo domain) must include video showing browser accessing IP, TLS cert confirming Arlo ownership
- Include business impact statement in every submission to help severity scoring
- Single award per vulnerability even if affects multiple products (common platform)
- Partial safe harbor
- California law applies

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
