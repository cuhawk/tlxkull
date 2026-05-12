# Xfinity Home & xFi Bug Bounty — Bugcrowd BBP

**Program URL:** https://bugcrowd.com/engagements/xfinity-home  
**Category:** Telecommunications / Safe harbor  
**Status:** ACTIVE (Expedited triage)  
**Started:** Sep 5, 2019  
**Scope rating:** 4 out of 4  
**Avg payout:** ~$3,820 (last 3 months)

---

## Reward Tiers

| Priority | Range |
|----------|-------|
| P1 | $3,500 – $5,500 (up to $10,000 for high-impact) |
| P2 | $1,500 – $2,500 |
| P3 | $300 – $600 |
| P4 | $0 – $250 |

### High-Impact P1 Bonus (up to $10,000)

**Xfinity Home:**
- Remote unauthorized access (via public internet, not same LAN/WiFi) to: cloud storage videos, live camera feeds
- Bypassing Armed Systems
- Abuse/Theft of Service

**Xfinity xFi:**
- Abuse/Theft of Service
- Unauthorized access to WiFi credentials
- Unauthorized access to Profile's Active Time
- Unauthorized access to Advanced Security settings or alerts

### VRT Amendments
| Finding | Adjusted Priority |
|---------|-------------------|
| High Impact Subdomain Takeover | P2 → P3 |
| Basic Subdomain Takeover | P3 → P4 |
| Swagger-UI XSS | P5 Informational (no bounty) |

---

## Required Header

All HTTP traffic must include:
```
X-Bug-Bounty: <bugcrowdusername>
```
Missing header → reduced reward payout.

---

## In-Scope Targets

All subdomains containing any of these keywords are in scope:

`xh, xhome, xhomeapi, xfi, dh, cl, si, siorc, smartinet, orc, melee, breeze, xrp, edp, odp, xdp, xpc, xpg, dhc, xmidt, webpa, codex, plume, chi, mesh, apg, spn, dx, wifi-motion, imp, whix, nion, speedtest, ipie, sed, pepr, activation, dhactivation, dh-commerce, pom, tr1d1um, icontrol, coverage`

### Key Endpoints

**Xfinity Home:**
- in: xhomeapi-*.codebig2.net  # API Gateway
- in: xhomeapi-*.cloud.comcast.net  # Device info API
- in: *-cvr-aws-*.sys.comcast.net  # CVR data endpoints
- in: *signalservice.comcast.net  # Live video
- in: oauth.xfinity.com  # User Authentication
- in: api.sc.xfinity.com  # User information API

**Xfinity xFi:**
- in: internet.xfinity.com  # xFi website
- in: siorc.xfinity.com  # Mobile app orchestration
- in: speedtest.xfinity.com  # Internet speed testing
- in: orc-xfi.com  # xFi orchestration layer
- in: smartinet.xfinity.com  # xFi orchestration layer

### Hardware / IoT (in scope)
- Xfinity Home: Touchscreen Controller, Window/Door Sensors, Wireless keypad, Wireless motion sensors, Cameras
- Xfinity xFi: xFi Gateways (XB3, XB6, XB7), xFi Pods
- I/O devices: USB, SIM, SD card slots (physically accessible, in scope)

---

## Out-of-Scope

- out: .hfc.comcastbusiness.net (ISP customer infrastructure)
- out: *.hsd1.*.comcast.net (ISP customer infrastructure)
- out: Any Comcast property not in scope above
- out: COPS Monitoring Solutions
- out: 3rd party integrations (see "Works with Xfinity" page)
- out: 3rd party Marketing/Analytics endpoints

### OOS Activity Types
- DoS / DDoS / wireless jamming
- Email spoofing (SPF/DKIM/DMARC)
- Automated scan reports without PoC
- Physical open chassis attacks (screws/breaking casing required)
- Pre-release/Beta/RC product versions
- Products no longer under active support
- Already known vulnerabilities (unless first external reporter)
- Third-party tools for cracking/validating secrets
- Rooted/jailbroken device required attacks
- Duplicate/known submissions
- Social engineering
- Theoretical security issues
- Protocol-specific flaws

---

## Access

- Must be a current Xfinity subscriber for comprehensive testing
- Non-subscribers can test with limited available surface

---

## Notes

- Program: coordinated disclosure (provide copy to Comcast before publication; no public disclosure until fully remediated)
- Do NOT contact Comcast executives/employees directly — use Bugcrowd platform only (violation = disqualification + potential ban)
- PGP key: see program page (securitydefectreporting@comcast.com)
- Rewards factor: impact assessment + researcher interaction + report quality/accuracy
