# Ring

> Platform: HackerOne — https://hackerone.com/ring
> Type: BBP
> Bounty: Low $200–$500 | Medium $600–$4,000 | High $6,000–$8,000 | Critical $25,000–$30,000
> Avg bounty: $200–$400
> Response efficiency: 97% | Avg first response: N/A | Total paid: $341,825
> Last scope update: 2025-11-11

## Scope

- in:  https://*.immedia-semi.com/*    # type: wildcard # max: critical
- in:  https://*.blinkforhome.com/*    # type: wildcard # max: critical
- in:  prd-ring-web-us.prd.rings.solutions    # type: url # max: critical
- in:  publicsafety.ring.com    # type: url # max: critical
- in:  https://ring.com/*    # type: other # max: critical
- in:  https://api.ring.com/*    # type: other # max: critical
- in:  https://fw.ring.com/*    # type: other # max: critical
- in:  https://app.ring.com/*    # type: other # max: critical
- in:  https://admin.ring.com/*    # type: other # max: critical
- in:  https://nw.ring.com/*    # type: other # max: critical
- in:  https://oauth.ring.com/*    # type: other # max: critical
- in:  https://billing.ring.com/*    # type: other # max: critical
- in:  Video Doorbell    # type: firmware # max: critical
- in:  Peephole Cam    # type: firmware # max: critical
- in:  Indoor Cam    # type: firmware # max: critical
- in:  Stickup Cam    # type: firmware # max: critical
- in:  Chime    # type: firmware # max: critical
- in:  Ring Alarm    # type: firmware # max: critical
- in:  Ring Smart Lighting Bridge    # type: firmware # max: critical
- in:  Blink Outdoor    # type: firmware # max: critical
- in:  Blink Indoor    # type: firmware # max: critical
- in:  Blink Sync Module 2    # type: firmware # max: critical
- in:  Blink Mini    # type: firmware # max: critical
- in:  Blink Video Doorbell    # type: firmware # max: critical
- in:  com.immediasemi.android.blink    # type: android_app # max: critical
- in:  com.ring.neighborhoods    # type: android_app # max: critical
- in:  com.ringapp    # type: android_app # max: critical
- in:  1013961111    # type: ios_app # max: critical
- in:  1218902777    # type: ios_app # max: critical
- in:  926252661    # type: ios_app # max: critical
- out:  Devices    # type: other # max: none
- out:  Services, Apps, Mobile    # type: other # max: none
- out:  Anything not in scope    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $341,825
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
