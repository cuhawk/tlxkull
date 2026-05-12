# bitdefenderbox2 — Bitdefender Box v2 (Bugcrowd BBP)

> **TYPE: Hardware/IoT device** — Requires physical Bitdefender Box v2 device (buy or qualify as Expert Researcher)
> Scope: vulnerabilities exploitable as a guest or remotely against the BOX hardware itself.
> Cloud app bugs → report to https://bugcrowd.com/bitdefender (separate program)

## Program info
- URL: https://bugcrowd.com/engagements/bitdefenderbox2
- Type: hardware / IoT
- Scope rating: 1/4
- Started: Feb 22, 2018

## Rewards
- P1: $2,500 – $5,000
- P2: $1,000 – $2,500
- P3: $500 – $1,000
- P4: $200 – $500

## Reward structure (from description)
- Remote RCE (not same LAN): ~$5,000
- Remote RCE (same LAN): ~$2,500
- Remote access/control without auth (not same LAN): varies by impact
- Remote access/control without auth (same LAN): varies by impact
- DoS (remote, not same LAN): $2,500
- DoS (same LAN): $1,000

## In scope
- type: hardware
  url: bitdefenderbox2 (physical device — Bitdefender Box v2)
  notes: vulnerabilities exploitable as guest or remotely; must own device or qualify as Expert Researcher

## Out of scope
- Bitdefender Central mobile apps (Android / iOS)
- central.bitdefender.com (webapp)
- Bitdefender Total Security / other Bitdefender products
- Attacking your own device from BOX Administrator standpoint

## Notes
- Box communicates via cloud app; cloud app bugs → https://bugcrowd.com/bitdefender
- Researchers must supply own device; acquire via Bitdefender website or Expert Researcher program
- Mobile app (Bitdefender Central): not in scope, but impact allowing control of someone else's device may be reviewed
