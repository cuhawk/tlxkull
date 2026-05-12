# Tesla Bug Bounty — Bugcrowd

**URL:** https://bugcrowd.com/engagements/tesla
**Category:** BBP
**Safe harbor:** Partial
**Disclosure:** Coordinated with explicit permission required
**Started:** 2015-08-04
**Special:** Vehicle/product bugs → vulnerabilityreporting@tesla.com (GPG), NOT Bugcrowd directly

## Auth / account setup
- Register with @bugcrowdninja.com email
- Do not spam forms
- Eligibility: 14+, no sanctions-country residents, no current/recent Tesla employees or contractors
- Hardware Research Registration: Must register owned hardware at vulnerabilityreporting@tesla.com BEFORE testing

## Targets

### Non-vehicle web targets
- in: *.tesla.com
- in: *.tesla.cn
- in: Any host verified to be owned by Tesla Motors Inc.
- in: Tesla iOS/Android mobile apps

### Vehicle Hardware
- in: Tesla vehicle hardware that you own (must register before testing)

## Rewards

### Non-vehicle (web/apps)
| Priority | Range |
|----------|-------|
| P1 | $3,000-10,000 |
| P2 | $500-4,000 |
| P3 | $200-700 |
| P4 | $100-200 |

### Vehicle Targets
| Priority | Range | Examples |
|----------|-------|---------|
| P1 Critical | $50,000-100,000 | Remote zero-click unconfined root on infotainment; RCE on CAN ECU; infotainment pivot to CAN bus |
| P2 High | $20,000-50,000 | Remote one-click root on infotainment; unconfined root persistence; remote zero-click peripherals |
| P3 Moderate | $10,000-20,000 | Unprivileged RCE on infotainment; unconfined root via ethernet/USB |
| P4 Low | $500-10,000 | Unprivileged persistence; local drive auth bypass; PIN-to-Drive bypass |

## Root access program
Tesla offers researcher SSH cert after novel root access finding on infotainment.

## Out of scope

### Vehicle / product
- Relay attacks
- Hardware glitching / side-channel attacks
- Confusing Autopilot by modifying environment
- Tegra persistence / secure boot
- Tegra physical access attacks
- Chromium/WebKit bugs without sandbox escape
- Superchargers

### Web / app
- WAF bypass
- Open redirects
- Internal IP disclosure
- SPF/DKIM/DMARC issues
- Self-XSS
- Clickjacking
- CSRF not impacting account security
- Missing security headers
- SSL/TLS configuration
- DoS
- Tesla account MFA issues (currently OOS)

## Notes
- Vehicle and energy product reports: email vulnerabilityreporting@tesla.com with GPG encryption for sensitive details
- Bugcrowd is used as the reward platform for all issues, but vehicle/product reports are submitted via email
