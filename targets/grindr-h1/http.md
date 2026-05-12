# Grindr

> Platform: HackerOne — https://hackerone.com/grindr
> Type: BBP
> Bounty: Low $250 | Medium $800 | High $1,500 | Critical $4,000
> Avg bounty: $250–$250
> Response efficiency: 94% | Avg first response: N/A | Total paid: $46,752
> Last scope update: 2026-04-24

## Scope

- in:  *.grindr.io    # type: wildcard # max: critical
- in:  *.grindr.com    # type: wildcard # max: critical
- in:  *.grindr.mobi    # type: wildcard # max: critical
- in:  web.grindr.com    # type: url # max: critical
- in:  com.grindrapp.android    # type: android_app # max: critical
- in:  319881193    # type: ios_app # max: critical
- in:  *.dev.grindr.io    # type: wildcard # max: medium # not eligible for bounty
- in:  *.dev2.grindr.io    # type: wildcard # max: medium # not eligible for bounty
- in:  preprod1.grindr.com    # type: url # max: medium # not eligible for bounty
- in:  *.grindr.work    # type: wildcard # max: critical
- in:  hue.dsci.grindr.io    # type: url # max: critical
- in:  jupyter.dsci.grindr.io    # type: url # max: critical
- in:  reporting-portal.grindr.com    # type: url # max: critical
- in:  spammer-monitor.dsci.grindr.io    # type: url # max: critical
- in:  vpn.preprod.dev.grindr.io    # type: url # max: critical
- in:  airflow-beta-master.dsci.grindr.io    # type: url # max: critical
- in:  admin.grindr.com    # type: url # max: critical
- in:  superset.dsci.grindr.io    # type: url # max: critical
- out:  *.intomore.com    # type: wildcard # max: none
- out:  *.grindrads.com    # type: wildcard # max: none
- out:  selfservice.grindr.com    # type: url # max: none
- out:  go.grindr.com    # type: url # max: none
- out:  grindr.atlassian.net    # type: url # max: none
- out:  blog.grindr.com    # type: url # max: none
- out:  help.grindr.com    # type: url # max: none
- out:  grindrbloop.com    # type: url # max: none
- out:  shop.grindrbloop.com    # type: url # max: none
- out:  kindr.grindr.com    # type: url # max: none
- out:  https://github.com/grindrlabs    # type: url # max: none
- out:  shop.grindr.com    # type: url # max: none
- out:  investors.grindr.com    # type: url # max: none
- out:  grindrtogo.grindr.com    # type: url # max: none
- out:  status.grindr.com    # type: url # max: none
- out:  github.com/thesokrin/vfd    # type: repo # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $46,752
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
