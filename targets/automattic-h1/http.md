# Automattic

> Platform: HackerOne — https://hackerone.com/automattic
> Type: BBP
> Bounty: N/A (VDP)
> Avg bounty: $100–$150
> Response efficiency: 68% | Avg first response: N/A | Total paid: $230,000
> Last scope update: 2026-04-08

## Scope

- in:  *.tumblr.com    # type: wildcard # max: critical
- in:  *.srvcs.tumblr.com    # type: wildcard # max: critical
- in:  api.tumblr.com    # type: url # max: critical
- in:  safe.tumblr.com    # type: url # max: critical
- in:  secure.tumblr.com    # type: url # max: critical
- in:  assets.tumblr.com    # type: url # max: critical
- in:  embed.tumblr.com    # type: url # max: critical
- in:  www.tumblr.com    # type: url # max: critical
- in:  t.umblr.com    # type: url # max: critical
- in:  wordpress.com    # type: url # max: critical
- in:  akismet.com    # type: url # max: critical
- in:  mailpoet.com    # type: url # max: critical
- in:  my.pressable.com    # type: url # max: critical
- in:  parse.ly    # type: url # max: critical
- in:  simplenote.com    # type: url # max: high
- in:  simperium.com    # type: url # max: high
- in:  gravatar.com    # type: url # max: high
- in:  clay.earth    # type: url # max: high
- in:  wpscan.com    # type: url # max: high
- in:  intensedebate.com    # type: url # max: medium
- in:  Jetpack    # type: repo # max: critical
- in:  WooCommerce    # type: other # max: critical
- in:  Crowdsignal    # type: other # max: critical
- in:  WordPress Plugins & Themes    # type: other # max: critical
- in:  WordPress VIP    # type: other # max: critical
- in:  WP Cloud    # type: other # max: critical
- in:  Texts    # type: other # max: high
- in:  Beeper    # type: other # max: high
- in:  com.tumblr    # type: android_app # max: high
- in:  com.tumblr.tumblr    # type: ios_app # max: high
- in:  com.clay.ios    # type: ios_app # max: high
- in:  WordPress.com VIP    # type: other # max: critical
- out:  scrollkit.com,*.scrollkit.com    # type: wildcard # max: none
- out:  learnboost.com,*.learnboost.com    # type: wildcard # max: none
- out:  *.txmblr.com    # type: wildcard # max: none
- out:  afterthedeadline.com,*.afterthedeadline.com    # type: wildcard # max: none
- out:  polishmywriting.com,*.polishmywriting.com    # type: wildcard # max: none
- out:  *.survey.fm    # type: wildcard # max: none
- out:  *.poll.fm    # type: wildcard # max: none
- out:  *.crowdsignal.net    # type: wildcard # max: none
- out:  try.pressable.com    # type: url # max: none
- out:  atavist.com    # type: url # max: none
- out:  happy.tools    # type: url # max: none
- out:  */xmlrpc.php    # type: other # max: none
- out:  learnboost.com,*.learnboost.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $230,000

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
