# Superbet

> Platform: HackerOne — https://hackerone.com/superbet
> Type: BBP
> Bounty: Low $250 | Medium $1,000 | High $5,000 | Critical $10,000
> Avg bounty: $250–$474
> Response efficiency: 99% | Avg first response: N/A | Total paid: $160,000
> Last scope update: 2026-04-23

## Scope

- in:  *.superbet.ro    # type: wildcard # max: critical
- in:  *.superbet.rs    # type: wildcard # max: critical
- in:  *.superbet.com    # type: wildcard # max: critical
- in:  *.spinaway.com    # type: wildcard # max: critical
- in:  *.luckydays.com    # type: wildcard # max: critical
- in:  *.luckydays.ca    # type: wildcard # max: critical
- in:  *.napoleoncasino.be    # type: wildcard # max: critical
- in:  *.napoleondice.be    # type: wildcard # max: critical
- in:  *.napoleongames.be    # type: wildcard # max: critical
- in:  *.napoleonsports.be    # type: wildcard # max: critical
- in:  *.superbet.pl    # type: wildcard # max: critical
- in:  *.happening.dev    # type: wildcard # max: critical
- in:  *.superbet.gr    # type: wildcard # max: critical
- in:  superbet.bet.br    # type: url # max: critical
- in:  https://napoleoncasino.be/en-be/game/hogamba-crash?demo=false    # type: url # max: critical
- in:  https://superbet.ro    # type: url # max: critical
- in:  https://superbet.pl    # type: url # max: critical
- in:  https://napoleoncasino.be    # type: url # max: critical
- in:  https://napoleonsports.be    # type: url # max: critical
- in:  https://napoleondice.be    # type: url # max: critical
- in:  https://napoleongames.be    # type: url # max: critical
- in:  https://superbet.rs    # type: url # max: critical
- in:  WGP Slot Games    # type: other # max: critical
- in:  https://napoleoncasino.be/nl-be/game/plinko-napoleon?demo=false    # type: other # max: critical
- in:  ro.superbet.sport    # type: android_app # max: critical
- in:  ro.superbet.games    # type: android_app # max: critical
- in:  *.magicjackpot.ro    # type: wildcard # max: critical
- out:  *.epic.superbet.ro    # type: wildcard # max: none
- out:  https://legacy-web.superbet.ro/session/login    # type: url # max: none
- out:  affiliates.superbet.com    # type: url # max: none
- out:  affiliates.superbet.rs    # type: url # max: none
- out:  affiliate.napoleongames.be    # type: url # max: none
- out:  https://retail.prod.incubator.superbet.ro/ssbt-api/    # type: url # max: none
- out:  http://surveys.superbet.com    # type: url # max: none
- out:  lp.superbet.pl    # type: url # max: none
- out:  lp.superbet.ro    # type: url # max: none
- out:  lp.superbet.com    # type: url # max: none
- out:  lp.superbet.rs    # type: url # max: none
- out:  lp.superbet.bet.br    # type: url # max: none
- out:  test.epic.superbet.ro    # type: url # max: none
- out:  test-gw.epic.superbet.ro    # type: url # max: none
- out:  https://legacy-web-stage.superbet.ro/metrics    # type: url # max: none
- out:  *old.superbet.ro/*    # type: wildcard # max: none
- out:  https://gw.epic.superbet.ro/api/v1/users/authenticate    # type: url # max: none
- out:  https://ct-dev-www.superbet.ro    # type: url # max: none
- out:  https://ax-www-pub.superbet.ro    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $160,000
- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
