# WordPress

> Platform: HackerOne — https://hackerone.com/wordpress
> Type: BBP
> Bounty: N/A (VDP)
> Avg bounty: $300–$325
> Response efficiency: 51% | Avg first response: N/A | Total paid: $100,000
> Last scope update: 2021-09-02

## Scope

- in:  *.wordpress.org    # type: wildcard # max: critical
- in:  *.buddypress.org,bbpress.org,profiles.wordpress.org    # type: wildcard # max: critical
- in:  *.wordcamp.org    # type: wildcard # max: critical
- in:  *.wordpress.net    # type: wildcard # max: low
- in:  munin-*.wordpress.org    # type: wildcard # max: low
- in:  api.wordpress.org    # type: url # max: critical
- in:  planet.wordpress.org    # type: url # max: critical
- in:  doaction.org    # type: url # max: critical
- in:  codex.wordpress.org,codex.bbpress.org,codex.buddypress.org    # type: url # max: medium
- in:  mercantile.wordpress.org    # type: url # max: medium
- in:  lists.wordpress.org    # type: url # max: medium
- in:  wordpressfoundation.org    # type: url # max: medium
- in:  irclogs.wordpress.org    # type: url # max: low
- in:  WordPress Core    # type: repo # max: critical
- in:  BuddyPress Core    # type: repo # max: critical
- in:  BBPress Core    # type: repo # max: critical
- in:  *.trac.wordpress.org, *.svn.wordpress.org, *.git.wordpress.org, github.com/WordPress    # type: repo # max: critical
- in:  Gutenberg    # type: repo # max: critical
- in:  GlotPress    # type: repo # max: critical
- in:  WP-CLI    # type: repo # max: critical
- in:  Official WordPress plugins    # type: repo # max: critical
- in:  gutenberg.run    # type: url # max: low
- out:  *.wordpress.com    # type: wildcard # max: none
- out:  status.wordpress.org,glotpress.blog,wordpress.tv    # type: url # max: none
- out:  https://github.com/wordpress-mobile/    # type: repo # max: none
- out:  Digital Ocean, AWS, etc    # type: other # max: none
- out:  Archived GitHub repositories    # type: other # max: none
- out:  org.wordpress.android    # type: android_app # max: none
- out:  335703880    # type: ios_app # max: none
- out:  https://github.com/wordpress-mobile/WordPress-iOS    # type: repo # max: none
- out:  wordpress.tv    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $100,000

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
