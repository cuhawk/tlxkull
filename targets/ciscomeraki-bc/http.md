# Cisco Meraki

> Platform: Bugcrowd — https://bugcrowd.com/engagements/ciscomeraki
> Type: VDP
> Bounty: P1 $6000–$10000 | P2 $2500–$6000 | P3 $500–$2500 | P4 $100–$500
> Status: In progress

## Scope

- in:  https://*.ikarem.io   # type: url
- in:  https://*.meraki.com   # type: url
- in:  https://*.network-auth.com   # type: url
- out: merakipartners.com   # type: domain
- out: developers.meraki.com   # type: domain
- out: smhelp.meraki.com   # type: domain
- out: community.meraki.com   # type: domain
- out: community-staging.meraki.com   # type: domain
- out: *.cisco.com   # type: wildcard
- out: documentation.meraki.com   # type: domain

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Hardware Targets (same P1-P4 bounty range)
- in: Cisco Campus Gateways (hardware)
- in: Cisco Catalyst 9200L Series Switches (Cloud-Managed)
- in: Cisco Meraki MX & Z Series Security Appliances (Including vMX)
- in: Cisco Meraki MS Switches
- in: Cisco Meraki MR Access Points
- in: Cisco Meraki MV Smart Cameras
- in: Cisco Meraki MG Fixed Wireless Access Devices
- note: Hardware testing via in-person HardPwn events or private bounties — not shipping devices to researchers

## Domain Notes
- *.ikarem.io: Meraki internal services → higher reward range
- *.meraki.com: Cisco Meraki Dashboard and integrated services
- *.network-auth.com: User-created content for Dashboard splash pages
- customer API keys used to interact with Meraki services: OOS
- DNS issues temporarily OOS: DNS config problems, dangling DNS records/zones
- Adobe Marketo tokens: OOS

## Auth
- Register at https://meraki.cisco.com/form/demo with @bugcrowdninja.com email
- Creates demo org with dashboard access
- Create 2nd user via Organization > Administrators
- Recommend 2 demo orgs for cross-account testing; use +1 suffix on email

## Focus Areas
- IDOR (unauthorized object/data/settings access)
- Privilege escalation (vertical and horizontal)
- Remote code execution as root / remote root login
- Remote configuration injection
- Direct exposure of: device secrets, cryptographic keys, MV camera footage, customer credentials/PII
- Full compromise of secure boot
- "Packet of death" or mass DoS

## OOS Attacks
- Customer credential exposure where Meraki is NOT responsible (customer misconfiguration, third-party breach)
- Subdomain takeover
- Email bombing/flooding
- Security feature deficiencies in on-prem products (e.g. 802.1x multi-auth vs multi-host on MX/MS)
- Outdated browser/plugin bugs
- Self-XSS (except novel attacks)
- Text injection, email spoofing, social engineering
- Path disclosure (unless real security impact)
- Missing Secure/HTTPOnly on cookies (except: dash_auth_token, dash_auth, devel_dash_auth, two_factor_auth)
- Login/forgot password brute force / lockout not enforced (unless configured in org)
- URL redirection
- Admin attacks against own org users (e.g. malicious splash pages)
- Any attack against Cisco/Meraki corporate infrastructure
- Discovery of services with known vulns without demonstrated exploit
- Enumeration (username, email, order#, serial#, license key) — requires advance permission from Cisco Meraki Security Team
- All brute force DoS, SSL/TLS attacks
- Attacks rendering device permanently inoperable
- Multifactor bypass for already-authenticated users
- MitM-only exploitable attacks
- Reflected downloads
- Hardware bugs requiring debugger to recreate
- Vulns in open source packages <1 month old
- Vuln not present in most recent beta firmware
- Feature deficiencies (missing SSL on Local Status Page, AMP/Content Filter bypass, URL blacklist bypass)
- Missing/altered public-key pins
- DLL injection for mobile apps
- Systems Manager enrollment auth disabled
- Same root cause in multiple endpoints = single submission

## Notes
- Partial safe harbor
- Coordinated disclosure; explicit permission required
