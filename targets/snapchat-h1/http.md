# Snapchat

> Platform: HackerOne — https://hackerone.com/snapchat
> Type: BBP
> Bounty: Low $4,000 | Medium $1,000–$10,000 | High $2,500–$20,000 | Critical $5,000–$35,000
> Avg bounty: $250–$375
> Response efficiency: 97% | Avg first response: N/A | Total paid: $1,563,281
> Last scope update: 2023-11-01

## Scope

- in:  accounts.snapchat.com    # type: url # max: critical
- in:  app.snapchat.com    # type: url # max: critical
- in:  *.sc-core.net    # type: url # max: critical
- in:  business.snapchat.com    # type: url # max: critical
- in:  store.snapchat.com    # type: url # max: critical
- in:  web.snapchat.com    # type: url # max: critical
- in:  kit.snapchat.com    # type: url # max: high
- in:  snappublisher.snapchat.com    # type: url # max: high
- in:  geofilters.snapchat.com    # type: url # max: high
- in:  ads.snapchat.com    # type: url # max: high
- in:  create.snapchat.com    # type: url # max: high
- in:  my.snapchat.com    # type: url # max: high
- in:  businesshelp.snapchat.com    # type: url # max: high
- in:  www.bitmoji.com    # type: url # max: medium
- in:  www.bitstrips.com    # type: url # max: medium
- in:  blog.playcanvas.com    # type: url # max: medium
- in:  code.playcanvas.com    # type: url # max: medium
- in:  developer.playcanvas.com    # type: url # max: medium
- in:  forum.playcanvas.com    # type: url # max: medium
- in:  launch.playcanvas.com    # type: url # max: medium
- in:  login.playcanvas.com    # type: url # max: medium
- in:  msg.playcanvas.com    # type: url # max: medium
- in:  playcanvas.com    # type: url # max: medium
- in:  relay.playcanvas.com    # type: url # max: medium
- in:  rt.playcanvas.com    # type: url # max: medium
- in:  store.playcanvas.com    # type: url # max: medium
- in:  playcanv.as    # type: url # max: medium
- in:  scan.snapchat.com    # type: url # max: low
- in:  spectacles.com    # type: url # max: low
- in:  map.snapchat.com    # type: url # max: low
- in:  story.snapchat.com    # type: url # max: low
- in:  https://lensstudio.snapchat.com/api/    # type: repo # max: critical
- in:  *.sc-corp.net    # type: other # max: critical
- in:  Tier A - Core Assets    # type: other # max: critical
- in:  Tier B - Non Core (Bitmoji, Playcanvas)    # type: other # max: medium
- in:  com.snapchat.android    # type: android_app # max: critical
- in:  com.bitstrips.imoji    # type: android_app # max: medium
- in:  Lens Studio    # type: downloadable_executables # max: medium
- in:  com.toyopagroup.picaboo    # type: ios_app # max: high
- in:  com.bitstrips.imoji    # type: ios_app # max: medium
- in:  Snap Camera    # type: downloadable_executables # max: medium
- in:  www.scan.me    # type: url # max: low
- out:  http://dev*.playcanvas.com    # type: wildcard # max: none
- out:  returns.spectacles.com    # type: url # max: none
- out:  support.snapchat.com    # type: url # max: none
- out:  dev.playcanv.as    # type: url # max: none
- out:  Spectacles charging case    # type: firmware # max: none
- out:  Spectacles    # type: firmware # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $1,563,281

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
