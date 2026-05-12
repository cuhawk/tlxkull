# netgear — NETGEAR Cash Rewards (Bugcrowd)

platform: bugcrowd
program_url: https://bugcrowd.com/engagements/netgear
category: bbp
safe_harbor: none (nondisclosure / legal terms only)
disclosure: coordinated
status: PAUSED (as of May 4, 2026 — indefinitely; do NOT test until resumed)

## Rewards

| Special | P1 | P2 | P3 | P4 |
|---------|----|----|----|----|
| $15,000 (Remote unauth admin access via internet) | $2,000 | $1,000 | $500 | $300 |

Special reward: $10,000 for remote unauthorized access to full NETGEAR customer database.
CVSS score takes precedence over VRT when discrepancies exist.

## In-Scope Products (Firmware / Router Web Management / Mobile Apps)

- in: Nighthawk Pro Gaming Routers — type: iot_firmware
- in: Nighthawk Pro Gaming Switches — type: iot_firmware
- in: Nighthawk Routers — type: iot_firmware
- in: Nighthawk Switches — type: iot_firmware
- in: Orbi — type: iot_firmware
- in: Insight Managed Smart Cloud Wireless Access Points — type: iot_web
- in: Meural Canvas and Frames — type: iot_firmware
- in: Cloud Infrastructure supporting above devices (see Bugcrowd targets list)

Latest firmware versions only eligible. Find by model at: https://www.netgear.com/support/

## OOS

- All NETGEAR products/properties not explicitly listed (except High Impact targets)
- Arlo products (separate program: Arlo Cash Rewards Program)
- NETGEAR AWS infrastructure
- Automated scanning attacks
- DoS/DDoS
- Secure/HTTPOnly cookie flags on non-sensitive cookies
- Duplicate reports / already-known issues
- Version disclosure without demonstrated exploit
- Using findings from one vuln to exploit further without permission

## Notes

- PROGRAM CURRENTLY PAUSED — do not test
- Arlo products: separate BBP at bugcrowd.com/arlo
- Non-cash scope gets kudos rewards only (see netgearkudos program)
- Same vuln across multiple devices = duplicates; bonus possible for enumeration of affected devices
- Rewards increased Jan 2025 to $300–$2,000 range
- High Impact: Remote unauth internet-facing admin access = $15,000 (default config)
