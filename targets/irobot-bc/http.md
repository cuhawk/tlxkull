# iRobot — Bugcrowd BBP
# https://bugcrowd.com/engagements/irobot
# Category: Electronics | Safe harbor: full | Started: Aug 24, 2017

## Scope

### Tier 1 — iRobot Cloud API (P1 $1000-$1500)
- in: https://aspen-ecommerce-prod.iot.irobotapi.com/dev/v1/ecommerce/entitlements [GET,POST]
- in: https://aspen-ecommerce-prod.iot.irobotapi.com/dev/v1/ecommerce/entitlements/{entitlement_id} [PUT,DELETE]
- in: https://zuora-ecommerce-prod.iot.irobotapi.com/dev/v1/ecommerce/notifications/raas [POST]
- in: https://aspen-ecommerce-prod.iot.irobotapi.com/dev/v1/ecommerce/robots/{robot_id}/entitlements [GET]
- in: https://aspen-ecommerce-prod.iot.irobotapi.com/dev/v1/ecommerce/users/{user_id}/entitlements [GET]

### Tier 2 — iRobot Devices (P1 $3500-$4500) [targets loading]
- in: iRobot Roomba™ 105, 205, 405, 505, 705 (cloud-connected)
# NOTE: Roomba models confirmed from CrowdStream: "iRobot Roomba™ 105" was target of accepted P1 Apr 2026

### Tier 3 — iRobot Mobile Apps (P1 $2500-$3000) [targets loading]
- in: Roomba Home™ iOS app
- in: Roomba Home™ Android app
- out: Classic iRobot Home Mobile Apps (iOS/Android)

### Tier 4 — iRobot Commercial Web Properties (P1 $750-$1000) [targets loading]
- in: (loading — visit https://bugcrowd.com/engagements/irobot for current list)

### Tier 5 — Other iRobot Web Apps (no monetary reward)
- in: https://homesupport.irobot.com (examples only, no bounty)
- in: https://media.irobot.com
- in: https://investor.irobot.com
- in: https://answers.irobot.com

## Out of scope
- Any iRobot domain/product not explicitly listed above
- DoS/DDoS
- Automated scanning tools
- Contacting iRobot support via automated tools
- Customer data or robots not owned by researcher
- DNS vulnerabilities

## Notes
- No automated scanners (Zap/Burp/Acunetix/Nikto/Nessus etc)
- Custom scripts/fuzzers allowed at <50 req/sec
- Self-provisioned account via @bugcrowdninja.com email
- Test Robot IDs: 6977840021925810, 3144460C10810750, 2A80AB73B5634DB9
- No disclosure
- Program reopened Jun 2025 after scope update
