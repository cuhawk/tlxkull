# hpe-networking-product-public — HPE Networking Product Public Program (Bugcrowd)

platform: bugcrowd
program_url: https://bugcrowd.com/engagements/hpe-networking-product-public
category: bbp
safe_harbor: full
disclosure: coordinated (60-day wait after advisory before public disclosure)
credentials: none (firmware/hardware; download OVAs from provided links)

## Rewards

### Group 1 (Increased bounties — AOS-10, AOS-CX, New Aruba Central)
| P1 | P2 | P3 | P4 |
|----|----|----|----|
| $5,000 | $3,000 | $1,200 | $600 |

### Group 2 (Standard bounties)
| P1 | P2 | P3 | P4 |
|----|----|----|----|
| $2,500 | $1,500 | $600 | $300 |

### Aruba Central - Old/Original UI (P1/P2 only — deprecated)
| P1 | P2 |
|----|-----|
| $2,500 | $1,500 |

### Group 3 (No monetary rewards — CVE + credit only)
- Aruba AirWave AMP
- Aruba InstantOn Switches
- Aruba User Experience Insight Sensors

## Scope

### Group 1 (In scope — higher priority, increased rewards)

- in: HPE Aruba Networking Wireless - AOS-10.7 and above Gateways (GW) — type: firmware/hardware
- in: HPE Aruba Networking Wireless - AOS-10.7 and above Access Points (AP) — type: firmware/hardware
- in: HPE Aruba Networking Central - New UI — type: web (*.central.arubanetworks.com)
- in: ArubaOS-CX Switches — type: firmware/hardware

### Group 2 (In scope — standard rewards)

- in: HPE Aruba Networking Wireless - AOS-8 Controllers — type: firmware/hardware
- in: HPE Aruba Networking Wireless - AOS-8 Instant AP (IAP) — type: firmware/hardware
- in: HPE Aruba Networking Wireless - AOS-10.4 Gateways (GW) — type: firmware/hardware
- in: HPE Aruba Networking Wireless - AOS-10.4 Access Points (AP) — type: firmware/hardware
- in: HPE Aruba Networking ClearPass Policy Manager (versions 6.11.x or 6.12.x) — type: hardware/software
- in: HPE Aruba Networking EdgeConnect SD-WAN Orchestrator — type: network_device
- in: HPE Networking Instant On APs and supporting backend infrastructure — type: hardware/api
- in: HPE Aruba Networking Fabric Composer — type: software
- in: HPE Aruba Networking NetEdit — type: software
- in: HPE Aruba Networking Private 5G — type: hardware/api
- in: HPE Aruba Networking SSE — type: web/desktop_app
- in: HPE Aruba Networking VIA — type: client_software

### Aruba Central Old UI (P1/P2 only)

- in: *.central.arubanetworks.com (old UI only — deprecated, EOL by end 2025) — type: wildcard

### Group 3 (CVE only, no cash)

- in: Aruba AirWave AMP (v8.3.0.4) — type: software
- in: Aruba InstantOn Switches — type: hardware
- in: Aruba User Experience Insight Sensors + https://dashboard.capenetworks.com/login — type: hardware/url

## Out-of-scope

- out: *.arubanetworks.com (not listed as in-scope)
- out: *.hpe.com (use https://hackerone.com/hpe_vdp instead)
- out: https://action.arubainstanton.com
- out: Reflected XSS on *.cloudguest.central.arubanetworks.com
- out: instant.arubanetworks.com / securelogin.arubanetworks.com (customer-owned infrastructure)
- out: HPE Networking Aruba Instant On Switches (no bounty)

## Firmware / OVA Download Links

- AOS-10.7 OVA: https://ln5.sync.com/dl/5ad62de10#bvefcjzk-uawzt3im-682mvu62-axihc3qj
- AOS-8 OVA: same link above
- AOS-CX Switch Simulator OVA: https://ln5.sync.com/dl/983c21430#hz7kuqsh-abef6rii-259d49v5-5f343sdd

## Version Requirements

- AOS-10: prefer 10.7.x (increased rewards); 10.4.x accepted at standard bounties
- AOS-8: prefer 8.13.x.x (latest LSR as of Jul 2025)
- AOS-CX: latest version
- ClearPass: 6.11.x or 6.12.x
- Static analysis without exploitability proof = rejected
- start-shell command bypass on AOS-CX = not accepted

## Notes

- Infrastructure (*.hpe.com): report to https://hackerone.com/hpe_vdp — not this program
- Contact: hpe-networking-bugcrowd@hpe.com for scope questions
- Same vuln in multiple branches = duplicate (only first report rewarded)
- Public disclosure: 60 days after HPE advisory; coordinate via Bugcrowd
- New Aruba Central: enable "New Central" slider in top-right of Central UI
- Old Central: P1/P2 only accepted (deprecated, being replaced)
- Rate limiting / DoS / open redirects = OOS
- DMARC without demonstrated impact = OOS
- Authenticated DoS requiring admin = OOS
